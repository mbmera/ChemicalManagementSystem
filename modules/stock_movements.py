import streamlit as st
import pandas as pd

from database import (
    get_active_chemicals,
    get_stock_movements,
    record_stock_movement
)


def show_stock_movements():
    st.subheader("Stock movements")
    st.caption("Record received, used, or disposed stock. Every movement updates the chemical balance and history.")

    chemicals = get_active_chemicals()

    if not chemicals:
        st.info("Register a chemical first.")
        return

    choices = {
        chemical[0]: f"{chemical[1]} (ID {chemical[0]})"
        for chemical in chemicals
    }

    chemical_id = st.selectbox(
        "Chemical",
        options=list(choices.keys()),
        format_func=lambda selected_id: choices[selected_id]
    )

    selected = next(
        chemical for chemical in chemicals
        if chemical[0] == chemical_id
    )

    st.metric("Current balance", f"{selected[5]} {selected[6]}")

    with st.form("stock_movement_form"):
        movement_type = st.radio(
            "Movement type",
            ["Receive", "Use", "Dispose"],
            horizontal=True
        )
        amount = st.number_input(
            f"Amount ({selected[6]})",
            min_value=0.01,
            value=1.0,
            step=0.01
        )
        reason = st.text_input("Reason or reference")
        submitted = st.form_submit_button("Record movement")

    if submitted:
        try:
            new_balance = record_stock_movement(
                chemical_id,
                movement_type,
                amount,
                reason
            )
            st.success(
                f"{movement_type} recorded. New balance: "
                f"{new_balance} {selected[6]}"
            )
        except ValueError as error:
            st.error(str(error))
            
    st.divider()
    st.subheader("Movement history")
    st.caption(f"Amounts and balances are in {selected[6]}.")

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
        st.dataframe(movement_table, hide_index=True)
    else:
        st.info("No stock movements recorded yet.")
