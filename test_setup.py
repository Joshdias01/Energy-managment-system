# test_setup.py
import pandas as pd
import os

print("Testing setup...")

# Check if data files exist
if os.path.exists('data/consumption_logs.csv'):
    print("✓ Consumption data found")
else:
    print("✗ Consumption data not found")

if os.path.exists('data/outage_reports.csv'):
    print("✓ Outage data found")
else:
    print("✗ Outage data not found")

# Test pandas
try:
    df = pd.read_csv('data/consumption_logs.csv')
    print(f"✓ Pandas working - loaded {len(df)} rows")
except Exception as e:
    print(f"✗ Pandas error: {e}")

# Test Ollama
try:
    from langchain_ollama import OllamaLLM
    llm = OllamaLLM(model="llama2")
    print("✓ Ollama LLM initialized")
except Exception as e:
    print(f"✗ Ollama error: {e}")

print("\nSetup test complete!")