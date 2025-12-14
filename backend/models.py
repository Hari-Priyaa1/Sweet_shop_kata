from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import declarative_base

# Base class which the models will inherit from
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    # Primary key for the user
    id = Column(Integer, primary_key=True, index=True)
    
    # User authentication fields
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # CRITICAL: Role field for authorization
    role = Column(String, default="customer") # 'customer' or 'staff'
    
    # Example of a boolean field (optional)
    is_active = Column(Boolean, default=True)
    pass

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False) # Store price as a float/decimal
    quantity = Column(Integer, default=0) # Stock quantity

    # This is optional but good: a foreign key linking to the seller
    # seller_id = Column(Integer, ForeignKey("users.id")) 
    # seller = relationship("User", back_populates="products")