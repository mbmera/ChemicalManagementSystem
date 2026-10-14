import pandas as pd
import streamlit as st

from database import get_active_chemicals, save_chemical


def show_chemical_register():
    st.subheader("Register a chemical")
    st.caption("Add an inventory record, then review or search active chemicals below.")

    with st.form("chemical_form"):
        product_name = st.text_input("Chemical or product name")
        manufacturer = st.text_input("Manufacturer")
        cas_number = st.text_input("CAS number (if applicable)")
        storage_location = st.text_input("Storage location")
        quantity = st.number_input("Quantity", min_value=0.0, value=0.0)
        unit = st.selectbox("Unit", ["L", "mL", "kg", "g", "pcs"])
        sds_reference = st.text_input("External SDS link or reference")

        submitted = st.form_submit_button("Register chemical")

    if submitted:
        if not product_name.strip():
            st.error("Enter a chemical or product name.")
        else:
            save_chemical(
                product_name.strip(),
                manufacturer.strip(),
                cas_number.strip(),
                storage_location.strip(),
                quantity,
                unit,
                sds_reference.strip()
            )
            st.success(f"{product_name} was saved.")

    st.divider()
    st.subheader("Active chemicals")
    st.caption("Search by product name, CAS number, or storage location.")
    
    chemicals = get_active_chemicals()

    if chemicals:
        chemical_table = pd.DataFrame(
            chemicals,
            columns=[
                "ID",
                "Product name",
                "Manufacturer",
                "CAS number",
                "Storage location",
                "Quantity",
                "Unit",
                "SDS reference"
            ]
        )
        
        search = st.text_input("Search active chemicals", placeholder="Name, CAS number, or storage location").strip()

        if search:
            matches = (
                chemical_table["Product name"].str.contains(
                    search, case=False, regex=False, na=False
                )
                | chemical_table["CAS number"].str.contains(
                    search, case=False, regex=False, na=False
                )
                | chemical_table["Storage location"].str.contains(
                    search, case=False, regex=False, na=False
                )
            )
            chemical_table = chemical_table[matches]

        st.dataframe(chemical_table, hide_index=True)
        
        
        
    else:
        st.info("No chemicals registered yet.")
