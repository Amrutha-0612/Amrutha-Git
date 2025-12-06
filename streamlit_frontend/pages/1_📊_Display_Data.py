import streamlit as st
import pandas as pd

# --- CONSTANTS ---
DATA_KEY = 'main_data_df'

# --- SET PAGE CONFIGURATION (MINIMAL CALL TO AVOID TYPE ERROR) ---
st.set_page_config()

# --- COLOR-CODED TITLE (ORANGE: #EE6C4D) ---
st.markdown("<h1 style='color: #EE6C4D;'>📊 Data Inspection and View</h1>", unsafe_allow_html=True)
st.markdown("---")

# Retrieve the DataFrame from the session state
df = st.session_state.get(DATA_KEY)

if df is not None:
    
    # --- FIX: AUTOMATICALLY DROP UNNECESSARY 'Unnamed' COLUMNS ---
    unnamed_cols = [col for col in df.columns if col.startswith('Unnamed:')]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)
        # Update session state immediately if we dropped columns
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
    
    # --- SECTION 1: FULL DATA VIEW / EDITOR ---
    st.markdown("<h3 style='color: #EE6C4D;'>Full Data Frame View</h3>", unsafe_allow_html=True)
    
    if enable_editing:
        st.warning("Editing Mode: Changes here will update the global data immediately.")
        
        # Use st.data_editor for in-app editing
        edited_df = st.data_editor(
            df, 
            use_container_width=True, 
            num_rows="dynamic",
            key="display_page_editor" 
        )
        
        # PERSISTENCE LOGIC:
        # If edits happen here, save them back to the MAIN data key
        if not edited_df.equals(df):
            st.session_state[DATA_KEY] = edited_df
            st.rerun() # Force a rerun so the new data is locked in
            
    else:
        # Display the DataFrame without editing
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    
    # --- SECTION 2: SUMMARY STATISTICS ---
    st.markdown("<h3 style='color: #EE6C4D;'>Summary Statistics (Numeric Data)</h3>", unsafe_allow_html=True)
    
    try:
        with st.expander("Show Descriptive Statistics"):
            st.dataframe(df.describe().T, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not generate summary statistics: {e}")

else:
    st.error("Data not loaded. Please go back to the Home page and upload a CSV file.")
