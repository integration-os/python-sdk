from datetime import datetime
from typing import Dict, Optional
from .types.generic import ListFilter

def convert_filter_to_query_params(filter: Optional[ListFilter]) -> Dict[str, str]:
    if not filter:
        return {}

    query_params = {}
    for key, value in filter.dict(exclude_none=True).items():
        if isinstance(value, str):
            query_params[key] = value
        elif isinstance(value, (int, float)):
            query_params[key] = str(value)
        elif isinstance(value, datetime):
            query_params[key] = value.isoformat()

    return query_params
