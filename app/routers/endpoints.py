from typing import List

from fastapi import FastAPI

from ..models.endpoints import Endpoint, EndpointOut
from ..db import endpoints as endpoint_db

endpoints = FastAPI()


@endpoints.get("/endpoints", response_model=List[EndpointOut])
async def get_endpoints():
    # Depends on security with the account_id
    db_endpoints = await endpoint_db.get_endpoints(account_id='default')
    return db_endpoints


@endpoints.post("/endpoints")
async def create_endpoint(endpoint: Endpoint):
    await endpoint_db.create_endpoint(account_id='default', endpoint=endpoint)

@endpoints.put("/endpoints/email/subscription/{customer_id}/{event_type}")
async def subscribe_email_endpoint(customer_id: str, event_type: str):
    pass

@endpoints.delete("/endpoints/email/subscription/{customer_id}/{event_type}")
async def unsubscribe_email_endpoint(customer_id: str, event_type: str):
    pass

@endpoints.get("/endpoints/{id}", response_model=EndpointOut)
async def get_endpoint(id: str):
    return await endpoint_db.get_endpoint(account_id='default', id=id)


@endpoints.delete("/endpoints/{id}")
async def delete_endpoint(id: str):
    pass


@endpoints.put("/endpoints/{id}")
async def update_endpoint(id: str, endpoint: Endpoint):
    pass

