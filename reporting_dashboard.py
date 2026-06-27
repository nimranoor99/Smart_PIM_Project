import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime

class DashboardGenerator:
    """Creates interactive dashboards and reports"""
    
    def __init__(self):
        # Load all the data
        try:
            self.catalog = pd.read_csv('product_catalog_with_anomalies.csv')
            self.sales = pd.read_csv('sales_data_clean.csv')
            self.anomalies = pd.read_csv('anomaly_detection_report.csv')
            self.quality_report = json.load(open('quality_report.json'))
            print("✅ Data loaded successfully!")
        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            print("Make sure you've run all previous scripts first!")
            exit()
    
    def create_simple_dashboard(self):
        """
        Creates individual charts and saves them separately
        This is more reliable than subplots
        """
        print("📊 Creating dashboard charts...")
        
        # --- Chart 1: Product Distribution by Category (Pie Chart) ---
        category_counts = self.catalog['category'].value_counts()
        fig1 = go.Figure(data=[go.Pie(
            labels=category_counts.index,
            values=category_counts.values,
            hole=0.3,
            marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        )])
        fig1.update_layout(
            title="📊 Product Distribution by Category",
            height=500,
            width=600
        )
        fig1.write_html('chart1_category_distribution.html')
        print("   ✅ Chart 1: Category Distribution")
        
        # --- Chart 2: Price Distribution by Category (Box Plot) ---
        fig2 = go.Figure(data=[go.Box(
            x=self.catalog['category'],
            y=self.catalog['price'],
            boxmean='sd',
            marker_color='#45B7D1'
        )])
        fig2.update_layout(
            title="💰 Price Distribution by Category",
            xaxis_title="Category",
            yaxis_title="Price ($)",
            height=500,
            width=600
        )
        fig2.write_html('chart2_price_distribution.html')
        print("   ✅ Chart 2: Price Distribution")
        
        # --- Chart 3: Anomalies by Type (Bar Chart) ---
        if not self.anomalies.empty:
            anomaly_types = self.anomalies['type'].value_counts()
            fig3 = go.Figure(data=[go.Bar(
                x=anomaly_types.index,
                y=anomaly_types.values,
                marker_color=['#FF6B6B', '#4ECDC4']
            )])
            fig3.update_layout(
                title="🚨 Anomalies by Type",
                xaxis_title="Anomaly Type",
                yaxis_title="Count",
                height=500,
                width=600
            )
            fig3.write_html('chart3_anomalies.html')
            print("   ✅ Chart 3: Anomalies by Type")
        else:
            print("   ⚠️ No anomalies found to chart")
        
        # --- Chart 4: Sales Trend (Line Chart) ---
        daily_sales = self.sales.groupby('date')['units_sold'].sum().reset_index()
        fig4 = go.Figure(data=[go.Scatter(
            x=daily_sales['date'],
            y=daily_sales['units_sold'],
            mode='lines+markers',
            line=dict(color='#2ECC71', width=3),
            marker=dict(size=6, color='#27AE60')
        )])
        fig4.update_layout(
            title="📈 Daily Sales Trend",
            xaxis_title="Date",
            yaxis_title="Units Sold",
            height=500,
            width=600
        )
        fig4.write_html('chart4_sales_trend.html')
        print("   ✅ Chart 4: Sales Trend")
        
        # --- Chart 5: Top Products by Sales (Horizontal Bar Chart) ---
        top_products = self.sales.groupby('product_id')['units_sold'].sum().nlargest(10)
        fig5 = go.Figure(data=[go.Bar(
            x=top_products.values,
            y=top_products.index,
            orientation='h',
            marker_color='#E74C3C'
        )])
        fig5.update_layout(
            title="🏆 Top 10 Products by Sales",
            xaxis_title="Units Sold",
            yaxis_title="Product ID",
            height=500,
            width=600
        )
        fig5.write_html('chart5_top_products.html')
        print("   ✅ Chart 5: Top Products")
        
        # --- Chart 6: Data Quality Summary (Table) ---
        quality_data = []
        for dataset, report in self.quality_report.items():
            quality_data.append([
                dataset,
                report['total_records'],
                report['summary']['records_after_cleansing'],
                len(report['cleansing_actions']),
                report['summary']['records_removed']
            ])
        
        fig6 = go.Figure(data=[go.Table(
            header=dict(
                values=['Dataset', 'Original', 'Cleaned', 'Actions', 'Removed'],
                fill_color='#2C3E50',
                font=dict(color='white', size=14),
                align='center'
            ),
            cells=dict(
                values=[
                    [d[0] for d in quality_data],
                    [d[1] for d in quality_data],
                    [d[2] for d in quality_data],
                    [d[3] for d in quality_data],
                    [d[4] for d in quality_data]
                ],
                fill_color='#ECF0F1',
                align='center',
                font=dict(size=12)
            )
        )])
        fig6.update_layout(
            title="📋 Data Quality Summary",
            height=400,
            width=600
        )
        fig6.write_html('chart6_quality_summary.html')
        print("   ✅ Chart 6: Quality Summary")
        
        # --- Create a simple HTML page that links all charts ---
        self.create_dashboard_page()
        
        print("\n🎉 All charts created successfully!")
        print("📁 Open 'dashboard_complete.html' to see everything together")
        
        return True
    
    def create_dashboard_page(self):
        """Creates a single HTML page with all charts embedded"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SmartPIM Analytics Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f6fa;
                    margin: 0;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 32px;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                .chart {{
                    background: white;
                    border-radius: 10px;
                    padding: 15px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .chart iframe {{
                    width: 100%;
                    height: 550px;
                    border: none;
                    border-radius: 5px;
                }}
                .full-width {{
                    grid-column: 1 / -1;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    color: #7f8c8d;
                    font-size: 14px;
                    border-top: 1px solid #ecf0f1;
                }}
                @media (max-width: 768px) {{
                    .grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 SmartPIM Analytics Dashboard</h1>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                <p style="font-size: 14px; opacity: 0.8;">Data Quality • Anomaly Detection • Sales Analytics</p>
            </div>
            
            <div class="grid">
                <div class="chart">
                    <iframe src="chart1_category_distribution.html"></iframe>
                </div>
                <div class="chart">
                    <iframe src="chart2_price_distribution.html"></iframe>
                </div>
                <div class="chart">
                    <iframe src="chart3_anomalies.html"></iframe>
                </div>
                <div class="chart">
                    <iframe src="chart4_sales_trend.html"></iframe>
                </div>
                <div class="chart full-width">
                    <iframe src="chart5_top_products.html" style="height: 450px;"></iframe>
                </div>
                <div class="chart full-width">
                    <iframe src="chart6_quality_summary.html" style="height: 350px;"></iframe>
                </div>
            </div>
            
            <div class="footer">
                <p>📊 Built with Python, Pandas, and Plotly | Data Quality Pipeline + Anomaly Detection</p>
                <p style="margin-top: 5px; font-size: 12px; color: #bdc3c7;">
                    Total Products: {len(self.catalog)} | Total Sales Records: {len(self.sales)} | Total Anomalies: {len(self.anomalies)}
                </p>
            </div>
        </body>
        </html>
        """
        
        with open('dashboard_complete.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("   ✅ Dashboard page created: dashboard_complete.html")
    
    def create_excel_report(self):
        """Generates an Excel file with multiple sheets"""
        print("\n📊 Creating Excel report...")
        
        try:
            with pd.ExcelWriter('SmartPIM_Report.xlsx', engine='openpyxl') as writer:
                # Sheet 1: Overview
                overview = pd.DataFrame({
                    'Metric': [
                        'Total Products', 
                        'Total Sales Records', 
                        'Total Anomalies', 
                        'Products with Anomalies', 
                        'Average Price', 
                        'Total Revenue'
                    ],
                    'Value': [
                        len(self.catalog),
                        len(self.sales),
                        len(self.anomalies),
                        len(self.catalog[self.catalog['product_anomaly'] == True]),
                        round(self.catalog['price'].mean(), 2),
                        round(self.sales['revenue'].sum(), 2) if 'revenue' in self.sales.columns else 0
                    ]
                })
                overview.to_excel(writer, sheet_name='Overview', index=False)
                
                # Sheet 2: Product Catalog with anomalies
                self.catalog.to_excel(writer, sheet_name='Product Catalog', index=False)
                
                # Sheet 3: Anomalies
                if not self.anomalies.empty:
                    self.anomalies.to_excel(writer, sheet_name='Anomalies', index=False)
                else:
                    pd.DataFrame({'Message': ['No anomalies found']}).to_excel(writer, sheet_name='Anomalies', index=False)
                
                # Sheet 4: Category Analysis
                category_analysis = self.catalog.groupby('category').agg({
                    'price': ['mean', 'min', 'max'],
                    'stock_quantity': 'sum',
                    'rating': 'mean'
                }).round(2)
                category_analysis.to_excel(writer, sheet_name='Category Analysis')
                
            print("✅ Excel report generated: SmartPIM_Report.xlsx")
            
        except Exception as e:
            print(f"❌ Error creating Excel report: {e}")

# ============== RUN THE PROGRAM ==============

print("\n" + "="*50)
print("📊 Generating Dashboard and Reports")
print("="*50)

# Create generator
dashboard_gen = DashboardGenerator()

# Create dashboard
dashboard_gen.create_simple_dashboard()

# Create Excel report
dashboard_gen.create_excel_report()

print("\n" + "="*50)
print("🎉 All reports generated successfully!")
print("="*50)
print("📁 Files created:")
print("   ✅ dashboard_complete.html (MAIN - open this!)")
print("   ✅ SmartPIM_Report.xlsx (open in Excel)")
print("   📊 Individual chart files also created")
print("="*50)
print("\n👉 Open 'dashboard_complete.html' in your browser!")