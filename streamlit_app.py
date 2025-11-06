# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Agentic Energy Assistant",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-size: 1.2rem;
        padding: 0.5rem;
        border-radius: 10px;
        font-weight: bold;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        border-left: 5px solid #1E88E5;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        consumption = pd.read_csv('data/consumption_logs.csv')
        outages = pd.read_csv('data/outage_reports.csv')
        consumption['date'] = pd.to_datetime(consumption['date'])
        outages['date'] = pd.to_datetime(outages['date'])
        return consumption, outages
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

consumption_data, outage_data = load_data()

if consumption_data is None or outage_data is None:
    st.error("Please make sure data files exist in the 'data' folder!")
    st.stop()

# Main header
st.markdown('<h1 class="main-header">⚡ Agentic Energy Assistant</h1>', unsafe_allow_html=True)

# Create three columns for inputs
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📍 Select Region")
    region = st.selectbox(
        "Choose a region:",
        ["All", "North", "South", "East", "West"],
        index=0
    )

with col2:
    st.subheader("📅 Start Date")
    start_date = st.date_input(
        "Select start date:",
        value=consumption_data['date'].min(),
        min_value=consumption_data['date'].min(),
        max_value=consumption_data['date'].max()
    )

with col3:
    st.subheader("📅 End Date")
    end_date = st.date_input(
        "Select end date:",
        value=consumption_data['date'].max(),
        min_value=consumption_data['date'].min(),
        max_value=consumption_data['date'].max()
    )

# Query input
st.subheader("💬 Enter Your Query")
query = st.text_area(
    "Ask anything about energy demand, supply, or outages:",
    placeholder="e.g., What was the peak demand? or Summarize outages by region",
    height=100,
    key="query_input"
)

