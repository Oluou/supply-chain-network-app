
# Service for integrating with EDGAR/edgartools
import edgar


class EdgarService:
    def __init__(self):
        self.client = edgar.tools.Client()

    def get_filings(self, cik, filing_type="10-K"):
        # Example: fetch filings for a company
        return self.client.get_filings(cik=cik, filing_type=filing_type)
