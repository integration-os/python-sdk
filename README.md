# IntegrationOS Python SDK

The IntegrationOS Python library offers a strongly-typed, Pydantic-based interface for seamless interaction with the IntegrationOS API. It's designed to facilitate easy integration and usage within server-side Python applications.

## Install

Using pip:

```jsx
pip install integrationos
```

## Configuration

To use the library you must provide an API key and Connection key. Both are located in the IntegrationOS dashboard.

```python
import asyncio
from integrationos import IntegrationOS

async def main():
    async with IntegrationOS("sk_live_1234") as integrate:
        response = await integrate.customers("live::xero::acme-inc").get("cus_OT3CLnirqcpjvw")
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
```


## Testing

1. Configure your environment variables (see `.env.sample`)

2. Build for local testing
    ```bash
    pip install -e .
    ```

3. Run tests
    ```bash
    > python tests/test_unified_api.py # Test Unified API
    > python tests/test_passthrough.py # Test Passthrough API
    > python tests/test_pagination.py # Test Pagination
    ```

## Full Documentation

Please refer to the official IntegrationOS [Documentation](https://docs.integrationos.com/docs/setup) and [API Reference](https://docs.integrationos.com/reference) for more information and Node.js usage examples.
