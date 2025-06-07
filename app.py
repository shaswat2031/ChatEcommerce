from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from models import User, Product, Order, CartItem, initialize_database

import uuid
from datetime import datetime, timedelta
import random
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    try:
        print(f"=== User Loader Called ===")
        print(f"Loading user ID: {user_id}")
        
        user = User.find_by_id(user_id)
        print(f"User loaded: {user.username if user else 'None'}")
        
        return user
    except Exception as e:
        print(f"Error in user loader: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Initialize database
initialize_database()

# Helper functions for product operations
def get_all_products():
    """Get all products from database"""
    try:
        products = Product.get_all()
        return [format_product_for_api(product) for product in products]
    except Exception as e:
        print(f"Error getting all products: {str(e)}")
        return []

def get_categories():
    """Get all unique categories from products"""
    try:
        products = Product.get_all()
        categories = list(set(product.category for product in products if product.category))
        return sorted(categories)
    except Exception as e:
        print(f"Error getting categories: {str(e)}")
        return ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Beauty', 'Automotive', 'Toys', 'Food', 'Health', 'Fashion']

def get_products_by_category(category):
    """Get products by category"""
    try:
        products = Product.find_by_category(category)
        return [format_product_for_api(product) for product in products]
    except Exception as e:
        print(f"Error getting products by category {category}: {str(e)}")
        return []

def search_products(query):
    """Search products by name or description"""
    try:
        products = Product.search(query)
        return [format_product_for_api(product) for product in products]
    except Exception as e:
        print(f"Error searching products with query '{query}': {str(e)}")
        return []

def get_products_in_price_range(min_price, max_price):
    """Get products within price range"""
    try:
        products = Product.find_by_price_range(min_price, max_price)
        return [format_product_for_api(product) for product in products]
    except Exception as e:
        print(f"Error getting products in price range ${min_price}-${max_price}: {str(e)}")
        return []

def get_featured_products(limit=10):
    """Get featured/random products"""
    try:
        import random
        all_products = Product.get_all()
        if len(all_products) <= limit:
            featured = all_products
        else:
            featured = random.sample(all_products, limit)
        return [format_product_for_api(product) for product in featured]
    except Exception as e:
        print(f"Error getting featured products: {str(e)}")
        return []

def format_product_for_api(product):
    """Format product for API response"""
    try:
        return {
            'id': str(product._id),
            'name': product.name,
            'category': product.category,
            'price': float(product.price),
            'description': product.description,
            'image_url': product.image_url,
            'stock': product.stock
        }
    except Exception as e:
        print(f"Error formatting product: {str(e)}")
        return None

@app.route('/')
def index():
    # Clear any invalid session data from old database
    if 'user_id' in session:
        try:
            # Try to load user, if it fails, clear session
            user = User.find_by_id(session['user_id'])
            if not user:
                session.clear()
        except:
            session.clear()
    
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"=== Login Debug ===")
        print(f"Username: {username}")
        print(f"Password provided: {'Yes' if password else 'No'}")
        
        user = User.find_by_username(username)
        print(f"User found: {user is not None}")
        
        if user:
            print(f"User ID: {user.get_id()}")
            print(f"User _id type: {type(user._id)}")
            print(f"Stored password hash: {user.password[:20]}...")
            
            password_check = check_password_hash(user.password, password)
            print(f"Password check result: {password_check}")
            
            if password_check:
                try:
                    print("Password verified, attempting login...")
                    
                    # Update last login
                    login_success = user.update_last_login()
                    print(f"Last login updated: {login_success}")
                    
                    # Login user with Flask-Login
                    login_result = login_user(user, remember=True)
                    print(f"login_user() result: {login_result}")
                    print(f"current_user.is_authenticated: {current_user.is_authenticated}")
                    
                    if current_user.is_authenticated:
                        print(f"Current user ID: {current_user.get_id()}")
                        print(f"Current username: {current_user.username}")
                        
                        # Verify session
                        session['user_id'] = user.get_id()
                        print(f"Session user_id set: {session.get('user_id')}")
                        
                        print("Redirecting to chat...")
                        return redirect(url_for('chat'))
                    else:
                        print("ERROR: User not authenticated after login_user()")
                        return render_template('login.html', error="Login failed. Please try again.")
                        
                except Exception as e:
                    print(f"Error during login process: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return render_template('login.html', error="Login failed. Please try again.")
            else:
                print("Password check failed")
        else:
            print("User not found")
            
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        full_name = request.form.get('full_name', '')
        phone = request.form.get('phone', '')
        
        print(f"=== Registration Debug ===")
        print(f"Username: {username}")
        print(f"Password provided: {'Yes' if password else 'No'}")
        
        if User.find_by_username(username):
            return render_template('register.html', error="Username already exists")
        
        try:
            new_user = User.create_user(username, password, email, full_name, phone)
            print(f"User created: {new_user is not None}")
            if new_user:
                print(f"New user ID: {new_user.get_id()}")
                print(f"Password hash: {new_user.password[:20]}...")
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return render_template('register.html', error="Registration failed. Please try again.")
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    """Enhanced chat interface with product integration"""
    print(f"=== Chat Route Debug ===")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user.username if current_user.is_authenticated else 'None'}")
    print(f"Session user_id: {session.get('user_id')}")
    
    return render_template('chat.html', username=current_user.username if current_user.is_authenticated else 'Guest')

