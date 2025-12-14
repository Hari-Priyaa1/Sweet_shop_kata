 # 🍰 Sweet Shop Kata - Full-Stack E-commerce Simulation

## 🚀 Project Overview

This project is a full-stack web application designed to simulate a sweet shop's inventory and sales management system. It supports role-based access control, distinguishing between a **Customer** who can browse and purchase sweets, and a **Seller** who has full CRUD (Create, Read, Update, Delete) rights over the product inventory.

The application serves as a complete demonstration of:
* **Role-Based Access Control (RBAC):** Secure login and protected API endpoints.
* **Full CRUD Functionality:** Inventory management for Sellers.
* **Database Initialization:** Consistent product data setup on the first run.

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend (API)** | **Python/FastAPI** | Fast and modern API framework. |
| **Database** | **SQLite (via SQLAlchemy)** | Lightweight, file-based database. |
| **Frontend (UI)** | **React.js** | Modern JavaScript library for building the user interface. |



📸 Application Screenshots



<img width="1539" height="877" alt="Screenshot 2025-12-14 225917" src="https://github.com/user-attachments/assets/6225ab1a-a564-4637-ab95-887f08126308" />


<img width="931" height="773" alt="Screenshot 2025-12-14 211638" src="https://github.com/user-attachments/assets/ef45b517-239a-4c5f-80db-06424803512d" />


 ## 🏃 Getting Started (How to RunLocally)

Follow these steps to get the Sweet Shop running on your machine:

### Prerequisites

* Python 3.8+
* Node.js and npm (for the frontend)

### 1. Backend Setup (FastAPI)

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```
    *The API will be available at `http://127.0.0.1:8000`.*

### 2. Frontend Setup (React)

1.  Open a **new terminal window** and navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the application:
    ```bash
    npm start
    ```
    *The frontend will open in your browser at `http://localhost:3000`.*

 

## 🤖 AI Usage Policy

This project utilized an AI assistant to accelerate development, adhering strictly to the assignment guidelines.

* The AI assistant **Gemini** was primarily used for generating initial boilerplate code (e.g., API route skeletons, React component scaffolding) and debugging complex integration issues (e.g., fixing SQLAlchemy relationships).
* All critical business logic, security validation, database schema design, and UI styling decisions were implemented or reviewed manually by the author.
* All commits where AI assistance was used include the required Co-authored-by trailer.

---
