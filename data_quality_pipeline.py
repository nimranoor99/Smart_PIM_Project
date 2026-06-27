# Import libraries
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging

# Set up logging (like a diary of what the program does)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ CLASS: A blueprint for our Data Quality Tool ============
class DataQualityValidator:
    """
    This class checks and fixes data quality issues
    Think of it as a quality control inspector for your data
    """
    
    def __init__(self):
        # Stores the quality report as a dictionary
        self.quality_report = {}
    
    def validate_and_cleanse(self, df, dataset_name):
        """
        Main function - checks all data quality rules and fixes issues
        
        Parameters:
        - df: the data (pandas DataFrame)
        - dataset_name: name of the dataset (for reporting)
        
        Returns:
        - cleaned data
        - quality report
        """
        
        logger.info(f"🔍 Starting validation for {dataset_name}")
        
        # Create a report dictionary to store results
        results = {
            'dataset': dataset_name,
            'total_records': len(df),  # How many rows originally
            'validation_checks': {},   # Problems found
            'cleansing_actions': [],   # What we fixed
            'summary': {}              # Summary stats
        }
        
        # -------- CHECK 1: Missing Values --------
        # .isnull() finds missing values, .sum() counts them
        missing = df.isnull().sum()
        # Store what we found
        results['validation_checks']['missing_values'] = missing[missing > 0].to_dict()
        
        # Fix missing values:
        # For price: replace missing with median (middle value)
        if 'price' in df.columns:
            df['price'].fillna(df['price'].median(), inplace=True)
            results['cleansing_actions'].append('✅ Filled missing price with median')
        
        # For weight: replace missing with mean (average)
        if 'weight_kg' in df.columns:
            df['weight_kg'].fillna(df['weight_kg'].mean(), inplace=True)
            results['cleansing_actions'].append('✅ Filled missing weight with mean')
        
        # For rating: replace missing with default 3.0
        if 'rating' in df.columns:
            df['rating'].fillna(3.0, inplace=True)
            results['cleansing_actions'].append('✅ Filled missing rating with default 3.0')
        
        # -------- CHECK 2: Duplicates --------
        # Check if any products are duplicated
        duplicates = df.duplicated(subset=['product_id'] if 'product_id' in df.columns 
                                   else df.columns.tolist())
        results['validation_checks']['duplicates'] = int(duplicates.sum())
        
        # Remove duplicates if found
        if duplicates.sum() > 0:
            df = df[~duplicates].reset_index(drop=True)
            results['cleansing_actions'].append(f'✅ Removed {duplicates.sum()} duplicate records')
        
        # -------- CHECK 3: Invalid Values --------
        # Check for negative prices (shouldn't happen in real data)
        if 'price' in df.columns:
            invalid_price = df[df['price'] < 0]
            results['validation_checks']['invalid_prices'] = len(invalid_price)
            # Fix: convert negative to positive, or cap at 10000
            df.loc[df['price'] < 0, 'price'] = df['price'].abs()
            df.loc[df['price'] > 10000, 'price'] = 10000
            results['cleansing_actions'].append('✅ Corrected invalid price values')
        
        # Check for negative stock
        if 'stock_quantity' in df.columns:
            invalid_stock = df[df['stock_quantity'] < 0]
            results['validation_checks']['negative_stock'] = len(invalid_stock)
            # Fix: set negative stock to 0
            df.loc[df['stock_quantity'] < 0, 'stock_quantity'] = 0
            results['cleansing_actions'].append('✅ Set negative stock to 0')
        
        # -------- CHECK 4: Format Validation --------
        # Make sure status values are in the right format
        if 'status' in df.columns:
            valid_statuses = ['Active', 'Inactive', 'Draft', 'Under Review']
            # Convert to title case (Active, not active)
            df['status'] = df['status'].str.title()
            # Check if any status is invalid
            invalid_status = df[~df['status'].isin(valid_statuses)]
            results['validation_checks']['invalid_status'] = len(invalid_status)
            # Fix: set invalid statuses to 'Draft'
            df.loc[~df['status'].isin(valid_statuses), 'status'] = 'Draft'
            results['cleansing_actions'].append('✅ Standardized status values')
        
        # -------- CHECK 5: Outliers (using IQR method) --------
        # IQR = Interquartile Range - finds statistical outliers
        if 'price' in df.columns:
            Q1 = df['price'].quantile(0.25)   # 25th percentile
            Q3 = df['price'].quantile(0.75)   # 75th percentile
            IQR = Q3 - Q1                     # Range of middle 50%
            
            # Outliers are values below Q1-1.5*IQR or above Q3+1.5*IQR
            outliers = df[(df['price'] < Q1 - 1.5*IQR) | (df['price'] > Q3 + 1.5*IQR)]
            results['validation_checks']['price_outliers'] = len(outliers)
            
            # Flag outliers but don't remove (will use for anomaly detection)
            df['price_outlier'] = df.index.isin(outliers.index)
        
        # -------- Summary --------
        results['summary'] = {
            'records_after_cleansing': len(df),
            'records_removed': results['total_records'] - len(df),
            'cleansing_actions_applied': len(results['cleansing_actions'])
        }
        
        # Store the report
        self.quality_report[dataset_name] = results
        
        return df, results
    
    def save_report(self, filename='quality_report.json'):
        """Save the quality report as a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.quality_report, f, indent=2, default=str)
        logger.info(f"📊 Quality report saved to {filename}")

# ============== RUN THE PROGRAM ==============

# Create an instance of the validator
validator = DataQualityValidator()

print("\n📊 Cleaning Product Catalog...")
catalog = pd.read_csv('product_catalog_raw.csv')
catalog_clean, catalog_report = validator.validate_and_cleanse(catalog, 'product_catalog')

print("\n📊 Cleaning Sales Data...")
sales = pd.read_csv('sales_data_raw.csv')
sales_clean, sales_report = validator.validate_and_cleanse(sales, 'sales_data')

# Save the cleaned data
catalog_clean.to_csv('product_catalog_clean.csv', index=False)
sales_clean.to_csv('sales_data_clean.csv', index=False)

# Save the quality report
validator.save_report()

print("\n✅ Data quality pipeline complete!")
print(f"Catalog: {len(catalog_clean)} clean records")
print(f"Sales: {len(sales_clean)} clean records")