@app.route('/profile')
@login_required
def profile():
    user_orders = Order.find_by_user(current_user.get_id())
    cart_count = CartItem.get_cart_count(current_user.get_id())
    total_spent = sum(order.total_amount for order in user_orders)
    
    return render_template('profile.html', 
                         user=current_user, 
                         orders_count=len(user_orders),
                         cart_count=cart_count,
                         total_spent=total_spent,
                         datetime=datetime)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        update_data = {
            'full_name': request.form.get('full_name', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'address': request.form.get('address', ''),
            'city': request.form.get('city', ''),
            'state': request.form.get('state', ''),
            'zip_code': request.form.get('zip_code', '')
        }
        
        # Handle date of birth
        dob_str = request.form.get('date_of_birth', '')
        if dob_str:
            try:
                update_data['date_of_birth'] = datetime.strptime(dob_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        current_user.update_profile(**update_data)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=current_user)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.username != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.get_all_users()
    orders = Order.get_all_orders()
    total_users = len(users)
    total_orders = len(orders)
    total_revenue = sum(order.total_amount for order in orders)
    
    return render_template('admin_dashboard.html', 
                         users=users[:10],  # Show latest 10 users
                         orders=orders[:10],  # Show latest 10 orders
                         total_users=total_users,
                         total_orders=total_orders,
                         total_revenue=total_revenue)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.username != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.get_all_users()
    return render_template('admin_users.html', users=users)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if current_user.username != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    orders = Order.get_all_orders()
    # Add user information to orders
    for order in orders:
        user = User.find_by_id(str(order.user_id))
        order.user = user
    
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/order/<order_id>')
@login_required
def admin_order_detail(order_id):
    if current_user.username != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    order = Order.find_by_id(order_id)
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('admin_orders'))
    
    # Get user information
    user = User.find_by_id(str(order.user_id))
    order.user = user
    
    return render_template('admin_order_detail.html', order=order)

