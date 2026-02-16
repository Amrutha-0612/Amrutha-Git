import streamlit as st
import pandas as pd
import plotly.express as px

# --- SET PAGE CONFIGURATION (MINIMAL CALL TO AVOID TYPE ERROR) ---
st.set_page_config()

# --- COLOR-CODED TITLE (ORANGE: #EE6C4D) ---
st.markdown("<h1 style='color: #EE6C4D;'>📈 Data Visualization Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Visual representation of current status, workload, and priority distribution.")
st.markdown("---")

# Retrieve the processed DataFrame from session state
df = st.session_state.get('main_data_df')

if df is not None:
    
    # --- SECTION 1: STATUS AND PRIORITY ---
    st.markdown("<h3 style='color: #EE6C4D;'>1. Delivery Status and Priority Breakdown</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # --- PROGRESS STATUS (Chart 1) ---
    with col1:
        st.subheader("Progress Status Distribution")
        if 'STATUS' in df.columns:
            status_counts = df['STATUS'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig_status = px.pie(
                status_counts, 
                values='Count', 
                names='Status', 
                title='Distribution of Progress Status', 
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig_status.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Status data ('STATUS' column) not found.")

    # --- WORKLOAD BY PRIORITY LEVEL (Chart 2) ---
    with col2:
        st.subheader("Workload by Priority Level")
        if 'PRIORITY' in df.columns:
            priority_counts = df['PRIORITY'].value_counts().reset_index()
            priority_counts.columns = ['Priority Level', 'Count']
            
            # Using custom orange for Medium to match branding
            fig_priority = px.bar(
                priority_counts, 
                x='Priority Level', 
                y='Count', 
                color='Priority Level', 
                title='Workload by Priority Level', 
                color_discrete_map={'High': '#e74c3c', 'Medium': '#EE6C4D', 'Low': '#3498db'},
                text='Count'
            )
            fig_priority.update_traces(textposition='outside')
            st.plotly_chart(fig_priority, use_container_width=True)
        else:
            st.info("Priority data ('PRIORITY' column) not found.")
            
    st.markdown("---")
    
    # --- SECTION 2: WORKLOAD BY AGENT ---
    st.markdown("<h3 style='color: #EE6C4D;'>2. Workload by Delivery Agent</h3>", unsafe_allow_html=True)
    
    # Using the standardized column name 'RESPONSIBLE_PERSON'
    if 'RESPONSIBLE_PERSON' in df.columns:
        person_workload = df['RESPONSIBLE_PERSON'].value_counts().reset_index()
        person_workload.columns = ['Agent', 'Count']
        
        fig_agent = px.bar(
            person_workload, 
            x='Agent', 
            y='Count', 
            title='Total Items Assigned per Delivery Agent', 
            color='Agent',
            # Using a neutral, soft palette for agents
            color_discrete_sequence=px.colors.qualitative.Antique, 
            text='Count'
        )
        fig_agent.update_traces(textposition='outside')
        st.plotly_chart(fig_agent, use_container_width=True)
    else:
        st.error("Cannot plot Workload by Person: Column 'RESPONSIBLE_PERSON' not found in the processed data.")
            
else:
    st.error("Data not loaded. Please go back to the Home page and upload a CSV file.")
