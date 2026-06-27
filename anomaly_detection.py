import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    """
    This class finds unusual patterns in data using Machine Learning
    
    Two methods:
    1. Isolation Forest: finds unusual products
    2. Z-score: finds unusual sales patterns
    """
    
    def __init__(self):
        self.models = {}  # Stores trained models
        self.anomaly_log = []  # List of all anomalies found
    
    def detect_products_anomalies(self, df):
        """
        Uses Isolation Forest algorithm to find unusual products
        
        How Isolation Forest works:
        - It's like playing "20 questions" to isolate data points
        - Normal products are easy to isolate (takes many questions)
        - Anomalous products are easy to isolate (few questions)
        - Points that are isolated quickly are likely anomalies
        """
        
        # Choose which features to use for anomaly detection
        features = ['price', 'stock_quantity', 'weight_kg', 'rating']
        feature_df = df[features].copy()
        
        # Handle any remaining NaN values
        feature_df = feature_df.fillna(feature_df.mean())
        
        # Scale features (so price doesn't dominate just because it's larger)
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_df)
        
        # Create and train Isolation Forest model
        # contamination=0.05 means we expect 5% of data to be anomalous
        iso_forest = IsolationForest(contamination=0.05, random_state=42)
        predictions = iso_forest.fit_predict(scaled_features)
        
        # Add anomaly flags to the data
        # -1 = anomaly, 1 = normal
        df['product_anomaly'] = predictions == -1
        df['anomaly_score'] = iso_forest.score_samples(scaled_features)
        
        # Log all anomalies found
        anomalies = df[df['product_anomaly']]
        for _, row in anomalies.iterrows():
            self.anomaly_log.append({
                'type': 'product_anomaly',
                'product_id': row['product_id'],
                'reason': f"Unusual combination: price=${row['price']:.2f}, stock={row['stock_quantity']}",
                'score': row['anomaly_score']
            })
        
        return df
    
    def detect_sales_anomalies(self, df):
        """
        Uses Z-score method to find unusual sales patterns
        
        Z-score = how many standard deviations a point is from the mean
        |Z-score| > 2 means the point is unusual
        """
        
        # 🔧 FIXED: Create pivot table without fillna parameter
        # First, ensure we have date as datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Create pivot table - sum units_sold for each product on each date
        sales_pivot = df.pivot_table(
            index='date', 
            columns='product_id', 
            values='units_sold',
            aggfunc='sum'
        )
        
        # 🔧 FIXED: Fill NaN values after creating the pivot table
        sales_pivot = sales_pivot.fillna(0)
        
        # Check top 20 products (to keep it manageable)
        for product in sales_pivot.columns[:20]:
            series = sales_pivot[product]
            
            # Calculate rolling statistics (7-day window)
            rolling_mean = series.rolling(window=7, center=True).mean()
            rolling_std = series.rolling(window=7, center=True).std()
            
            # Calculate Z-scores
            z_scores = (series - rolling_mean) / rolling_std
            
            # Find anomalies: |Z-score| > 2
            anomalies = z_scores.abs() > 2
            
            # Log anomalies
            for date, is_anomaly in anomalies.items():
                if is_anomaly and not pd.isna(is_anomaly):
                    self.anomaly_log.append({
                        'type': 'sales_anomaly',
                        'date': date,
                        'product_id': product,
                        'reason': f"Unusual sales: {int(series[date])} units (z-score: {z_scores[date]:.2f})",
                        'units': int(series[date])
                    })
        
        return None  # We already have the anomalies logged
    
    def generate_anomaly_report(self):
        """Create a summary report of all anomalies"""
        
        if not self.anomaly_log:
            return pd.DataFrame(), {'total_anomalies': 0, 'product_anomalies': 0, 'sales_anomalies': 0}
        
        # Convert log to DataFrame
        report = pd.DataFrame(self.anomaly_log)
        report['timestamp'] = pd.Timestamp.now()
        
        # Create summary statistics
        summary = {
            'total_anomalies': len(report),
            'product_anomalies': len(report[report['type'] == 'product_anomaly']),
            'sales_anomalies': len(report[report['type'] == 'sales_anomaly']),
            'top_reasons': report['reason'].value_counts().head(5).to_dict()
        }
        
        return report, summary

# ============== RUN THE PROGRAM ==============

# Load cleaned data
print("\n🔍 Loading data...")
try:
    catalog = pd.read_csv('product_catalog_clean.csv')
    sales = pd.read_csv('sales_data_clean.csv')
    print("✅ Data loaded successfully!")
except FileNotFoundError:
    print("❌ Error: Clean data files not found!")
    print("📌 Please run data_quality_pipeline.py first")
    exit()

# Initialize detector
detector = AnomalyDetector()

print("\n🔍 Detecting product anomalies...")
catalog_with_anomalies = detector.detect_products_anomalies(catalog)
catalog_with_anomalies.to_csv('product_catalog_with_anomalies.csv', index=False)
print(f"✅ Found {len(catalog_with_anomalies[catalog_with_anomalies['product_anomaly']])} product anomalies")

print("\n🔍 Detecting sales anomalies...")
detector.detect_sales_anomalies(sales)

# Generate report
anomaly_report, anomaly_summary = detector.generate_anomaly_report()
anomaly_report.to_csv('anomaly_detection_report.csv', index=False)

print("\n" + "="*50)
print("✅ Anomaly detection complete!")
print("="*50)
print(f"🔴 Total anomalies found: {anomaly_summary['total_anomalies']}")
print(f"   - Product anomalies: {anomaly_summary['product_anomalies']}")
print(f"   - Sales anomalies: {anomaly_summary['sales_anomalies']}")
print("="*50)
print("📁 Files created:")
print("   - product_catalog_with_anomalies.csv")
print("   - anomaly_detection_report.csv")
print("="*50)