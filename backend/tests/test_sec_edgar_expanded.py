from sec_edgar_downloader import Downloader

import os
import glob
import re
from datetime import datetime

# --- CONFIG ---


COMPANY = "0000320193"  # Apple Inc. CIK
TICKER = "AAPL"  # Apple Inc. ticker
FORM_TYPE = "10-K"
YEARS = [2023, 2022, 2021]  # Broaden to last 3 years
COMPANY_NAME = "Your Company Name"
EMAIL = "your.email@example.com"


# --- DOWNLOAD FILINGS ---
dl = Downloader()
dl.get(FORM_TYPE, COMPANY, amount=10)  # Download up to 10 most recent 10-Ks
dl.get(FORM_TYPE, TICKER, amount=10)  # Also try ticker for robustness

# --- FIND FILINGS FOR YEAR ---
search_dirs = [
    os.path.join("SEC-Edgar-filings", COMPANY, FORM_TYPE),
    os.path.join("SEC-Edgar-filings", TICKER, FORM_TYPE)
]
filings = []
for filings_dir in search_dirs:
    if os.path.exists(filings_dir):
        filings.extend(glob.glob(os.path.join(filings_dir, "*")))



def get_filing_year(filing_dir):
    txt_files = glob.glob(os.path.join(filing_dir, "*.txt"))
    if not txt_files:
        return None
    with open(txt_files[0], "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("FILED AS OF DATE:"):
                date_str = line.split(":")[1].strip()
                if len(date_str) >= 4:
                    return int(date_str[:4])
            if line.startswith("CONFORMED PERIOD OF REPORT:"):
                date_str = line.split(":")[1].strip()
                if len(date_str) >= 4:
                    return int(date_str[:4])
    return None

filings_by_year = {}
print("All found filings and their detected years (from metadata):")
for filing in filings:
    year = get_filing_year(filing)
    if year:
        print(f"{filing} -> {year}")
        if year not in filings_by_year:
            filings_by_year[year] = []
        filings_by_year[year].append(filing)
    else:
        print(f"{filing} -> year not detected")

filings_for_years = []
for year_filings in filings_by_year.values():
    filings_for_years.extend(year_filings)

# --- EXTRACT TEXT FROM FILING ---
def extract_text_from_filing(filing_path):
    txt_files = glob.glob(os.path.join(filing_path, "*.txt"))
    if not txt_files:
        return None
    with open(txt_files[0], "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# Only process the most recent filing
if filings_for_years:
    # Find the most recent by year (and if multiple, pick the latest by directory name)
    filings_with_years = [(filing, get_filing_year(filing)) for filing in filings_for_years]
    filings_with_years = [fw for fw in filings_with_years if fw[1] is not None]
    if filings_with_years:
        most_recent_year = max(filings_with_years, key=lambda x: x[1])[1]
        most_recent_filings = [fw[0] for fw in filings_with_years if fw[1] == most_recent_year]
        most_recent_filing = sorted(most_recent_filings)[-1]
        text = extract_text_from_filing(most_recent_filing)
        if text:
            # Extract the EX-21.1 section (subsidiaries table) as HTML
            ex21_match = re.search(r'<TYPE>EX-21.1[\s\S]*?<TEXT>([\s\S]*?)</TEXT>', text, re.IGNORECASE)
            if ex21_match:
                html = ex21_match.group(1)
                try:
                    from bs4 import BeautifulSoup
                except ImportError:
                    print("BeautifulSoup4 is required. Please install with 'pip install beautifulsoup4'.")
                    exit(1)
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')
                if table:
                    print("\nSubsidiaries Table from Most Recent Filing:\n")
                    print("| Subsidiary Name | Jurisdiction |")
                    print("|---|---|")
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            # Get text from the first and last cell (name, jurisdiction)
                            name = cells[0].get_text(strip=True)
                            jurisdiction = cells[-1].get_text(strip=True)
                            # Skip empty or header rows
                            if name and jurisdiction and name.lower() != 'subsidiaries of' and 'jurisdiction' not in jurisdiction.lower():
                                print(f"| {name} | {jurisdiction} |")
                else:
                    print("No subsidiaries table found in the EX-21.1 section.")
            else:
                print("Subsidiaries EX-21.1 section not found in the most recent filing.")
        else:
            print(f"No text found for {most_recent_filing}")
    else:
        print("No filings with detected year found.")
else:
    print("No filings found.")
