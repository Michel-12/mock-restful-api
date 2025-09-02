from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from main import api
from database import get_db
from models import BaseDB, User, Customer, Product
import pytest
from auth import bcrypt_context, create_access_token, authenticate_user
from datetime import datetime, timedelta
from decimal import Decimal

#Create Memory db clone and override normal db
DATABASE_URL = "sqlite:///:memory" 
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

api.dependency_overrides[get_db] = override_get_db

#Create testclient
client = TestClient(api)

#Setup Pytest DB and data
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    BaseDB.metadata.create_all(bind=engine)  # Create the tables

    #Create test items
    session = TestingSessionLocal()
    existing_customer = Customer(name="test_name", address="test address", phone_number="1234567",birth_date=datetime(2000, 1, 1))
    nonuser_customer = Customer(name="test_name2", address="test address2", phone_number="7654321",birth_date=datetime(1999, 12, 12))
    existing_user = User(username="1234567", hashed_password=bcrypt_context.hash("test"))
    existing_admin = User(username="admin", hashed_password=bcrypt_context.hash("admin"))

    test_products = [
        Product(name='TestPhone1', description='Test Desc1', category='Mobile test', price=100),
        Product(name='TestPhone2', description='Test Desc2', category='Mobile test', price=50),
        Product(name='TestTV', description='Test Desc3', category='TV test', price=150)
    ]

    session.add_all([existing_customer,nonuser_customer,existing_user, existing_admin] + test_products)
    session.commit()
    session.close()

    yield  # This allows the test to run
    BaseDB.metadata.drop_all(bind=engine)  # Drop the tables after the test

#Test whether the root can be read
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Server is running"

#Run User tests
def test_create_user():
    payload = {
        "username": "test",
        "password": "1234"
    }
    response = client.post("/auth/", json=payload)
    assert response.status_code == 201
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == payload["username"]).first()
    assert user is not None
    assert user.customer_id is None  # no matching Customer in this test
    db.close()

def test_create_customer():
    payload = {
        "username": "7654321",
        "password": "1234"
    }
    response = client.post("/auth/", json=payload)
    assert response.status_code == 201
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == payload["username"]).first()
    assert user is not None
    assert user.customer_id == 2  # no matching Customer in this test
    db.close()
    
def test_duplicate_user():
    payload = {
        "username": "1234567",
        "password": "test"
    }
    response = client.post("/auth/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this username already exists"

def test_authorized_endpoint():
    db = TestingSessionLocal()
    user = authenticate_user("1234567", "test", db)
    db.close()    
    token = create_access_token(
        username = user.username,
        user_id = user.id,
        expires_delta=timedelta(minutes=15)
    )
    response = client.get("/auth-check",headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200 
    assert response.json() == "1234567"
   
def test_unauthorized_endpoint():
    response = client.get("/auth-check")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" or "Authentication Failed"

#Run product retrieval tests
def test_get_all_products():
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3 
    names = [p["name"] for p in data]
    assert "TestPhone1" in names and "TestPhone2" in names and "TestTV" in names

def test_filter_products_by_category():
    response = client.get("/products", params={"category": "Mobile test"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for p in data:
        assert p["category"] == "Mobile test"

def test_sort_products_by_price_asc():
    response = client.get("/products", params={"sort_price": "asc"})
    assert response.status_code == 200
    data = response.json()
    prices = [Decimal(p["price"]) for p in data]
    assert prices == sorted(prices)

def test_sort_products_by_price_desc():
    response = client.get("/products", params={"sort_price": "desc"})
    assert response.status_code == 200
    data = response.json()
    prices = [Decimal(p["price"]) for p in data]
    assert prices == sorted(prices, reverse=True)

def test_filter_and_sort_products():
    response = client.get("/products", params={"category": "Mobile test", "sort_price": "asc"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    prices = [Decimal(p["price"]) for p in data]
    assert prices == sorted(prices)
    for p in data:
        assert p["category"] == "Mobile test"

def test_single_product():
    response = client.get('/products/1')
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == 'TestPhone1'
    assert data["description"] == 'Test Desc1'
    assert data["category"] == 'Mobile test'
    assert Decimal(data["price"]) == 100

def test_wrong_product():
    response = client.get('/products/100')
    assert response.status_code == 404
    assert response.json()['detail'] == "Product not found"

#Run customer retrieval tests
def test_my_customer_retrieval():
    db = TestingSessionLocal()
    user = authenticate_user("1234567", "test", db)
    db.close()    
    token = create_access_token(
        username = user.username,
        user_id = user.id,
        expires_delta=timedelta(minutes=15)
    )
    response = client.get("/customers/me",headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200 
    data = response.json()
    assert data["name"] == 'test_name'
    assert data["address"] == 'test address'

def test_unauth_customer_retrieval():
    response = client.get("/customers/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" or "Authentication Failed"


def test_my_customer_patch():
    db = TestingSessionLocal()
    user = authenticate_user("1234567", "test", db)
    db.close()    
    token = create_access_token(
        username = user.username,
        user_id = user.id,
        expires_delta=timedelta(minutes=15)
    )
    payload = {
        "name": "Updated Name",
        "address": "Updated Address"
    }
    response = client.patch("/customers/me",json=payload,headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200 
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["address"] == "Updated Address"
    assert data["phone_number"] == "1234567"

def test_unauth_customer_patch():
    payload = {
        "name": "Updated Name",
        "address": "Updated Address"
    }
    response = client.patch("/customers/me",json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" or "Authentication Failed"

#Run Admin post test
def test_admin_add_product():
    db = TestingSessionLocal()
    user = authenticate_user("admin", "admin", db)
    db.close()    
    token = create_access_token(
        username = user.username,
        user_id = user.id,
        expires_delta=timedelta(minutes=15)
    )
    payload = {
        "name": "Test product",
        "description": "Test description",
        "category": "Test category",
        "price": 1234.45
    }
    response = client.post("/products",json=payload,headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200 
    products = response.json()
    assert any(p["name"] == "Test product" for p in products)
    assert any(p["category"] == "Test category" for p in products)
    assert any(float(p["price"]) == 1234.45 for p in products)

def test_user_add_product():
    db = TestingSessionLocal()
    user = authenticate_user("1234567", "test", db)
    db.close()    
    token = create_access_token(
        username = user.username,
        user_id = user.id,
        expires_delta=timedelta(minutes=15)
    )
    payload = {
        "name": "User product",
        "description": "User description",
        "category": "User category",
        "price": 0.01
    }
    response = client.post("/products",json=payload,headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401 
    assert response.json()["detail"] == "Authentication Failed"