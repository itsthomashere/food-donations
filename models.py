from dataclasses import dataclass
from typing import Optional

from sqlmodel import SQLModel, Field
from datetime import datetime

# Define the model representing your dataset table
class Dataset(SQLModel, table=True):
    __tablename__ = 'dataset'
    product_code: Optional[int] = Field(default=None, primary_key=True)
    product_name: str
    category: str
    price: float
    weight: float

class DonatedFoodItem(SQLModel, table=True):
    __tablename__ = "donation_history"
    date_received: datetime
    product_code: Optional[int] = Field(default=None, primary_key=True)
    product_name: str
    category: str
    price: float
    weight: float
    quantity: int
    total_price: float
    total_weight: float

class MissingBarcode(SQLModel, table=True):
    __tablename__ = 'barcode_queue'
    date_added: datetime
    product_code: Optional[int] = Field(default=None, primary_key=True)
    status: str

# @dataclass
# class MissingBarcode:
#     product_code: str

# @dataclass
# class DatasetItem:
#     product_code: int
#     product_name: str
#     category: str
#     price: float
#     weight: float

# @dataclass
# class DonatedFoodItem:
#     date_received: str
#     product_code: int
#     product_name: str
#     category: str
#     price: float
#     weight: float
#     quantity: int
#     total_price: float
#     total_weight: float

