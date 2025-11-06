# generate_data.py - Run this script to create large datasets
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate dates for a full year
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=x) for x in range(365)]

# Regions
regions = ['North', 'South', 'East', 'West']

# Generate consumption data
consumption_data = []

for date in dates:
    for region in regions:
        # Different base demands for different regions
        base_demand = {
            'North': 1200,
            'South': 900,
            'East': 1000,
            'West': 700
        }
        
        # Add seasonal variation
        month = date.month
        if month in [6, 7, 8]:  # Summer - higher demand
            seasonal_factor = 1.3
        elif month in [12, 1, 2]:  # Winter - higher demand
            seasonal_factor = 1.2
        else:
            seasonal_factor = 1.0
        
        # Add day of week variation
        if date.weekday() < 5:  # Weekday
            weekday_factor = 1.1
        else:  # Weekend
            weekday_factor = 0.85
        
        # Random variation
        random_factor = np.random.uniform(0.9, 1.1)
        
        # Calculate demand
        demand = int(base_demand[region] * seasonal_factor * weekday_factor * random_factor)
        
        # Supply is usually 5-10% higher than demand
        supply = int(demand * np.random.uniform(1.05, 1.10))
        
        # Random hour (peak hours are more common)
        hour = np.random.choice([10, 11, 12, 13, 14, 15, 16, 17, 18], p=[0.08, 0.1, 0.12, 0.15, 0.18, 0.15, 0.12, 0.08, 0.02])
        
        consumption_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'region': region,
            'demand_mw': demand,
            'supply_mw': supply,
            'hour': hour,
            'day_of_week': date.strftime('%A'),
            'month': date.strftime('%B'),
            'temperature': np.random.randint(15, 35) if month in [5, 6, 7, 8, 9] else np.random.randint(-5, 20)
        })

# Create DataFrame
df_consumption = pd.DataFrame(consumption_data)
df_consumption.to_csv('data/consumption_logs.csv', index=False)
print(f"Generated {len(df_consumption)} consumption records")

# Generate outage data
outage_causes = [
    'Equipment Failure',
    'Weather',
    'Maintenance',
    'Grid Overload',
    'Transformer Issue',
    'Cable Fault',
    'Substation Problem',
    'Natural Disaster',
    'Human Error',
    'Cyber Attack'
]

outage_descriptions = {
    'Equipment Failure': [
        'Transformer malfunction at substation',
        'Circuit breaker failure',
        'Generator breakdown',
        'Relay system error'
    ],
    'Weather': [
        'Storm damage to transmission lines',
        'Lightning strike on equipment',
        'Heavy rainfall caused flooding',
        'High winds damaged power poles'
    ],
    'Maintenance': [
        'Scheduled maintenance at power plant',
        'Preventive maintenance on transformers',
        'Grid modernization work',
        'Equipment upgrade and testing'
    ],
    'Grid Overload': [
        'Peak demand exceeded capacity',
        'System overload during heatwave',
        'Circuit overload in residential area'
    ],
    'Transformer Issue': [
        'Transformer oil leak',
        'Overheating transformer',
        'Transformer insulation breakdown'
    ],
    'Cable Fault': [
        'Underground cable damage',
        'Cable insulation failure',
        'Overhead line fault'
    ],
    'Substation Problem': [
        'Substation equipment malfunction',
        'Control system failure',
        'Switchgear problem'
    ],
    'Natural Disaster': [
        'Earthquake damaged infrastructure',
        'Flood in power station',
        'Wildfire near transmission lines'
    ],
    'Human Error': [
        'Incorrect switching operation',
        'Accidental equipment damage',
        'Configuration error'
    ],
    'Cyber Attack': [
        'DDoS attack on control system',
        'Malware in SCADA system',
        'Unauthorized access attempt'
    ]
}

outage_data = []

# Generate 200-300 random outages throughout the year
num_outages = np.random.randint(200, 300)

for _ in range(num_outages):
    date = np.random.choice(dates)
    region = np.random.choice(regions)
    cause = np.random.choice(outage_causes)
    description = np.random.choice(outage_descriptions[cause])
    
    # Duration varies by cause
    if cause == 'Maintenance':
        duration = np.random.randint(2, 8)
    elif cause in ['Weather', 'Natural Disaster']:
        duration = np.random.randint(4, 24)
    elif cause == 'Grid Overload':
        duration = np.random.randint(1, 4)
    else:
        duration = np.random.randint(1, 12)
    
    outage_data.append({
        'date': date.strftime('%Y-%m-%d'),
        'region': region,
        'duration_hours': duration,
        'cause': cause,
        'description': description,
        'affected_customers': np.random.randint(500, 50000),
        'severity': np.random.choice(['Low', 'Medium', 'High', 'Critical'], p=[0.3, 0.4, 0.2, 0.1])
    })

# Create DataFrame
df_outages = pd.DataFrame(outage_data)
df_outages = df_outages.sort_values('date').reset_index(drop=True)
df_outages.to_csv('data/outage_reports.csv', index=False)
print(f"Generated {len(df_outages)} outage records")

print("\nData generation complete!")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
print(f"Total consumption records: {len(df_consumption)}")
print(f"Total outage records: {len(df_outages)}")