from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re
import os

# Keywords for review analysis
TRAFFIC_KEYWORDS = ['wait', 'queue', 'vente', 'kø', 'busy', 'travelt']
DROPIN_KEYWORDS = ['drop-in', 'drop in']

def is_mobile_number(phone_str):
    if not phone_str or str(phone_str) == 'nan':
        return False
    # Remove all non-digits
    digits = re.sub(r'\D', '', str(phone_str))
    # Norwegian mobile numbers are 8 digits starting with 4 or 9
    # If they have the country code 47, it's 10 digits starting with 474 or 479
    if len(digits) == 8 and digits[0] in ['4', '9']:
        return True
    if len(digits) == 10 and digits.startswith('47') and digits[2] in ['4', '9']:
        return True
    return False

def calculate_score(row, reviews_text):
    score = 50
    notes = []

    # 1. Booking System
    if str(row.get('Has Booking System', 'Yes')).strip().lower() == 'no':
        score += 30
        notes.append("+30 (No existing system)")
    else:
        score -= 30
        notes.append("-30 (Already has booking system)")

    # 2. Phone Number
    if is_mobile_number(row.get('Phone', '')):
        score += 15
        notes.append("+15 (Mobile number)")

    # 3. Reviews Sentiment
    reviews_lower = reviews_text.lower()
    
    found_traffic = [kw for kw in TRAFFIC_KEYWORDS if kw in reviews_lower]
    if found_traffic:
        score += 15
        notes.append(f"+15 (Mentions traffic/wait: {found_traffic[0]})")
        
    found_dropin = [kw for kw in DROPIN_KEYWORDS if kw in reviews_lower]
    if found_dropin:
        score += 10
        notes.append("+10 (Mentions drop-in)")

    # Clamp score between 1 and 100
    score = max(1, min(100, score))
    
    return score, " | ".join(notes)

def score_leads(input_csv="barbers_tromso.csv", output_csv="barbers_tromso_scored.csv"):
    if not os.path.exists(input_csv):
        print(f"Input file '{input_csv}' not found. Please run main.py first.")
        return

    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    
    scores = []
    summary_notes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        for index, row in df.iterrows():
            url = row.get('Google Maps URL', '')
            name = row.get('Name', 'Unknown')
            
            reviews_text = ""
            if url and str(url) != 'nan':
                try:
                    print(f"[{index+1}/{len(df)}] Analyzing reviews for: {name}...")
                    page.goto(url, timeout=60000)
                    time.sleep(3) # Wait for Google Maps to render the sidebar
                    
                    # Extract review snippets shown on the main pane
                    # The class wiI7pd is commonly used by Google Maps for review text
                    review_elements = page.locator('span.wiI7pd')
                    
                    if review_elements.count() > 0:
                        texts = review_elements.all_inner_texts()
                        reviews_text = " ".join(texts)
                    
                except Exception as e:
                    print(f"  Error loading reviews for {name}: {e}")
            
            score, note = calculate_score(row, reviews_text)
            scores.append(score)
            summary_notes.append(note)
            
            print(f"  -> Score: {score}")

        browser.close()

    df['Lead Score (1-100)'] = scores
    df['Scoring Logic'] = summary_notes
    
    # Sort by Lead Score descending
    df = df.sort_values(by='Lead Score (1-100)', ascending=False)
    
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nScoring complete! Ranked leads saved to {output_csv}")

if __name__ == "__main__":
    score_leads()
