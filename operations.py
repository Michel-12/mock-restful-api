from auth import authrouter
from starlette import status
from database import db_dependency
from models import CreatedUserRequest, Token, User, Customer, Product, ProductResponse, CustomerResponse, CustomerUpdate, ProductCreate
from auth import bcrypt_context, authenticate_user, authenticate_user, create_access_token, user_dependency
from fastapi import Depends, HTTPException, APIRouter, Query
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Optional
from datetime import timedelta

#Create router for operations
router = APIRouter()

#####################
## AUTH Endpoints  ##
#####################

#Create user with hashed pass and link to customer is username is customer phone number
@authrouter.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreatedUserRequest):
    #Check if user already exists
    existing_user = db.query(User).filter(User.username == create_user_request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username already exists")
    #Check if username corresponds with Customer phone number
    customer = db.query(Customer).filter(Customer.phone_number == create_user_request.username).first()
    #Create user
    create_user_model = User(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        customer_id=customer.id if customer else None
    )
    db.add(create_user_model)
    db.commit()

#Create endpoint with Token response that creates form for user/pass
@authrouter.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return{'access_token': token, 'token_type': 'bearer'}

#####################
## Open Endpoints  ##
#####################

#Test endpoint
@router.get('/')
def read_root():
    return "Server is running" 

@router.get('/products', response_model=list[ProductResponse])
async def get_public_products(
    db: db_dependency, 
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_price: Optional[str] = Query(None, description="Sort by price: 'asc','desc'")
):
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)

    if sort_price == 'asc':
        query = query.order_by(Product.price.asc())
    elif sort_price == 'desc':
        query = query.order_by(Product.price.desc())

    products = query.all()
    if products:
        return products
    raise HTTPException(status_code=404, detail="Products not found")

@router.get('/products/{product_id}', response_model=ProductResponse)
async def get_public_product(product_id: int, db: db_dependency):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


#####################
## User Endpoints  ##
#####################

#Test authorized endpoint
@router.get('/auth-check', status_code=status.HTTP_200_OK)
async def user_authentication(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return user["username"]

@router.get('/customers/me', response_model=CustomerResponse)
async def get_my_info(user: user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    customer = db.query(Customer).filter(Customer.phone_number == user["username"]).first()
    if customer:
        return customer
    raise HTTPException(status_code=404, detail="Customer not found")

@router.patch('/customers/me', response_model=CustomerResponse)
async def update_my_info(user: user_dependency, db:db_dependency, update:CustomerUpdate):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    customer = db.query(Customer).filter(Customer.phone_number == user["username"]).first()
    if customer:
        if update.name is not None:
            customer.name = update.name
        if update.address is not None:
            customer.address = update.address
        db.commit()
        db.refresh(customer)
        return customer
    raise HTTPException(status_code=404, detail="Customer not found")

#####################
## Admin Endpoints ##
#####################

@router.post('/products', response_model=list[ProductResponse])
async def add_product(user: user_dependency, db:db_dependency, new_product:ProductCreate):
    if user is None or user["username"] != "admin":
        raise HTTPException(status_code=401, detail='Authentication Failed')
    product = Product(
        name=new_product.name,
        description=new_product.description,
        category=new_product.category,
        price=new_product.price
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    query = db.query(Product)
    return query.all()
