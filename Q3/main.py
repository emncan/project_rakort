from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import databases
from models import database, User, Order, connect_to_db, disconnect_from_db
import sqlalchemy.future

app = FastAPI()


def get_db():
    """
    Dependency function that returns the database connection.

    This function allows FastAPI to inject the database connection into the
    request handlers that require it.

    Returns:
        databases.Database: The asynchronous database connection.
    """
    return database


class UserBase(BaseModel):
    """
    Pydantic model for creating a new user.
    """
    username: str
    email: str
    full_name: str
    address: str
    phone: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class OrderCreate(BaseModel):
    """
    Pydantic model for creating a new order.
    """
    product_name: str
    quantity: int
    price: int
    shipping_address: str
    billing_address: str
    user_id: int


@app.on_event("startup")
async def startup():
    """
    Connects to the database when the application starts.

    This function is triggered by FastAPI's 'startup' event and is used to
    establish the database connection when the application is launched.
    """
    await connect_to_db()


@app.on_event("shutdown")
async def shutdown():
    """
    Disconnects from the database when the application shuts down.

    This function is triggered by FastAPI's 'shutdown' event and ensures that
    the database connection is properly closed when the application shuts down.
    """
    await disconnect_from_db()


@app.post("/users/", response_model=UserCreate)
async def create_user(
        user: UserCreate,
        db: databases.Database = Depends(get_db)):
    """
    Creates a new user in the database.

    This endpoint allows the creation of a new user. It checks if the provided
    username already exists and returns an error if it does. Otherwise, it creates
    the user and returns the created user's details.

    Args:
        user (UserCreate): The user data to create.
        db (databases.Database): The database connection.

    Returns:
        UserCreate: The details of the newly created user.
    """
    query = "SELECT * FROM users WHERE username = :username"
    db_user = await db.fetch_one(query, values={"username": user.username})
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered")

    query = "INSERT INTO users (username, email, full_name, address, phone) VALUES (:username, :email, :full_name, :address, :phone) RETURNING *"
    new_user = await db.fetch_one(query, values={"username": user.username, "email": user.email, "full_name": user.full_name, "address": user.address, "phone": user.phone})
    return new_user


@app.put("/users/{user_id}", response_model=UserUpdate)
async def update_user(
        user_id: int,
        user: UserUpdate,
        db: databases.Database = Depends(get_db)):
    """
    Updates an existing user in the database.

    This endpoint allows updating the details of a user by their user ID.
    It first checks if the user exists, and then updates the user's details.

    Args:
        user_id (int): The ID of the user to be updated.
        user (UserUpdate): The updated user data.
        db (databases.Database): The database connection.

    Returns:
        UserUpdate: The updated details of the user.
    """
    query = "SELECT * FROM users WHERE id = :user_id"
    db_user = await db.fetch_one(query, values={"user_id": user_id})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    query = "UPDATE users SET username = :username, email = :email, full_name = :full_name, address = :address, phone = :phone WHERE id = :user_id RETURNING *"
    updated_user = await db.fetch_one(query, values={"username": user.username, "email": user.email, "full_name": user.full_name, "address": user.address, "phone": user.phone, "user_id": user_id})
    return updated_user


@app.delete("/users/{user_id}", response_model=UserCreate)
async def delete_user(user_id: int, db: databases.Database = Depends(get_db)):
    """
    Deletes a user from the database.

    This endpoint deletes a user based on the provided user ID. It checks
    whether the user exists and removes the user from the database.

    Args:
        user_id (int): The ID of the user to be deleted.
        db (databases.Database): The database connection.

    Returns:
        UserCreate: The details of the deleted user.
    """
    query = "SELECT * FROM users WHERE id = :user_id"
    db_user = await db.fetch_one(query, values={"user_id": user_id})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    query = "DELETE FROM users WHERE id = :user_id RETURNING *"
    deleted_user = await db.fetch_one(query, values={"user_id": user_id})
    return deleted_user


@app.post("/orders/", response_model=OrderCreate)
async def create_order(
        order: OrderCreate,
        db: databases.Database = Depends(get_db)):
    """
    Creates a new order in the database.

    This endpoint allows creating a new order. The order is added to the
    database along with the user's ID who placed the order.

    Args:
        order (OrderCreate): The order data to be created.
        db (databases.Database): The database connection.

    Returns:
        OrderCreate: The details of the newly created order.
    """
    query = "INSERT INTO orders (product_name, quantity, price, shipping_address, billing_address ,user_id) VALUES (:product_name, :quantity, :price, :shipping_address, :billing_address, :user_id) RETURNING *"
    new_order = await db.fetch_one(query, values={"product_name": order.product_name, "quantity": order.quantity, "price": order.price, "shipping_address": order.shipping_address, "billing_address": order.billing_address, "user_id": order.user_id})
    return new_order


@app.get("/users/{user_id}/orders/", response_model=List[OrderCreate])
async def get_orders(user_id: int, db: databases.Database = Depends(get_db)):
    """
    Retrieves all orders for a specific user.

    This endpoint fetches all the orders associated with the user
    identified by the given user ID.

    Args:
        user_id (int): The ID of the user whose orders are to be retrieved.
        db (databases.Database): The database connection.

    Returns:
        List[OrderCreate]: A list of orders placed by the user.
    """
    query = "SELECT * FROM orders WHERE user_id = :user_id"
    user_orders = await db.fetch_all(query, values={"user_id": user_id})
    if not user_orders:
        raise HTTPException(status_code=404, detail="User has no orders")
    return user_orders


@app.delete("/orders/{order_id}", response_model=OrderCreate)
async def delete_order(
        order_id: int,
        db: databases.Database = Depends(get_db)):
    """
    Deletes an order from the database.

    This endpoint deletes an order based on the provided order ID.
    It checks whether the order exists and removes it from the database.

    Args:
        order_id (int): The ID of the order to be deleted.
        db (databases.Database): The database connection.

    Returns:
        OrderCreate: The details of the deleted order.
    """
    query = "SELECT * FROM orders WHERE id = :order_id"
    db_order = await db.fetch_one(query, values={"order_id": order_id})
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    query = "DELETE FROM orders WHERE id = :order_id RETURNING *"
    deleted_order = await db.fetch_one(query, values={"order_id": order_id})
    return deleted_order
