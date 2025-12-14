from pydantic import BaseModel,Field, ConfigDict
from typing import Literal

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: str

class UserCreate(UserBase):
    password: str = Field(..., max_length=72)
    role: Literal["customer", "seller", "admin"] = "customer"

class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    
    

# --- NEW: Token Schema (for successful login) ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    price: float = Field(..., gt=0.0) # Price must be greater than zero
    quantity: int = Field(..., ge=0) # Quantity must be zero or greater

class ProductCreate(ProductBase):
    pass # Inherits all fields from ProductBase

class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    # Optional: seller_id: int 

class PurchaseSweet(BaseModel):
    quantity: int = Field(gt=0, description="The quantity of the sweet to purchase.")

class RestockSweet(BaseModel):
    quantity: int = Field(gt=0, description="The quantity of the sweet to restock.")