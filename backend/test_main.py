import pytest
from fastapi.testclient import TestClient 
from sqlalchemy.orm import Session
from backend.main import app 

# Imports for database access and models
from backend.database import SessionLocal 
from backend import models

# Initialize the TestClient with our app
client = TestClient(app)

# --- Fixture to handle Database session in tests ---
@pytest.fixture(scope="function")
def db_session():
    """Provides a clean, independent DB session for each test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Cleanup Functions for TDD isolation ---

def cleanup_test_user(db: Session):
    """Deletes the standard 'testuser' used for registration tests."""
    db.query(models.User).filter(models.User.username == "testuser").delete()
    db.commit()

def cleanup_login_test_user(db: Session):
    """Deletes the standard 'loginuser' used for login tests."""
    db.query(models.User).filter(models.User.username == "loginuser").delete()
    db.commit()

def cleanup_products(db: Session):
    """Deletes the specific products used in the security and CRUD tests."""
    test_product_names = [
        "Corrected Truffle", 
        "Unauthorized Candy", 
        "Forbidden Lollipop",
        "Test Product A",
        "Test Product B",
        "ID Test Candy",
        "Old Name",           # For Update Test
        "To Be Updated",    # For Update Test
        "Test Update Old Name",
        "Test Update New Name",
        "Product To Delete",  # For Delete Test
        "Product To Be Forbidden Deleted", # For Delete Test
    ]
    
    # Delete all products whose names match the ones used in the tests
    db.query(models.Product).filter(
        models.Product.name.in_(test_product_names)
    ).delete(synchronize_session=False)
    
    db.commit()
    
# --- Helper for Authentication/Token Retrieval ---

def get_auth_token(username, password):
    """Logs in a user and returns the Bearer token."""
    login_data = {
        "username": username,
        "password": password
    }
    response = client.post("/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

# --- User Setup Helpers (Include cleanup_products here for isolation) ---

def setup_seller_user(db: Session):
    """Registers a user with the 'seller' role and ensures a clean DB state."""
    username = "seller_user"
    password = "sellerpass42"
    
    # Cleanup: Delete test products and user before starting
    cleanup_products(db)
    db.query(models.User).filter(models.User.username == username).delete()
    db.commit()
    
    # Register the seller user
    seller_data = {
        "username": username,
        "email": "seller@example.com",
        "password": password,
        "role": "seller" 
    }
    client.post("/register", json=seller_data)
    
    return username, password

def setup_customer_user(db: Session):
    """Registers a user with the default 'customer' role and ensures a clean DB state."""
    username = "customer_user"
    password = "customerpass42"
    
    # Cleanup: Delete test products and user before starting
    cleanup_products(db)
    db.query(models.User).filter(models.User.username == username).delete()
    db.commit()
    
    # Register the customer user
    customer_data = {
        "username": username,
        "email": "customer@example.com",
        "password": password,
        "role": "customer" 
    }
    client.post("/register", json=customer_data)
    
    return username, password

# =======================================================
# --- 13 Final Tests: User Auth & Product CRUD ---
# =======================================================

# --- 1. Root Endpoint Test ---
def test_read_main_status():
    """Test that the root endpoint returns a successful status code (200)."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Sweet Shop API!"}

# --- 2. Registration Test ---
def test_register_user_success(db_session: Session):
    """Tests successful user registration."""
    cleanup_test_user(db_session)
    test_user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "ShortPass42",
        "role": "customer"
    }
    response = client.post("/register", json=test_user_data)
    assert response.status_code == 201
    
