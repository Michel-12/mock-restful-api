# mock-restful-api

A mock RESTful API created with Python FastAPI. It provides layered access to a database of customers and products. Whilst products can be retrieved by any user, authenticated accounts are required to access customer personal data or modify company data. 

**How to run it?**
1. Activate the included Python virtual environment
	  * If not possible, requirements.txt lists the required packages
2. Test the functionality of the API using pytest
	```python -m pytest```
3. Run the api using uvicorn
	```uvicorn main:api --reload```
4. Go to http://127.0.0.1:8000/docs to access the swagger interactive interface
	Alternatively, visit the URL provided by uvicorn and append with /docs

**General overview**
[image](brainstorm.png)
The general idea of this API is to provide access to an digital services provider's database. This is done with restricted access due to the nature of personal and private company information. Any user can retrieve general information about products. Customers can register themselves as users, using their phone number as their username. Then they can access their personal information and update it accordingly. An admin user can also add products to the database.

Features such as admin product deletion, customer access to their active products have yet to be implemented due to the 5 hour time constraint. With little effort these should be able to be added.

**Available Endpoints**
The available endpoints are listed in the docs.html file. This description provides a quick overview:

__Public access__
* GET / -- Returns "Server is Running" to check Server status
* GET /products -- Returns available products with description, category and price
* POST /create_user -- Allows for the creation of a new user. 
	Creating user: 0626249375 with custom password will allow access to customer 4
	Any other created users will not be able access anything
**User access**
* POST /token -- retrieves access token for user after successful login
* GET /auth-check --Returns username for user
* GET /customers/me -- Returns customer data for logged in customer
* PATH /customers/me -- Allows logged in customer to adjust name and/or address
**Admin access**
* POST /products -- Allows logged in admin to add a product to the product table

**File structure**
* main.py - Runs FastAPI instance
* operations.py - Contains available endpoints
* models.py - Contains DB and Request Schemas
* database.py - Configures the database
* db_init.py - Restore file for if db is lost 
	* If no more mock.db, run this before running api
* auth.py - Configures user authentication
* test_api.py - Configures the pytest 
* mock.db - database with Customers, Products, Users and CustomerProducts tables
* pytest.ini - File to silence irrelevant deprecation warning
* requirements.txt - File will all required python packages
* brainstorm.png - Visual representation of API ideation
* README.md - This file

If there are any questions about this, feel free to contact me or post them on the repository. 