@app.route('/admin/order/<order_id>/update-status', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    if current_user.username != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        print(f"=== Admin Status Update Debug ===")
        print(f"Order ID: {order_id}")
        print(f"Request data: {request.get_data()}")
        
        data = request.get_json()
        new_status = data.get('status') if data else None
        
        print(f"New status: {new_status}")
        
        valid_statuses = ['Processing', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Status is required'})
        
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        # Find order by ID
        order = Order.find_by_id(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        print(f"Found order: {order.order_number}")
        print(f"Current status: {order.status}")
        
        # Update status
        order.update_status(new_status)
        
        print(f"Status updated to: {new_status}")
        
        return jsonify({
            'success': True, 
            'message': f'Order status updated to {new_status}',
            'new_status': new_status
        })
        
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/api/cart/count', methods=['GET'])
@login_required
def get_cart_count():
    try:
        cart_count = CartItem.get_cart_count(current_user.get_id())
        return jsonify({'count': cart_count})
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})

@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    try:
        print(f"=== Add to Cart Debug ===")
        print(f"User: {current_user.username}")
        print(f"User ID: {current_user.get_id()}")
        print(f"Request content type: {request.content_type}")
        print(f"Request data: {request.get_data()}")
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        print(f"Parsed data: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'})
        
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        print(f"Product ID: {product_id}")
        print(f"Product ID type: {type(product_id)}")
        print(f"Product ID length: {len(product_id) if product_id else 'None'}")
        print(f"Quantity: {quantity}")
        
        # Validate input
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'})
        
        if quantity < 1:
            return jsonify({'success': False, 'message': 'Invalid quantity'})
        
        # Validate ObjectId format
        if len(product_id) != 24:
            print(f"Invalid ObjectId format: {product_id}")
            return jsonify({'success': False, 'message': 'Invalid product ID format'})
        
        # Find product
        print(f"Searching for product with ID: {product_id}")
        product = Product.find_by_id(product_id)
        print(f"Product found: {product.name if product else 'None'}")
        
        if not product:
            # Let's also try to see what products exist
            all_products = Product.get_all()
            print(f"Total products in database: {len(all_products)}")
            if all_products:
                print(f"Sample product IDs: {[str(p._id) for p in all_products[:3]]}")
            return jsonify({'success': False, 'message': 'Product not found'})
        
        # Add to cart
        user_id = current_user.get_id()
        print(f"Adding to cart for user: {user_id}")
        
        cart_item = CartItem.add_to_cart(user_id, product_id, quantity)
        print(f"Cart item result: {cart_item is not None}")
        
        if not cart_item:
            return jsonify({'success': False, 'message': 'Failed to add item to cart'})
        
        # Get updated cart count
        cart_count = CartItem.get_cart_count(user_id)
        print(f"Updated cart count: {cart_count}")
        
        response_data = {
            'success': True, 
            'message': f'{product.name} added to cart!',
            'cart_count': cart_count
        }
        print(f"Response: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"=== ERROR in add_to_cart ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.get_user_cart(current_user.get_id())
    total = sum(item.quantity * product.price for item, product in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/api/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    item_id = request.json.get('item_id')
    CartItem.remove_from_cart(item_id, current_user.get_id())
    return jsonify({'success': True})

@app.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.get_user_cart(current_user.get_id())
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('view_cart'))
    
    total = sum(item.quantity * product.price for item, product in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/api/process-payment', methods=['POST'])
@login_required
def process_payment():
    payment_data = request.json or {}
    
    # Simulate payment processing
    card_number = payment_data.get('card_number', '').replace(' ', '')
    if len(card_number) != 16 or not card_number.isdigit():
        return jsonify({'success': False, 'message': 'Invalid card number'})
    
    # Simulate random payment failures (10% chance)
    if random.random() < 0.1:
        return jsonify({'success': False, 'message': 'Payment declined. Please try again.'})
    
    # Create order
    cart_items = CartItem.get_user_cart(current_user.get_id())
    total = sum(item.quantity * product.price for item, product in cart_items)
    
    # Prepare order items
    order_items = []
    for cart_item, product in cart_items:
        order_items.append({
            'product_id': str(product._id),
            'product_name': product.name,
            'quantity': cart_item.quantity,
            'price': product.price,
            'total': cart_item.quantity * product.price
        })
    
    order = Order.create_order(
        current_user.get_id(),
        total,
        payment_data.get('address', ''),
        'Card ending in ' + card_number[-4:],
        order_items
    )
    
    # Clear cart
    CartItem.clear_cart(current_user.get_id())
    
    return jsonify({
        'success': True, 
        'order_number': order.order_number,
        'message': 'Payment successful! Your order is being processed.'
    })

@app.route('/orders')
@login_required
def order_history():
    orders = Order.find_by_user(current_user.get_id())
    return render_template('orders.html', orders=orders)

@app.route('/order/<order_number>')
@login_required
def track_order(order_number):
    order = Order.find_by_order_number(order_number, current_user.get_id())
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('order_history'))
    
    # Simulate order progression
    days_since_order = (datetime.utcnow() - order.created_at).days
    if days_since_order >= 5:
        order.update_status('Delivered')
    elif days_since_order >= 3:
        order.update_status('Shipped')
    elif days_since_order >= 1:
        order.update_status('Confirmed')
    
    return render_template('track_order.html', order=order)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.username == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    recent_orders = Order.find_by_user(current_user.get_id())[:5]
    cart_count = CartItem.get_cart_count(current_user.get_id())
    total_spent = sum(order.total_amount for order in Order.find_by_user(current_user.get_id()))
    
    return render_template('dashboard.html', 
                         recent_orders=recent_orders, 
                         cart_count=cart_count, 
                         total_spent=total_spent)

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """Enhanced chatbot API with comprehensive product recommendations"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower().strip()
        
        if not user_message:
            return jsonify({
                'response': "I didn't catch that. Could you please tell me what you're looking for?",
                'products': []
            })
        
        # Enhanced greeting responses
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'start', 'begin']
        if any(greeting in user_message for greeting in greetings):
            cart_count = CartItem.get_cart_count(current_user.get_id())
            featured = get_featured_products(6)
            categories = get_categories()
            response = f"Hello {current_user.username}! 👋 Welcome to our store!\n\nYou have {cart_count} items in your cart.\n\nAvailable categories: {', '.join(categories[:5])}{'...' if len(categories) > 5 else ''}\n\nHere are some popular products:"
            return jsonify({
                'response': response,
                'products': featured
            })
        
        # Cart-related queries
        if 'cart' in user_message:
            cart_count = CartItem.get_cart_count(current_user.get_id())
            if any(word in user_message for word in ['show', 'view', 'check', 'see']):
                response = f"You have {cart_count} items in your cart. Would you like to view your cart?"
                return jsonify({
                    'response': response, 
                    'products': [],
                    'action': 'show_cart'
                })
            else:
                response = f"You currently have {cart_count} items in your cart. I can help you add more items or view your cart!"
                return jsonify({'response': response, 'products': []})
        
        # Category-based searches with comprehensive coverage
        categories = get_categories()
        found_category = None
        
        # Enhanced category matching with more aliases
        category_aliases = {
            'electronics': ['electronics', 'electronic', 'tech', 'technology', 'gadgets', 'devices', 'phones', 'laptops', 'computers', 'tablet', 'tablets'],
            'clothing': ['clothing', 'clothes', 'apparel', 'fashion', 'wear', 'shirts', 'pants', 'shoes', 'sneakers', 'dress', 'dresses', 'jacket', 'jackets'],
            'home & garden': ['home', 'garden', 'house', 'kitchen', 'furniture', 'appliances', 'decor', 'indoor', 'outdoor', 'dining', 'bedroom', 'living room'],
            'sports': ['sports', 'sport', 'fitness', 'exercise', 'gym', 'workout', 'athletic', 'recreation', 'running', 'cycling', 'swimming'],
            'books': ['books', 'book', 'reading', 'literature', 'novels', 'education', 'learning', 'textbook', 'textbooks', 'fiction', 'non-fiction'],
            'beauty': ['beauty', 'cosmetics', 'makeup', 'skincare', 'personal care', 'grooming', 'fragrance', 'perfume', 'lotion'],
            'automotive': ['automotive', 'car', 'auto', 'vehicle', 'truck', 'motorcycle', 'parts', 'accessories', 'tools'],
            'toys': ['toys', 'toy', 'games', 'kids', 'children', 'play', 'fun', 'educational', 'puzzle', 'board games'],
            'food': ['food', 'grocery', 'snacks', 'ingredients', 'cooking', 'eating', 'beverages', 'drinks', 'organic'],
            'health': ['health', 'medical', 'wellness', 'supplements', 'vitamins', 'healthcare', 'pharmacy', 'medicine'],
            'fashion': ['fashion', 'style', 'trendy', 'designer', 'luxury', 'accessories', 'jewelry', 'watches', 'bags']
        }
        
        # Check for category matches
        for category in categories:
            category_lower = category.lower()
            if category_lower in user_message:
                found_category = category
                break
            
            # Check aliases
            if category_lower in category_aliases:
                for alias in category_aliases[category_lower]:
                    if alias in user_message:
                        found_category = category
                        break
                if found_category:
                    break
        
        # Enhanced search patterns
        search_patterns = [
            'show', 'find', 'search', 'looking for', 'need', 'want', 'get me',
            'recommend', 'suggest', 'help me find', 'i want to buy', 'browse',
            'display', 'list', 'see some', 'what do you have'
        ]
        
        is_search_query = any(pattern in user_message for pattern in search_patterns)
        
        if found_category:
            products = get_products_by_category(found_category)[:12]
            if products:
                response = f"Here are some great {found_category} products I found for you ({len(products)} items):"
                return jsonify({
                    'response': response,
                    'products': products,
                    'category': found_category  # Add category info for frontend
                })
            else:
                response = f"Sorry, we don't have any {found_category} products in stock right now. Here are some alternatives from other categories:"
                alternatives = get_featured_products(8)
                return jsonify({
                    'response': response,
                    'products': alternatives
                })
        
        # Price-based filtering with enhanced patterns
        import re
        
        # Under/below/less than price
        under_patterns = [
            r'under \$?(\d+)',
            r'below \$?(\d+)',
            r'less than \$?(\d+)',
            r'cheaper than \$?(\d+)',
            r'maximum \$?(\d+)',
            r'max \$?(\d+)'
        ]
        
        for pattern in under_patterns:
            match = re.search(pattern, user_message)
            if match:
                max_price = float(match.group(1))
                products = get_products_in_price_range(0, max_price)[:10]
                if products:
                    response = f"Here are {len(products)} products under ${max_price}:"
                    return jsonify({
                        'response': response,
                        'products': products
                    })
        
        # Over/above/more than price
        over_patterns = [
            r'over \$?(\d+)',
            r'above \$?(\d+)',
            r'more than \$?(\d+)',
            r'expensive than \$?(\d+)',
            r'minimum \$?(\d+)',
            r'min \$?(\d+)'
        ]
        
        for pattern in over_patterns:
            match = re.search(pattern, user_message)
            if match:
                min_price = float(match.group(1))
                products = get_products_in_price_range(min_price, 10000)[:10]
                if products:
                    response = f"Here are {len(products)} products over ${min_price}:"
                    return jsonify({
                        'response': response,
                        'products': products
                    })
          # Between price range
        between_match = re.search(r'between \$?(\d+) and \$?(\d+)', user_message)
        if between_match:
            min_price = float(between_match.group(1))
            max_price = float(between_match.group(2))
            products = get_products_in_price_range(min_price, max_price)[:10]
            if products:
                response = f"Here are {len(products)} products between ${min_price} and ${max_price}:"
                return jsonify({
                    'response': response,
                    'products': products
                })
        
        # Brand-specific searches
        popular_brands = [
            'apple', 'samsung', 'google', 'microsoft', 'sony', 'nintendo',
            'nike', 'adidas', 'puma', 'under armour',
            'canon', 'nikon', 'gopro',
            'ikea', 'kitchenaid', 'dyson',
            'lego', 'barbie', 'hot wheels',
            'fenty', 'urban decay', 'loreal',
            'wilson', 'spalding', 'callaway'
        ]
        
        for brand in popular_brands:
            if brand in user_message:
                brand_products = search_products(brand)[:8]
                if brand_products:
                    response = f"Here are {brand.title()} products I found:"
                    return jsonify({
                        'response': response,
                        'products': brand_products
                    })
        
        # Specific product searches
        product_keywords = {
            'phone': ['iphone', 'samsung', 'smartphone', 'mobile'],
            'laptop': ['macbook', 'dell', 'microsoft surface', 'computer'],
            'headphones': ['airpods', 'beats', 'sony', 'wireless'],
            'shoes': ['nike', 'adidas', 'sneakers', 'running'],
            'watch': ['rolex', 'fitbit', 'smartwatch', 'timepiece'],
            'book': ['novel', 'education', 'reading', 'literature']
        }
        
        for keyword, related_terms in product_keywords.items():
            if keyword in user_message or any(term in user_message for term in related_terms):
                products = search_products(keyword)[:8]
                if products:
                    response = f"Here are {keyword} products I found:"
                    return jsonify({
                        'response': response,
                        'products': products
                    })
        
        # General product search
        if is_search_query:
            search_terms = user_message
            for pattern in search_patterns:
                search_terms = search_terms.replace(pattern, '')
            
            stop_words = ['a', 'an', 'the', 'for', 'me', 'some', 'any', 'good', 'best', 'great', 'nice']
            words = [word for word in search_terms.split() if word not in stop_words and len(word) > 2]
            
            if words:
                all_results = []
                for word in words:
                    results = search_products(word)
                    all_results.extend(results)
                
                seen = set()
                unique_products = []
                for product in all_results:
                    if product and product['id'] not in seen:
                        seen.add(product['id'])
                        unique_products.append(product)
                        if len(unique_products) >= 12:
                            break
                
                if unique_products:
                    search_term = ' '.join(words)
                    response = f"I found {len(unique_products)} products for '{search_term}':"
                    return jsonify({
                        'response': response,
                        'products': unique_products
                    })
        
        # Categories listing
        if any(word in user_message for word in ['categories', 'category', 'sections', 'departments', 'what do you have', 'what categories']):
            categories = get_categories()
            response = f"We have {len(categories)} categories:\n\n{', '.join(categories)}\n\nJust ask me about any category! For example: 'show me electronics' or 'find books'"
            sample_products = get_featured_products(6)
            return jsonify({
                'response': response,
                'products': sample_products
            })
        
        # Help and information queries
        if any(word in user_message for word in ['help', 'what can you do', 'commands', 'options', 'how to', 'guide']):
            categories = get_categories()
            response = f"""🤖 I can help you with:

🛍️ **Browse by Category**: "show me {categories[0].lower()}" or "find {categories[1].lower()}"
💰 **Price Filtering**: "products under $100" or "between $50 and $200"
🏷️ **Brand Search**: "Apple products" or "Nike shoes"
🔍 **Product Search**: "find laptops" or "show headphones"
🛒 **Cart Management**: "show my cart" or "add to cart"
📦 **Order Tracking**: "my orders" or "track order"

**Available Categories**: {', '.join(categories[:8])}{'...' if len(categories) > 8 else ''}

Try asking: "show me electronics under $500" or "find Nike shoes"!"""
            
            sample_products = get_featured_products(4)
            return jsonify({
                'response': response,
                'products': sample_products
            })
        
        # Order and shipping queries
        if any(word in user_message for word in ['order', 'orders', 'shipping', 'delivery', 'track']):
            recent_orders = Order.find_by_user(current_user.get_id())[:3]
            if recent_orders:
                response = f"You have {len(Order.find_by_user(current_user.get_id()))} total orders. Your most recent orders:"
                return jsonify({
                    'response': response,
                    'products': [],
                    'action': 'show_orders'
                })
            else:
                response = "You don't have any orders yet. Let me show you some great products to get started!"
                featured = get_featured_products(8)
                return jsonify({
                    'response': response,
                    'products': featured
                })
        
        # Default response with category suggestions
        categories = get_categories()
        responses = [
            f"I'm here to help you find amazing products! We have {len(categories)} categories to explore.",
            f"Let me show you some popular items, or ask about any of our {len(categories)} categories!",
            f"I can help you discover great products. Try asking about {', '.join(categories[:3])}, or any other category!",
            "Not sure what you need? Here are some trending products, or tell me what category interests you:"
        ]
        
        random_products = get_featured_products(8)
        response = random.choice(responses)
        suggestion = f"💡 Try: 'show me {random.choice(categories).lower()}', 'products under $100', or 'help' for more options"
        
        return jsonify({
            'response': response,
            'products': random_products,
            'suggestion': suggestion
        })
        
    except Exception as e:
        print(f"Error in chat_api: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'response': "Sorry, I encountered an error. Please try again! You can ask me about our product categories or search for specific items.",
            'products': get_featured_products(4) if 'get_featured_products' in globals() else []
        })

@app.route('/api/products')
def api_products():
    """Enhanced API endpoint to get products with filtering"""
    try:
        category = request.args.get('category')
        search_query = request.args.get('search')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        limit = request.args.get('limit', 20, type=int)
        
        if category:
            products = get_products_by_category(category)
        elif search_query:
            products = search_products(search_query)
        elif min_price is not None and max_price is not None:
            products = get_products_in_price_range(min_price, max_price)
        else:
            products = get_all_products()
        
        # Apply limit
        if limit:
            products = products[:limit]
        
        return jsonify({
            'success': True,
            'products': products,
            'total': len(products),
            'categories': get_categories()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'products': []
        })

@app.route('/api/categories')
def api_categories():
    """API endpoint to get all categories with product counts"""
    try:
        categories = get_categories()
        category_data = []
        
        for category in categories:
            products = get_products_by_category(category)
            category_data.append({
                'name': category,
                'count': len(products),
                'sample_products': products[:3]
            })
        
        return jsonify({
            'success': True,
            'categories': category_data,
            'total_categories': len(categories)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/featured-products')
def api_featured_products():
    """API endpoint to get featured products"""
    try:
        limit = request.args.get('limit', 10, type=int)
        products = get_featured_products(limit)
        return jsonify({
            'success': True,
            'products': products,
            'total': len(products)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'products': []
        })

@app.errorhandler(500)
def internal_error(error):
    session.clear()
    return render_template('error.html', error="Internal server error. Please try logging in again."), 500

if __name__ == '__main__':
    app.run(debug=True)
