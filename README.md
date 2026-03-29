# 🛒 E-Commerce Microservices (Flask)

## 📌 Overview
This project is a microservices-based e-commerce backend built using Flask.  
It demonstrates real-world backend architecture and authentication systems, including JWT token management and service separation.

---

## 🧱 Architecture

The system is designed using a microservices approach:

- **API Gateway** – Entry point for client requests
- **User Service** – Handles authentication and JWT logic
- **Product Service** – Manages product data
- **Order Service** – Handles order processing

---

## 🔐 Authentication Flow

This project implements secure JWT authentication:

1. **Login**
   - User receives:
     - Access Token (short-lived)
     - Refresh Token (long-lived)

2. **Access Protected Routes**
   - Use access token

3. **Refresh Token**
   - When access token expires:
   - Send refresh token → receive new tokens

4. **Logout**
   - Refresh token is revoked
   - Cannot be reused

5. **Login Success**
   - User can view products
   - User can order products
   
6. **Order Logic and Stock Logic**
   - Order -> Pending -> reduce stock (Pending is under 10 minutes)
   - If order is not completed within 10 minutes -> Cancelled -> stock is restored
   - Payment Success -> Completed 
   - Payment Failure -> Cancelled -> stock is restored

---

## 🔄 Token Features

- Refresh Token Rotation
- Token Revocation (Blacklist)
- Expiration Handling
- Secure Token Storage (JTI-based)

---

## 🛠 Tech Stack

- Python (Flask)
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Flask-Migrate
- SQLite
- Docker

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Bearly11/e-commerce-microservice-flask.git
cd e-commerce-microservice-flask