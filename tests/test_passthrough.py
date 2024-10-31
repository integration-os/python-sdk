import os
import pytest
from typing import AsyncGenerator, Dict, Any
from dotenv import load_dotenv
from integrationos import IntegrationOS
from integrationos.types.generic import Response

load_dotenv()

API_KEY = str(os.getenv('INTEGRATIONOS_API_KEY'))
CONNECTION_KEY = str(os.getenv('INTEGRATIONOS_PASSTHROUGH_CONNECTION_KEY'))
INTEGRATIONOS_BASE_URL = str(os.getenv('INTEGRATIONOS_BASE_URL')) or "https://api.integrationos.com/v1"
PASSTHROUGH_PATH = str(os.getenv('INTEGRATIONOS_PASSTHROUGH_PATH'))

@pytest.fixture(name="client")
async def client_fixture() -> AsyncGenerator[IntegrationOS, None]:
    """Fixture to provide an initialized IntegrationOS client."""
    async with IntegrationOS(API_KEY, INTEGRATIONOS_BASE_URL) as client:
        yield client

async def make_passthrough_request(
    client: IntegrationOS, 
    connection_key: str,
    method: str,
    path: str,
    data: Dict[str, Any],
    headers: Dict[str, str],
    query_params: Dict[str, str]
) -> Response[Any]:
    """Helper function to make passthrough requests."""
    return await client.passthrough(connection_key).call(
        method=method,
        path=path,
        data=data or {},
        headers=headers or {},
        query_params=query_params or {}
    )

@pytest.mark.asyncio
class TestPassthrough:
    """Test suite for passthrough functionality."""

    async def test_passthrough_request(self, client: AsyncGenerator[IntegrationOS, None]):
        integration = await anext(client)
        response = await make_passthrough_request(
            client=integration,
            connection_key=CONNECTION_KEY,
            method='POST',
            path=PASSTHROUGH_PATH,
            data={},
            headers={},
            query_params={}
        )
        
        assert response is not None, "Expected a response"
        assert response.passthrough is not None, "Expected passthrough data"
        print(f"\n✅ Successfully received passthrough response: {response}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
