from playwright.sync_api import sync_playwright
import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import re

# UiT Coordinates
UIT_COORDS = (69.6813, 18.9730)
BOOKING_KEYWORDS = ['book', 'appointment', 'ledig tid', 'timma', 'bestill', 'timebestilling', 'reserver', 'booking']

def accept_cookies(page):
    try:
        button = page.locator('button:has-text("Accept all")')
        if button.count() > 0:
            button.first.click()
            time.sleep(2)
    except Exception as e:
        print("No cookie dialog or error:", e)

def scrape_barbers():
    results = []
    with sync_playwright() as p:
        # Run headed so we can see what's happening and avoid some bot detections
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        page.goto('https://www.google.com/maps/search/barber+in+Tromso/', timeout=60000)
        accept_cookies(page)
        
        time.sleep(5)
        print("Scrolling through results...")
        
        try:
            # Scroll to load more results. Google Maps uses a specific feed container.
            # We hover over the search results area and scroll down.
            page.mouse.move(200, 400)
            for _ in range(15):
                page.mouse.wheel(0, 2000)
                time.sleep(1.5)
        except Exception as e:
            print("Scrolling error:", e)
            
        print("Extracting URLs...")
        # Find all place links
        links = page.locator('a[href*="/maps/place/"]').all()
        urls = [link.get_attribute('href') for link in links]
        
        # Deduplicate and clean URLs
        urls = list(dict.fromkeys([u for u in urls if u]))
        print(f"Found {len(urls)} potential barber locations.")

        for url in urls:
            try:
                page.goto(url, timeout=60000)
                time.sleep(3)
                
                title = page.locator('h1').inner_text() if page.locator('h1').count() > 0 else "Unknown"
                
                # Extract Address
                address_loc = page.locator('button[data-item-id="address"]')
                address = address_loc.inner_text().replace('\n', ' ').strip() if address_loc.count() > 0 else ""
                
                # Extract Phone
                phone_loc = page.locator('button[data-item-id^="phone:tel:"]')
                if phone_loc.count() == 0:
                     phone_loc = page.locator('button[data-tooltip*="phone"]')
                phone = phone_loc.inner_text().replace('\n', ' ').strip() if phone_loc.count() > 0 else ""
                
                # Extract Website
                website_loc = page.locator('a[data-item-id="authority"]')
                if website_loc.count() == 0:
                    website_loc = page.locator('a[data-tooltip="Open website"]')
                website = website_loc.get_attribute('href') if website_loc.count() > 0 else ""
                
                # Check if Google Maps itself shows a booking/appointment link
                appointment_loc = page.locator('a[data-item-id="action:make_appointment"]')
                has_google_booking = "Yes" if appointment_loc.count() > 0 else "No"
                
                if title != "Unknown":
                    results.append({
                        'Name': title,
                        'Address': address,
                        'Phone': phone,
                        'Website': website,
                        'Has Google Booking': has_google_booking,
                        'Google Maps URL': url
                    })
                    print(f"Scraped: {title}")
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                
        browser.close()
    return pd.DataFrame(results)

def verify_and_enrich(df):
    geolocator = Nominatim(user_agent="barber_scraper_tromso")
    
    distances = []
    has_booking = []
    
    for index, row in df.iterrows():
        address = row['Address']
        dist = "Unknown"
        if address:
            try:
                search_address = f"{address}, Norway" if "Norway" not in address and "Norge" not in address else address
                location = geolocator.geocode(search_address, timeout=10)
                if location:
                    dist = round(geodesic(UIT_COORDS, (location.latitude, location.longitude)).km, 2)
            except Exception as e:
                print(f"Geocoding error for {address}: {e}")
        distances.append(dist)
        
        website = row['Website']
        booking_found = row.get('Has Google Booking', 'No')
        
        if website and booking_found == "No":
            try:
                resp = requests.get(website, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
                if resp.status_code == 200:
                    text = resp.text.lower()
                    if any(kw in text for kw in BOOKING_KEYWORDS):
                        booking_found = "Yes"
            except Exception as e:
                print(f"Error checking website {website}: {e}")
        has_booking.append(booking_found)
        
    df['Distance to UiT (km)'] = distances
    df['Has Booking System'] = has_booking
    return df

if __name__ == "__main__":
    print("Starting scraping process. Please do not close the browser window that opens...")
    df = scrape_barbers()
    if not df.empty:
        print("Scraping completed. Cross-examining data and calculating distances...")
        df_enriched = verify_and_enrich(df)
        
        # Clean up columns order
        df_enriched = df_enriched[['Name', 'Phone', 'Address', 'Distance to UiT (km)', 'Has Booking System', 'Website', 'Google Maps URL']]
        
        df_enriched.to_csv('barbers_tromso.csv', index=False, encoding='utf-8-sig')
        print("Data successfully saved to 'barbers_tromso.csv'. You can now import this into Google Sheets.")
    else:
        print("No data found. This might be due to a layout change in Google Maps.")
