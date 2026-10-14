from datetime import date

import streamlit as st

from database import (
    delete_sds,
    get_all_chemicals,
    get_sds_file,
    get_sds_versions,
    save_sds,
    get_sds_review_dates,
    update_sds_review_dates
)


def show_sds_management():
    st.subheader("Safety data sheets")
    st.caption("Upload, review, download, and manage SDS versions for registered chemicals.")

    chemicals = get_all_chemicals()

    if not chemicals:
        st.info("Register a chemical before uploading an SDS.")
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

    with st.form("upload_sds_form"):
        revision_text = st.text_input(
            "SDS revision date (YYYY-MM-DD)",
            placeholder="2026-09-27"
        )
        uploaded_file = st.file_uploader(
            "Choose an SDS PDF",
            type=["pdf"]
        )
        submitted = st.form_submit_button("Upload SDS")

    if submitted:
        try:
            revision_date = date.fromisoformat(revision_text.strip())

            if uploaded_file is None:
                st.error("Choose a PDF file.")
                return

            save_sds(
                chemical_id,
                uploaded_file.name,
                revision_date.isoformat(),
                uploaded_file.getvalue()
            )
            st.success("SDS uploaded and saved.")

        except ValueError as error:
            st.error(
                "Enter a valid revision date in YYYY-MM-DD format. "
                f"Details: {error}"
            )
            
    st.divider()
    st.subheader("Saved SDS versions")

    versions = get_sds_versions(chemical_id)

    if not versions:
        st.info("No SDS has been uploaded for this chemical yet.")
    else:
        for sds_id, file_name, revision_date, uploaded_at in versions:
            st.write(
                f"**Revision:** {revision_date} | "
                f"**File:** {file_name} | "
                f"**Uploaded:** {uploaded_at}"
            )

            review_dates = get_sds_review_dates(sds_id)

            if review_dates is None:
                st.error("Could not find this SDS version.")
            else:
                last_reviewed = review_dates[0] or ""
                review_due = review_dates[1] or ""

                with st.form(f"review_sds_form_{sds_id}"):
                    last_reviewed_input = st.text_input(
                        "Last reviewed (YYYY-MM-DD)",
                        value=last_reviewed,
                        placeholder="2026-09-29",
                        key=f"last_reviewed_{sds_id}"
                    )
                    review_due_input = st.text_input(
                        "Next review due (YYYY-MM-DD)",
                        value=review_due,
                        placeholder="2027-09-29",
                        key=f"review_due_{sds_id}"
                    )
                    review_submitted = st.form_submit_button(
                        "Save review dates"
                    )

                if review_submitted:
                    try:
                        last_reviewed_date = date.fromisoformat(
                            last_reviewed_input.strip()
                        )
                        review_due_date = date.fromisoformat(
                            review_due_input.strip()
                        )

                        if review_due_date < last_reviewed_date:
                            st.error(
                                "The next review date cannot be earlier "
                                "than the last reviewed date."
                            )
                        else:
                            update_sds_review_dates(
                                sds_id,
                                last_reviewed_date.isoformat(),
                                review_due_date.isoformat()
                            )
                            st.success("SDS review dates saved.")
                            st.rerun()

                    except ValueError:
                        st.error(
                            "Enter both dates in YYYY-MM-DD format."
                        )
            
            
            sds_file = get_sds_file(sds_id)

            if sds_file:
                st.download_button(
                    label=f"Download SDS version {sds_id}",
                    data=sds_file[1],
                    file_name=sds_file[0],
                    mime="application/pdf",
                    key=f"download_sds_{sds_id}"
                )
                
        
            with st.expander("Remove an uploaded SDS version"):
                version_names = {
                    version[0]: f"{version[1]} — revision {version[2]} (ID {version[0]})"
                    for version in versions
                }
                with st.form(f"delete_sds_form_{sds_id}"):
                #with st.form("delete_sds_form"):
                    selected_sds_id = st.selectbox(
                        "SDS version to remove",
                        options=list(version_names.keys()),
                        format_func=lambda sds_id: version_names[sds_id]
                    )
                    confirmed = st.checkbox(
                        "I understand this permanently deletes the selected PDF"
                    )
                    delete_submitted = st.form_submit_button(
                        "Delete selected SDS"
                    )

                if delete_submitted:
                    if not confirmed:
                        st.error("Tick the confirmation box before deleting.")
                    elif delete_sds(selected_sds_id, chemical_id):
                        st.success("SDS version deleted.")
                        st.rerun()
                    else:
                        st.error("The selected SDS version was not found.")
