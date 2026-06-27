from flask import Flask, jsonify, request
import pandas as pd
import json

# ============ SET UP THE API ============

# Create the Flask app (like creating a website)
app = Flask(__name__)

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    API endpoint: /api/products
    Gets product data with anomalies
    
    Example: http://localhost:5001/api/products?status=active&anomalies=true
    """
    
    # Get parameters from the URL
    status = request.args.get('status', 'all')
    include_anomalies = request.args.get('anomalies', 'false').lower() == 'true'
    
    # Load the data
    df = pd.read_csv('product_catalog_with_anomalies.csv')
    
    # Filter by status if specified
    if status != 'all':
        df = df[df['status'].str.lower() == status.lower()]
    
    # Filter out anomalies if not requested
    if not include_anomalies:
        df = df[df['product_anomaly'] != True]
    
    # Return as JSON (web format)
    return jsonify({
        'status': 'success',
        'count': len(df),
        'products': df.to_dict('records')
    })

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    """
    API endpoint: /api/anomalies
    Gets all detected anomalies
    """
    
    df = pd.read_csv('anomaly_detection_report.csv')
    return jsonify({
        'status': 'success',
        'count': len(df),
        'anomalies': df.to_dict('records')
    })

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    API endpoint: /api/dashboard/stats
    Gets summary statistics for the dashboard
    """
    
    catalog = pd.read_csv('product_catalog_with_anomalies.csv')
    sales = pd.read_csv('sales_data_clean.csv')
    anomalies = pd.read_csv('anomaly_detection_report.csv')
    
    stats = {
        'total_products': len(catalog),
        'total_sales_records': len(sales),
        'total_anomalies': len(anomalies),
        'avg_price': float(catalog['price'].mean()),
        'total_revenue': float(sales['revenue'].sum() if 'revenue' in sales.columns else 0),
        'top_categories': catalog['category'].value_counts().head(5).to_dict()
    }
    
    return jsonify(stats)

# ============== RUN THE API ==============

if __name__ == '__main__':
    print("\n🚀 Starting API Server...")
    print("🌐 API will be available at: http://localhost:5001")
    print("📊 Try these URLs in your browser:")
    print("   - http://localhost:5001/api/dashboard/stats")
    print("   - http://localhost:5001/api/products")
    print("   - http://localhost:5001/api/anomalies")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(port=5001, debug=True)