# Generate Report Button
if st.button("🔍 Generate Report", type="primary"):
    if query:
        with st.spinner("Processing your query..."):
            # Filter data based on selections
            filtered_consumption = consumption_data.copy()
            filtered_outages = outage_data.copy()
            
            # Apply date filter
            filtered_consumption = filtered_consumption[
                (filtered_consumption['date'] >= pd.to_datetime(start_date)) &
                (filtered_consumption['date'] <= pd.to_datetime(end_date))
            ]
            filtered_outages = filtered_outages[
                (filtered_outages['date'] >= pd.to_datetime(start_date)) &
                (filtered_outages['date'] <= pd.to_datetime(end_date))
            ]
            
            # Apply region filter
            if region != "All":
                filtered_consumption = filtered_consumption[filtered_consumption['region'] == region]
                filtered_outages = filtered_outages[filtered_outages['region'] == region]
            
            # Process query
            query_lower = query.lower()
            response = ""
            
            try:
                if "peak demand" in query_lower:
                    if len(filtered_consumption) > 0:
                        peak_row = filtered_consumption.loc[filtered_consumption['demand_mw'].idxmax()]
                        response = f"✅ Peak demand observed on {peak_row['date'].strftime('%Y-%m-%d')} in {peak_row['region']} region with {peak_row['demand_mw']} MW"
                    else:
                        response = "No data available for the selected filters."
                
                elif "outage" in query_lower:
                    if len(filtered_outages) > 0:
                        if "region" in query_lower:
                            summary = {}
                            for _, row in filtered_outages.iterrows():
                                r = row['region']
                                if r not in summary:
                                    summary[r] = {'count': 0, 'hours': 0}
                                summary[r]['count'] += 1
                                summary[r]['hours'] += row['duration_hours']
                            
                            result = []
                            for r, data in summary.items():
                                result.append(f"**{r}**: {data['count']} outages, {data['hours']} hrs")
                            response = "\n\n".join(result)
                        else:
                            total_outages = len(filtered_outages)
                            total_hours = filtered_outages['duration_hours'].sum()
                            avg_duration = filtered_outages['duration_hours'].mean()
                            response = f"**Total Outages**: {total_outages}\n\n**Total Duration**: {total_hours} hours\n\n**Average Duration**: {avg_duration:.2f} hours"
                    else:
                        response = "No outage data available for the selected filters."
                
                elif "gap" in query_lower or ("demand" in query_lower and "supply" in query_lower):
                    if len(filtered_consumption) > 0:
                        filtered_consumption['gap'] = filtered_consumption['supply_mw'] - filtered_consumption['demand_mw']
                        analysis = filtered_consumption.groupby('region')['gap'].agg(['mean', 'min', 'max'])
                        response = f"**Demand-Supply Gap Analysis:**\n\n{analysis.to_string()}"
                    else:
                        response = "No data available for the selected filters."
                
                elif "summary" in query_lower or "report" in query_lower:
                    if len(filtered_consumption) > 0:
                        peak_demand = filtered_consumption['demand_mw'].max()
                        avg_demand = filtered_consumption['demand_mw'].mean()
                        total_supply = filtered_consumption['supply_mw'].sum()
                        total_outages = len(filtered_outages)
                        total_outage_hours = filtered_outages['duration_hours'].sum() if len(filtered_outages) > 0 else 0
                        
                        response = f"""**📊 Summary Report**

**Peak Demand**: {peak_demand} MW

**Average Demand**: {avg_demand:.2f} MW

**Total Supply**: {total_supply} MW

**Total Outages**: {total_outages}

**Total Outage Hours**: {total_outage_hours} hrs

**Date Range**: {start_date} to {end_date}

**Region**: {region}

**Records Analyzed**: {len(filtered_consumption)} consumption records"""
                    else:
                        response = "No data available for the selected filters."
                
                else:
                    response = "❓ Please ask about:\n- Peak demand\n- Outages by region\n- Demand-supply gap\n- Summary report"
                
                # Display result
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.success("✅ Query Processed Successfully!")
                st.markdown("### 📊 Results:")
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Show visualizations
                if len(filtered_consumption) > 0:
                    st.markdown("---")
                    st.markdown("## 📈 Visualizations & Analytics")
                    
                    # Create tabs for different visualizations
                    tab1, tab2, tab3, tab4 = st.tabs(["📈 Demand Trends", "⚡ Supply vs Demand", "🔴 Outage Analysis", "📊 Statistics"])
                    
                    with tab1:
                        st.markdown("### Energy Demand Over Time")
                        fig1 = px.line(
                            filtered_consumption, 
                            x='date', 
                            y='demand_mw', 
                            color='region',
                            title=f'Energy Demand Trends - {region}',
                            labels={'demand_mw': 'Demand (MW)', 'date': 'Date'}
                        )
                        fig1.update_layout(height=500)
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with tab2:
                        st.markdown("### Supply vs Demand Comparison")
                        fig2 = go.Figure()
                        
                        if region == "All":
                            for r in filtered_consumption['region'].unique():
                                region_data = filtered_consumption[filtered_consumption['region'] == r]
                                fig2.add_trace(go.Scatter(
                                    x=region_data['date'], 
                                    y=region_data['demand_mw'], 
                                    mode='lines', 
                                    name=f'{r} - Demand'
                                ))
                                fig2.add_trace(go.Scatter(
                                    x=region_data['date'], 
                                    y=region_data['supply_mw'], 
                                    mode='lines', 
                                    name=f'{r} - Supply', 
                                    line=dict(dash='dash')
                                ))
                        else:
                            fig2.add_trace(go.Scatter(
                                x=filtered_consumption['date'], 
                                y=filtered_consumption['demand_mw'], 
                                mode='lines', 
                                name='Demand',
                                line=dict(color='red')
                            ))
                            fig2.add_trace(go.Scatter(
                                x=filtered_consumption['date'], 
                                y=filtered_consumption['supply_mw'], 
                                mode='lines', 
                                name='Supply',
                                line=dict(color='green', dash='dash')
                            ))
                        
                        fig2.update_layout(
                            title='Supply vs Demand Comparison', 
                            xaxis_title='Date', 
                            yaxis_title='Power (MW)',
                            height=500
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    with tab3:
                        st.markdown("### Outage Analysis")
                        if len(filtered_outages) > 0:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                outage_by_region = filtered_outages.groupby('region')['duration_hours'].sum().reset_index()
                                fig3 = px.bar(
                                    outage_by_region, 
                                    x='region', 
                                    y='duration_hours', 
                                    title='Total Outage Duration by Region',
                                    labels={'duration_hours': 'Total Hours', 'region': 'Region'},
                                    color='duration_hours',
                                    color_continuous_scale='Reds'
                                )
                                fig3.update_layout(height=400)
                                st.plotly_chart(fig3, use_container_width=True)
                            
                            with col2:
                                if 'cause' in filtered_outages.columns:
                                    outage_by_cause = filtered_outages['cause'].value_counts().reset_index()
                                    outage_by_cause.columns = ['cause', 'count']
                                    fig4 = px.pie(
                                        outage_by_cause, 
                                        values='count', 
                                        names='cause', 
                                        title='Outages by Cause',
                                        hole=0.4
                                    )
                                    fig4.update_layout(height=400)
                                    st.plotly_chart(fig4, use_container_width=True)
                            
                            # Outage timeline
                            st.markdown("#### Outage Timeline")
                            fig5 = px.scatter(
                                filtered_outages,
                                x='date',
                                y='duration_hours',
                                color='region',
                                size='duration_hours',
                                hover_data=['cause', 'region'],
                                title='Outage Events Over Time'
                            )
                            fig5.update_layout(height=400)
                            st.plotly_chart(fig5, use_container_width=True)
                        else:
                            st.info("ℹ️ No outage data available for the selected period.")
                    
                    with tab4:
                        st.markdown("### Key Performance Indicators")
                        
                        # Metrics row
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Peak Demand", f"{filtered_consumption['demand_mw'].max()} MW")
                        with col2:
                            st.metric("📈 Avg Demand", f"{filtered_consumption['demand_mw'].mean():.2f} MW")
                        with col3:
                            st.metric("🔴 Total Outages", len(filtered_outages))
                        with col4:
                            total_outage_hrs = filtered_outages['duration_hours'].sum() if len(filtered_outages) > 0 else 0
                            st.metric("⏱️ Outage Hours", f"{total_outage_hrs} hrs")
                        
                        st.markdown("---")
                        
                        # Statistical summary table
                        st.markdown("### 📊 Statistical Summary by Region")
                        summary_stats = filtered_consumption.groupby('region').agg({
                            'demand_mw': ['mean', 'max', 'min', 'std'],
                            'supply_mw': ['mean', 'max', 'min']
                        }).round(2)
                        st.dataframe(summary_stats, use_container_width=True)
                        
                        # Box plot for demand distribution
                        st.markdown("### 📦 Demand Distribution by Region")
                        fig6 = px.box(
                            filtered_consumption,
                            x='region',
                            y='demand_mw',
                            color='region',
                            title='Demand Distribution Across Regions'
                        )
                        fig6.update_layout(height=400)
                        st.plotly_chart(fig6, use_container_width=True)
                
                # Show data table
                with st.expander("📋 View Raw Data"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Consumption Data**")
                        st.dataframe(filtered_consumption.head(100), use_container_width=True)
                        st.caption(f"Showing first 100 of {len(filtered_consumption)} records")
                    with col2:
                        st.markdown("**Outage Data**")
                        st.dataframe(filtered_outages.head(100), use_container_width=True)
                        st.caption(f"Showing first 100 of {len(filtered_outages)} records")
                        
            except Exception as e:
                st.error(f"❌ Error processing query: {str(e)}")
                st.exception(e)
    else:
        st.warning("⚠️ Please enter a query before generating the report.")

# Sidebar with information
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/lightning-bolt.png", width=80)
    
    st.header("📖 User Guide")
    st.markdown("""
    ### How to use:
    1. **Select Region**: Choose a specific region or view all
    2. **Select Dates**: Pick your date range
    3. **Enter Query**: Ask your question
    4. **Generate Report**: Click to get results
    
    ### Sample Queries:
    - What was the peak demand?
    - Summarize outages by region
    - Show demand-supply gap
    - Give me a summary report
    - How many outages occurred?
    
    ### Features:
    - ⚡ Real-time analysis
    - 📊 Interactive visualizations
    - 📈 Trend analysis
    - 📋 Raw data access
    - 🔍 Advanced filtering
    """)
    
    st.divider()
    
    st.header("📊 Dataset Overview")
    st.metric("🌍 Total Regions", consumption_data['region'].nunique())
    st.metric("📅 Date Range", f"{(consumption_data['date'].max() - consumption_data['date'].min()).days} days")
    st.metric("📝 Consumption Records", f"{len(consumption_data):,}")
    st.metric("🔴 Outage Records", f"{len(outage_data):,}")
    st.metric("⚡ Peak Demand", f"{consumption_data['demand_mw'].max()} MW")
    st.metric("📊 Avg Demand", f"{consumption_data['demand_mw'].mean():.2f} MW")
    
    st.divider()
    st.caption("Powered by Agentic AI 🤖")