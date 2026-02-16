import streamlit as st
import pandas as pd
import auth as auth_db
from datetime import timedelta

# --- CONSTANTS ---
DATA_KEY = 'main_data_df'

# --- SET PAGE CONFIGURATION ---
st.set_page_config(layout="wide")

# --- COLOR-CODED TITLE ---
st.markdown("<h1 style='color: #EE6C4D;'>📊 Data Inspection and View</h1>", unsafe_allow_html=True)
st.markdown("---")

# Retrieve the DataFrame from the session state
df = st.session_state.get(DATA_KEY)

if df is not None:
    # Cleanup unnamed columns
    unnamed_cols = [col for col in df.columns if col.startswith('Unnamed:')]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)
        st.session_state[DATA_KEY] = df
        
    st.header("Data Overview")

    col_config, col_edit = st.columns([2, 1])
    with col_edit:

    # User option to enable editing
        enable_editing = st.checkbox("✅ Enable Data Editing?", help="Check this box to modify the data directly.")

    with col_config:
        st.metric(label="Total Records", value=f"{len(df):,}")
        st.metric(label="Total Columns", value=len(df.columns))

    st.markdown("---")
    
    if enable_editing:
        st.warning("Editing Mode: Changes will be saved to your account automatically.")
        
        # Use st.data_editor for in-app editing
        edited_df = st.data_editor(
            df, 
            use_container_width=True, 
            num_rows="dynamic",
            key="display_page_editor" 
        )
        
        # PERSISTENCE LOGIC
        if not edited_df.equals(df):
            # 1. Recalculate Logic (Optional: Re-run priority logic if dates changed)
            try:
                edited_df["EXPECTED DELIVERY DATE"] = pd.to_datetime(edited_df["EXPECTED DELIVERY DATE"])
                edited_df["ACTUAL DELIVERY DATE"] = pd.to_datetime(edited_df["ACTUAL DELIVERY DATE"])
                edited_df["Duration"] = edited_df["ACTUAL DELIVERY DATE"] - edited_df["EXPECTED DELIVERY DATE"]
                edited_df["Days Late"] = (edited_df["Duration"].dt.total_seconds() / (60 * 60 * 24)).fillna(0)
                
                def calc_priority(days):
                    if days > 5: return "High"
                    if days > 0: return "Medium"
                    return "Low"
                
                edited_df["PRIORITY"] = edited_df["Days Late"].apply(calc_priority)
            except:
                pass # Fallback if user is mid-typing dates

            # 2. Save to Session State
            st.session_state[DATA_KEY] = edited_df
            
            # 3. CRITICAL: Save to Database
            if 'username' in st.session_state:
                filename = st.session_state.get('current_file_name', 'Edited_Data.csv')
                auth_db.save_user_data(st.session_state['username'], edited_df, filename)
            
            st.rerun() 
            
    else:
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    with st.expander("Show Descriptive Statistics"):
        st.dataframe(df.describe().T, use_container_width=True)

else:
    st.error("Data not loaded. Please go back to the Home page and upload a file.")
