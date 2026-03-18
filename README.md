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

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Bearly11/e-commerce-microservice-flask.git
cd e-commerce-microservice-flask