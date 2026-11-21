from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="SolarSahayak AI",
    page_icon="☀️",
    layout="wide"
)


# SOLARSAHAYAK PROFESSIONAL THEME

st.markdown("""
<style>

/* Main dashboard background */
.stApp {
    background-color: #0B1426;
    color: #F8FAFC;
}

/* Headings */
h1, h2, h3 {
    color: #F8FAFC !important;
    font-weight: 700 !important;
}

/* Solar yellow accent */
div[data-testid="stMetricValue"] {
    color: #FACC15;
    font-weight: 700;
}

/* Metric labels */
div[data-testid="stMetricLabel"] {
    color: #CBD5E1;
}

/* Buttons */
.stButton > button {
    background-color: #FACC15;
    color: #0B1426;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #FDE047;
    color: #0B1426;
}

/* Data tables */
div[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Dividers */
hr {
    border-color: #334155;
}

/* Dashboard content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

</style>
""", unsafe_allow_html=True)


# SOLARSAHAYAK SIDEBAR NAVIGATION

with st.sidebar:
    st.title("SolarSahayak AI")
    st.caption("Rana Solar Solution")
    st.divider()

    st.subheader("Dashboard Sections")

    st.markdown("[Overview](#application-verification-overview)")
    st.markdown("[Customer Verification](#customer-document-verification)")
    st.markdown("[AI Correction Reports](#ai-powered-customer-correction-report)")
    st.markdown("[Document Analytics](#document-verification-analytics)")
    st.markdown("[Application Filters](#advanced-application-filters)")

    st.divider()

    st.info(
        "Academic prototype using synthetic data. "
        "All verification results require staff review."
    )

# Load dataset
DATA_FILE = str(Path(__file__).resolve().parent / "SolarSahayak_Dashboard_Data.xlsx")

@st.cache_data
def load_data():
    return pd.read_excel(DATA_FILE)

df = load_data()

# Dashboard title
st.title("☀️ SolarSahayak AI")
st.subheader("Rana Solar Solution")
st.write("Generative AI-Based Solar Loan Document Verification")

st.info(
    "Academic prototype using customer data. "
    "Verification results require staff review."
)

st.divider()

# Dashboard metrics
total = len(df)

document_review = (
    df["Final Verification Status"]
    .eq("DOCUMENT_REVIEW_REQUIRED")
    .sum()
)

name_review = (
    df["Final Verification Status"]
    .eq("NAME_REVIEW_REQUIRED")
    .sum()
)

