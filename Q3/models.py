import databases
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

Base = declarative_base()

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/rakortDB"

database = databases.Database(DATABASE_URL)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    address = Column(String, index=True)
    phone = Column(String, index=True)
    orders = relationship("Order", back_populates="owner")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Integer)
    shipping_address = Column(String)
    billing_address = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="orders")


engine = sqlalchemy.create_engine(DATABASE_URL, echo=True, future=True)


async def connect_to_db():
    await database.connect()


async def disconnect_from_db():
    await database.disconnect()

Base.metadata.create_all(bind=engine)
