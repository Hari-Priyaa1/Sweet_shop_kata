from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.database import SessionLocal, engine
from backend import models, schemas, auth

from backend.auth import check_role # Import the role checker

# Initialize the application
app = FastAPI()

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)
# --- NEW: Product Initialization Function ---

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the required role: only 'seller' can create, update, or delete a product
seller_dependency = check_role("seller")

# --- Auth Endpoints ---

@app.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Hash the password and create the user
    hashed_password = auth.get_password_hash(user.password)
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Function to authenticate user (needed for login endpoint)
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user

# The Working Login Endpoint (to make test_login_user_success pass)
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Token creation logic 
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Product Endpoints ---

@app.post("/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    current_seller: models.User = Depends(seller_dependency) 
):
    # 1. Check for product name uniqueness (Good practice)
    db_product = db.query(models.Product).filter(models.Product.name == product.name).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Product name already exists")

    # 2. Create the new Product object
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )
    
    # 3. Add, commit, and refresh the product
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

# --- Product Read Endpoints ---

@app.get("/products", response_model=list[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    """Retrieve a list of all products (public endpoint)."""
    products = db.query(models.Product).all()
    return products

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieve a single product by ID (public endpoint)."""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# --- Product Update Endpoint ---
@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int, 
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_seller: models.User = Depends(seller_dependency) 
):
    # 1. Find the product
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # --- UNIQUE NAME CHECK ---
    if db_product.name != product.name:
        # Check if the NEW name is already used by any OTHER product
        existing_product = db.query(models.Product).filter(
            models.Product.name == product.name
        ).first()

        if existing_product:
            raise HTTPException(status_code=400, detail="Product name already exists")
    # -------------------------
        
    # 2. Update all fields
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.quantity = product.quantity
    
    # 3. Commit the changes
    # The IntegrityError should now be prevented by the check above
    db.commit()
    db.refresh(db_product)
    
    return db_product

# --- Product Delete Endpoint ---
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_seller: models.User = Depends(seller_dependency) 
):
    # 1. Find the product
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # 2. Delete the product
    db.delete(db_product)
    db.commit()
    
    # HTTP 204 No Content is returned automatically
@app.post("/products/{product_id}/purchase", response_model=schemas.Product)
def purchase_sweet(
    product_id: int,
    purchase: schemas.PurchaseSweet, # Expects {'quantity': int}
    db: Session = Depends(get_db),
    # Any logged-in user (customer or seller) can purchase
    current_user: models.User = Depends(auth.get_current_user) 
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Sweet not found")

    if db_product.quantity < purchase.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Only {db_product.quantity} available.")

    # Deduct stock
    db_product.quantity -= purchase.quantity
    
    db.commit()
    db.refresh(db_product)
    
    return db_product

@app.post("/products/{product_id}/restock", response_model=schemas.Product)
def restock_sweet(
    product_id: int,
    restock: schemas.RestockSweet, # Expects {'quantity': int}
    db: Session = Depends(get_db),
    # Only the 'seller' (admin) role can restock
    current_seller: models.User = Depends(seller_dependency) 
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Sweet not found")

    # Add stock
    db_product.quantity += restock.quantity
    
    db.commit()
    db.refresh(db_product)
    
    return db_product

# --- NEW: Product Search Endpoint ---
@app.get("/products/search", response_model=list[schemas.Product])
def search_products(
    query: str = "", # Optional query parameter
    db: Session = Depends(get_db)
):
    """
    Search for sweets by name or description (case-insensitive partial match).
    """
    search_pattern = f"%{query}%"
    
    # Use OR to search in both name and description
    products = db.query(models.Product).filter(
        or_(
            models.Product.name.ilike(search_pattern),
            models.Product.description.ilike(search_pattern)
        )
    ).all()
    
    return products

# --- Root Endpoint ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sweet Shop API!"}