ready = (
    df["Final Verification Status"]
    .eq("READY_FOR_STAFF_REVIEW")
    .sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Applications", total)
col2.metric("Document Review", document_review)
col3.metric("Name Review", name_review)
col4.metric("Staff Review Ready", ready)

st.divider()

# Verification chart
st.subheader("Application Verification Overview")

status_counts = (
    df["Final Verification Status"]
    .value_counts()
    .reset_index()
)

status_counts.columns = ["Status", "Applications"]

fig = px.bar(
    status_counts,
    x="Status",
    y="Applications",
    color="Status",
    title="Solar Loan Application Verification Status"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Customer Application Records")

st.dataframe(
    df[[
        "Application ID",
        "Customer Name (Fictional)",
        "Customer Type",
        "City",
        "Loan Amount (INR)",
        "Final Verification Status"
    ]],
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Preliminary document-status checks only. "
    "No automated loan approval or rejection."
)


st.divider()

st.header("Customer Document Verification")

# Select application
selected_id = st.selectbox(
    "Select Customer Application ID",
    df["Application ID"].tolist()
)

# Retrieve selected customer
customer = df[
    df["Application ID"] == selected_id
].iloc[0]

st.subheader("Customer Information")

col1, col2, col3 = st.columns(3)

col1.write(
    f"**Customer Name:** {customer['Customer Name (Fictional)']}"
)

col2.write(
    f"**Customer Type:** {customer['Customer Type']}"
)

col3.write(
    f"**City:** {customer['City']}"
)

st.write(
    f"**Loan Amount:** INR {customer['Loan Amount (INR)']:,.0f}"
)

st.write(
    f"**Verification Status:** {customer['Final Verification Status']}"
)

st.subheader("Document Verification Results")

missing = customer["Missing Document List"]
unreadable = customer["Unreadable Document List"]

if pd.notna(missing) and str(missing).strip():
    st.error("Missing Document Entries:")
    st.write(str(missing).replace("_", " "))

if pd.notna(unreadable) and str(unreadable).strip():
    st.warning("Unreadable Document Entries:")
    st.write(str(unreadable).replace("_", " "))

if str(customer["Name Mismatch"]).lower() == "yes":
    st.warning("Name mismatch flagged. Staff review required.")

if (
    (pd.isna(missing) or not str(missing).strip())
    and (pd.isna(unreadable) or not str(unreadable).strip())
    and str(customer["Name Mismatch"]).lower() != "yes"
):
    st.success("No recorded document problems. Staff review required.")

st.info(
    "Document issues are based on synthetic status records. "
    "Final requirements must be confirmed by staff."
)


st.divider()

st.header("AI-Powered Customer Correction Report")

st.write(
    "Generate a personalized customer correction "
    "message using Google Gemini AI."
)

# Check whether an AI report already exists
existing_report = customer.get(
    "AI Generated Correction Report"
)

if pd.notna(existing_report) and str(existing_report).strip():

    st.success("Previously Generated AI Report Available")

    st.text_area(
        "AI Correction Report",
        value=str(existing_report),
        height=300
    )

else:

    st.info(
        "No AI report has been generated for this application."
    )

    if st.button("Generate AI Correction Report"):

        from google import genai
        from google.genai import types
        # Access Gemini key through Streamlit Secrets

        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            if not api_key:
                st.error("Gemini API key is unavailable.")
                st.stop()

            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    timeout=30000
                )
            )

            prompt = f"""
You are SolarSahayak AI, an assistant for
Rana Solar Solution.

Convert this preliminary verification report
into a short, professional customer message:

{customer['Customer Correction Report']}

Instructions:
- Use simple English.
- Mention customer name and application ID.
- Explain missing and unreadable entries.
- Mention name mismatch if flagged.
- Do not invent bank requirements.
- Do not promise loan approval.
- Mention that staff must confirm requirements.
- Keep the message under 150 words.
"""

            with st.spinner("Generating AI report..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )

            if response.text:

                # PERMANENT AI REPORT STORAGE
                report_text = response.text

                st.session_state[
                    f"report_{selected_id}"
                ] = report_text

                # Update the matching application
                df.loc[
                    df["Application ID"] == selected_id,
                    "AI Generated Correction Report"
                ] = report_text

                # Save to Google Drive
                try:
                    # Public deployment: no permanent Excel writes
                    st.info(
                        "Report generated for this session. "
                        "Use the download button to save a copy."
                    )
                except Exception as save_error:
                    st.warning(
                        f"Report generated but not saved: {save_error}"
                    )

                st.success("AI Report Generated Successfully!")

                st.text_area(
                    "Generated Customer Message",
                    value=response.text,
                    height=300
                )

            else:
                st.warning("Gemini returned an empty response.")

        except Exception as e:
            st.error(f"Gemini API Error: {e}")

st.caption(
    "AI-generated messages are drafts and require "
    "staff approval before being sent to customers."
)


# Download AI correction report
session_report = st.session_state.get(
    f"report_{selected_id}"
)

saved_report = customer.get(
    "AI Generated Correction Report"
)

report_to_download = (
    session_report
    if session_report
    else saved_report
)

if pd.notna(report_to_download) and str(report_to_download).strip():

    st.download_button(
        label="Download AI Correction Report",
        data=str(report_to_download),
        file_name=f"SolarSahayak_{selected_id}_Report.txt",
        mime="text/plain",
        key=f"download_{selected_id}"
    )


st.divider()
st.header("Document Verification Analytics")

st.write(
    "Analyze missing and unreadable document entries "
    "across all customer applications."
)

# Document columns
doc_cols = [
    "BANK_STATEMENT",
    "ELECTRICITY_BILL_INFO",
    "FORM16_2Y",
    "ITR_2Y",
    "KYC_ADDRESS",
    "KYC_ID",
    "OWNER_AADHAAR",
    "OWNER_BANK_PROOF",
    "OWNER_EMAIL",
    "OWNER_HOME_LOCATION",
    "OWNER_MOBILE",
    "PAN",
    "SBI_SAVINGS_ACCOUNT_PROOF",
    "SITE_FEASIBILITY",
    "VENDOR_CUSTOMER_AGREEMENT",
    "VENDOR_QUOTATION"
]

# Calculate document issue counts
document_analysis = pd.DataFrame({
    "Document": doc_cols,
    "Missing": [
        df[col].eq("Missing").sum()
        for col in doc_cols
    ],
    "Unreadable": [
        df[col].eq("Unreadable").sum()
        for col in doc_cols
    ]
})

# Display chart
fig_docs = px.bar(
    document_analysis,
    x="Document",
    y=["Missing", "Unreadable"],
    barmode="group",
    title="Missing and Unreadable Entries by Document Type"
)

fig_docs.update_layout(
    xaxis_tickangle=-45,
    height=550
)

st.plotly_chart(
    fig_docs,
    use_container_width=True
)

st.subheader("Document Issue Summary")

st.dataframe(
    document_analysis,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Counts represent recorded document issues, "
    "not confirmed mandatory-document deficiencies."
)


st.divider()

st.header("Advanced Application Filters")

st.write(
    "Filter customer applications by employment type, "
    "city, and verification status."
)

# Filter controls
col1, col2, col3 = st.columns(3)

with col1:
    selected_type = st.selectbox(
        "Customer Type",
        ["All"] + sorted(df["Customer Type"].dropna().unique().tolist())
    )

with col2:
    selected_city = st.selectbox(
        "City",
        ["All"] + sorted(df["City"].dropna().unique().tolist())
    )

with col3:
    selected_status = st.selectbox(
        "Verification Status",
        ["All"] + sorted(
            df["Final Verification Status"].dropna().unique().tolist()
        )
    )

# Apply selected filters
filtered_df = df.copy()

if selected_type != "All":
    filtered_df = filtered_df[
        filtered_df["Customer Type"] == selected_type
    ]

if selected_city != "All":
    filtered_df = filtered_df[
        filtered_df["City"] == selected_city
    ]

if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["Final Verification Status"] == selected_status
    ]

