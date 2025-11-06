# main.py
from langchain_ollama import OllamaLLM
from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.report_agent import ReportAgent

class EnergyManagementSystem:
    def __init__(self):
        self.llm = OllamaLLM(model="llama2")
        self.data_agent = DataAgent(self.llm)
        self.analysis_agent = AnalysisAgent(self.llm)
        self.report_agent = ReportAgent(self.llm)
    
    def process_query(self, query: str) -> str:
        query = query.lower().strip()
        
        if "peak demand" in query:
            return self.data_agent.get_peak_demand()
        elif "outage" in query and "region" in query:
            return self.analysis_agent.analyze_outages_by_region()
        elif "gap" in query or ("demand" in query and "supply" in query):
            return self.analysis_agent.analyze_demand_supply_gap()
        elif "plot" in query or "visual" in query:
            return self.report_agent.create_demand_plot()
        elif "summary" in query or "report" in query:
            return self.report_agent.generate_summary()
        else:
            return "I'm sorry, I don't understand that query. Please ask about peak demand, outages by region, demand-supply gap, or request a visualization."

def main():
    print("Energy Management System")
    print("=" * 50)
    print("\nYou can ask questions like:")
    print("- What was the peak demand?")
    print("- Can you summarize outages by region?")
    print("- Tell me about the demand patterns")
    print("- What's the gap between supply and demand?")
    print("\nType 'exit' to quit")
    print("-" * 50)
    
    system = EnergyManagementSystem()
    
    while True:
        query = input("\nEnter your query: ").strip()
        
        if query.lower() == 'exit':
            print("Thank you for using the Energy Management System!")
            break
        
        response = system.process_query(query)
        print("\nResponse:")
        print(response)

if __name__ == "__main__":
    main()