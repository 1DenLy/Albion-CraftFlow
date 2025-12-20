import pytest
import respx
import httpx
import time
from unittest.mock import AsyncMock, MagicMock
from src.ingesting.client import AlbionApiClient
from src.ingesting.service import IngestorService
from src.ingesting.config import IngestorConfig
from src.ingesting.schemas import AlbionPriceDTO


# Fixtures

@pytest.fixture
def mock_config():
    return IngestorConfig(
        albion_api_url="https://test.albion-api.com",
        max_rate=10.0,  # 10 req/sec
        concurrency=2,
        batch_size=50
    )


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_location_map.return_value = {"Lymhurst": 1}
    return repo


@pytest.fixture
def mock_processor():
    processor = MagicMock()
    processor.process.return_value = [{"item_id": "T4_BAG", "price": 100}]
    return processor


@pytest.fixture
def client(mock_config):
    return AlbionApiClient(mock_config)


@pytest.fixture
def service(client, mock_repo, mock_processor, mock_config):
    return IngestorService(client, mock_repo, mock_processor, mock_config)


# --- Test Cases ---

@pytest.mark.asyncio
async def test_sc01_contract_validation(client, mock_config):
    """
    SC-01: Contract Validation
    """
    items = ["T4_BAG", "T5_BAG"]
    location = "Lymhurst"

    async with respx.mock(base_url=mock_config.albion_api_url) as respx_mock:
        route = respx_mock.get(f"/stats/prices/{','.join(items)}").mock(
            return_value=httpx.Response(200, json=[])
        )

        await client.fetch_prices(items, location)

        assert route.called
        request = route.calls.last.request

        # Assertions
        assert "AlbionCraftFlowProject" in request.headers["User-Agent"]
        assert request.url.params["locations"] == location
        assert request.url.params["qualities"] == "1,2,3,4,5"


@pytest.mark.asyncio
async def test_sc02_resilience_retries(client, mock_config):
    """
    SC-02: Resilience Retries
    """
    items = ["T4_BAG"]

    async with respx.mock(base_url=mock_config.albion_api_url) as respx_mock:
        # Mock returns 429, then 502, then 200 OK
        route = respx_mock.get(f"/stats/prices/{items[0]}").mock(
            side_effect=[
                httpx.Response(429),
                httpx.Response(502),
                httpx.Response(200, json=[])
            ]
        )

        results = await client.fetch_prices(items, "Lymhurst")

        # Assertions
        assert route.call_count == 3
        assert isinstance(results, list)


@pytest.mark.asyncio
async def test_sc03_rate_limiting(service, mock_config, mock_repo):
    """
    SC-03: Rate Limiter check (no bursts)
    Config: max_rate=10/sec (1 request every 100 ms).
    Processing 50 items with batch_size=1 -> 50 requests.
    Expected time >= 50 / 10 = 5.0 sec.
    """
    # Override config for this test
    service.config.max_rate = 10.0
    service.config.batch_size = 1

    from aiolimiter import AsyncLimiter
    service.limiter = AsyncLimiter(max_rate=10.0, time_period=1.0)

    items = [f"Item_{i}" for i in range(50)]

    async with respx.mock(base_url=mock_config.albion_api_url) as respx_mock:
        respx_mock.get(path__regex=r"/stats/prices/.*").mock(
            return_value=httpx.Response(200, json=[])
        )

        start_time = time.perf_counter()
        await service.start("Lymhurst", items)
        end_time = time.perf_counter()

        duration = end_time - start_time


        assert duration >= 4.5
        assert mock_repo.save_batch_results.call_count == 50


@pytest.mark.asyncio
async def test_sc04_batching_strategy(service, mock_config, mock_repo):
    """
    SC-04: Batching Strategy (Breaking down requests to avoid URI Too Long)
    Input: 200 items. Batch Size: 50.
    Expected: 4 requests to the client.
    """
    service.config.batch_size = 50
    items = [f"Item_{i}" for i in range(200)]

    service.client.fetch_prices = AsyncMock(return_value=[])

    await service.start("Lymhurst", items)

    assert service.client.fetch_prices.call_count == 4

    # Verify that each call contains no more than 50 items
    for call in service.client.fetch_prices.call_args_list:
        args, _ = call
        batch_items = args[0]
        assert len(batch_items) <= 50