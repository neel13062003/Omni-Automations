import streamlit as st
import requests
from streamlit_tags import st_tags
import pandas as pd
import json
from io import StringIO

# Fetch template data from API
def fetch_templates():
    url = "https://api.omni.tatatelebusiness.com/template-messages/653f568b132edefedf54baed/templates-name?channel=whatsappBSP&excludedTypes=orderStatus"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzE4OTQyMDg4M2U4ZTgwMzk0MGI1YTQiLCJhY2Nlc3MiOiJhdXRoIiwiZGV2aWNlIjoid2ViQXBwIiwiaWF0IjoxNzQ3MTE1MzQ1LCJleHAiOjE3NDczNzQ1NDV9.Xy2RG4vYlkeMHimoIjPkAFiZ7Bqecm6CIhZkJoEH7bL_Tl-qzf3gHwhqFka1WL4duOdq192qoB_X1gHmT_8N1PT1BXsHtD9RVyjeFx-z2guCgDsCXlvVBG-9-3Ys_c_z-Zpm7AKMigFjl6S0P8vh78up7bjmUK7RSRNklODSHfnkdCOO3xVqlo1F3NCR-emvCCydJV_25uVlFqdZ47nRkf6K49Fw8fMhEE0WiLjtcQN3lfUVTWHqlQ37sjwxQ2sH_1s1SNyDG2H7w_G0rvFnhv_uXwQgNFOkL5CLlmNP2yfW4F_S5zzbCAknNPkEAt9oPTPqOEo4jO8_bvyVJy67k4SGB-f81dPFB1WWSIm2985bvXE1BYj4whN0KbQGdRm2ZAdV7JEEkvO4UKg8pXz38bg5-QdcPb98Q_GSHGEjX5pc5d0LmM-nQGg5V5YhAM1yroo_9t_K47viH0OTfe4tAler2oQuE-NHSX1SoH1HyYKZyqQDulb8xue9LK9qzGE_RDhtrlNy7L4Kw2vFZ6S2n96trTj-iq00BDhEZCwAS89vcv-siC1o6QvATwEN2jrGHIFZfIfdG8AQluK6RSoBvGJrrVPtibLBdaE2_H792cC2ka6yh2Skm-ZfcNP2eK9q2isZQdw15y3YI02fwI-hGHDlA3HmtWGlsGjYdhucYCU",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://omni.tatatelebusiness.com",
        "Referer": "https://omni.tatatelebusiness.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        return []


st.set_page_config(page_title="WhatsApp Template Checker", layout="wide")
st.title("📋 WhatsApp Template Status Checker")
st.caption("Search for multiple template names with tag-based or list input. Automatically bifurcates into UTILITY & MARKETING.")

# Input text for bulk template names
input_text = st.text_area("Paste list of template names (JSON array format):", height=100, placeholder='["template_1", "template_2", "template_3"]')

# Initialize
parsed_list = []
tags = []
combined_templates = []

# Parse pasted templates
if input_text.strip():
    try:
        parsed_list = json.loads(input_text)
        if not isinstance(parsed_list, list):
            st.error("Input must be a JSON list.")
            parsed_list = []
    except json.JSONDecodeError:
        st.error("Invalid list format. Use proper JSON array syntax.")
        parsed_list = []

# Manual tag input
tags = st_tags(
    label='Or enter template names manually:',
    text='Press enter to add more',
    value=[],
    suggestions=[],
    maxtags=50,
    key='1'
)

# Combine both inputs
combined_templates = list(set(tags + parsed_list))

# Sidebar Filters
st.sidebar.header("Filter Options")
filter_type = st.sidebar.multiselect("Type", options=["text", "interactive", "media"])
filter_category = st.sidebar.multiselect("Category", options=["MARKETING", "UTILITY", "OTP", "TRANSACTIONAL"])
filter_language = st.sidebar.multiselect("Language Code", options=["en", "hi", "gu", "mr", "ta", "te"])

# Fetch and display on button click
if st.button("Fetch Templates"):
    if not combined_templates:
        st.warning("Please enter at least one template name.")
    else:
        with st.spinner("Fetching templates..."):
            all_templates = fetch_templates()
            matched = []

            for name in combined_templates:
                name = name.lower()
                matches = [t for t in all_templates if name in t.get('name', '').lower()]
                matched.extend(matches)

        # Apply Filters
        if filter_type:
            matched = [t for t in matched if t.get('type') in filter_type]
        if filter_category:
            matched = [t for t in matched if t.get('category') in filter_category]
        if filter_language:
            matched = [t for t in matched if any(lang.get("languageCode") in filter_language for lang in t.get("languages", []))]

        if matched:
            st.success(f"✅ Found {len(matched)} matching templates after filtering.")

            # Bifurcate
            utility_templates = [t for t in matched if t.get('category') == 'UTILITY']
            marketing_templates = [t for t in matched if t.get('category') == 'MARKETING']

            st.subheader("UTILITY Templates")
            utility_names = [t['name'] for t in utility_templates]
            st.code(json.dumps(utility_names, indent=2))

            st.subheader("MARKETING Templates")
            marketing_names = [t['name'] for t in marketing_templates]
            st.code(json.dumps(marketing_names, indent=2))

            # Show all templates
            st.subheader("All Matched Templates")
            for i, template in enumerate(matched, 1):
                st.markdown(f"**{i}. {template.get('name', 'Unnamed')}**")
                st.json(template)

            # DataFrame for export
            def to_df(data):
                return pd.DataFrame([
                    {
                        "name": t["name"],
                        "type": t["type"],
                        "category": t["category"],
                        "languages": ", ".join([lang["languageCode"] for lang in t.get("languages", [])])
                    }
                    for t in data
                ])

            # Export buttons
            if matched:
                st.download_button("⬇️ Download All (CSV)", to_df(matched).to_csv(index=False), "matched_templates.csv", "text/csv")
                st.download_button("⬇️ Download All (JSON)", json.dumps(matched, indent=2), "matched_templates.json", "application/json")
            if utility_templates:
                st.download_button("⬇️ Download UTILITY Only (CSV)", to_df(utility_templates).to_csv(index=False), "utility_templates.csv", "text/csv")
            if marketing_templates:
                st.download_button("⬇️ Download MARKETING Only (CSV)", to_df(marketing_templates).to_csv(index=False), "marketing_templates.csv", "text/csv")
        else:
            st.info("⚠️ No matching templates found.")