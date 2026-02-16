import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# --- SET PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Risk Tracker")

# --- PROFESSIONAL TITLE (COLOR APPLIED) ---
st.markdown("<h1 style='color: #EE6C4D;'>🚨 Late Deliveries Detail Report</h1>", unsafe_allow_html=True)
st.markdown("Identify and analyze shipments that failed to meet the expected delivery date.")
st.markdown("---")

# Retrieve the processed DataFrame from session state
# This ensures that any edits or additions made in the 'Display Data' page are captured here.
df = st.session_state.get('main_data_df')

if df is not None:
    
    # --- GUARANTEE REQUIRED COLUMNS EXIST AND ARE CONVERTED ---
    required_cols = ["EXPECTED DELIVERY DATE", "ACTUAL DELIVERY DATE"]
    
    # Check if the required columns are in the DataFrame
    if all(col in df.columns for col in required_cols):
        
        # 1. Force conversion to datetime objects (Essential for accurate subtraction after edits)
        df["EXPECTED DELIVERY DATE"] = pd.to_datetime(df["EXPECTED DELIVERY DATE"], dayfirst=True, errors='coerce')
        df["ACTUAL DELIVERY DATE"] = pd.to_datetime(df["ACTUAL DELIVERY DATE"], dayfirst=True, errors='coerce')
        
        # 2. Recalculate Duration and Days Late inside this page 
        # This ensures that even if you added a new row, the 'Late' status is calculated immediately.
        df["Duration"] = df["ACTUAL DELIVERY DATE"] - df["EXPECTED DELIVERY DATE"]
        
        def calculate_status(dur):
            if pd.isnull(dur): return "Pending"
            return "Late" if dur > timedelta(days=0) else "On Time"

        df["Delivery Status"] = df["Duration"].apply(calculate_status)
        df["Days Late"] = (df["Duration"].dt.total_seconds() / (60 * 60 * 24)).fillna(0)
        
        # KPI Calculations
        total_records = len(df) # This will correctly show 61 if a new row was added
        df_delivered = df.dropna(subset=["ACTUAL DELIVERY DATE"]).copy()
        delayed_df = df_delivered[df_delivered["Duration"] > timedelta(days=0)].copy()
        
        total_delivered = len(df_delivered)
        total_delayed = len(delayed_df)
        
        # --- 1. KEY PERFORMANCE INDICATORS (KPIs) ---
        st.markdown("<h3 style='color: #EE6C4D;'>1. Delay Summary Metrics</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info("System Total")
            # This metric now reflects the absolute count of rows (e.g., updates from 60 to 61)
            st.metric(label="Total Records", value=total_records)
            
        with col2:
            st.warning("Total Late Shipments")
            st.metric(label="Delayed Count", value=total_delayed, 
                      delta=f"{total_delayed / total_delivered * 100:.1f}% of Delivered" if total_delivered > 0 else None)

        if not delayed_df.empty:
            avg_delay = delayed_df['Days Late'].mean().round(2)
            max_delay = delayed_df['Days Late'].max().round(2)

            with col3:
                st.error("Average Delay Time")
                st.metric(label="Avg. Days Late", value=avg_delay)
                
            with col4:
                st.error("Maximum Delay Time")
                st.metric(label="Max Days Late", value=max_delay)
        
        st.markdown("---")

        # --- 2. DELAYED ITEMS TABLE ---
        st.markdown("<h3 style='color: #EE6C4D;'>2. List of All Delayed Shipments</h3>", unsafe_allow_html=True)
        
        if delayed_df.empty:
            st.success("🎉 No delayed deliveries found in the current selection!")
        else:
            st.info(f"Showing {len(delayed_df)} items with recorded delays.")
            
            ideal_columns = [
                "ID NO.", "NAME", "EXPECTED DELIVERY DATE", 
                "ACTUAL DELIVERY DATE", "Days Late", 
                "RESPONSIBLE_PERSON", "PRIORITY"
            ]
            
            available_cols = [col for col in ideal_columns if col in delayed_df.columns]
            
            st.dataframe(
                delayed_df[available_cols].sort_values(by="Days Late", ascending=False), 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Days Late": st.column_config.NumberColumn("Days Late", format="%.2f days"),
                    "EXPECTED DELIVERY DATE": st.column_config.DateColumn("Expected"),
                    "ACTUAL DELIVERY DATE": st.column_config.DateColumn("Actual")
                }
            )

        st.markdown("---")

        # --- 3. PERFORMANCE CHART ---
        st.markdown("<h3 style='color: #EE6C4D;'>3. Overall Delivery Performance</h3>", unsafe_allow_html=True)

        # Performance split including Pending items
        performance_counts = df["Delivery Status"].value_counts().reset_index()
        performance_counts.columns = ['Status', 'Count']

        fig = px.bar(
            performance_counts, 
            x='Status', 
            y='Count', 
            color='Status',
            color_discrete_map={'On Time': '#2ecc71', 'Late': '#e74c3c', 'Pending': '#f1c40f'},
            text='Count',
            title="Total Distribution: On-Time vs Late vs Pending"
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Cannot perform late delivery analysis: Missing 'ACTUAL DELIVERY DATE' or 'EXPECTED DELIVERY DATE' columns. Please check your Home Page mapping.")
        
else:
    st.error("Data not loaded. Please go back to the Home page and upload a CSV file.")
