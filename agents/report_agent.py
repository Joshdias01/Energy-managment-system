import plotly.express as px
import pandas as pd
from langchain.tools import Tool

class ReportAgent:
    def __init__(self, llm):
        self.llm = llm
        self.consumption_data = pd.read_csv('data/consumption_logs.csv')
        self.outage_data = pd.read_csv('data/outage_reports.csv')
    
    def generate_summary(self) -> str:
        peak_row = self.consumption_data.loc[self.consumption_data['demand_mw'].idxmax()]
        outage_summary = self.analyze_outages_by_region()
        return f"Summary Report:\n- Peak Demand: {peak_row['demand_mw']} MW on {peak_row['date']}\n- Outages: {outage_summary}"
    
    def create_demand_plot(self) -> str:
        fig = px.line(self.consumption_data, x='date', y='demand_mw', 
                     color='region', title='Demand Trends')
        fig.write_html('demand_plot.html')
        return "Demand plot saved as 'demand_plot.html'"
    
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
    
    def get_tools(self):
        return [
            Tool(
                name="generate_summary",
                func=self.generate_summary,
                description="Generate summary report"
            ),
            Tool(
                name="create_plot",
                func=self.create_demand_plot,
                description="Create demand visualization"
            )
        ]