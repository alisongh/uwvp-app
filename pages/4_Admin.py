import json
import pandas as pd
import streamlit as st
from backend import backend

config_data = backend.load_data(r"config.json")
data = backend.load_data(r"data_update.json")
agency_df = pd.DataFrame(data["agency_list"], columns=["Agency"])
question_category_df = pd.DataFrame(
    list(data["question_category"].keys())[:-1], columns=["Category"]
)

st.session_state["agency_df"] = agency_df
agency_list = data["agency_list"]
agency_index = 0

st.set_page_config(page_title="Admin", layout="wide")

st.sidebar.markdown(config_data["made_by"])
st.session_state.button_change_agency_clicked = None


if "update_df" not in st.session_state:
    st.warning("Please go to Explore page and explore the data first.", icon="🚨")
else:
    update_df = st.session_state.update_df
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Agencies")
        st.metric(label="Number of Agencies", value=len(data["agency_list"]))
        with st.expander("See Data"):
            st.data_editor(agency_df, width=550, height=550, hide_index=True, num_rows="dynamic")
        # Get the original agency list
        agency_option = st.selectbox("Choose the agency you want to change: ", agency_list)
        new_agency_input = st.text_input("Type in the new agency name: ")

        # Find out the index of the selected agency in the json data
        for i in range(len(agency_list)):
            if agency_option in agency_list[i]:
                agency_index = i
        st.write("The updated agency is ", new_agency_input)
        button_change_agency_clicked = st.button("Change Agency")
        if button_change_agency_clicked:
            st.session_state.button_change_agency_clicked = True
        if st.session_state.button_change_agency_clicked:
            # Open and read the json data
            with open("data_update.json", "r", encoding="cp866") as file:
                json_data = json.load(file)
                file.close()
            # Change the selected agency value to the new value
            json_data["agency_list"][agency_index] = str(new_agency_input)
            # Load and save the json data
            with open("data_update.json", "w+", encoding="cp866") as file:
                file.write(json.dumps(json_data))

            st.write("The agency is updated. Please refresh the page to see the update.")
            agency_df = pd.DataFrame(data["agency_list"], columns=["Agency"])
            st.session_state.agency_df = agency_df

    with col2:
        st.header("Question Categories")
        st.metric(label="Number of Categories", value=len(data["question_category"]))
        with st.expander("See Data"):
            st.data_editor(
                question_category_df, width=550, height=550, hide_index=True, num_rows="dynamic"
            )

    with col3:
        st.header("Responses")
        st.metric(label="Number of Responses", value=len(update_df["Respondent ID"]))
        with st.expander("See Data"):
            st.data_editor(
                update_df[["Respondent ID", "IP Address"]],
                width=550,
                height=550,
                hide_index=True,
                num_rows="dynamic",
            )
    st.divider()
    col4, _, _ = st.columns(3)
    with col4:
        st.header("Questions")
        question_df = data["update_col_wo_comments_list"]
        st.metric(label="Number of Questions", value=len(question_df))
        with st.expander("See Data"):
            st.data_editor(
                question_df,
                column_config={
                    "widgets": st.column_config.TextColumn(
                        "Questions",
                        help="List of Questions in the survey 🎈",
                        width="large",
                        required=True,
                )},
                height=550,
                hide_index=True,
                num_rows="dynamic",
            )