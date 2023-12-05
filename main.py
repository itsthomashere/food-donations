"""
Streamlit App for Food Donation Company Sign-up Form
"""

import streamlit as st

def main():
    st.title("Food Donation Company Sign-up Form")

    with st.form("sign_up_form"):
        # Organization Information
        st.subheader("Organization Information")
        org_name = st.text_input("Organization Name")
        npo_number = st.text_input("Registered NPO Number")
        npo_certificate = st.file_uploader("Upload NPO Certificate", type=['pdf', 'jpg', 'png'])
        address = st.text_area("Physical Address")
        email = st.text_input("Email Address")
        phone_number = st.text_input("Phone Number")

        # Operational Details
        st.subheader("Operational Details")
        org_type = st.selectbox("Type of Organization", ["Permanent Care Facility", "Shelter", "Orphanage", "Rehabilitation Centre", "ECD", "Seniors Club", "Other"])
        beneficiaries = st.number_input("Number of Beneficiaries Currently Assisting", min_value=0)
        activity_description = st.text_area("Description of Current Activities")
        operating_duration = st.number_input("Operating Duration in Months", min_value=0)

        # Governance and Compliance
        st.subheader("Governance and Compliance")
        board_details = st.text_area("Constitution and Governing Board Details")
        board_members = st.text_area("List of Board Members and Contact Details")
        bank_account_details = st.text_input("Bank Account Details")
        endorsement_letters = st.file_uploader("Upload Endorsement Letters", accept_multiple_files=True)

        # Food Safety and Handling
        st.subheader("Food Safety and Handling")
        food_safety_adherence = st.checkbox("Confirm Adherence to Food Safety and Health Regulations")
        equipment_details = st.text_area("Details of Equipment and Utensils for Food Preparation")

        # Record Keeping and Reporting
        st.subheader("Record Keeping and Reporting")
        record_keeping_acknowledgment = st.checkbox("Acknowledge Requirement to Keep Daily Records of Beneficiaries")
        annual_survey_agreement = st.checkbox("Agree to Complete Annual Surveys from FoodForward SA")

        # Other Commitments
        st.subheader("Other Commitments")
        non_discrimination_agreement = st.checkbox("Agree to Not Discriminate")
        no_sale_exchange_agreement = st.checkbox("Agree to Not Sell or Exchange Donated Food")
        unannounced_visits_agreement = st.checkbox("Available for Unannounced Visits by FoodForward SA")
        volunteer_provision_agreement = st.checkbox("Willing to Provide Volunteers for Annual Food Drive")

        # Agreements and Consent
        st.subheader("Agreements and Consent")
        food_handling_requirements_agreement = st.checkbox("Agree to FoodForward SA’s Minimum Food Handling Requirements")
        meeting_attendance_agreement = st.checkbox("Agree to Attend Required Meetings")
        partnership_agreement = st.checkbox("Agree to Sign FoodForward SA’s Partnership Agreement")

        # Submit Button
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Form Submitted Successfully!")

if __name__ == "__main__":
    main()

