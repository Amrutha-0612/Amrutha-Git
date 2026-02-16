import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title="Logistics Analytics")

# --- ZOHO-INSPIRED STYLING ---
st.markdown("""
<style>
    .metric-card { 
        background: white; 
        padding: 1.5rem; 
        border-radius: 12px; 
        border: 1px solid #E0E6ED; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }
    .main-header { font-weight: 700; font-size: 2.2rem; color: #1A2B3C; }
    h3 { color: #EE6C4D; margin-top: 2rem; }
    
    /* Table styling */
    .stDataFrame {
        border: 1px solid #E0E6ED;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🧪 Full Logistics Analytics</h1>", unsafe_allow_html=True)
st.markdown("Detailed breakdown of performance across all data dimensions.")
st.markdown("---")

# Retrieve the processed DataFrame from session state
df = st.session_state.get('main_data_df')

if df is not None:
    # --- 1. GLOBAL PERFORMANCE STRIP ---
    st.subheader("🌐 Global Performance Metrics")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Total Records", len(df))
    
    with m2:
        if 'Sales' in df.columns:
            st.metric("Total Sales Amount", f"₹{df['Sales'].sum():,.2f}")
        elif 'Days Late' in df.columns:
            st.metric("Avg. System Delay", f"{df['Days Late'].mean():.1f} Days")
            
    with m3:
        if 'Delivery Status' in df.columns:
            late_count = len(df[df['Delivery Status'] == 'Late'])
            st.metric("Total Late Deliveries", late_count, delta=f"{late_count/len(df)*100:.1f}%", delta_color="inverse")
            
    with m4:
        if 'Delivery Status' in df.columns:
            on_time_rate = (len(df[df['Delivery Status'] == 'On Time'])/len(df)*100)
            st.metric("On-Time Performance", f"{on_time_rate:.1f}%")

    st.markdown("---")

    # --- 2. DIMENSIONAL EXPLORER ---
    st.markdown("<h3>🔍 Dimension Insights Explorer</h3>", unsafe_allow_html=True)
    
    # Auto-detect categorical columns for analysis
    # We exclude ID and Date columns for cleaner selection
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    exclude = ['Order ID', 'Customer ID', 'Product ID', 'Order Date', 'Ship Date', 'Delivery Status', 'PRIORITY']
    explore_cols = [c for c in categorical_cols if c not in exclude]
    
    if explore_cols:
        col_select, col_empty = st.columns([1, 2])
        target_col = col_select.selectbox("Analyze Breakdown By:", explore_cols, index=0)
        
        # Prepare Analysis Data
        agg_dict = {target_col: 'count'}
        if 'Days Late' in df.columns: agg_dict['Days Late'] = 'mean'
        if 'Sales' in df.columns: agg_dict['Sales'] = 'sum'
        
        stats = df.groupby(target_col).agg(agg_dict).rename(columns={
            target_col: 'Volume (Order Count)', 
            'Days Late': 'Avg Delay (Days)',
            'Sales': 'Total Amount (₹)'
        }).reset_index()

        # --- FIXING THE "MESSY" GRAPH ---
        # We sort by Volume and take Top 15 to keep the graph readable
        stats_sorted = stats.sort_values(by='Volume (Order Count)', ascending=False)
        top_n = st.slider("Show Top N Categories in Chart:", 5, 30, 15)
        stats_plot = stats_sorted.head(top_n)

        col_table, col_chart = st.columns([1, 1])
        
        with col_table:
            st.write(f"**Detailed Table: {target_col}**")
            st.dataframe(stats.sort_values(by='Volume (Order Count)', ascending=False), 
                         use_container_width=True, hide_index=True)
        
        with col_chart:
            st.write(f"**Top {top_n} by Volume: {target_col}**")
            # Use a horizontal bar chart for better text legibility
            fig_dim = px.bar(
                stats_plot, 
                y=target_col, 
                x='Volume (Order Count)', 
                orientation='h',
                color='Volume (Order Count)',
                color_continuous_scale='Blues',
                text='Volume (Order Count)'
            )
            fig_dim.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_dim, use_container_width=True)
    else:
        st.warning("No valid categorical columns found for analysis.")

    st.markdown("---")

    # --- 3. WORKLOAD & RISK (Specific to Logistics) ---
    st.markdown("<h3>🚨 Workload & Risk Matrix</h3>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Agent/Segment Workload")
        if 'RESPONSIBLE_PERSON' in df.columns:
            agent_data = df['RESPONSIBLE_PERSON'].value_counts().reset_index()
            agent_data.columns = ['Entity', 'Count']
            fig_agent = px.pie(agent_data, values='Count', names='Entity', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_agent, use_container_width=True)
        else:
            st.warning("'RESPONSIBLE_PERSON' column missing for workload view.")

    with c2:
        st.subheader("Priority Distribution")
        if 'PRIORITY' in df.columns:
            prio_data = df['PRIORITY'].value_counts().reset_index()
            prio_data.columns = ['Level', 'Count']
            fig_prio = px.bar(prio_data, x='Level', y='Count', color='Level',
                            color_discrete_map={'🔴 High': '#e74c3c', '🟠 Medium': '#EE6C4D', '🟢 Low': '#3498db'})
            st.plotly_chart(fig_prio, use_container_width=True)
        else:
            st.warning("'PRIORITY' column missing.")

else:
    st.error("Data not loaded. Please return to the Home page and upload your file.")
