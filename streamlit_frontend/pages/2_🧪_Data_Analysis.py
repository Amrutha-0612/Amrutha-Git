import streamlit as st
import pandas as pd
import plotly.express as px

# --- SET PAGE CONFIGURATION ---
st.set_page_config()

# --- COLOR-CODED TITLE (ORANGE: #EE6C4D) ---
st.markdown("<h1 style='color: #EE6C4D;'>🔬 Agent Workload and Priority Analysis</h1>", unsafe_allow_html=True)
st.markdown("Detailed breakdown of item assignment and special handling requirements.")
st.markdown("---")

# Retrieve the processed DataFrame from session state
df = st.session_state.get('main_data_df')

if df is not None:
    
    # --- NEW SECTION: PENDING ORDER ANALYSIS (Based on STATUS) ---
    st.markdown("<h3 style='color: #EE6C4D;'>0. Pending Orders Overview</h3>", unsafe_allow_html=True)
    
    # Logic: Identify Pending Orders based on STATUS column
    if 'STATUS' in df.columns:
        # Normalize status to lowercase for comparison
        # Pending = Anything that is NOT 'delivered'
        # Adjust 'delivered' string if your CSV uses a different term (e.g., 'Completed')
        pending_mask = df['STATUS'].astype(str).str.strip().str.lower() != 'delivered'
        
        # Create a Pending DataFrame
        df_pending = df[pending_mask].copy()
        
        total_pending = len(df_pending)
        total_orders = len(df)
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.metric(label="Total Pending Orders", value=total_pending, 
                      delta=f"{total_pending/total_orders*100:.1f}% of Total")
            st.caption("*Based on items where Status is not 'Delivered'.*")
            
        with col_p2:
            if not df_pending.empty and 'RESPONSIBLE_PERSON' in df_pending.columns:
                # Mini-chart for pending per agent
                pending_per_agent = df_pending['RESPONSIBLE_PERSON'].value_counts().reset_index()
                pending_per_agent.columns = ['Agent', 'Pending Count']
                
                fig_pending = px.bar(pending_per_agent, x='Pending Count', y='Agent', orientation='h',
                                     title="Pending Items by Agent", height=250,
                                     color_discrete_sequence=['#EE6C4D'])
                fig_pending.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_pending, use_container_width=True)
            elif df_pending.empty:
                st.success("No pending orders found! All items are delivered.")
    else:
        st.warning("Cannot calculate Pending Orders: 'STATUS' column missing.")

    st.markdown("---")

    # --- SECTION 1: WORKLOAD DISTRIBUTION ---
    st.markdown("<h3 style='color: #EE6C4D;'>1. Workload Distribution by Agent and Priority</h3>", unsafe_allow_html=True)
    
    col_w1, col_w2 = st.columns(2)
    
    # 1.1 Workload by Responsible Person (Bar Chart)
    with col_w1:
        st.subheader("👤 Items Assigned Per Agent")
        if 'RESPONSIBLE_PERSON' in df.columns:
            person_workload = df['RESPONSIBLE_PERSON'].value_counts().reset_index()
            person_workload.columns = ['Agent', 'Total Items']
            
            # Display as a bar chart (Workload)
            fig_person = px.bar(
                person_workload,
                x='Agent',
                y='Total Items',
                color='Agent',
                title='Total Items Assigned',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                text='Total Items'
            )
            st.plotly_chart(fig_person, use_container_width=True)
            
        else:
            st.warning("Column 'RESPONSIBLE_PERSON' (Delivery Agent) not found for workload analysis.")

    # 1.2 Work Distribution by Priority (Pie Chart)
    with col_w2:
        st.subheader("⭐ Distribution by Priority")
        if 'PRIORITY' in df.columns:
            priority_counts = df['PRIORITY'].value_counts().reset_index()
            priority_counts.columns = ['Priority', 'Total Items']
            
            # Display as a pie chart (Priority)
            fig_priority = px.pie(
                priority_counts,
                values='Total Items',
                names='Priority',
                title='Proportion of Priority Levels',
                color_discrete_map={'High': '#e74c3c', 'Medium': '#EE6C4D', 'Low': '#3498db'} # Using custom orange for Medium
            )
            fig_priority.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_priority, use_container_width=True)
            
        else:
            st.warning("Priority data not available (missing 'PRIORITY' column).")

    st.markdown("---")
    
    # --- SECTION 2: PRIORITY VS AGENT BREAKDOWN ---
    st.markdown("<h3 style='color: #EE6C4D;'>2. Priority Breakdown by Agent</h3>", unsafe_allow_html=True)
    
    if 'RESPONSIBLE_PERSON' in df.columns and 'PRIORITY' in df.columns:
        # Calculate cross-tabulation for stacked bar chart
        priority_person_df = df.groupby(['RESPONSIBLE_PERSON', 'PRIORITY']).size().reset_index(name='Count')
        
        fig_priority_person = px.bar(
            priority_person_df,
            x='RESPONSIBLE_PERSON',
            y='Count',
            color='PRIORITY',
            title='Priority Stacked Breakdown per Agent',
            category_orders={"PRIORITY": ["High", "Medium", "Low"]},
            color_discrete_map={'High': '#e74c3c', 'Medium': '#EE6C4D', 'Low': '#3498db'}, # Using custom orange for Medium
            text='Count'
        )
        fig_priority_person.update_layout(xaxis_title="Delivery Agent", yaxis_title="Number of Items")
        st.plotly_chart(fig_priority_person, use_container_width=True)
        
    else:
        st.info("Cannot generate Priority vs. Agent breakdown due to missing data columns.")

    st.markdown("---")
    
    # --- SECTION 3: SPECIAL INSTRUCTIONS TABLE ---
    st.markdown("<h3 style='color: #EE6C4D;'>3. Special Instructions/Issues List</h3>", unsafe_allow_html=True)
    
    if 'NOTES' in df.columns:
        # Clean and identify items with notes (re-using cleaning from top if needed, or re-calculating)
        df['NOTES_CLEAN'] = df['NOTES'].fillna('').astype(str).str.strip()
        items_with_notes = df[df['NOTES_CLEAN'] != ''].copy()
        
        st.info(f"Total items requiring special attention (Notes/Issues): **{len(items_with_notes)}**")
        
        if not items_with_notes.empty:
            # Select relevant columns for display
            display_cols = ['ID NO.', 'NAME', 'STATUS', 'NOTES', 'RESPONSIBLE_PERSON', 'PRIORITY']
            # Filter columns that exist in the DataFrame
            existing_cols = [col for col in display_cols if col in items_with_notes.columns]
            
            # Use st.dataframe with a clear title
            st.dataframe(
                items_with_notes[existing_cols], 
                use_container_width=True, 
                hide_index=True,
                # Configure the NOTES column to be wide for better readability
                column_config={"NOTES": st.column_config.TextColumn("Notes/Instructions", width="large")}
            )
        
    else:
        st.warning("Notes column ('NOTES') not found for special instruction analysis.")

else:
    st.error("Data not loaded. Please go back to the Home page and upload a CSV file.")
