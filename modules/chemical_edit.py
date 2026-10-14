import streamlit as st

from database import (
    get_active_chemicals, 
    get_chemical_by_id, 
    update_chemical,
    get_minimum_stock,
    set_minimum_stock
)    


def show_chemical_edit():
    st.subheader("Edit chemical")
    st.caption("Update chemical details and its low-stock alert threshold. Use Stock movements to change quantity.")

    chemicals = get_active_chemicals()

    if not chemicals:
        st.info("No chemicals registered yet.")
        return

    choices = {
        chemical[0]: f"{chemical[1]} (ID {chemical[0]})"
        for chemical in chemicals
    }

    chemical_id = st.selectbox(
        "Select a chemical to edit",
        options=list(choices.keys()),
        format_func=lambda selected_id: choices[selected_id]
    )

    chemical = get_chemical_by_id(chemical_id)

    if chemical is None:
        st.error("Chemical not found.")
        return

    with st.form("edit_chemical_form"):
        product_name = st.text_input("Chemical or product name", value=chemical[1])
        manufacturer = st.text_input("Manufacturer", value=chemical[2] or "")
        cas_number = st.text_input("CAS number", value=chemical[3] or "")
        storage_location = st.text_input(
            "Storage location", value=chemical[4] or ""
        )
        quantity = float(chemical[5] or 0)
        unit = chemical[6]
        st.info(f"Current stock: {quantity} {unit}. Record quantity changes on the Stock movements page.")
        
        minimum_stock = st.number_input(
            f"Low stock alert threshold ({unit})",
            min_value=0.0,
            value=get_minimum_stock(chemical_id),
            step=0.1
        )
        
        

        units = ["L", "mL", "kg", "g", "pcs"]
        current_unit = chemical[6] if chemical[6] in units else "L"
        unit = st.selectbox(
            "Unit", units, index=units.index(current_unit)
        )

        sds_reference = st.text_input(
            "External SDS link or reference", value=chemical[7] or ""
        )

        submitted = st.form_submit_button("Save changes")

    if submitted:
        if not product_name.strip():
            st.error("Enter a chemical or product name.")
        else:
            
            set_minimum_stock(chemical_id, minimum_stock)
            update_chemical(
                chemical_id,
                product_name.strip(),
                manufacturer.strip(),
                cas_number.strip(),
                storage_location.strip(),
                sds_reference.strip()
            )
            st.success("Chemical updated. Open Chemical details to verify it.")
