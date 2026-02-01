from sec_edgar_downloader import Downloader

if __name__ == "__main__":
    dl = Downloader()
    dl.get("10-K", "AAPL", amount=1)
    print("Downloaded latest 10-K for AAPL (Apple Inc.) to ./SEC-Edgar-filings/")
