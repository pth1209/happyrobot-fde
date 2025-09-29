import os
from numpy import str_
import pandas as pd
from typing import List, Optional

from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# Define the API key name and get the actual key from an environment variable
API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("API_KEY") 

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="Acme Logistics Load API",
    description="API for searching and retrieving available freight loads.",
    version="1.0.0"
)

# Load the data from a JSON file into a pandas DataFrame when the app starts
try:
    loads_df = pd.read_json("loads.json")
except FileNotFoundError:
    print("Error: loads.json not found. Please create it.")
    loads_df = pd.DataFrame() # Create an empty dataframe to avoid crashing

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Dependency to verify the API key."""
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_KEY not configured on the server."
        )
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )

class Load(BaseModel):
    """Defines the structure of a single load, based on the provided fields."""
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: int
    notes: Optional[str] = None
    weight: int
    commodity_type: str
    num_of_pieces: int
    miles: int
    dimensions: str

@app.get("/v1/loads/{load_id}", response_model=List[Load])
async def get_load(
    load_id: str,
    api_key: str = Security(get_api_key)
):
    """
    Retrieve a specific load by load_id.
    """
    if loads_df.empty:
        return []

    # Filter by load_id (exact match since load_id is unique)
    query_df = loads_df[loads_df['load_id'] == load_id]

    return query_df.to_dict(orient='records')


@app.get("/health")
def health_check():
    return {"status": "ok"}