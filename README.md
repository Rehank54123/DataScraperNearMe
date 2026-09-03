# DataScraperNearMe - Tromso Barbers

This project automates the extraction of barbershop data from Google Maps for the Tromso area, enriches the data with proximity information to UiT (The Arctic University of Norway), and verifies if the barbershop has an existing booking system.

## Features
- **Scraper**: Uses Playwright to extract the name, address, phone number, and website of barbershops directly from Google Maps search results.
- **Enrichment**: 
  - Uses `geopy` to calculate the straight-line distance from each barbershop to UiT.
  - Visits each extracted website and searches for common booking keywords (`book`, `appointment`, `ledig tid`, `timma`, etc.) to determine if a booking system exists.
- **Export**: Generates a clean `barbers_tromso.csv` file that can be easily imported into Google Sheets for sharing.

## Setup Instructions

1. Install Python 3.8 or higher.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the Playwright browser binaries:
   ```bash
   playwright install chromium
   ```

## Running the Scraper

To run the data collection, execute the main script:
```bash
python main.py
```

The script will launch a visible Chrome browser. Please **do not interact with or close** this browser window while it scrolls through results and extracts URLs. Once complete, it will verify the websites in the background and output a `barbers_tromso.csv` file in this directory.

## Uploading to Google Sheets

1. Open [Google Sheets](https://sheets.google.com).
2. Create a Blank Spreadsheet.
3. Go to **File -> Import -> Upload**.
4. Drag and drop the `barbers_tromso.csv` file.
5. Select "Replace spreadsheet" and click **Import data**.
6. Share the sheet with your friend!
