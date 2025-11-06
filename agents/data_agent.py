# agents/data_agent.py
import pandas as pd
from langchain.tools import Tool

class DataAgent:
    def __init__(self, llm):
        self.llm = llm
        self.consumption_data = pd.read_csv('data/consumption_logs.csv')
        self.outage_data = pd.read_csv('data/outage_reports.csv')
    
    def get_peak_demand(self) -> str:
        peak_row = self.consumption_data.loc[self.consumption_data['demand_mw'].idxmax()]
        return f"Peak demand observed on {peak_row['date']} in {peak_row['region']} with {peak_row['demand_mw']} MW"
    
    def get_tools(self):
        return [
            Tool(
                name="get_peak_demand",
                func=self.get_peak_demand,
                description="Get information about peak demand"
            )
        ]