# Display filtered results
st.metric(
    "Applications Matching Filters",
    len(filtered_df)
)

st.dataframe(
    filtered_df[[
        "Application ID",
        "Customer Name (Fictional)",
        "Customer Type",
        "City",
        "Loan Amount (INR)",
        "Final Verification Status"
    ]],
    use_container_width=True,
    hide_index=True
)




# STEP 4.6.3 - FILTERED EXCEL DOWNLOAD

from io import BytesIO

export_columns = [
    "Application ID",
    "Customer Name (Fictional)",
    "Customer Type",
    "City",
    "State",
    "Loan Amount (INR)",
    "Missing Document List",
    "Unreadable Document List",
    "Name Mismatch",
    "Final Verification Status"
]

# Prepare Excel file in memory
excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    filtered_df[export_columns].to_excel(
        writer,
        sheet_name="Verification Results",
        index=False
    )

excel_buffer.seek(0)

st.download_button(
    label="Download Filtered Applications (Excel)",
    data=excel_buffer.getvalue(),
    file_name="SolarSahayak_Filtered_Applications.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    key="filtered_excel_download"
)

st.caption(
    "Export contains synthetic application data and "
    "preliminary verification results, not bank decisions."
)


# CUSTOMER DOCUMENT CHECKLIST

st.divider()
st.header("Customer Document Checklist")

st.write(
    "Review the recorded status of each document "
    "for the selected customer."
)

checklist_rows = []

