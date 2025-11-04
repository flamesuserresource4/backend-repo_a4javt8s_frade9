"""
Database Schemas for FarmConnect

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


class Product(BaseModel):
    """
    Farm marketplace listings (produce and compost)
    Collection: "product"
    """
    title: str = Field(..., description="Product title, e.g., Fresh Tomatoes or Wet Waste Compost")
    description: Optional[str] = Field(None, description="Short description of the product")
    price: float = Field(..., ge=0, description="Price in local currency")
    unit: str = Field(..., description="Unit for the price, e.g., per kg, per bag")
    category: Literal["produce", "compost"] = Field(..., description="Type of product")
    seller_name: str = Field(..., description="Seller's display name")
    image_url: Optional[HttpUrl] = Field(None, description="Image of the product")
    location: Optional[str] = Field(None, description="Location or city of the seller")
    in_stock: bool = Field(True, description="Whether product is available")


class Tutorial(BaseModel):
    """
    Tutorial videos and guides about organic farming
    Collection: "tutorial"
    """
    title: str = Field(..., description="Tutorial title")
    description: Optional[str] = Field(None, description="What this tutorial covers")
    author: str = Field(..., description="Creator's display name")
    video_url: Optional[HttpUrl] = Field(None, description="Video URL (to be used when uploads are enabled)")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Thumbnail image URL")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Duration in seconds")


class Message(BaseModel):
    """
    Community chat messages
    Collection: "message"
    """
    name: str = Field(..., description="Sender display name")
    text: str = Field(..., min_length=1, max_length=1000, description="Message content")
    room: str = Field("general", description="Chat room identifier")
