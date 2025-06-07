from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import uuid
from bson.objectid import ObjectId
from bson.errors import InvalidId

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']

# Collections
users_collection = db['users']
products_collection = db['products']
orders_collection = db['orders']
cart_collection = db['cart_items']

class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.email = ''
        self.full_name = ''
        self.phone = ''
        self.created_at = datetime.utcnow()
        self.last_login = None
        self.address = ''
        self.city = ''
        self.state = ''
        self.zip_code = ''
        self.date_of_birth = None
        self._id = None

    # Flask-Login required methods
    def get_id(self):
        """Return the user ID as a string"""
        return str(self._id) if self._id else None

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return True

    @property
    def is_active(self):
        """Return True if the user is active"""
        return True

    @property
    def is_anonymous(self):
        """Return False as this is not an anonymous user"""
        return False

    def update_last_login(self):
        """Update the last login timestamp"""
        try:
            self.last_login = datetime.utcnow()
            if self._id:
                users_collection.update_one(
                    {'_id': self._id},
                    {'$set': {'last_login': self.last_login}}
                )
                print(f"Updated last login for user {self.username}")
                return True
        except Exception as e:
            print(f"Error updating last login: {str(e)}")
            return False

    @staticmethod
    def get_all_users():
        """Get all users (admin only)"""
        try:
            users_data = list(users_collection.find())
            return [User.from_dict(user) for user in users_data]
        except Exception as e:
            print(f"Error getting all users: {str(e)}")
            return []

    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        try:
            print(f"=== Finding user by ID: {user_id} ===")
            if isinstance(user_id, str):
                if len(user_id) != 24:  # MongoDB ObjectId should be 24 characters
                    print(f"Invalid ObjectId length: {len(user_id)}")
                    return None
                user_id = ObjectId(user_id)
            
            user_data = users_collection.find_one({'_id': user_id})
            print(f"User data found: {user_data is not None}")
            
            if user_data:
                user = User.from_dict(user_data)
                print(f"User object created: {user.username if user else 'None'}")
                return user
            return None
        except Exception as e:
            print(f"Error finding user by ID {user_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        try:
            print(f"=== Finding user by username: {username} ===")
            user_data = users_collection.find_one({'username': username})
            print(f"User data found: {user_data is not None}")
            
            if user_data:
                user = User.from_dict(user_data)
                print(f"User object created: {user.username if user else 'None'}")
                return user
            return None
        except Exception as e:
            print(f"Error finding user by username {username}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def create_user(username, password, email='', full_name='', phone=''):
        """Create a new user"""
        try:
            hashed_password = generate_password_hash(password)
            user_data = {
                'username': username,
                'password': hashed_password,
                'email': email,
                'full_name': full_name,
                'phone': phone,
                'created_at': datetime.utcnow(),
                'last_login': None,
                'address': '',
                'city': '',
                'state': '',
                'zip_code': '',
                'date_of_birth': None
            }
            
            result = users_collection.insert_one(user_data)
            user_data['_id'] = result.inserted_id
            return User.from_dict(user_data)
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None

    @staticmethod
    def from_dict(data):
        """Create User object from dictionary"""
        try:
            if not data:
                return None
            
            print(f"=== Creating user from dict ===")
            print(f"Username: {data.get('username')}")
            print(f"Has _id: {'_id' in data}")
            
            user = User(data['username'], '')  # Password will be set from data
            user._id = data['_id']
            user.password = data['password']
            user.email = data.get('email', '')
            user.full_name = data.get('full_name', '')
            user.phone = data.get('phone', '')
            user.created_at = data.get('created_at', datetime.utcnow())
            user.last_login = data.get('last_login')
            user.address = data.get('address', '')
            user.city = data.get('city', '')
            user.state = data.get('state', '')
            user.zip_code = data.get('zip_code', '')
            user.date_of_birth = data.get('date_of_birth')
            
            print(f"User created successfully: {user.username}")
            print(f"User ID: {user.get_id()}")
            
            return user
        except Exception as e:
            print(f"Error creating user from dict: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

class Product:
    def __init__(self, name, category, price, description, image_url, stock=100):
        self.name = name
        self.category = category
        self.price = price
        self.description = description
        self.image_url = image_url
        self.stock = stock
        self._id = None

    @staticmethod
    def get_all():
        """Get all products"""
        try:
            products_data = products_collection.find()
            return [Product.from_dict(product) for product in products_data]
        except Exception as e:
            print(f"Error getting all products: {str(e)}")
            return []

    @staticmethod
    def find_by_category(category):
        """Find products by category"""
        try:
            products_data = products_collection.find({'category': {'$regex': category, '$options': 'i'}})
            return [Product.from_dict(product) for product in products_data]
        except Exception as e:
            print(f"Error finding products by category {category}: {str(e)}")
            return []

    @staticmethod
    def search(query):
        """Search products by name, category, or description"""
        try:
            filter_query = {
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'category': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]
            }
            products_data = products_collection.find(filter_query)
            return [Product.from_dict(product) for product in products_data]
        except Exception as e:
            print(f"Error searching products with query '{query}': {str(e)}")
            return []

    @staticmethod
    def find_by_price_range(min_price, max_price):
        """Find products within price range"""
        try:
            filter_query = {
                'price': {
                    '$gte': min_price,
                    '$lte': max_price
                }
            }
            products_data = products_collection.find(filter_query)
            return [Product.from_dict(product) for product in products_data]
        except Exception as e:
            print(f"Error finding products in price range ${min_price}-${max_price}: {str(e)}")
            return []

    @staticmethod
    def create_product(name, category, price, description, image_url):
        product_data = {
            'name': name,
            'category': category,
            'price': price,
            'description': description,
            'image_url': image_url,
            'stock': 100,
            'created_at': datetime.utcnow()
        }
        result = products_collection.insert_one(product_data)
        product_data['_id'] = result.inserted_id
        return Product.from_dict(product_data)
    
    @staticmethod
    def search_products(query=None, max_price=None, min_price=None, limit=8):
        filter_query = {}
        
        if query:
            filter_query['$or'] = [
                {'name': {'$regex': query, '$options': 'i'}},
                {'category': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        
        if max_price:
            filter_query['price'] = {'$lte': max_price}
        
        if min_price:
            if 'price' in filter_query:
                filter_query['price']['$gte'] = min_price
            else:
                filter_query['price'] = {'$gte': min_price}
        
        products_data = products_collection.find(filter_query).limit(limit)
        return [Product.from_dict(product) for product in products_data]
    
    @staticmethod
    def find_by_id(product_id):
        """Find product by ID"""
        try:
            print(f"=== Finding product by ID: {product_id} ===")
            print(f"Product ID type: {type(product_id)}")
            
            # Handle string ObjectId conversion
            if isinstance(product_id, str):
                if len(product_id) != 24:  # MongoDB ObjectId should be 24 characters
                    print(f"Invalid ObjectId length: {len(product_id)}")
                    return None
                try:
                    product_id = ObjectId(product_id)
                    print(f"Converted to ObjectId: {product_id}")
                except Exception as e:
                    print(f"Failed to convert to ObjectId: {str(e)}")
                    return None
            
            product_data = products_collection.find_one({'_id': product_id})
            print(f"Product data found: {product_data is not None}")
            
            if product_data:
                print(f"Product name: {product_data.get('name')}")
                return Product.from_dict(product_data)
            return None
        except Exception as e:
            print(f"Error finding product by ID {product_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def from_dict(data):
        """Create Product object from dictionary"""
        try:
            if not data:
                return None
            
            print(f"=== Creating product from dict ===")
            print(f"Product name: {data.get('name')}")
            print(f"Has _id: {'_id' in data}")
            
            product = Product(
                data['name'],
                data['category'],
                data['price'],
                data['description'],
                data['image_url'],
                data.get('stock', 100)
            )
            product._id = data['_id']
            
            print(f"Product created successfully: {product.name}")
            return product
        except Exception as e:
            print(f"Error creating product from dict: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

class Order:
    def __init__(self, data=None):
        if data:
            self._id = data.get('_id')
            self.user_id = data.get('user_id')
            self.order_number = data.get('order_number')
            self.total_amount = data.get('total_amount')
            self.status = data.get('status', 'Processing')
            self.shipping_address = data.get('shipping_address')
            self.payment_method = data.get('payment_method')
            self.items = data.get('items', [])
            self.created_at = data.get('created_at', datetime.utcnow())
    
    @staticmethod
    def create_order(user_id, total_amount, shipping_address, payment_method, items):
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            
            order_data = {
                'user_id': user_obj_id,
                'order_number': str(uuid.uuid4())[:8].upper(),
                'total_amount': total_amount,
                'status': 'Processing',
                'shipping_address': shipping_address,
                'payment_method': payment_method,
                'items': items,
                'created_at': datetime.utcnow()
            }
            result = orders_collection.insert_one(order_data)
            order_data['_id'] = result.inserted_id
            return Order(order_data)
        except (InvalidId, TypeError):
            return None
    
    @staticmethod
    def find_by_user(user_id):
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            orders_data = orders_collection.find({'user_id': user_obj_id}).sort('created_at', -1)
            return [Order(order) for order in orders_data]
        except (InvalidId, TypeError):
            return []
    
    @staticmethod
    def find_by_order_number(order_number, user_id):
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            order_data = orders_collection.find_one({
                'order_number': order_number,
                'user_id': user_obj_id
            })
            return Order(order_data) if order_data else None
        except (InvalidId, TypeError):
            return None
    
    @staticmethod
    def find_by_id(order_id):
        try:
            if isinstance(order_id, str):
                object_id = ObjectId(order_id)
            else:
                object_id = order_id
                
            order_data = orders_collection.find_one({'_id': object_id})
            return Order(order_data) if order_data else None
        except (InvalidId, TypeError):
            return None
    
    @staticmethod
    def get_all_orders():
        orders_data = orders_collection.find().sort('created_at', -1)
        return [Order(order) for order in orders_data]
    
    def update_status(self, status):
        self.status = status
        orders_collection.update_one({'_id': self._id}, {'$set': {'status': status}})

class CartItem:
    def __init__(self, data=None):
        if data:
            self._id = data.get('_id')
            self.user_id = data.get('user_id')
            self.product_id = data.get('product_id')
            self.quantity = data.get('quantity', 1)
            self.created_at = data.get('created_at', datetime.utcnow())
    
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        try:
            print(f"=== CartItem.add_to_cart Debug ===")
            print(f"Input - user_id: {user_id}, product_id: {product_id}, quantity: {quantity}")
            
            # Convert string IDs to ObjectId
            if isinstance(user_id, str):
                user_obj_id = ObjectId(user_id)
            else:
                user_obj_id = user_id
                
            if isinstance(product_id, str):
                product_obj_id = ObjectId(product_id)
            else:
                product_obj_id = product_id
            
            print(f"Converted - user_obj_id: {user_obj_id}, product_obj_id: {product_obj_id}")
            
            # Check if item already exists in cart
            existing_item = cart_collection.find_one({
                'user_id': user_obj_id,
                'product_id': product_obj_id
            })
            
            print(f"Existing item: {existing_item is not None}")
            
            if existing_item:
                # Update quantity if item exists
                new_quantity = existing_item['quantity'] + quantity
                print(f"Updating quantity from {existing_item['quantity']} to {new_quantity}")
                
                result = cart_collection.update_one(
                    {'_id': existing_item['_id']},
                    {'$set': {'quantity': new_quantity}}
                )
                print(f"Update result: {result.modified_count} documents modified")
                
                existing_item['quantity'] = new_quantity
                return CartItem(existing_item)
            else:
                # Create new cart item
                cart_data = {
                    'user_id': user_obj_id,
                    'product_id': product_obj_id,
                    'quantity': quantity,
                    'created_at': datetime.utcnow()
                }
                print(f"Creating new cart item: {cart_data}")
                
                result = cart_collection.insert_one(cart_data)
                print(f"Insert result: {result.inserted_id}")
                
                cart_data['_id'] = result.inserted_id
                return CartItem(cart_data)
                
        except Exception as e:
            print(f"=== ERROR in CartItem.add_to_cart ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_user_cart(user_id):
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            cart_items = cart_collection.find({'user_id': user_obj_id})
            items_with_products = []
            
            for item in cart_items:
                product = Product.find_by_id(item['product_id'])
                if product:
                    items_with_products.append((CartItem(item), product))
            
            return items_with_products
        except (InvalidId, TypeError):
            return []
    
    @staticmethod
    def remove_from_cart(item_id, user_id):
        try:
            item_obj_id = ObjectId(item_id) if isinstance(item_id, str) else item_id
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            
            cart_collection.delete_one({
                '_id': item_obj_id,
                'user_id': user_obj_id
            })
        except (InvalidId, TypeError):
            pass
    
    @staticmethod
    def clear_cart(user_id):
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            cart_collection.delete_many({'user_id': user_obj_id})
        except (InvalidId, TypeError):
            pass
    
    @staticmethod
    def get_cart_count(user_id):
        try:
            user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            return cart_collection.count_documents({'user_id': user_obj_id})
        except (InvalidId, TypeError):
            return 0

# Initialize database with sample data
def initialize_database():
    """Initialize database with sample data if empty"""
    try:
        # Check if products exist
        if products_collection.count_documents({}) == 0:
            print("No products found. Loading sample products from JSON...")
            import json
            import os
            
            # Try to load from JSON file
            json_file_path = os.path.join(os.path.dirname(__file__), 'mongodb_products.json')
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    products_data = json.load(f)
                
                # Insert products
                if products_data:
                    products_collection.insert_many(products_data)
                    print(f"Loaded {len(products_data)} products from JSON file")
            else:
                print("JSON file not found, creating basic sample products...")
                # Create basic sample products if JSON file doesn't exist
                sample_products = [
                    {
                        "name": "Sample iPhone",
                        "category": "Electronics", 
                        "price": 999.99,
                        "description": "Sample smartphone",
                        "image_url": "https://via.placeholder.com/150",
                        "stock": 50
                    },
                    {
                        "name": "Sample Laptop",
                        "category": "Electronics",
                        "price": 1299.99, 
                        "description": "Sample laptop computer",
                        "image_url": "https://via.placeholder.com/150",
                        "stock": 30
                    }
                ]
                products_collection.insert_many(sample_products)
                print(f"Created {len(sample_products)} sample products")
        
        # Check if users exist
        if users_collection.count_documents({}) == 0:
            print("No users found. Creating admin user...")
            admin_user = User.create_user('admin', 'admin123', 'admin@store.com', 'Administrator', '555-0000')
            if admin_user:
                print("Admin user created successfully")
        
        print("Database initialization completed")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
