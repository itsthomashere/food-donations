DONATION_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS donation_log (
date_received DATE,
product_code VARCHAR(13),
product_name VARCHAR(255),
category VARCHAR(255),
price NUMERIC(10, 2),
weight NUMERIC(10, 2),
quantity INT,
total_price NUMERIC(10, 2),
total_weight NUMERIC(10, 2));
"""

MISSING_BARCODES_TABLE = """
CREATE TABLE IF NOT EXISTS missing_barcodes (
product_code VARCHAR(13) PRIMARY KEY);
"""
