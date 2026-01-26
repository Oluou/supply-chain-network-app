from sec_edgar_downloader import Downloader

if __name__ == "__main__":
    # Provide your company name and email address as required by the package
    dl = Downloader("Your Company Name", "your.email@example.com")
    dl.get("10-K", "AAPL", limit=1)
    print("Downloaded latest 10-K for AAPL (Apple Inc.) to ./SEC-Edgar-filings/")
