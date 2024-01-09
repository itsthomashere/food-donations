import re


def standardise_weight(weight_tuple: tuple) -> float:
    value, unit = weight_tuple
    if unit == 'g':
        return round(float(value) / 1000, 2)  # Convert grams to kilograms and round off to two decimal places
    elif unit == 'kg':
        return round(float(value), 2)  # No conversion needed, round off to two decimal places
    elif unit == 'ml':
        return round(float(value) / 1000, 2)  # Convert milliliters to liters and round off to two decimal places
    elif unit == 'L':
        return round(float(value), 2)  # No conversion needed, round off to two decimal places
    else:
        return 0.0


def extract_weight(prod_name: str) -> float:
    def is_fractional_weight() -> bool:
        pattern = r'\b\d+(?:\.\d+)?\b'
        match = re.search(pattern, prod_name)
        return bool(match)

    def is_combination_weight() -> bool:
        pattern = r'\b(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*([kKmMlLgG])\b'
        match = re.search(pattern, prod_name)
        return bool(match)

    def extract_fractional_weight() -> float:
        pattern = r'\b\d+(?:\.\d+)?\b'
        match = re.search(pattern, prod_name)
        if match:
            return float(match.group(0))

    def extract_combination_weight() -> float:
        pattern = r'\b(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*([kKmMlLgG])\b'
        match = re.search(pattern, prod_name)
        if match:
            quantity = int(match.group(1))
            weight_per_unit = float(match.group(2))
            unit = match.group(3).lower()
            return int(quantity * weight_per_unit)

    def extract_singular_weight() -> float | int:
        pattern = r'(\b[1-9]\d*|\d)\s?(k?g|m?l)\b'
        match = re.search(pattern, prod_name, re.IGNORECASE)
        if match:
            weight_value = int(match.group(1))
            unit = match.group(2).lower()
            return weight_value

    if is_combination_weight():
        weight = extract_combination_weight()
        return weight
    elif is_fractional_weight():
        weight = extract_fractional_weight()
        return weight
    else:
        weight = extract_singular_weight()
        return weight


def extract_weight_type(prod_name: str) -> str | None:
    pattern = r"\b(ml|g|kg|L)\b"
    match = re.search(pattern, prod_name)
    if match:
        return match.group(1)
    return None


def weight_extract(product_name):
    match = re.search(r"[0-9]+ (g|kg)", product_name)
    if match is not None:
        extract_weight = match.group()
        return extract_weight
    else:
        return None

def weight_converter(extracted_weight):
    if " g" in extracted_weight:
        weight = extracted_weight.replace(" g", "")
        weight = float(weight) / 1000
    else:
        weight = float(extracted_weight.replace(" kg", ""))
    return weight

def weight_extract_convert(weight_string):
    if weight_string is None:
        return None

    # combination regular expression
    combination_weight_re = "[0-9]+ x [0-9]+ (g|kg|ml|L)"
    # singular regular expression
    singular_weight_re = "[0-9]+ (g|kg|ml|L)"

    # check for combination string
    if re.search(combination_weight_re, weight_string):
        # split the string into list - [num units , weight_per_unit]
        combination_split = re.search(combination_weight_re, weight_string).group().split(' x ')
        # num_units
        num_units = int(combination_split[0])
        # unit_string - [g,kg,ml, l]
        weight_unit_string = combination_split[1]
        # check if weight unit is grams
        if (" g" in weight_unit_string):
            # remove the gram unit, convert string to float
            weight = float(weight_unit_string.replace(" g", ""))
            # divide weight by 1000 to convert to kg
            weight = weight / 1000 * num_units
        # check if weight unit is ml
        elif (" ml" in weight_unit_string):
            # remove the ml unit, convert string to float
            weight = float(weight_unit_string.replace(" ml", ""))
            # divide wight by 1000 to L - 1l -kg
            weight = weight / 1000 * num_units
        # check if kg unit in string
        elif " kg" in weight_unit_string:
            # remove the kg unit in string, convert string to float
            weight = float(weight_unit_string.replace(" kg", "")) * num_units
        else:
            # remove L unit in string, convert string to float
            weight = float(weight_unit_string.replace(" L", "")) * num_units

    elif re.search(singular_weight_re, weight_string):
        # singular algorithm
        weight_string_singular = re.search(singular_weight_re, weight_string).group()
        if " g" in weight_string_singular:
            weight = float(weight_string_singular.replace(" g", "")) / 1000
        elif " ml" in weight_string_singular:
            weight = float(weight_string_singular.replace(" ml", "")) / 1000
        elif " kg" in weight_string_singular:
            weight = float(weight_string_singular.replace(" kg", ""))
        else:
            weight = float(weight_string_singular.replace(" L", ""))
    else:
        weight = 0.0
    try:
        return round(weight, 2)
    except:
        return 0.0