for doc in doc_cols:

    status = str(customer[doc]).strip()

    if status == "Received":
        action = "No issue recorded"

    elif status == "Missing":
        action = "Confirm requirement and request if applicable"

    elif status == "Unreadable":
        action = "Request clearer information or document"

    elif status == "Not recorded":
        action = "Check whether this item is applicable"

    else:
        action = "Manual review required"

    checklist_rows.append({
        "Document": doc.replace("_", " ").title(),
        "Status": status,
        "Suggested Action": action
    })

checklist_df = pd.DataFrame(checklist_rows)

st.dataframe(
    checklist_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Checklist is based on synthetic document-status "
    "records. Staff must confirm applicable bank requirements."
)


# STAFF REVIEW RECOMMENDATIONS

st.divider()
st.header("Staff Review Recommendations")

recommendations = []

# Check missing documents
missing_docs = [
    doc for doc in doc_cols
    if str(customer[doc]).strip() == "Missing"
]

if missing_docs:
    recommendations.append(
        "Confirm whether the missing items are required "
        "under the applicable bank checklist before "
        "requesting them from the customer."
    )

# Check unreadable documents
unreadable_docs = [
    doc for doc in doc_cols
    if str(customer[doc]).strip() == "Unreadable"
]

if unreadable_docs:
    recommendations.append(
        "Review unreadable entries and request clearer "
        "copies or information where applicable."
    )

# Check name mismatch
if str(customer["Name Mismatch"]).strip().lower() == "yes":
    recommendations.append(
        "Manually verify the recorded name discrepancy "
        "against the relevant documents."
    )

# Check credit review flag
if str(customer["Credit Review"]).strip() == "BANK_REVIEW_REQUIRED":
    recommendations.append(
        "Refer the application for bank credit review. "
        "Do not automatically approve or reject the loan."
    )

# Check not-recorded statuses
not_recorded_docs = [
    doc for doc in doc_cols
    if str(customer[doc]).strip() == "Not recorded"
]

if not_recorded_docs:
    recommendations.append(
        "Check whether unrecorded document categories "
        "are applicable to this application."
    )

# No recorded problems
if not recommendations:
    recommendations.append(
        "No recorded verification issues identified. "
        "Proceed with staff review before bank submission."
    )

# Display recommendations
for number, recommendation in enumerate(
    recommendations, start=1
):
    st.write(f"{number}. {recommendation}")

st.info(
    "These are rule-based staff recommendations, "
    "not AI-generated credit decisions or bank approvals."
)


# CUSTOMER VERIFICATION SUMMARY

st.divider()
st.header("Customer Verification Summary")

# Count recorded document issues
missing_count = sum(
    str(customer[doc]).strip() == "Missing"
    for doc in doc_cols
)

unreadable_count = sum(
    str(customer[doc]).strip() == "Unreadable"
    for doc in doc_cols
)

not_recorded_count = sum(
    str(customer[doc]).strip() == "Not recorded"
    for doc in doc_cols
)

name_mismatch = (
    str(customer["Name Mismatch"]).strip().lower() == "yes"
)

# Display summary metrics
c1, c2, c3, c4 = st.columns(4)

c1.metric("Missing Entries", missing_count)
c2.metric("Unreadable Entries", unreadable_count)
c3.metric("Not Recorded", not_recorded_count)
c4.metric(
    "Name Mismatch",
    "Yes" if name_mismatch else "No"
)

st.subheader("Recommended Next Action")

if missing_count > 0 or unreadable_count > 0:
    st.warning(
        "Document review required. Confirm applicable "
        "requirements and resolve recorded document issues."
    )

elif name_mismatch:
    st.warning(
        "Name verification required. Staff should "
        "investigate the recorded discrepancy."
    )

else:
    st.success(
        "No recorded document problems or name mismatch. "
        "Proceed to staff review."
    )

# Independent credit review warning
if str(customer["Credit Review"]).strip() == "BANK_REVIEW_REQUIRED":
    st.warning(
        "Separate bank credit review is required. "
        "This is not an automated loan rejection."
    )

st.caption(
    "Summary is based on synthetic application records. "
    "Final requirements and eligibility must be confirmed "
    "by authorized staff and the partner bank."
)
