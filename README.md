# E-commerce Sales Chatbot

## Overview

A Flask-based chatbot for an e-commerce platform, featuring product search, authentication, and a responsive UI with Tailwind CSS.

## Features

- User authentication and session management
- Chatbot interface for product search and exploration
- RESTful API for product data
- Mock inventory with 100+ products
- Responsive design (desktop, tablet, mobile)
- Chat history stored in session

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   python app.py
   ```
3. Access at [http://localhost:5000](http://localhost:5000)

## Technology Stack

- Python, Flask, Flask-Login, Flask-SQLAlchemy
- SQLite (for mock data)
- HTML5, Tailwind CSS, JavaScript

## Challenges

- Ensuring session continuity and chat history storage
- Designing a simple yet effective chatbot UI
- Mocking a realistic product inventory

## Extensibility

- Add advanced NLP for chatbot
- Integrate payment and order modules
- Enhance product filtering and recommendations

## License

MIT
