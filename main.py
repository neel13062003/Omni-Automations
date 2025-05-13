import streamlit as st

st.set_page_config(page_title="Tata Tele WhatsApp Tools", layout="centered")

st.title("📲 Tata Tele WhatsApp Template Tools")

st.markdown("### Select a tool below:")
col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Open Template Checker"):
        st.switch_page("pages/st1.py")

with col2:
    if st.button("📩 Open Template Creator"):
        st.switch_page("pages/st2.py")
