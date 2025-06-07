# E-commerce Chatbot Application

A modern Flask-based e-commerce platform featuring an intelligent chatbot interface, comprehensive product management, user authentication, shopping cart functionality, and administrative tools.

## 🎯 Overview

This application combines traditional e-commerce functionality with an AI-powered chatbot interface that helps users discover products through natural language conversations. Built with Flask and MongoDB, it provides a seamless shopping experience with modern UI components.

## ✨ Key Features

### 🤖 Intelligent Chatbot
- **Natural Language Processing**: Understands various ways users express product searches
- **Category Recognition**: Automatically detects product categories from user messages
- **Price Filtering**: Supports price range queries ("under $100", "between $50-$200")
- **Brand Search**: Recognizes popular brand names and suggests relevant products
- **Contextual Responses**: Provides helpful suggestions and alternatives
- **Interactive Product Display**: Shows products with images, prices, and descriptions

### 🛒 E-commerce Functionality
- **Product Catalog**: Comprehensive product database with categories, pricing, and descriptions
- **Shopping Cart**: Add/remove items, view cart summary, quantity management
- **Secure Checkout**: Simulated payment processing with validation
- **Order Management**: Order history, tracking, and status updates
- **User Profiles**: Personal information management and order history

### 👤 User Management
- **Authentication System**: Secure user registration and login
- **Session Management**: Persistent user sessions with Flask-Login
- **Profile Management**: User information editing and preferences
- **Password Security**: Werkzeug password hashing and verification

### 👨‍💼 Administrative Panel
- **User Management**: View all registered users with privacy controls
- **Order Management**: Track all orders, update statuses, view details
- **Sales Analytics**: Revenue tracking, user statistics, order summaries
- **System Overview**: Dashboard with key metrics and recent activity

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Tailwind CSS**: Modern, utility-first CSS framework
- **Interactive Animations**: Smooth transitions and hover effects
- **Intuitive Navigation**: Clean, user-friendly interface design

## 🏗️ Architecture

### Backend Components
```
app.py                 # Main Flask application with routes and business logic
models.py             # MongoDB data models (User, Product, Order, CartItem)
settings.py           # Configuration file (legacy Django structure)
requirements.txt      # Python dependencies
```

### Frontend Templates
```
templates/
├── login.html           # User authentication
├── register.html        # User registration
├── chat.html           # Main chatbot interface
├── dashboard.html      # User dashboard
├── profile.html        # User profile management
├── cart.html           # Shopping cart view
├── checkout.html       # Payment processing
├── orders.html         # Order history
├── track_order.html    # Order tracking
├── admin_dashboard.html # Admin overview
├── admin_users.html    # User management
├── admin_orders.html   # Order management
└── admin_order_detail.html # Detailed order view
```

## 🔧 Technology Stack

### Backend
- **Flask**: Lightweight Python web framework
- **Flask-Login**: User session management
- **PyMongo**: MongoDB database driver
- **Werkzeug**: Password hashing and security utilities

### Database
- **MongoDB**: NoSQL database for flexible document storage
- **Collections**: users, products, orders, cart_items

### Frontend
- **HTML5**: Semantic markup structure
- **Tailwind CSS**: Utility-first styling framework
- **JavaScript**: Interactive functionality and AJAX requests
- **Responsive Design**: Mobile-first approach

### Development Tools
- **Python 3.x**: Core programming language
- **MongoDB**: Local database instance
- **Modern Browser**: For testing and development

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure you have Python 3.7+ installed
python --version

# Install MongoDB and start the service
# Windows: Download from MongoDB website
# macOS: brew install mongodb
# Linux: apt-get install mongodb
```

### Installation Steps

1. **Clone and Navigate**
   ```bash
   cd d:\Development\test\Django
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start MongoDB**
   ```bash
   # Windows
   mongod

   # macOS/Linux
   sudo systemctl start mongod
   ```

4. **Initialize Database**
   ```bash
   python app.py
   # Database will auto-initialize with sample data
   ```

5. **Access Application**
   ```
   http://localhost:5000
   ```

### Default Credentials
```
Admin Account:
- Username: admin
- Password: admin123

Regular User:
- Register a new account through the interface
```

## 📊 Database Schema

### Users Collection
```javascript
{
  "_id": ObjectId,
  "username": String,
  "password": String (hashed),
  "email": String,
  "full_name": String,
  "phone": String,
  "created_at": Date,
  "last_login": Date,
  "address": String,
  "city": String,
  "state": String,
  "zip_code": String,
  "date_of_birth": Date
}
```

