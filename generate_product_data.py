# LINE 1-2: Import libraries (pre-built code that others wrote)
# pandas = helps us work with tables of data (like Excel)
# numpy = helps with math and numbers
import pandas as pd
import numpy as np

# LINE 4-6: Import more tools for working with dates and random numbers
from datetime import datetime, timedelta
import random
import hashlib

# LINE 8: This sets a "random seed" so we always get the same random numbers
# This is important so your results are consistent
np.random.seed(42)

# LINE 11-39: This is a FUNCTION - a reusable block of code
# Think of it like a recipe that makes a product catalog
def generate_product_catalog(n_products=500):
    """
    This function creates a fake product catalog with 500 products.
    It intentionally adds errors so we can practice fixing them!
    """
    
    # These are lists of possible values for our products
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    brands = ['TechPro', 'StyleCo', 'HomeSweet', 'FitLife', 'ReadWell']
    statuses = ['Active', 'Inactive', 'Draft', 'Under Review']
    
    # LINE 20-31: Create a DICTIONARY of product data
    # Think of this as an Excel spreadsheet with columns
    products = {
        # Product IDs: P000001, P000002, etc.
        'product_id': [f'P{str(i).zfill(6)}' for i in range(1, n_products+1)],
        
        # Product names: Product 1, Product 2, etc.
        'name': [f'Product {i}' for i in range(1, n_products+1)],
        
        # Randomly pick a category for each product
        'category': [random.choice(categories) for _ in range(n_products)],
        
        # Randomly pick a brand
        'brand': [random.choice(brands) for _ in range(n_products)],
        
        # Prices between $10 and $1000, rounded to 2 decimals
        'price': np.random.uniform(10, 1000, n_products).round(2),
        
        # Stock between 0 and 500
        'stock_quantity': np.random.randint(0, 500, n_products),
        
        # Random status
        'status': [random.choice(statuses) for _ in range(n_products)],
        
        # Random dates (up to 90 days ago)
        'last_updated': [datetime.now() - timedelta(days=random.randint(0, 90)) 
                        for _ in range(n_products)],
        
        # Random supplier
        'supplier': [f'Supplier_{random.randint(1,20)}' for _ in range(n_products)],
        
        # Weight between 0.1 and 15kg
        'weight_kg': np.random.uniform(0.1, 15, n_products).round(2),
        
        # Rating between 1 and 5
        'rating': np.random.uniform(1, 5, n_products).round(1)
    }
    
    # LINE 34: Convert the dictionary to a pandas DataFrame (like an Excel table)
    df = pd.DataFrame(products)
    
    # NOW WE INTENTIONALLY ADD ERRORS TO PRACTICE DATA CLEANING
    # This is what makes our project realistic!
    
    # ERROR 1: Missing values (30 products have no price)
    df.loc[random.sample(df.index.tolist(), 30), 'price'] = np.nan
    
    # ERROR 2: Missing weights (25 products have no weight)
    df.loc[random.sample(df.index.tolist(), 25), 'weight_kg'] = np.nan
    
    # ERROR 3: Missing ratings (15 products have no rating)
    df.loc[random.sample(df.index.tolist(), 15), 'rating'] = np.nan
    
    # ERROR 4: Duplicate entries (copy first 20 products)
    duplicates = df.iloc[0:20].copy()
    duplicates['product_id'] = [f'P{str(i).zfill(6)}' for i in range(1001, 1021)]
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # ERROR 5: Invalid negative prices (10 products)
    df.loc[df.sample(10).index, 'price'] = -50
    
    # ERROR 6: Invalid negative stock (10 products)
    df.loc[df.sample(10).index, 'stock_quantity'] = -100
    
    # ERROR 7: Extreme outliers (5 products with crazy prices)
    df.loc[df.sample(5).index, 'price'] = 99999
    
    # ERROR 8: Formatting issues (status in lowercase)
    df.loc[df.sample(10).index, 'status'] = df.loc[df.sample(10).index, 'status'].str.lower()
    
    # LINE 46: Return the finished DataFrame
    return df

# LINE 49-64: Generate sales data (another function)
def generate_sales_data(product_ids, n_days=90):
    """
    Creates fake sales data for 90 days
    """
    # Create list of dates
    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
    sales_data = []
    
    # For each date
    for date in dates:
        # Randomly select products that sold that day (50-200 products)
        for pid in np.random.choice(product_ids, size=random.randint(50, 200), replace=False):
            # Base sales - Poisson distribution (like real sales patterns)
            base_sales = np.random.poisson(lam=15)
            
            # Add weekend boost (more sales on weekends)
            if date.weekday() in [5, 6]:  # 5=Saturday, 6=Sunday
                base_sales *= 1.3
            
            # INTENTIONAL ANOMALIES (unusual sales patterns)
            if random.random() < 0.02:  # 2% chance of anomaly
                if random.random() < 0.5:
                    base_sales *= 5  # Spike - 5x normal sales
                else:
                    base_sales *= 0.1  # Drop - 90% decrease
            
            # Record this sale
            sales_data.append({
                'date': date,
                'product_id': pid,
                'units_sold': int(base_sales),
                'revenue': float(base_sales * np.random.uniform(10, 100))
            })
    
    return pd.DataFrame(sales_data)

# ============== THIS IS WHERE THE PROGRAM ACTUALLY RUNS ==============

# LINE 67-79: Generate and save the data
print("Generating product catalog...")
catalog = generate_product_catalog(500)  # Create 500 products
catalog.to_csv('product_catalog_raw.csv', index=False)  # Save to CSV file
print(f"✅ Created {len(catalog)} products")

print("Generating sales data...")
sales = generate_sales_data(catalog['product_id'].unique(), 90)  # 90 days of sales
sales.to_csv('sales_data_raw.csv', index=False)  # Save to CSV file

print(f"✅ Created {len(sales)} sales records")
print("🎉 Data generation complete!")