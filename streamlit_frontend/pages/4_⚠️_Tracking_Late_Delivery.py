import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# --- SET PAGE CONFIGURATION (MINIMAL CALL TO AVOID TYPE ERROR) ---
st.set_page_config() 

# --- PROFESSIONAL TITLE (COLOR APPLIED) ---
st.markdown("<h1 style='color: #EE6C4D;'>🚨 Late Deliveries Detail Report</h1>", unsafe_allow_html=True)
st.markdown("Identify and analyze shipments that failed to meet the expected delivery date.")
st.markdown("---")

# Retrieve the processed DataFrame from session state
df = st.session_state.get('main_data_df')

if df is not None:
    
    # --- GUARANTEE REQUIRED COLUMNS EXIST AND ARE CONVERTED ---
    required_cols = ["EXPECTED DELIVERY DATE", "ACTUAL DELIVERY DATE"]
    
    # Check if the required columns are in the DataFrame
    if all(col in df.columns for col in required_cols):
        
        # 1. Force conversion to datetime objects (Essential for subtraction)
        df["EXPECTED DELIVERY DATE"] = pd.to_datetime(df["EXPECTED DELIVERY DATE"], dayfirst=True, errors='coerce')
        df["ACTUAL DELIVERY DATE"] = pd.to_datetime(df["ACTUAL DELIVERY DATE"], dayfirst=True, errors='coerce')
        
        # 2. Calculate Duration and Days Late (Must be done to find "Late")
        df["Duration"] = df["ACTUAL DELIVERY DATE"] - df["EXPECTED DELIVERY DATE"]
        df["Delivery Status"] = df["Duration"].apply(
            lambda x: "Late" if x > timedelta(days=0) else "On Time"
        )
        df["Days Late"] = (df["Duration"].dt.total_seconds() / (60 * 60 * 24))
        
        # Filter for items that have been delivered
        df_delivered = df.dropna(subset=["ACTUAL DELIVERY DATE"]).copy()
        
        # Filter for all deliveries where the duration is positive (i.e., Late)
        delayed_df = df_delivered[df_delivered["Duration"] > timedelta(days=0)].copy()
        
        total_delivered = len(df_delivered)
        total_delayed = len(delayed_df)
        
        # --- 1. KEY PERFORMANCE INDICATORS (KPIs) ---
        st.markdown("<h3 style='color: #EE6C4D;'>1. Delay Summary Metrics</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info("Total Deliveries")
            st.metric(label="Delivered Count", value=total_delivered)
            
        with col2:
            st.warning("Total Late Shipments")
            st.metric(label="Delayed Count", value=total_delayed, 
                      delta=f"{total_delayed / total_delivered * 100:.1f}% of Total" if total_delivered > 0 else None)

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
            
            # Display the detailed list, using standardized column names
            st.dataframe(
                delayed_df[[
                    "ID NO.", "NAME", "EXPECTED DELIVERY DATE", "ACTUAL DELIVERY DATE", "Days Late", "RESPONSIBLE_PERSON", "PRIORITY"
                ]].sort_values(by="Days Late", ascending=False), 
                use_container_width=True,
                column_config={
                    "Days Late": st.column_config.NumberColumn("Days Late", format="%.2f days"),
                    "RESPONSIBLE_PERSON": "Delivery Agent"
                }
            )

        st.markdown("---")

        # --- 3. PERFORMANCE CHART ---
        st.markdown("<h3 style='color: #EE6C4D;'>3. Overall Delivery Performance</h3>", unsafe_allow_html=True)

        status_counts = df_delivered["Delivery Status"].value_counts().reset_index()
        status_counts.columns = ['Delivery Status', 'Count']

        # Use Plotly for an interactive performance chart
        fig = px.bar(
            status_counts, 
            x='Delivery Status', 
            y='Count', 
            color='Delivery Status',
            color_discrete_map={'On Time': '#2ecc71', 'Late': '#e74c3c'},
            text='Count',
            title="Delivery Performance: On-Time vs Late Count"
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Cannot perform late delivery analysis: Missing 'ACTUAL DELIVERY DATE' or 'EXPECTED DELIVERY DATE' columns in the uploaded data. Please check your Home Page file.")
        
else:
    st.error("Data not loaded. Please go back to the Home page and upload a CSV file.")