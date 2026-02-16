import streamlit as st
import pandas as pd
import io
import json
from datetime import timedelta
import auth as auth_db 
import base64

# --- PAGE SETUP ---
st.set_page_config(
    page_title="LogiTrack Pro | Delivery Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
def local_css():
    st.markdown("""
    <style>
        /* Main Background and Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
        }
        /* FIX FOR OVERLAPPING TEXT IN EXPANDERS */
        div[data-testid="stExpander"] summary span p {
            display: none !important;
        }

        /* Gradient Header */
        .main-header {
            background: linear-gradient(90deg, #293241 0%, #EE6C4D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 3rem;
            margin-bottom: 0px;
        }

        /* Card Styling for Login */
        .login-card {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            border-left: 5px solid #EE6C4D;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #293241;
        }
        section[data-testid="stSidebar"] .stText, section[data-testid="stSidebar"] label {
            color: white !important;
        }

        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(238, 108, 77, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)

# --- DYNAMIC SVG LOGO ---
def display_logo():
    # A professional vector logo for "LogiTrack"
    logo_svg = """
    <svg width="200" height="60" viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 10 L50 10 L60 30 L30 30 Z" fill="#EE6C4D" />
        <path d="M30 30 L60 30 L50 50 L20 50 Z" fill="#EE6C4D" opacity="0.8" />
        <text x="70" y="42" font-family="Inter, sans-serif" font-weight="800" font-size="24" fill="#293241">LogiTrack</text>
        <text x="165" y="42" font-family="Inter, sans-serif" font-weight="400" font-size="24" fill="#EE6C4D">Pro</text>
    </svg>
    """
    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)
    return logo_svg

# --- AUTHENTICATION & INITIALIZATION ---
local_css()
auth_db.create_usertable()
DATA_KEY = 'main_data_df'

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

auth_db.create_usertable()
DATA_KEY = 'main_data_df'

# --- DATA PROCESSING FUNCTION ---
@st.cache_data
def process_and_normalize_data(df_raw, mapping):
    """
    Renames columns and calculates Status, Days Late, and Priority based on dates.
    """
    rename_dict = {v: k for k, v in mapping.items() if v != "N/A"}
    df = df_raw.rename(columns=rename_dict).copy()
    
    try:
        if "EXPECTED DELIVERY DATE" in df.columns:
            df["EXPECTED DELIVERY DATE"] = pd.to_datetime(df["EXPECTED DELIVERY DATE"], dayfirst=True, errors='coerce')
        if "ACTUAL DELIVERY DATE" in df.columns:
            df["ACTUAL DELIVERY DATE"] = pd.to_datetime(df["ACTUAL DELIVERY DATE"], dayfirst=True, errors='coerce')
        
        if "EXPECTED DELIVERY DATE" in df.columns and "ACTUAL DELIVERY DATE" in df.columns:
            # Calculate duration and status
            df["Duration"] = df["ACTUAL DELIVERY DATE"] - df["EXPECTED DELIVERY DATE"]
            df["Days Late"] = (df["Duration"].dt.total_seconds() / (60 * 60 * 24)).fillna(0)
            
            # Logic: Priority based on Days Late
            def calculate_priority(days):
                if days > 5: return "High"
                if days > 0: return "Medium"
                return "Low"
            
            # Update Priority and Status
            df["PRIORITY"] = df["Days Late"].apply(calculate_priority)
            df["Delivery Status"] = df["Duration"].apply(lambda x: "Late" if x > timedelta(days=0) else "On Time")
            
            # Handle Pending
            mask_not_delivered = df["ACTUAL DELIVERY DATE"].isna()
            df.loc[mask_not_delivered, "Delivery Status"] = "Pending"
            df.loc[mask_not_delivered, "PRIORITY"] = "Medium" # Default for pending
            
    except Exception as e:
        st.error(f"Error processing dates: {e}")
    return df

# ==========================================
# AUTHENTICATION UI
# ==========================================

if not st.session_state['logged_in']:
    st.sidebar.title("🔐 Account Access")
    choice = st.sidebar.radio("Navigation", ["Login", "Sign Up"])

    st.markdown("<h1 style='color: #EE6C4D;'>📦 Delivery Progress Tracker</h1>", unsafe_allow_html=True)
    st.markdown("Please log in to access your saved dashboard.")
    st.markdown("---")

    if choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            if auth_db.login_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                
                # --- LOAD SAVED DATA ON LOGIN ---
                saved_data, saved_filename = auth_db.get_user_data(username)
                if saved_data is not None:
                    st.session_state[DATA_KEY] = saved_data
                    st.session_state['current_file_name'] = saved_filename
                
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Sign Up":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')
        
        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            elif auth_db.check_user_exists(new_user):
                st.warning("Username already exists.")
            else:
                if auth_db.add_userdata(new_user, new_password):
                    st.success("Account created!")
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = new_user
                    st.rerun()

# ==========================================
# MAIN APP
# ==========================================
else:
    st.sidebar.title(f"👤 {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()

    st.markdown("<h1 style='color: #EE6C4D;'>📦 Delivery Progress Tracker</h1>", unsafe_allow_html=True)
    
    has_data = DATA_KEY in st.session_state
    
    if has_data:
        st.info(f"📁 **Currently Using:** `{st.session_state.get('current_file_name', 'Saved Progress')}`")
        if st.button("🔄 Upload a Different File"):
            del st.session_state[DATA_KEY]
            st.rerun()
    else:
        st.markdown("Upload a dataset to begin or resume your work.")
        uploaded_file = st.file_uploader("📂 Upload Dataset (CSV or Excel):", type=["csv", "xlsx"])

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_raw = pd.read_csv(uploaded_file)
                else:
                    df_raw = pd.read_excel(uploaded_file)
                
                # --- DATA PREVIEW (FIRST 5 ENTRIES) ---
                st.write("### 📄 Raw Data Preview (First 5 Rows)")
                st.dataframe(df_raw.head(5), use_container_width=True)
                
                with st.expander("🛠️ Column Mapping Configuration", expanded=True):
                    with st.form("mapping_form"):
                        all_cols = ["N/A"] + df_raw.columns.tolist()
                        col1, col2 = st.columns(2)
                        
                        def get_index(options, search_terms):
                            for i, opt in enumerate(options):
                                if any(term in str(opt).upper() for term in search_terms) and opt != "N/A": return i
                            return 0

                        with col1:
                            map_id = st.selectbox("ID / Order Number", all_cols, index=get_index(all_cols, ["ID", "NO", "ORDER"]))
                            map_name = st.selectbox("Product Name", all_cols, index=get_index(all_cols, ["NAME", "ITEM", "PRODUCT"]))
                            map_expected = st.selectbox("Expected Date", all_cols, index=get_index(all_cols, ["EXPECTED", "DUE"]))
                            map_actual = st.selectbox("Actual Date", all_cols, index=get_index(all_cols, ["ACTUAL", "REAL"]))
                        with col2:
                            map_agent = st.selectbox("Delivery Agent", all_cols, index=get_index(all_cols, ["AGENT", "PERSON", "DRIVER"]))
                            map_priority = st.selectbox("Priority Level", all_cols, index=get_index(all_cols, ["PRIORITY", "URGENCY"]))
                            map_status = st.selectbox("Order Status", all_cols, index=get_index(all_cols, ["STATUS"]))
                            map_notes = st.selectbox("Notes", all_cols, index=get_index(all_cols, ["NOTE", "REMARK"]))

                        if st.form_submit_button("✅ Confirm & Save"):
                            mapping = {
                                'ID NO.': map_id, 'NAME': map_name,
                                'EXPECTED DELIVERY DATE': map_expected, 'ACTUAL DELIVERY DATE': map_actual,
                                'RESPONSIBLE_PERSON': map_agent, 'PRIORITY': map_priority,
                                'STATUS': map_status, 'NOTES': map_notes
                            }
                            df_processed = process_and_normalize_data(df_raw, mapping)
                            
                            st.session_state[DATA_KEY] = df_processed
                            st.session_state['current_file_name'] = uploaded_file.name
                            auth_db.save_user_data(st.session_state['username'], df_processed, uploaded_file.name)
                            
                            st.success("Data Saved Successfully!")
                            st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    if DATA_KEY in st.session_state:
        st.page_link("pages/1_📊_Display_Data.py", label="📊 Display Data & Edit", icon="👀")
        st.page_link("pages/2_🧪_Data_Analysis.py", label="🧪 Data Analysis", icon="🔬")
        st.page_link("pages/3_📈_Graph_Plotting.py", label="📈 Graph Plotting", icon="📈")
        st.page_link("pages/4_⚠️_Tracking_Late_Delivery.py", label="⚠️ Tracking Late Deliveries", icon="🚨")
