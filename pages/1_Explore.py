import os
import warnings
import pandas as pd
import streamlit as st
from backend import backend
from manipulateData import manipulateData
warnings.filterwarnings('ignore')

config_data = backend.load_data(r"config.json")

data = backend.load_data(r"data_update.json")

st.set_page_config(page_title="Explore", layout="wide")


st.sidebar.markdown(config_data["made_by"])


if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
    st.session_state.analyzis_done = None
    st.session_state.button_analyze_clicked = None

    

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None
    st.session_state.button_concat_clicked = None
    st.session_state.concat_done = None
    st.session_state.files_analyzis_done = None


# Set up page tabs
tab1, tab2 = st.tabs(["Analyze Single File", "Analyze Multiple Files"])



with tab1:
    st.columns((1, 2, 1))[1].warning(
        "Warning: If you used the Analyze Multiple Files function already, please REFRESH the page before uploading single files.",
        icon="🚫",
    )
    # Upload file button

    uploaded_file = st.columns((1, 2, 1))[1].file_uploader(
        ":warning: Upload One Excel File", accept_multiple_files=False, type=["xlsx"]
    )

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.analyzis_done = False
        st.session_state.button_analyze_clicked = False

    if st.session_state.uploaded_file is not None:
        uploaded_file = st.session_state.uploaded_file

        st.write('  ')
        # Check if the uploaded file is Excel extension

        if uploaded_file.type != config_data["file_type_excel"]:
            st.error(f"The extension {os.path.splitext(uploaded_file.name)[1]} is not supported")
            st.stop()
    # Analyze single Excel file

    button_analyze_clicked = st.columns((1, 2, 1))[1].button("Analyze the Document")
    if button_analyze_clicked:
        st.session_state.button_analyze_clicked = True
    if st.session_state.button_analyze_clicked:

        st.spinner("Reading data...")
        # Read and load json file

        json_file = r"data_update.json"
        data = backend.load_data(json_file)
        # Read the uploaded file

        df = pd.read_excel(uploaded_file)

        # Transform the data

        update_df = backend.transform_df(df, data)
        st.session_state["update_df"] = update_df
        # Download ExcelWriter file

        update_csv = update_df.to_csv(index=False).encode(config_data["encoding"])
        st.columns((1, 2, 1))[1].download_button(
            label="Download",
            data=update_csv,
            file_name="update_df.csv",
            mime=config_data["mime_csv"],
            key="download_button",
        )

        st.columns((1, 2, 1))[1].header("Table of Survey")
        st.columns((1, 2, 1))[1].dataframe(update_df)


with tab2:
    # Analyze multiple Excel files

    st.columns((1, 2, 1))[1].warning(
        "Warning: If you used the Analyze Single File function already, please REFRESH the page before uploading multiple files.",
        icon="🚫",
    )
    uploaded_files = st.columns((1, 2, 1))[1].file_uploader(
        ":warning: Upload Multiple Excel Files", accept_multiple_files=True, type=["xlsx"]
    )

    if uploaded_files is not None:
        st.session_state.uploaded_files = uploaded_files
        st.session_state.button_concat_clicked = False
        st.session_state.concat_done = False
        st.session_state.files_analyzis_done = False
    if st.session_state.uploaded_files is not None:
        uploaded_files = st.session_state.uploaded_files
        

        st.write('  ')
        # Check if uploaded files are Excel extensions

        for aFile in uploaded_files:
            if aFile.type != config_data["file_type_excel"]:
                st.error(f"The extension {os.path.splitext(aFile.name)[1]} is not supported")
                st.stop()
        button_concat_clicked = st.columns((1, 2, 1))[1].button("Merge and Analyze the Documents")
        if button_concat_clicked:
            st.session_state.button_concat_clicked = True
        if st.session_state.button_concat_clicked:
            with st.columns((1, 2, 1))[1].status("Merging documents"):
                st.write("Merging the documents...")
                merged_df = manipulateData.concat_dfs(uploaded_files, data)
                st.write("Documents are merged successfully.")
            st.session_state["update_df"] = merged_df
            st.columns((1, 2, 1))[1].header("Table of Survey")
            st.columns((1, 2, 1))[1].dataframe(merged_df)