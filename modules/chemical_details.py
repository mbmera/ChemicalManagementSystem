import streamlit as st
import pandas as pd
from database import (
    get_all_chemicals,
    get_chemical_by_id,
    get_sds_versions,
    get_stock_movements,
    get_sds_review_dates,
    get_minimum_stock,
    get_chemicals_with_status
)
from datetime import date

def show_chemical_details():
    st.subheader("Chemical details")
    st.caption("Review inventory, safety data sheet status, and stock history for a chemical.")

    chemicals = get_all_chemicals()

    if not chemicals:
        st.info("No chemicals registered yet.")
        return

    choices = {
        chemical[0]: f"{chemical[1]} (ID {chemical[0]})"
        for chemical in chemicals
    }

    chemical_id = st.selectbox(
        "Select a chemical",
        options=list(choices.keys()),
        format_func=lambda selected_id: choices[selected_id]
    )

    chemical = get_chemical_by_id(chemical_id)

    if chemical is None:
        
        st.error("Chemical not found.")
        return
    
    status_by_id = {
        item[0]: item[4]
        for item in get_chemicals_with_status()
    }
    st.metric("Status", status_by_id[chemical_id])

    st.divider()
    labels = [
        "ID",
        "Product name",
        "Manufacturer",
        "CAS number",
        "Storage location",
        "Quantity",
        "Unit",
        "External SDS link or reference"
    ]

    for label, value in zip(labels, chemical):
        st.write(f"**{label}:** {value if value not in (None, '') else '—'}")
    
    current_stock = float(chemical[5] or 0)
    minimum_stock = get_minimum_stock(chemical_id)

    st.subheader("Stock status")
    st.metric("Current stock", f"{current_stock} {chemical[6]}")

    if minimum_stock > 0:
        st.write(
            f"**Low stock threshold:** {minimum_stock} {chemical[6]}"
        )

        if current_stock <= minimum_stock:
            st.warning("Stock is at or below the alert threshold.")
        else:
            st.success("Stock is above the alert threshold.")
    else:
        st.info("No low stock threshold has been set.")
    
    
     
    
    st.divider()
    st.subheader("Safety data sheet")

    sds_versions = get_sds_versions(chemical_id)

    if sds_versions:
        latest = sds_versions[0]
        st.success(
            f"Latest SDS: {latest[1]} — revision {latest[2]}"
        )
        
        st.caption(
            f"{len(sds_versions)} saved version(s). "
            "Open SDS management to view or download them."
        )
        
        
        st.subheader("SDS review status")

        for sds_id, file_name, revision_date, uploaded_at in sds_versions:
            review_dates = get_sds_review_dates(sds_id)

            st.write(f"**{file_name}** — SDS revision {revision_date}")

            if not review_dates or not review_dates[1]:
                st.warning("Review date not set.")
                continue

            last_reviewed = review_dates[0]
            review_due = date.fromisoformat(review_dates[1])
            days_remaining = (review_due - date.today()).days

            st.caption(
                f"Last reviewed: {last_reviewed or 'Not recorded'} | "
                f"Next review due: {review_due}"
            )

            if days_remaining < 0:
                st.error(f"Review overdue by {abs(days_remaining)} day(s).")
            elif days_remaining == 0:
                st.warning("Review is due today.")
            elif days_remaining <= 30:
                st.warning(f"Review due in {days_remaining} day(s).")
            else:
                st.success(f"Review due in {days_remaining} day(s).")
    else:
        st.warning("No SDS uploaded for this chemical.")

    st.divider()
    st.subheader("Stock history")

    movements = get_stock_movements(chemical_id)

    if movements:
        movement_table = pd.DataFrame(
            movements,
            columns=[
                "Recorded at",
                "Type",
                "Amount",
                "Balance after",
                "Reason"
            ]
        )
        st.caption(f"Amounts and balances are in {chemical[6]}.")
        st.dataframe(movement_table, hide_index=True)
    else:
        st.info("No stock movements recorded yet.")
