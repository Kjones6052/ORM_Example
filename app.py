# Importing as needed
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

# Instantiating Flask App
app = Flask(__name__)

# Configure SQLAlchemy to connect to database using connection parameteres "user:password@host/db_name"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:7Raffi!Codes7@localhost/e_commerce_db'

# Enable app to use SQLAlchemy and Marshmallow
db = SQLAlchemy(app) # Gives full access to SQL database functionality
ma = Marshmallow(app) # Gives access to data parsing and validation

class CustomerSchema(ma.Schema): # Class Schema for Customer(s)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")
        
customer_schema = CustomerSchema() # Initializing for single use
customers_schema = CustomerSchema(many=True) # Initializing for multiple use


class Customer(db.Model):
    __tablename__ = "Customers" # Defines table for Customers
    id = db.Column(db.Integer, primary_key=True) # Creating id as the primary key for table
    name = db.Column(db.String(255), nullable=False) # Creating name column for table
    email = db.Column(db.String(320)) # Creating email column for table
    phone = db.Column(db.String(15)) # Creating phone column for table
    orders = db.relationship('Order', backref='customer') # Establishing relationship between Customer and Order

class Order(db.Model):
    __tablename__ = "Orders" # Defines table for orders
    id = db.Column(db.Integer, primary_key=True) # Creating id as the primary key for table
    date = db.Column(db.Date, nullable=False) # Creating date column for table
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id')) # Creating customer id as a foreign key column for table
    
# Creating one-to-one relationship
class CustomerAccount(db.Model):
    __tablename__ = "Customer_Accounts" # Defines table for Customer Accounts
    id = db.Column(db.Integer, primary_key=True) # Creating id as the primary key for table
    username = db.Column(db.String(255), unique=True, nullable=False) # Creating User Name column for table
    password = db.Column(db.String(255), nullable=False) # Creating Password column for table
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id')) # Creating Customer ID as foreign key column for table
    customer = db.relationship('Customer', backref='customer_account', uselist=False) # Establishing one-to-one relationship to and from Customers table

# Creating many-to-many relationship
order_product = db.Table('Order_Product',
                         db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
                         db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
                         )

class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True) # Creating id as the primary key for table
    name = db.Column(db.String(255), nullable=False) # Creating name column for table
    price = db.Column(db.Float, nullable=False) # Creating price column for table
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products')) # Creating relationship between Products and Order

# GET request
@app.route('/customers', methods=['GET']) # Route to GET Customers
def get_customers(): # Method to GET Customers
    customers = Customer.query.all() # Execute query to get all customers
    return customers_schema.jsonify(customers) # jsonify data according to schema

# POST request
@app.route('/customers', methods=['POST']) # Route to POST new customer
def add_customer(): # Method to add new customer
    try:
        customer_data = customer_schema.load(request.json) # Validate and deserialize input
    except ValidationError as err: # Error handling
        return jsonify(err.messages), 400 # Jsonify error with type indicator
    
    # Adding customer info into a variable for query execution
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer) # Execute query to add new customer
    db.session.commit() # Commit changes to the database
    return jsonify({"message": "New Customer added successfully."}), 201 # Display message to user with type indicator

# PUT request
@app.route('/customers/<int:id>', methods=['PUT']) # Route to UPDATE customer
def update_customer(id): # Method to update customer
    customer = Customer.query.get_or_404(id) # Retrieve customer by customer ID or produce 404 if not found
    try:
        customer_data = customer_schema.load(request.json) # Get customer data
    except ValidationError as err: # Error handling
        return jsonify(err.messages), 400 # Display error message to user with type indicator
    
    # Defining customer data
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit() # Commit changes to the database
    return jsonify({"message": "Customer details updated successfully"}), 200 # Display message to user with type indicator

# DELETE request
@app.route('/customers/<int:id>', methods=['DELETE']) # Route to DELETE a customer
def delete_customer(id): # Method to delete customer
    customer = Customer.query.get_or_404(id) # Retrieve customer by customer id or produce 404 if not found
    db.session.delete(customer) # Execute query to delete customer
    db.session.commit() # Commit changes to the database
    return jsonify({"message": "Customer removed successfully"}), 200 # Display message to user with type indicator

# Initialize the database and create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)