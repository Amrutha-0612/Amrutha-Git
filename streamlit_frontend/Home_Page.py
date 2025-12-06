import streamlit as st
import pandas as pd
import io
import json
from datetime import timedelta

# --- CONSTANTS ---
DATA_KEY = 'main_data_df'

# --- DATA PROCESSING FUNCTION (Centralized data cleaning and calculation) ---
@st.cache_data
def process_data(df_raw):
    """Performs all necessary data cleaning and calculations."""
    
    # 1. Rename and Clean Columns 
    df_raw.columns = df_raw.columns.str.strip()
    df = df_raw.rename(columns={
        'TOT. AMT': 'TOTAL_AMOUNT', 
        'CUSTOMER NAME ': 'CUSTOMER_NAME', 
        'DELIVERY AGENT': 'RESPONSIBLE_PERSON', 
        'ACTUAL': 'ACTUAL DELIVERY DATE'
    }).copy()
    
    df["EXPECTED DELIVERY DATE"] = pd.to_datetime(df["EXPECTED DELIVERY DATE"], dayfirst=True, errors='coerce')
    df["ACTUAL DELIVERY DATE"] = pd.to_datetime(df["ACTUAL DELIVERY DATE"], dayfirst=True, errors='coerce')
    
    df["EXPECTED DELIVERY DATE"] = df["EXPECTED DELIVERY DATE"].dt.date
    df["ACTUAL DELIVERY DATE"] = df["ACTUAL DELIVERY DATE"].dt.date
    
    df["EXPECTED DELIVERY DATE"] = pd.to_datetime(df["EXPECTED DELIVERY DATE"])
    df["ACTUAL DELIVERY DATE"] = pd.to_datetime(df["ACTUAL DELIVERY DATE"])

    # 3. Calculate Duration and Status (Required for downstream pages)
    df["Duration"] = df["ACTUAL DELIVERY DATE"] - df["EXPECTED DELIVERY DATE"]
    
    delivered_df = df.dropna(subset=["ACTUAL DELIVERY DATE"]).copy()
    delivered_df["Delivery Status"] = delivered_df["Duration"].apply(
        lambda x: "Late" if x > timedelta(days=0) else "On Time"
    )
    delivered_df["Days Late"] = (delivered_df["Duration"].dt.total_seconds() / (60 * 60 * 24))
    
    # 4. Merge results back
    df = df.merge(delivered_df[['ID NO.', 'Delivery Status', 'Days Late']], on='ID NO.', how='left')
    df['Delivery Status'] = df['Delivery Status'].fillna('N/A')
    
    # Final formatting: Convert back to just date objects for display if desired, 
    df["EXPECTED DELIVERY DATE"] = df["EXPECTED DELIVERY DATE"].dt.date
    df["ACTUAL DELIVERY DATE"] = df["ACTUAL DELIVERY DATE"].dt.date
    
    return df

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Delivery Tracker - Upload",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UI ELEMENTS ---

# --- PROFESSIONAL TITLE (CUSTOM COLOR APPLIED: #EE6C4D) ---
st.markdown("<h1 style='color: #EE6C4D;'>📦 Delivery Workload Tracker</h1>", unsafe_allow_html=True)
st.markdown("Upload a CSV file once. Data persists across pages until browser is closed.")
st.markdown("---")

# 1. User Input & File Uploader
name = st.text_input("Enter your name:", value=" ")
st.markdown(f"<h3 style='color: #EE6C4D;'>Welcome, {name.title()}!</h3>", unsafe_allow_html=True)

# 2. Current File Status Indicator
if 'current_file_name' in st.session_state:
    st.info(f"📂 **Current Active File:** {st.session_state['current_file_name']}")
else:
    st.info("📂 No file currently loaded.")

uploaded_file = st.file_uploader("Upload a new file to replace the current data:", type="csv")

# 3. Handle New File Upload Logic
if uploaded_file is not None:
    # Check if this is a NEW file upload or just a rerun
    if st.session_state.get('last_uploaded_file_id') != uploaded_file.file_id:
        try:
            df_raw = pd.read_csv(uploaded_file)
            df_processed = process_data(df_raw)
            
            # Initialize/Overwrite session state with new file data
            st.session_state[DATA_KEY] = df_processed
            st.session_state['last_uploaded_file_id'] = uploaded_file.file_id
            st.session_state['current_file_name'] = uploaded_file.name # Store filename
            
            # Confirmation Message
            st.success(f"✅ Successfully uploaded: **{uploaded_file.name}**")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error loading file: {e}")
            
    # If the file is already processed (e.g. on rerun), just show success silently
    elif st.session_state.get(DATA_KEY) is not None:
         pass

st.markdown("---")

# 4. NAVIGATION LINKS
st.markdown("<h3 style='color: #EE6C4D;'>Choose Your Analysis Option:</h3>", unsafe_allow_html=True)

# Retrieve the CURRENT state of the data (which might have been edited on other pages)
df_current = st.session_state.get(DATA_KEY)

if df_current is not None:
    
    st.success(f"Ready for analysis! Current dataset contains **{len(df_current)}** records.")
        
    st.page_link("pages/1_📊_Display_Data.py", 
                 label="📊 Display Data & Edit", 
                 icon="👀")

    st.page_link("pages/2_🧪_Data_Analysis.py", 
                 label="🧪 Data Analysis", 
                 icon="🔬")

    st.page_link("pages/3_📈_Graph_Plotting.py", 
                 label="📈 Graph Plotting", 
                 icon="📈")
    
    st.page_link("pages/4_⚠️_Tracking_Late_Delivery.py", 
                 label="⚠️ Tracking Late Deliveries", 
                 icon="🚨")

else:
    st.warning("Please upload a CSV file to enable analysis options.")
