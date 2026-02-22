
# Route definitions

from fastapi import APIRouter

router = APIRouter()                                                                   

@router.get("/health")                                                                 
async def ping():
    # TODO: Return actual result from model connection or else
    return {"result": "healthy"}

# TODO: Add functional routes
