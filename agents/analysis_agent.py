import pandas as pd
from langchain.tools import Tool

class AnalysisAgent:
    def __init__(self, llm):
        self.llm = llm
        self.consumption_data = pd.read_csv('data/consumption_logs.csv')
        self.outage_data = pd.read_csv('data/outage_reports.csv')
    
    def analyze_outages_by_region(self) -> str:
        summary = {}
        for _, row in self.outage_data.iterrows():
            region = row['region']
            if region not in summary:
                summary[region] = {'count': 0, 'hours': 0}
            summary[region]['count'] += 1
            summary[region]['hours'] += row['duration_hours']
        
        result = []
        for region, data in summary.items():
            result.append(f"{region}: {data['count']} outages, {data['hours']} hrs")
        return ". ".join(result)
    
    def analyze_demand_supply_gap(self) -> str:
        self.consumption_data['gap'] = self.consumption_data['supply_mw'] - self.consumption_data['demand_mw']
        analysis = self.consumption_data.groupby('region')['gap'].agg(['mean', 'min', 'max'])
        return f"Demand-Supply Gap Analysis:\n{analysis.to_string()}"
    
    def get_tools(self):
        return [
            Tool(
                name="analyze_outages",
                func=self.analyze_outages_by_region,
                description="Analyze outages by region"
            ),
            Tool(
                name="analyze_gap",
                func=self.analyze_demand_supply_gap,
                description="Analyze demand-supply gap"
            )
        ]