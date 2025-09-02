#Init file to create mock db entries
#Be sure to run this in the same directory as main.py

from database import session, engine
from models import Customer, Product, CustomerProduct, BaseDB, User
from datetime import datetime
from auth import bcrypt_context

# Create all tables based on models
BaseDB.metadata.create_all(bind=engine)

#Add customers and products
customers = [
    Customer(name='Manish Helderman', address='Nieuweweg 128, 3281 AM Numansdorp', phone_number='0646383282', birth_date=datetime(1946, 2, 10)),
    Customer(name='Aart Lens', address='Ambachtspad 109, 3945 BG Cohen', phone_number='0671220908', birth_date=datetime(2005, 12, 13)),
    Customer(name='Theun Mensen', address='Kasteeldrift 83, 3436 TN Nieuwegein', phone_number='0630718383', birth_date=datetime(2006, 3, 28)),
    Customer(name='Dakota Hussein', address='Deventerweg 197, 7213 EH Gorssel', phone_number='0626249375', birth_date=datetime(1956, 3, 25)),
]

products = [
    Product(name='Bundel 15GB', description='Sim Only phone plan 15 GB', category='Mobile phone plan', price=21),
    Product(name='Bundel 8GB', description='Sim Only phone plan 8 GB', category='Mobile phone plan', price=18.50),
    Product(name='Bundel 0GB', description='Sim Only phone plan 0 GB', category='Mobile phone plan', price=15),
    Product(name='KPN TV+ Streaming', description='TV plan for online services', category='TV plan', price=3.50),
    Product(name='KPN TV+ TV', description='TV plan for TV broadcasts', category='TV plan', price=12.50),
    Product(name='Snel 100Mbit/s', description='Internet plan with 100 Mbit/s', category='Internet plan', price=42.50),
    Product(name='Superfiber 4', description='Internet plan with 4 Gbit/s', category='Internet plan', price=37.50),
]

session.add_all(customers + products)
session.commit()  

#Link customers and products
customer_products = [
    CustomerProduct(customer_id=1, product_id=1, quantity=2),
    CustomerProduct(customer_id=1, product_id=4, quantity=1),
    CustomerProduct(customer_id=1, product_id=6, quantity=1),
    CustomerProduct(customer_id=2, product_id=1, quantity=1),
    CustomerProduct(customer_id=2, product_id=3, quantity=1),
    CustomerProduct(customer_id=2, product_id=5, quantity=1),
    CustomerProduct(customer_id=2, product_id=7, quantity=1),
    CustomerProduct(customer_id=3, product_id=2, quantity=1),
    CustomerProduct(customer_id=3, product_id=5, quantity=1),
    CustomerProduct(customer_id=3, product_id=6, quantity=1),
    CustomerProduct(customer_id=4, product_id=3, quantity=1),
    CustomerProduct(customer_id=4, product_id=7, quantity=1),
]

#Create users
users = [
    User(username= "0646383282", hashed_password=bcrypt_context.hash("password123"), customer_id=1),
    User(username= "0671220908", hashed_password=bcrypt_context.hash("123password"), customer_id=2),
    User(username= "0630718383", hashed_password=bcrypt_context.hash("qwerty123"), customer_id=3),
    User(username= "admin", hashed_password=bcrypt_context.hash("admin"), customer_id=4)
]

session.add_all(customer_products + users)
session.commit()