### Products Collection
```javascript
{
  "_id": ObjectId,
  "name": String,
  "category": String,
  "price": Number,
  "description": String,
  "image_url": String,
  "stock": Number,
  "created_at": Date
}
```

### Orders Collection
```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "order_number": String,
  "total_amount": Number,
  "status": String,
  "shipping_address": String,
  "payment_method": String,
  "items": Array,
  "created_at": Date
}
```

### Cart Items Collection
```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "product_id": ObjectId,
  "quantity": Number,
  "created_at": Date
}
```

## 🎮 Chatbot Commands

### Basic Interactions
```
"Hello" / "Hi"           → Welcome message with featured products
"Help"                   → List of available commands
"Categories"             → Show all product categories
```

### Product Discovery
```
"Show me electronics"    → Electronics category products
"Find laptops"          → Search for laptop products
"Products under $100"   → Price-filtered results
"Between $50 and $200"  → Price range search
"Apple products"        → Brand-specific search
```

### Shopping Actions
```
"Show my cart"          → Display cart contents
"My orders"             → Show order history
"Track order [number]"  → Order status tracking
```

## 🔌 API Endpoints

### Authentication
```
POST /login              # User login
POST /register           # User registration
GET  /logout             # User logout
```

### Chat & Products
```
POST /api/chat           # Chatbot interaction
GET  /api/products       # Get products with filters
GET  /api/categories     # Get all categories
GET  /api/featured-products # Get featured products
```

### Shopping Cart
```
POST /api/cart/add       # Add item to cart
POST /api/cart/remove    # Remove item from cart
GET  /api/cart/count     # Get cart item count
```

### Orders
```
POST /api/process-payment # Process checkout
GET  /orders             # Order history
GET  /order/<number>     # Track specific order
```

### Admin (Requires admin privileges)
```
GET  /admin/dashboard    # Admin overview
GET  /admin/users        # User management
GET  /admin/orders       # Order management
POST /admin/order/<id>/update-status # Update order status
```

## 🎨 UI Components

### Responsive Design Features
- **Mobile-First**: Optimized for small screens
- **Tablet Support**: Medium screen adaptations
- **Desktop Enhanced**: Full-featured desktop experience

### Interactive Elements
- **Hover Effects**: Card animations and button responses
- **Loading States**: Visual feedback during operations
- **Form Validation**: Real-time input validation
- **Modal Dialogs**: Status updates and confirmations

### Color Scheme
- **Primary**: Blue tones for main actions
- **Success**: Green for positive actions
- **Warning**: Yellow for alerts
- **Error**: Red for problems
- **Neutral**: Gray scale for content

## 🔍 Troubleshooting

### Common Issues

**Database Connection Problems**
```bash
# Check MongoDB status
mongod --version
ps aux | grep mongod

# Restart MongoDB service
sudo systemctl restart mongod
```

**Login Issues**
```bash
# Clear browser cookies and session data
# Check user credentials in MongoDB
# Verify password hashing in models.py
```

**Product Loading Problems**
```bash
# Initialize database with sample data
python -c "from models import initialize_database; initialize_database()"
```

**Port Conflicts**
```bash
# Change Flask port in app.py
app.run(debug=True, port=5001)
```

## 🚦 Development Workflow

### Adding New Features
1. **Model Changes**: Update `models.py` for data structure changes
2. **Route Implementation**: Add new routes in `app.py`
3. **Template Creation**: Create HTML templates in `templates/`
4. **API Integration**: Update chatbot logic for new features
5. **Testing**: Verify functionality across all user types

### Code Structure
```python
# Example route pattern
@app.route('/new-feature')
@login_required
def new_feature():
    # Business logic
    # Database operations
    # Template rendering
    return render_template('new_feature.html', data=data)
```

## 📈 Future Enhancements

### Planned Features
- **Advanced NLP**: Integration with GPT or other AI models
- **Real Payment Processing**: Stripe/PayPal integration
- **Inventory Management**: Stock tracking and alerts
- **Product Reviews**: User ratings and feedback system
- **Recommendation Engine**: Personalized product suggestions
- **Multi-language Support**: Internationalization
- **Mobile App**: React Native or Flutter companion app

### Performance Optimizations
- **Database Indexing**: Optimize MongoDB queries
- **Caching Layer**: Redis for session and product caching
- **CDN Integration**: Static asset delivery optimization
- **API Rate Limiting**: Prevent abuse and ensure stability

## 📄 License

MIT License - Feel free to use this project for learning, development, or commercial purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or issues:
- Check the troubleshooting section
- Review the API documentation
- Examine the code comments for implementation details
- Test with the default admin account for full functionality

---

**Built with ❤️ using Flask, MongoDB, and modern web technologies**