# --- 3. Login Test ---
def test_login_user_success(db_session: Session):
    """Tests successful user login using the /token endpoint."""
    cleanup_login_test_user(db_session)
    test_user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpass42",
        "role": "customer"
    }
    client.post("/register", json=test_user_data)
    login_data = {"username": "loginuser", "password": "loginpass42"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

# --- 4. Product Creation Success (as Seller) Test ---
def test_create_product_success_as_seller(db_session: Session):
    """Tests successful product creation when authenticated as a 'seller'."""
    seller_username, seller_password = setup_seller_user(db_session) 
    token = get_auth_token(seller_username, seller_password)
    new_product_data = {
        "name": "Corrected Truffle",
        "description": "Rich, dark chocolate truffles.",
        "price": 4.50,
        "quantity": 100
    }
    response = client.post(
        "/products", 
        json=new_product_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Corrected Truffle"
    
# --- 5. Product Creation Unauthorized (No Token) Test ---
def test_create_product_unauthorized_no_token():
    """Tests product creation fails without any authentication."""
    new_product_data = {
        "name": "Unauthorized Candy",
        "description": "Sweet but forbidden.",
        "price": 1.00,
        "quantity": 10
    }
    response = client.post("/products", json=new_product_data)
    assert response.status_code == 401
    
# --- 6. Product Creation Forbidden (Wrong Role) Test ---
def test_create_product_forbidden_wrong_role(db_session: Session):
    """Tests product creation fails when authenticated as a 'customer'."""
    customer_username, customer_password = setup_customer_user(db_session)
    token = get_auth_token(customer_username, customer_password)
    new_product_data = {
        "name": "Forbidden Lollipop",
        "description": "Not for customers to create.",
        "price": 2.00,
        "quantity": 50
    }
    response = client.post(
        "/products", 
        json=new_product_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "must have the role 'seller'" in response.json()["detail"]

# --- 7. Read Products (List) Test ---
def test_read_products_list(db_session: Session):
    """Tests the public endpoint to list all products."""
    cleanup_products(db_session) 
    seller_username, seller_password = setup_seller_user(db_session)
    token = get_auth_token(seller_username, seller_password)
    
    product_a_data = {"name": "Test Product A", "description": "A", "price": 10.00, "quantity": 10}
    client.post("/products", json=product_a_data, headers={"Authorization": f"Bearer {token}"})

    product_b_data = {"name": "Test Product B", "description": "B", "price": 5.00, "quantity": 20}
    client.post("/products", json=product_b_data, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/products")
    
    assert response.status_code == 200
    products_list = response.json()
    product_names = [p["name"] for p in products_list if p["name"] in ["Test Product A", "Test Product B"]]
    assert len(product_names) >= 2


# --- 8. Read Product (By ID) Success Test ---
def test_read_product_by_id_success(db_session: Session):
    """Tests retrieving a single product by its ID."""
    cleanup_products(db_session)
    seller_username, seller_password = setup_seller_user(db_session)
    token = get_auth_token(seller_username, seller_password)
    
    new_product_data = {"name": "ID Test Candy", "description": "Sweet", "price": 2.50, "quantity": 5}
    response = client.post("/products", json=new_product_data, headers={"Authorization": f"Bearer {token}"})
    product_id = response.json()["id"]

    response = client.get(f"/products/{product_id}")
    
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "ID Test Candy"


# --- 9. Read Product (By ID) Not Found Test ---
def test_read_product_by_id_not_found():
    """Tests failure when retrieving a product with a non-existent ID."""
    non_existent_id = 999999 
    response = client.get(f"/products/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


# --- 10. Update Product Success (as Seller) Test ---
def test_update_product_success_as_seller(db_session: Session):
    """Tests successful product update when authenticated as a 'seller'."""
    cleanup_products(db_session)
    seller_username, seller_password = setup_seller_user(db_session)
    token = get_auth_token(seller_username, seller_password)

    # 1. Create the product
    initial_data = {"name": "Test Update Old Name", "description": "Old Desc", "price": 1.00, "quantity": 10}
    response = client.post("/products", json=initial_data, headers={"Authorization": f"Bearer {token}"})
    product_id = response.json()["id"]

    # 2. Update the product
    update_data = {"name": "Test Update New Name", "description": "Updated", "price": 99.99, "quantity": 5}
    response = client.put(
        f"/products/{product_id}", 
        json=update_data, 
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["name"] == "Test Update New Name"
    assert updated_product["price"] == 99.99
    assert updated_product["quantity"] == 5
# --- 11. Update Product Forbidden (Wrong Role) Test ---
def test_update_product_forbidden_wrong_role(db_session: Session):
    """Tests product update fails when authenticated as a 'customer'."""
    cleanup_products(db_session)
    # Seller creates product
    seller_username, seller_password = setup_seller_user(db_session)
    seller_token = get_auth_token(seller_username, seller_password)
    initial_data = {"name": "To Be Updated", "description": "Test", "price": 1.00, "quantity": 1}
    response = client.post("/products", json=initial_data, headers={"Authorization": f"Bearer {seller_token}"})
    product_id = response.json()["id"]

    # Customer attempts the update
    customer_username, customer_password = setup_customer_user(db_session)
    customer_token = get_auth_token(customer_username, customer_password)
    
    update_data = {"name": "Should Fail", "description": "Fail", "price": 5.00, "quantity": 5}
    response = client.put(
        f"/products/{product_id}", 
        json=update_data, 
        headers={"Authorization": f"Bearer {customer_token}"}
    )

    assert response.status_code == 403
    assert "must have the role 'seller'" in response.json()["detail"]


# --- 12. Delete Product Success (as Seller) Test ---
def test_delete_product_success_as_seller(db_session: Session):
    """Tests successful product deletion when authenticated as a 'seller'."""
    cleanup_products(db_session)
    seller_username, seller_password = setup_seller_user(db_session)
    token = get_auth_token(seller_username, seller_password)

    # 1. Create the product
    initial_data = {"name": "Product To Delete", "description": "Test", "price": 2.00, "quantity": 1}
    response = client.post("/products", json=initial_data, headers={"Authorization": f"Bearer {token}"})
    product_id = response.json()["id"]

    # 2. Delete the product
    response = client.delete(
        f"/products/{product_id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204 

    # 3. Verify deletion by trying to read it
    read_response = client.get(f"/products/{product_id}")
    assert read_response.status_code == 404


# --- 13. Delete Product Forbidden (Wrong Role) Test ---
def test_delete_product_forbidden_wrong_role(db_session: Session):
    """Tests product deletion fails when authenticated as a 'customer'."""
    cleanup_products(db_session)
    # Seller creates product
    seller_username, seller_password = setup_seller_user(db_session)
    seller_token = get_auth_token(seller_username, seller_password)
    initial_data = {"name": "Product To Be Forbidden Deleted", "description": "Test", "price": 1.00, "quantity": 1}
    response = client.post("/products", json=initial_data, headers={"Authorization": f"Bearer {seller_token}"})
    product_id = response.json()["id"]

    # Customer attempts the delete
    customer_username, customer_password = setup_customer_user(db_session)
    customer_token = get_auth_token(customer_username, customer_password)
    
    response = client.delete(
        f"/products/{product_id}", 
        headers={"Authorization": f"Bearer {customer_token}"}
    )

    assert response.status_code == 403
    assert "must have the role 'seller'" in response.json()["detail"]