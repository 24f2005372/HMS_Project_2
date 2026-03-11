# Hospital Management System V2 (Decoupled Architecture)
### Modern Application Development II - Final Submission

## Project Overview
HMS V2 is a modern, decoupled web application designed to manage hospital operations efficiently.
- **Architecture:** Decoupled (REST API Backend + SPA Frontend).
- **Backend:** Flask (Python) serving JSON.
- **Frontend:** Vue.js (Vue 3) with Bootstrap 5.
- **Advanced Features:** Asynchronous Jobs (Celery logic), Caching (Redis logic), and Data Analytics (Chart.js).

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-CORS.
- **Frontend:** Vue.js 3, Axios, Vue Router.
- **Database:** SQLite (Relational).
- **Styling:** Bootstrap 5.
- **Tools:** Redis, Celery, Chart.js.

---

## Installation & Run Instructions

Since the `node_modules` and `venv` folders are excluded for submission size, please follow these steps to set up the environment.

### Step 1: Backend Setup (Terminal 1)
1. Navigate to the backend folder:
   ```bash
   cd backend
````

2.  Create and activate virtual environment:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```
3.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Initialize the Database (Factory Reset):
    ```bash
    python setup_db.py
    ```
5.  Start the API Server:
    ```bash
    python app.py
    ```
    *Server runs at https://www.google.com/search?q=http://127.0.0.1:5000*

### Step 2: Frontend Setup (Terminal 2)

1.  Open a new terminal and navigate to the frontend folder:
    ```bash
    cd frontend
    ```
2.  Install JavaScript dependencies:
    ```bash
    npm install
    ```
3.  Start the Vue Development Server:
    ```bash
    npm run serve
    ```
    *App runs at http://localhost:8080*

-----

## Login Credentials (Default Users)

Use these credentials to test the different roles:

### 1\. Admin (Pre-created)

  - **Username:** `admin`
  - **Password:** `admin123`
  - **Features:** Dashboard Charts, Manage Doctors (CRUD), Search.

### 2\. Doctor (Create via Admin first)

  - **Suggested Username:** `House`
  - **Suggested Password:** `admin123`
  - **Features:** View Appointments, Medical History Modal, Complete Diagnosis.

### 3\. Patient (Register via App)

  - **Suggested Username:** `John`
  - **Suggested Password:** `admin123`
  - **Features:** Book Appt, Cancel Appt, Search Doctors, Export History (CSV).

-----

## API Documentation

The API specification is provided in the `openapi.yaml` file located in the root directory.
