from typing import TypeVar, Generic, Callable, List, Optional, Awaitable
from pydantic import BaseModel
from .types.generic import ListFilter, ListResponse, Pagination

T = TypeVar('T', bound=BaseModel)

class PaginationHelper(Generic[T]):
    """
    A helper class to handle pagination of list endpoints.
    """
    
    def __init__(
        self,
        fetch_function: Callable[[ListFilter], Awaitable[ListResponse[T]]],
        filter: Optional[ListFilter] = None
    ):
        self._fetch_function = fetch_function
        self.filter = filter or ListFilter()
        self._current_batch: List[T] = []
        self._next_batch: Optional[List[T]] = None
        self._current_cursor: Optional[str] = None
        self._next_cursor: Optional[str] = None
        self._is_initialized: bool = False

    async def initialize(self) -> None:
        """Initialize the pagination helper by fetching the first two batches."""
        if self._is_initialized:
            return

        # Fetch first batch with filter
        first_response = await self._fetch_function(self.filter)
        self._current_batch = first_response.unified
        self._current_cursor = first_response.pagination.nextCursor

        # If there's more data, fetch second batch
        if self._current_cursor:
            # Create new filter with cursor while preserving other filter params
            next_filter = ListFilter(
                **self.filter.model_dump(exclude_none=True),
                cursor=self._current_cursor
            )
            second_response = await self._fetch_function(next_filter)
            self._next_batch = second_response.unified
            self._next_cursor = second_response.pagination.nextCursor

        self._is_initialized = True

    async def get_next_batch(self) -> List[T]:
        """
        Get the next batch of items.
        
        Returns:
            List[T]: The next batch of items
        """
        if not self._is_initialized:
            await self.initialize()

        # Store current batch to return
        batch_to_return = self._current_batch

        # Move next batch to current
        self._current_batch = self._next_batch or []
        self._current_cursor = self._next_cursor

        # Fetch next batch if there's more data
        if self._current_cursor:
            next_filter = ListFilter(
                **self.filter.model_dump(exclude_none=True),
                cursor=self._current_cursor
            )
            response = await self._fetch_function(next_filter)
            self._next_batch = response.unified
            self._next_cursor = response.pagination.nextCursor
        else:
            self._next_batch = None
            self._next_cursor = None

        return batch_to_return

    def has_more_data(self) -> bool:
        """
        Checks if there is more data to fetch.
        
        Returns:
            bool: True if there is more data to fetch
        """
        if not self._is_initialized:
            return True

        return bool(
            self._current_batch or 
            (self._next_batch is not None and self._next_batch)
        )
