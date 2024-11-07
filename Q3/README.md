# FastAPI PostgreSQL CRUD API

This is a simple **FastAPI** application with **PostgreSQL** integration. It provides a basic API for managing `users` and `orders` with **CRUD** operations (Create, Read, Update, Delete).

## Features

- **User Management**: Allows creating, updating and deleting users.
- **Order Management**: Allows creating and retrieving orders associated with users.
- **Asynchronous Database Queries**: Utilizes async queries for faster response times.
- **PostgreSQL Integration**: Uses PostgreSQL as the database for persistence.


## Requirements

- Python 3.8+
- PostgreSQL 12+

### Install Dependencies

To install the project dependencies, run:

```bash
pip install -r requirements.txt
```

### Setup Database

- Replace username, password, and db_name with your PostgreSQL credentials in the DATABASE_URL string in models.py
    ```bash
    DATABASE_URL = "postgresql://username:password@localhost/db_name"
    ```
- Make sure you have a running PostgreSQL instance, and then create the necessary tables by running:
    ```bash
    uvicorn app.main:app --reload
    ```
This will automatically create the database tables if they don't exist yet.

## Running the Application

### Start FastAPI Application

To start the FastAPI development server, run:
```bash
    uvicorn app.main:app --reload
```

### View API Documentation
FastAPI automatically generates interactive documentation for your API. You can access it by navigating to:
```bash
    http://127.0.0.1:8000/docs#/
```
![fastapi](https://github.com/user-attachments/assets/0ce90c0f-7fa6-4492-a9df-cdcb232a7533)

## Testing the Application
To test the create_user endpoints programmatically, you can use the provided test_create_user.py script.

The script will:
- Create a user using the POST /users/ endpoint.
```bash
    python test_create_and_delete_user.py
```
