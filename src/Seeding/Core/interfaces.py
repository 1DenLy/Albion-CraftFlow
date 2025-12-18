from typing import Protocol, Any, List

class IDataProvider(Protocol):
    async def fetch(self) -> Any:
        """
        Retrieves raw data from the source.
        Returns:
            List[Any] or Dict[str, Any] depending on the provider.
        """
        ...