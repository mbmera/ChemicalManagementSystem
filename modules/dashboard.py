import streamlit as st
from datetime import date, timedelta

from database import (
    get_active_chemicals,
    get_chemicals_with_status,
    get_sds_versions,
    get_minimum_stock,
    get_sds_review_records,
    get_sds_without_review_date
)


def show_dashboard():
    st.subheader("Chemical management dashboard")
    st.caption("A current overview of inventory coverage, stock levels, and SDS review actions.")

    active = get_active_chemicals()
    low_stock = [
        chemical for chemical in active
        if get_minimum_stock(chemical[0]) > 0
        and float(chemical[5] or 0) <= get_minimum_stock(chemical[0])
    ]
    all_chemicals = get_chemicals_with_status()

    archived_count = sum(
        1 for chemical in all_chemicals
        if chemical[4] == "Archived"
    )
    
    missing_sds = [
        chemical for chemical in active
        if not get_sds_versions(chemical[0])
    ]
    
    zero_stock = [
        chemical for chemical in active
        if float(chemical[5] or 0) == 0
    ]

    col1, col2, col3 = st.columns(3)
    col1.metric("Active chemicals", len(active))
    col2.metric("Archived chemicals", archived_count)
    col3.metric("Active without uploaded SDS", len(missing_sds))
    
    
    st.divider()
    st.subheader("Missing uploaded SDS")

    if missing_sds:
        for chemical in missing_sds:
            st.write(
                f"**{chemical[1]}** (ID {chemical[0]}) "
                f"— {chemical[4] or 'Location not entered'}"
            )
    else:
        st.success("All active chemicals have an uploaded SDS.")
        
        
    st.divider()
    st.subheader("Inventory alerts")
    st.markdown("**Active chemicals with zero stock**")

    if zero_stock:
        for chemical in zero_stock:
            st.write(f"**{chemical[1]}** (ID {chemical[0]})")
    else:
        st.success("No active chemicals have zero stock.")
        
    st.markdown("**Low stock**")

    if low_stock:
        for chemical in low_stock:
            threshold = get_minimum_stock(chemical[0])
            st.warning(
                f"{chemical[1]} (ID {chemical[0]}): "
                f"{chemical[5]} {chemical[6]} remaining; "
                #f"alert threshold is {threshold} {chemical[6]}."
                f"alert threshold is {threshold:.1f} {chemical[6]}."
            )
    else:
        st.success("No active chemicals are at or below their alert threshold.")
        
        
    st.divider()
    st.subheader("SDS reviews due soon or overdue")

    today = date.today()
    cutoff_date = today + timedelta(days=30)
    review_records = get_sds_review_records()

    review_alerts = []
    for record in review_records:
        review_due = date.fromisoformat(record[6])

        if review_due <= cutoff_date:
            review_alerts.append((record, review_due))

    if review_alerts:
        for record, review_due in review_alerts:
            chemical_name = record[2]
            file_name = record[3]

            if review_due < today:
                days_overdue = (today - review_due).days
                st.error(
                    f"{chemical_name} — {file_name}: review overdue "
                    f"by {days_overdue} day(s); due {review_due}."
                )
            elif review_due == today:
                st.warning(
                    f"{chemical_name} — {file_name}: review is due today."
                )
            else:
                days_remaining = (review_due - today).days
                st.info(
                    f"{chemical_name} — {file_name}: review due in "
                    f"{days_remaining} day(s), on {review_due}."
                )
    else:
        st.success("No SDS reviews are due in the next 30 days.")
        
        
    st.divider()
    st.subheader("SDS versions without a review date")

    unscheduled_sds = get_sds_without_review_date()

    if unscheduled_sds:
        for record in unscheduled_sds:
            sds_id, chemical_name, file_name, revision_date, uploaded_at = record
            st.warning(
                f"{chemical_name} — {file_name} "
                f"(SDS ID {sds_id}, revision {revision_date}): "
                "review date not set."
            )
    else:
        st.success(
            "All uploaded SDS versions for active chemicals "
            "have a review due date."
        )
