import streamlit as st
import requests

token = st.secrets["tata_tele"]["crud"]

st.set_page_config(page_title="Tata Tele WhatsApp Template Creator", layout="centered")

st.title("📩 WhatsApp Template Creator - Tata Tele")

# User input form
with st.form("template_form"):
    st.subheader("📝 Template Details")

    template_name = st.text_input("Template Name", "reminder_01_05_09_010113")
    language = st.selectbox("Language", ["hi", "en", "gu", "ta", "te"])
    category = st.selectbox("Category", ["UTILITY", "TRANSACTIONAL", "MARKETING"])
    body_text = st.text_area(
        "Template Body",
        "{{1}} session is scheduled for {{2}}.\n\n*Meeting* link:\n{{3}}"
    )

    st.subheader("🔧 Example Values for Variables")
    var1 = st.text_input("Value for {{1}}", "MSME Work")
    var2 = st.text_input("Value for {{2}}", "3 PM")
    var3 = st.text_input("Value for {{3}}", "https://example.com")

    submitted = st.form_submit_button("Create Template")

if submitted:
    st.info("Sending request to Tata Tele API...")

    headers = {
        "accept": "application/json",
        "Authorization": token,  # 🔐 Replace with actual token or secure it using st.secrets
        "Content-Type": "application/json"
    }

    payload = {
        "name": template_name,
        "language": language,
        "category": category,
        "allowCategoryChange": False,
        "components": [
            {
                "type": "BODY",
                "text": body_text,
                "example": {
                    "body_text": [[var1, var2, var3]]
                }
            }
        ]
    }

    try:
        response = requests.post(
            "https://wb.omni.tatatelebusiness.com/templates",
            json=payload,
            headers=headers
        )

        if response.status_code in (200, 201):
            st.success("✅ Template created successfully!")
            st.json(response.json())
        else:
            st.error(f"❌ Failed to create template. Status code: {response.status_code}")
            st.code(response.text, language="json")
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
