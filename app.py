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
    return User.find_by_id(user_id)

# Initialize database
initialize_database()

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
        user = User.find_by_username(username)
        if user and check_password_hash(user.password, password):
            user.update_last_login()
            login_user(user)
            return redirect(url_for('chat'))
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
        
        if User.find_by_username(username):
            return render_template('register.html', error="Username already exists")
        
        User.create_user(username, password, email, full_name, phone)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
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
    return render_template('chat.html', username=current_user.username)

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
        print(f"Quantity: {quantity}")
        
        # Validate input
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'})
        
        if quantity < 1:
            return jsonify({'success': False, 'message': 'Invalid quantity'})
        
        # Find product
        product = Product.find_by_id(product_id)
        print(f"Product found: {product.name if product else 'None'}")
        
        if not product:
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
    payment_data = request.json
    
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
def chatbot():
    user_message = request.json.get('message', '').lower().strip()
    
    # Shopping-related commands
    if 'cart' in user_message and ('show' in user_message or 'view' in user_message):
        cart_count = CartItem.get_cart_count(current_user.get_id())
        response = f"You have {cart_count} items in your cart. Would you like to view your cart or continue shopping?"
        return jsonify({'response': response, 'products': [], 'action': 'show_cart'})
    
    # Enhanced greeting responses
    if any(word in user_message for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        cart_count = CartItem.get_cart_count(current_user.get_id())
        response = f"Hello! 👋 I'm your personal shopping assistant. You currently have {cart_count} items in your cart. I can help you find products, manage your cart, track orders, and more! What are you looking for today?"
        return jsonify({'response': response, 'products': []})
    
    # Price-based filtering
    max_price = None
    min_price = None
    
    if 'under' in user_message or 'below' in user_message or 'less than' in user_message:
        price_match = re.search(r'\$?(\d+)', user_message)
        if price_match:
            max_price = float(price_match.group(1))
    
    if 'over' in user_message or 'above' in user_message or 'more than' in user_message:
        price_match = re.search(r'\$?(\d+)', user_message)
        if price_match:
            min_price = float(price_match.group(1))
    
    # Enhanced search logic
    search_terms = user_message.replace('show me', '').replace('find', '').replace('i need', '').replace('looking for', '').strip()
    
    products = Product.search_products(search_terms, max_price, min_price)
    
    if products:
        response = f"Found {len(products)} products for '{search_terms}':"
        product_list = [{
            'id': str(p._id),
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'description': p.description,
            'image_url': p.image_url
        } for p in products]
    else:
        response = f"Sorry, no products found for '{user_message}'. Try searching for: Electronics, Fashion, Books, Gaming, or other categories."
        product_list = []
    
    # Store chat in session
    if 'chat_history' not in session:
        session['chat_history'] = []
    session['chat_history'].append({'user': user_message, 'bot': response})
    session.modified = True
    
    return jsonify({'response': response, 'products': product_list})

@app.errorhandler(500)
def internal_error(error):
    # Clear session on internal errors that might be related to invalid user IDs
    session.clear()
    return render_template('error.html', error="Internal server error. Please try logging in again."), 500

if __name__ == '__main__':
    app.run(debug=True)
