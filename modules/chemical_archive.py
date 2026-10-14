import streamlit as st

from database import (
    archive_chemical,
    get_chemicals_with_status,
    restore_chemical,
)


def show_chemical_archive():
    st.subheader("Archive or restore chemical")
    st.caption("Archived chemicals remain in the system and can be restored later.")

    chemicals = get_chemicals_with_status()

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

    selected = next(
        chemical for chemical in chemicals
        if chemical[0] == chemical_id
    )

    status_col, balance_col = st.columns(2)
    status_col.metric("Status", selected[4])
    balance_col.metric("Current balance", f"{selected[2]} {selected[3]}")

    if selected[4] == "Active":
        with st.form("archive_form"):
            confirmed = st.checkbox(
                "I confirm this chemical should be archived"
            )
            submitted = st.form_submit_button("Archive chemical")

        if submitted:
            if not confirmed:
                st.error("Tick the confirmation box first.")
            else:
                try:
                    archive_chemical(chemical_id)
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    else:
        if st.button("Restore chemical"):
            try:
                restore_chemical(chemical_id)
                st.rerun()
            except ValueError as error:
                st.error(str(error))
