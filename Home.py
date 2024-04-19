import streamlit as st
from backend import *
from string import Template


config_data = backend.load_data(r"config.json")
st.set_page_config(page_title="Survey Data Analysis Application")
st.markdown("# <div style='text-align: center;'>Survey Data Analysis Application</div>", 
            unsafe_allow_html=True)
st.divider()
with open("Home.md", "r") as file:
    st.markdown(file.read())

st.sidebar.markdown(config_data["made_by"])

template = Template("  - intent: $intent\n    examples : |\n$examples")

