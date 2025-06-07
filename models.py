from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
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

class User:
    def __init__(self, data=None):
        if data:
            self._id = data.get('_id')
            self.username = data.get('username')
            self.password = data.get('password')
            self.email = data.get('email')
            self.full_name = data.get('full_name')
            self.phone = data.get('phone')
            self.address = data.get('address')
            self.city = data.get('city')
            self.state = data.get('state')
            self.zip_code = data.get('zip_code')
            self.date_of_birth = data.get('date_of_birth')
            self.created_at = data.get('created_at', datetime.utcnow())
            self.last_login = data.get('last_login')
            self.is_active = data.get('is_active', True)
            self.profile_picture = data.get('profile_picture', 'https://via.placeholder.com/150')
    
    def get_id(self):
        return str(self._id)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    @staticmethod
    def create_user(username, password, email=None, full_name=None, phone=None):
        user_data = {
            'username': username,
            'password': generate_password_hash(password),
            'email': email,
            'full_name': full_name,
            'phone': phone,
            'created_at': datetime.utcnow(),
            'is_active': True,
            'profile_picture': 'https://via.placeholder.com/150'
        }
        result = users_collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)
    
    @staticmethod
    def find_by_username(username):
        user_data = users_collection.find_one({'username': username})
        return User(user_data) if user_data else None
    
    @staticmethod
    def find_by_id(user_id):
        try:
            # Try to convert to ObjectId
            if isinstance(user_id, str) and len(user_id) == 24:
                object_id = ObjectId(user_id)
            elif isinstance(user_id, ObjectId):
                object_id = user_id
            else:
                # Invalid ID format, return None
                return None
                
            user_data = users_collection.find_one({'_id': object_id})
            return User(user_data) if user_data else None
        except (InvalidId, TypeError):
            # If ObjectId conversion fails, return None
            return None
    
    @staticmethod
    def get_all_users():
        users_data = users_collection.find().sort('created_at', -1)
        return [User(user) for user in users_data]
    
    def update_profile(self, **kwargs):
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if update_data:
            users_collection.update_one({'_id': self._id}, {'$set': update_data})
            for key, value in update_data.items():
                setattr(self, key, value)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        users_collection.update_one({'_id': self._id}, {'$set': {'last_login': self.last_login}})

class Product:
    def __init__(self, data=None):
        if data:
            self._id = data.get('_id')
            self.name = data.get('name')
            self.category = data.get('category')
            self.price = data.get('price')
            self.description = data.get('description')
            self.image_url = data.get('image_url')
            self.stock = data.get('stock', 100)
            self.created_at = data.get('created_at', datetime.utcnow())
    
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
        return Product(product_data)
    
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
        return [Product(product) for product in products_data]
    
    @staticmethod
    def find_by_id(product_id):
        try:
            if isinstance(product_id, str) and len(product_id) == 24:
                object_id = ObjectId(product_id)
            elif isinstance(product_id, ObjectId):
                object_id = product_id
            else:
                return None
                
            product_data = products_collection.find_one({'_id': object_id})
            return Product(product_data) if product_data else None
        except (InvalidId, TypeError):
            return None
    
    @staticmethod
    def get_categories():
        return products_collection.distinct('category')

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
    # Check if admin user exists
    admin_user = users_collection.find_one({'username': 'admin'})
    if not admin_user:
        User.create_user('admin', 'admin123', 'admin@example.com', 'Administrator')
    
    # Check if products exist
    if products_collection.count_documents({}) == 0:
        products_data = [
            # Electronics - Smartphones
            {'name': 'iPhone 15 Pro Max', 'category': 'Electronics', 'price': 1199.99, 'description': 'Latest iPhone with A17 Pro chip, titanium design, and advanced camera system'},
            {'name': 'Samsung Galaxy S24 Ultra', 'category': 'Electronics', 'price': 1299.99, 'description': 'Premium Android phone with S Pen, 200MP camera, and AI features'},
            {'name': 'Google Pixel 8 Pro', 'category': 'Electronics', 'price': 999.99, 'description': 'Google\'s flagship with advanced AI photography and pure Android experience'},
            
            # Books
            {'name': 'The Seven Husbands of Evelyn Hugo', 'category': 'Books', 'price': 16.99, 'description': 'Captivating novel about a reclusive Hollywood icon\'s life story'},
            {'name': 'Atomic Habits', 'category': 'Books', 'price': 17.99, 'description': 'Proven way to build good habits and break bad ones by James Clear'},
            
            # Fashion
            {'name': 'Levi\'s 501 Original Jeans', 'category': 'Fashion', 'price': 89.99, 'description': 'Classic straight-leg jeans with authentic fits and vintage details'},
            {'name': 'Nike Air Force 1', 'category': 'Fashion', 'price': 110.99, 'description': 'Iconic basketball shoe with leather upper and air cushioning'},
            
            # Gaming
            {'name': 'PlayStation 5 Console', 'category': 'Gaming', 'price': 499.99, 'description': 'Next-gen gaming console with 4K gaming and ray tracing'},
            {'name': 'Xbox Series X', 'category': 'Gaming', 'price': 499.99, 'description': 'Most powerful Xbox with 4K gaming at 60fps'},
        ]
        
        for product_data in products_data:
            Product.create_product(
                product_data['name'],
                product_data['category'],
                product_data['price'],
                product_data['description'],
                'https://via.placeholder.com/150'
            )
