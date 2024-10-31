from typing import Any, Dict, Generic, Optional, Type, TypeVar, cast
import httpx
from pydantic import BaseModel
from .types.generic import (
    UnifiedOptions, Response, ListFilter, ListResponse, 
    Count, DeleteOptions, HttpStatusCode, ResponseError, APIError
)
from .utils import convert_filter_to_query_params

T = TypeVar('T', bound=BaseModel)

class Resource(Generic[T]):
    def __init__(self, client: httpx.AsyncClient, connection_key: str, resource_name: str, model_class: Type[T]):
        self.client = client
        self.connection_key = connection_key
        self.resource_name = resource_name
        self._model_class = model_class

    def get_request_headers(self, options: Optional[UnifiedOptions] = None) -> Dict[str, str]:
        headers = {
            'x-integrationos-connection-key': self.connection_key,
            'Content-Type': 'application/json',
        }
        if options and options.passthrough_headers:
            headers.update(options.passthrough_headers)
        return headers

    def _convert_to_model(self, data: Dict[str, Any]) -> T:
        """Convert dictionary data to model instance"""
        return self._model_class(**data)

    async def make_request_single(
        self, 
        method: str, 
        url: str, 
        data: Any = None, 
        options: Optional[UnifiedOptions] = None, 
        query_params: Optional[Dict[str, str]] = None, 
        status_code: Optional[int] = None,
        response_model: Optional[Type[BaseModel]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response[Any]:
        try:
            request_headers = headers or self.get_request_headers(options)
            params = {**(query_params or {}), **(options.passthrough_query or {} if options else {})}

            if isinstance(data, BaseModel):
                request_data = data.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_unset=True,
                    exclude_defaults=True,
                    mode='json',
                )
            else:
                request_data = data
            
            response = await self.client.request(
                method, 
                url, 
                json=request_data,
                headers=request_headers, 
                params=params, 
                timeout=30.0
            )
            response.raise_for_status()

            json_response = response.json()
            
            unified_data = None
            if json_response and not url.startswith('/passthrough'):
                if unified_data_dict := json_response.get('unified'):
                    if isinstance(unified_data_dict, dict):
                        model_cls = response_model or self._model_class
                        unified_data = model_cls(**unified_data_dict)
                    else:
                        unified_data = unified_data_dict

            return Response(
                unified=unified_data,
                passthrough=json_response if url.startswith('/passthrough') else None,
                meta=json_response.get('meta', {}),
                headers=dict(response.headers),
                statusCode=status_code or response.status_code
            )

        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            try:
                error_json = e.response.json()
            except:
                print(f"Error Response Text: {error_text}")
            
            raise APIError(ResponseError(
                type="APIError",
                code=e.response.status_code,
                status=e.response.status_code,
                key="error",
                message=str(error_json if 'error_json' in locals() else error_text),
                meta={
                    "response_text": error_text,
                    "response_json": error_json if 'error_json' in locals() else None,
                    "request_data": request_data,
                    "request_url": url,
                    "request_method": method
                }
            ))

    async def make_request_list(
        self, 
        method: str, 
        url: str, 
        data: Any = None, 
        options: Optional[UnifiedOptions] = None, 
        query_params: Optional[Dict[str, str]] = None, 
        status_code: Optional[int] = None
    ) -> ListResponse[T]:
        try:
            headers = self.get_request_headers(options)
            params = {**(query_params or {}), **(options.passthrough_query or {} if options else {})}
            
            request_data = data.model_dump(by_alias=True, exclude_none=True) if isinstance(data, BaseModel) else data
            
            response = await self.client.request(
                method, 
                url, 
                json=request_data,
                headers=headers, 
                params=params, 
                timeout=30.0
            )
            response.raise_for_status()

            json_response = response.json()
            
            unified_items = []
            if json_response.get('unified'):
                for item in json_response['unified']:
                    if isinstance(item, dict):
                        unified_items.append(self._convert_to_model(item))
                    else:
                        unified_items.append(item)

            return ListResponse(
                unified=unified_items,
                passthrough=json_response.get('passthrough'),
                pagination=json_response['pagination'],
                meta=json_response.get('meta', {}),
                headers=dict(response.headers),
                statusCode=status_code or response.status_code
            )

        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            try:
                error_json = e.response.json()
            except:
                print(f"Error Response Text: {error_text}")
            
            raise APIError(ResponseError(
                type="APIError",
                code=e.response.status_code,
                status=e.response.status_code,
                key="error",
                message=str(error_json if 'error_json' in locals() else error_text),
                meta={
                    "response_text": error_text,
                    "response_json": error_json if 'error_json' in locals() else None,
                    "request_data": request_data,
                    "request_url": url,
                    "request_method": method
                }
            ))


class UnifiedResourceImpl(Resource[T]):
    async def create(self, object: T, options: Optional[UnifiedOptions] = None) -> Response[T]:
        return cast(Response[T], await self.make_request_single(
            method='POST', 
            url=f'/unified/{self.resource_name}', 
            data=object, 
            options=options, 
            status_code=HttpStatusCode.Created.value,
        ))

    async def upsert(self, object: T, options: Optional[UnifiedOptions] = None) -> Response[T]:
        return cast(Response[T], await self.make_request_single(
            method='PUT', 
            url=f'/unified/{self.resource_name}', 
            data=object, 
            options=options, 
            status_code=HttpStatusCode.OK.value
        ))

    async def list(self, filter: Optional[ListFilter] = None, options: Optional[UnifiedOptions] = None) -> ListResponse[T]:
        query_params = convert_filter_to_query_params(filter) if filter else None

        return await self.make_request_list(
            'GET', 
            url=f'/unified/{self.resource_name}', 
            data=None, 
            options=options, 
            query_params=query_params, 
            status_code=HttpStatusCode.OK.value
        )

    async def get(self, id: str, options: Optional[UnifiedOptions] = None) -> Response[T]:
        return cast(Response[T], await self.make_request_single(
            'GET', 
            url=f'/unified/{self.resource_name}/{id}', 
            data=None, 
            options=options, 
            status_code=HttpStatusCode.OK.value
        ))

    async def update(self, id: str, object: T, options: Optional[UnifiedOptions] = None) -> Response[T]:
        return cast(Response[T], await self.make_request_single(
            'PATCH', 
            f'/unified/{self.resource_name}/{id}', 
            data=object, 
            options=options, 
            status_code=HttpStatusCode.NoContent.value
        ))

    async def count(self, options: Optional[UnifiedOptions] = None) -> Response[Count]:
        response = await self.make_request_single(
            'GET', 
            f'/unified/{self.resource_name}/count', 
            data=None, 
            options=options,
            status_code=HttpStatusCode.OK.value,
            response_model=Count
        )
        return cast(Response[Count], response)

    async def delete(
        self, 
        id: str, 
        delete_options: Optional[DeleteOptions] = None, 
        options: Optional[UnifiedOptions] = None
    ) -> Response[T]:
        query_params = delete_options.model_dump(exclude_none=True) if delete_options else {}

        return cast(Response[T], await self.make_request_single(
            method='DELETE', 
            url=f'/unified/{self.resource_name}/{id}', 
            data=None, 
            options=options, 
            query_params=query_params, 
            status_code=HttpStatusCode.NoContent.value
        ))


class PassthroughResourceImpl(Resource[T]):
    async def call(
        self, 
        method: str, 
        path: str, 
        data: Any = None, 
        headers: Optional[Dict[str, str]] = None, 
        query_params: Optional[Dict[str, str]] = None
    ) -> Response[T]:
        return cast(Response[T], await self.make_request_single(
            method, 
            f'/passthrough/{path}', 
            data, 
            None,
            query_params,
            None,
            None,
            headers
        ))
