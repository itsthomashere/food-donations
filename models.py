from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st
from typing import Optional
import datetime

Base = declarative_base()

class FoodItem(Base):
    __tablename__ = 'dataset'
    product_code = Column(Integer, primary_key=True, index=True, nullable=True)
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)

class DonatedFoodItem(Base):
    __tablename__ = "donation_history"
    date_received = Column(DateTime, nullable=False)
    product_code = Column(Integer, primary_key=True, index=True, nullable=True)
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    total_weight = Column(Float, nullable=False)

class MissingItem(Base):
    __tablename__ = "missing_items"
    date_added = Column(DateTime, nullable=False)
    product_code = Column(Integer, primary_key=True, index=True, nullable=True)
    status = Column(String, nullable=False)

# Base.metadata.create_all(engine)
