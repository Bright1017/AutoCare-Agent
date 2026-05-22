# app/schemas/shop.py

from pydantic import BaseModel, Field
from typing import Optional, List

class MechanicShop(BaseModel):
    """
    Schema representing a validated mechanic shop entity 
    extracted from the database dataset.
    """
    id: str = Field(..., description="Unique Yelp business identifier ID")
    name: str = Field(..., description="Name of the auto repair service shop")
    stars: float = Field(default=0.0, description="Average historical rating out of 5 stars")
    categories: str = Field(default="Auto Repair", description="Comma-separated operational specialties")
    address: Optional[str] = Field(default="Lagos, Nigeria", description="Physical location address of the shop")
    review_context: str = Field(..., description="Aggregated text chunks or reviews used for semantic matching")

    class Config:
        from_attributes = True  # Allows compatibility if you map this from ORM or database objects later