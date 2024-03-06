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

DONATION_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS donation_history (
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

FIND_DATASET_ITEM_BY_PRODUCT_CODE = """
SELECT product_code, product_name, category, price, weight FROM dataset WHERE product_code = :product_code
"""

DONATION_HISTORY_INSERT_FOOD_ITEM = """
INSERT INTO donation_history (date_received, product_code, product_name, category, price, weight, quantity, total_price, total_weight)
VALUES (:date_received, :product_code, :product_name, :category, :price, :weight, :quantity, :total_price, :total_weight)
ON CONFLICT (product_code)
DO UPDATE SET
quantity = donation_history.quantity + EXCLUDED.quantity,
total_price = donation_history.price * (donation_history.quantity + EXCLUDED.quantity),
total_weight = donation_history.weight * (donation_history.quantity + EXCLUDED.quantity);
"""

CHECK_EXISTENCE_DONATION_HISTORY = """
SELECT COUNT(*)
FROM donation_log
WHERE product_code = :product_code AND date_received = :date_received;
"""

