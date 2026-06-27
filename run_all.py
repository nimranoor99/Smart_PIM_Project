# run_all.py - This runs everything at once!
import subprocess
import sys

scripts = [
    'generate_product_data.py',
    'data_quality_pipeline.py',
    'anomaly_detection.py',
    'reporting_dashboard.py'
]

print("🚀 Running full pipeline...")
print("="*50)

for script in scripts:
    print(f"\n📌 Running {script}...")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"❌ Error in {script}")
        break
    print(f"✅ {script} completed")

print("\n" + "="*50)
print("🎉 All done! Open dashboard_complete.html")