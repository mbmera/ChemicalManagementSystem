import streamlit as st

APP_VERSION = "1.0.0"

st.set_page_config(
    page_title="Chemical Management System",
    page_icon="🧪",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --cms-ink: #102b43;
        --cms-muted: #43596b;
        --cms-accent: #086b70;
        --cms-border: #c9d6e0;
        --cms-surface: #ffffff;
        --cms-background: #f6f8fa;
    }

    .stApp {
        background: var(--cms-background);
        color: var(--cms-ink);
        font-size: 1.05rem;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCaptionContainer"] {
        color: var(--cms-ink);
        font-size: 1rem;
        line-height: 1.55;
    }

    [data-testid="stSidebar"] {
        background: #e3eff8;
        border-right: 1px solid #c9d6e0;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.25rem;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--cms-ink);
        font-size: 0.98rem;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.25rem;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 0.55rem;
        padding: 0.6rem 0.7rem;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label,
    [data-testid="stSidebar"] [role="radiogroup"] label > div,
    [data-testid="stSidebar"] [role="radiogroup"] label p {
        color: var(--cms-ink);
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        line-height: 1.35;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: #edf5f5;
    }

    [data-testid="stHeader"] {
        background: rgba(245, 248, 250, 0.92);
    }

    h1, h2, h3 {
        color: var(--cms-ink);
        letter-spacing: -0.02em;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--cms-muted);
    }

    div[data-testid="stMetric"] {
        background: var(--cms-surface);
        border: 1px solid var(--cms-border);
        border-radius: 0.75rem;
        padding: 1rem 1.1rem;
    }

    div[data-testid="stForm"], div[data-testid="stExpander"] {
        border-color: var(--cms-border);
        border-radius: 0.65rem;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 0.5rem;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: var(--cms-accent);
        border-color: var(--cms-accent);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

from database import (
    create_database, 
    create_sds_table, 
    create_stock_movements_table, 
    add_chemical_status_column,
    add_minimum_stock_column,
    add_sds_review_columns
)
from modules.stock_movements import show_stock_movements
from modules.chemical_register import show_chemical_register
from modules.chemical_details import show_chemical_details
from modules.chemical_edit import show_chemical_edit
from modules.sds_management import show_sds_management
from modules.chemical_archive import show_chemical_archive
from modules.dashboard import show_dashboard

create_database()
add_chemical_status_column()
add_minimum_stock_column()
create_sds_table()
add_sds_review_columns()
create_stock_movements_table()

with st.sidebar:
    st.markdown("## 🧪 Chemical operations")
    st.caption("Laboratory inventory and safety records")
    st.caption(f"Version {APP_VERSION}")
    st.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Chemical register", "Chemical details", "Edit chemical", "SDS management", "Stock movements", "Archive / restore", "Dashboard"],
)

st.title("Chemical Management System")

if page == "Chemical register":
    show_chemical_register()
elif page == "Chemical details":
    show_chemical_details()

elif page == "Edit chemical":
    show_chemical_edit()
    
elif page == "SDS management":
    show_sds_management()
    
elif page == "Stock movements":
    show_stock_movements()
    
elif page == "Archive / restore":
    show_chemical_archive()
    
elif page == "Dashboard":
    show_dashboard()
