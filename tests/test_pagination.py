import os
import pytest
from typing import AsyncGenerator, List
from dotenv import load_dotenv
from integrationos import IntegrationOS, ListFilter
from integrationos.paginate import PaginationHelper
from integrationos.types.models import Contacts

load_dotenv()

API_KEY = str(os.getenv('INTEGRATIONOS_API_KEY'))
CONNECTION_KEY = str(os.getenv('INTEGRATIONOS_CONNECTION_KEY'))
INTEGRATIONOS_BASE_URL = str(os.getenv('INTEGRATIONOS_BASE_URL')) or "https://api.integrationos.com/v1"

@pytest.fixture(name="client")
async def client_fixture() -> AsyncGenerator[IntegrationOS, None]:
    """Fixture to provide an initialized IntegrationOS client."""
    async with IntegrationOS(API_KEY, INTEGRATIONOS_BASE_URL) as client:
        yield client

async def fetch_all_contacts(integrate: IntegrationOS, connection_key: str) -> List[Contacts]:
    """Helper function to fetch all contacts using pagination."""
    paginator = PaginationHelper[Contacts](
        lambda params: integrate.contacts(connection_key).list(params),
        filter=ListFilter(limit=30)
    )
    
    contacts: List[Contacts] = []
    total_fetched = 0

    while paginator.has_more_data():
        batch = await paginator.get_next_batch()
        contacts.extend(batch)
        total_fetched += len(batch)
        print(f"\n✅ Progress: Fetched batch of {len(batch)} contacts. Total: {total_fetched}")
    
    return contacts

@pytest.mark.asyncio
class TestPagination:
    """Test suite for pagination functionality."""

    async def test_fetch_all_contacts(self, client: AsyncGenerator[IntegrationOS, None]):
        """Test fetching all contacts with pagination."""
        integrate = await anext(client)
        contacts = await fetch_all_contacts(integrate, CONNECTION_KEY)
        
        assert isinstance(contacts, list), "Expected contacts to be a list"
        assert all(isinstance(contact, Contacts) for contact in contacts), "All items should be Contact instances"
        assert len(contacts) >= 0, "Expected to fetch zero or more contacts"
        
        print(f"\n✅ Successfully fetched {len(contacts)} contacts in total")

    @pytest.mark.parametrize("limit", [10, 20, 30])
    async def test_pagination_with_different_limits(self, client: AsyncGenerator[IntegrationOS, None], limit: int):
        """Test pagination with different batch sizes."""
        integrate = await anext(client)
        paginator = PaginationHelper[Contacts](
            lambda params: integrate.contacts(CONNECTION_KEY).list(params),
            filter=ListFilter(limit=limit)
        )

        first_batch = await paginator.get_next_batch()
        
        # Verify batch size respects the limit
        assert len(first_batch) <= limit, f"Batch size should not exceed the limit of {limit}"
        assert all(isinstance(contact, Contacts) for contact in first_batch), "All items should be Contact instances"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
