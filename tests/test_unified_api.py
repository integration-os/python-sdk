import os
import pytest
from random import randint
from typing import AsyncGenerator
from dotenv import load_dotenv
from integrationos import IntegrationOS, ListFilter
from integrationos.types.models import Contacts, Emails
from integrationos.types.generic import Response

load_dotenv()

API_KEY = str(os.getenv('INTEGRATIONOS_API_KEY'))
CONNECTION_KEY = str(os.getenv('INTEGRATIONOS_CONNECTION_KEY'))
INTEGRATIONOS_BASE_URL = str(os.getenv('INTEGRATIONOS_BASE_URL')) or "https://api.integrationos.com/v1"

@pytest.fixture(name="client")
async def client_fixture() -> AsyncGenerator[IntegrationOS, None]:
    """Fixture to provide an initialized IntegrationOS client."""
    async with IntegrationOS(API_KEY, INTEGRATIONOS_BASE_URL) as client:
        yield client

@pytest.fixture(name="test_contact")
def test_contact_fixture() -> Contacts:
    """Fixture to provide a test contact."""
    return Contacts(
        firstName="John",
        lastName="Doe",
        emails=[
            Emails(
                email=f"python-sdk-{randint(1, 10000)}@example.com"
            )
        ]
    )

@pytest.mark.asyncio
class TestUnifiedAPI:
    """Test suite for unified API functionality."""

    async def test_full_contact_lifecycle(self, client: AsyncGenerator[IntegrationOS, None], test_contact: Contacts):
        """Test the complete lifecycle of a contact."""
        integrate = await anext(client)
        
        # Test Create
        create_response = await integrate.contacts(CONNECTION_KEY).create(test_contact)
        assert create_response.unified is not None, "Expected unified data in response"
        assert create_response.unified.id is not None, "Expected contact ID in response"
        contact_id = create_response.unified.id
        print(f"\n✅ Created Contact with ID: {contact_id}")

        # Test Get
        get_response = await integrate.contacts(CONNECTION_KEY).get(contact_id)
        assert get_response.unified is not None, "Expected unified data in response"
        assert get_response.unified.id == contact_id, "ID mismatch in get response"
        print(f"\n✅ Retrieved contact: {get_response.unified.model_dump_json()}")

        # Test Update
        update_data = Contacts(
            firstName="Updated First name",
            lastName="Updated Last name"
        )
        update_response = await integrate.contacts(CONNECTION_KEY).update(contact_id, update_data)
        assert update_response.meta is not None, "Expected meta data in update response"

        # Verify Update
        verify_response = await integrate.contacts(CONNECTION_KEY).get(contact_id)
        assert verify_response.unified is not None, "Expected unified data in verify response"
        assert verify_response.unified.firstName == "Updated First name", "First name not updated"
        assert verify_response.unified.lastName == "Updated Last name", "Last name not updated"
        print(f"\n✅ Updated and verified contact: {verify_response.unified.model_dump_json()}")

        # Test Delete
        delete_response = await integrate.contacts(CONNECTION_KEY).delete(contact_id)
        assert delete_response.meta is not None, "Expected meta data in delete response"
        
        # Verify Deletion
        try:
            await integrate.contacts(CONNECTION_KEY).get(contact_id)
            pytest.fail("Expected contact to be deleted")
        except Exception:
            pass
        
        print(f"\n✅ Successfully deleted contact")

    async def test_list_contacts(self, client: AsyncGenerator[IntegrationOS, None]):
        """Test listing contacts with different filters."""
        integrate = await anext(client)
        list_filter = ListFilter(limit=2)
        
        response = await integrate.contacts(CONNECTION_KEY).list(list_filter)
        assert response.unified is not None, "Expected unified data in response"
        assert len(response.unified) <= 2, "Expected no more than 2 contacts"
        assert response.pagination is not None, "Expected pagination data"
        
        print(f"\n✅ Successfully listed contacts: {[contact.model_dump_json() for contact in response.unified]}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
