
# Service for integrating with USAspending ORM
import usaspending


class USASpendingService:
    def __init__(self):
        self.client = usaspending.client.Client()

    def get_contracts(self, **kwargs):
        # Example: fetch contracts with filters
        return self.client.get_contracts(**kwargs)
