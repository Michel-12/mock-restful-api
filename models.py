from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, UniqueConstraint
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date

#####################
##    DB Models    ##
#####################

#Abstract model used to prevent repetitive code
class BaseDB(DeclarativeBase):
    __abstract__ = True  
    id = Column(Integer, primary_key=True)

#Table of Customers with id, name, address, tel num, d.o.b.
class Customer(BaseDB):
    __tablename__ = 'customers'
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, unique=True)
    birth_date = Column(Date)
    #1-1 relation with a user
    user = relationship("User", back_populates="customer", uselist=False)

#Table of Products with id, name, description, type, price
class Product(BaseDB):
    __tablename__ = 'products'
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)
    price = Column(Numeric(10,2))

#Association table connecting customers to 1+ of a product
class CustomerProduct(BaseDB):
    __tablename__ = 'customerproducts'
    customer_id = Column(Integer, ForeignKey('customers.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    #Uniqueness constraint on customer and product ids
    __table_args__ = (UniqueConstraint("customer_id", "product_id", name="customer_product_id"),)

    customer = relationship("Customer", backref="customerproducts")
    product = relationship("Product", backref="customerproducts")

#Table of Authorized Users with id, unique name and pass
class User(BaseDB):
    __tablename__ = 'users'
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    #Users are linked to only 1 customer, or no customer (eg. admin)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True, unique=True)
    customer = relationship("Customer", back_populates="user")

#####################
## Endpoint Models ##
#####################

#User Request for Auth
class CreatedUserRequest(BaseModel):
    username: str
    password: str

#Token Class for Auth Swagger Integration
class Token(BaseModel):
    access_token: str
    token_type: str

class ProductResponse(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: Decimal
    id: int

class CustomerResponse(BaseModel):
    name: str
    address: str
    phone_number: str
    birth_date: date
    id: int

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: Decimal

