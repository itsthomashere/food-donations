from dataclasses import dataclass
from typing import Optional

@dataclass
class MissingBarcode:
    product_code: str

@dataclass
class DatasetItem:
    product_code: str
    product_name: str
    category: str
    price: float
    weight: float

@dataclass
class DonatedFoodItem:
    date_received: str
    product_code: str
    product_name: str
    category: str
    price: float
    weight: float
    quantity: int
    total_price: float
    total_weight: float

