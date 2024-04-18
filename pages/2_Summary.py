import streamlit as st
from backend import *
from manipulateData import *
import plotly.express as px

config_data = backend.load_data(r"config.json")
data = backend.load_data(r"data_update.json")
st.set_page_config(page_title="Summary", layout="wide")

st.sidebar.markdown(config_data["made_by"])
st.session_state.button_pivot_clicked = None
st.session_state.button_summary_clicked = None
if "update_df" not in st.session_state:
    st.warning("Please go to Explore page and explore the data first.", icon="🚨")
else:
    update_df = st.session_state.update_df

    tab1, tab2, tab3, tab4 = st.tabs(["Agency", "Department/Program/Unit", "Department/Program/Unit by Question", "Question Category"])

    with tab1:
        group_df = update_df.groupby("Agency")["Respondent ID"].count()
        group_df.columns = ["Agency", "Count"]
        st.dataframe(group_df)

    with tab2:
        group_df = update_df.groupby(["Respondent ID", "Start Date", "Department/Program/Unit"]).count()
        group_df = group_df.reset_index()[["Respondent ID", "Start Date", "Department/Program/Unit"]]
        st.dataframe(group_df, hide_index=True, width=600)

    with tab3:
        st.session_state.button_pivot_clicked = False 
        option = st.selectbox(
            "Choose the question you want to summarize: ",
            data["update_col_wo_comments_list"]
        )
        col_options = st.multiselect(
            "Choose the columns you want to explore: (Must select Department/Program/Unit)",
            ["Respondent ID", 
             "Collector ID", 
             "IP Address", 
             "Agency", 
             "Department/Program/Unit"],
            default="Department/Program/Unit"
        )
        button_pivot_clicked = st.button("Summarize Unit")
        if button_pivot_clicked:
            st.session_state.button_pivot_clicked = True
        if st.session_state.button_pivot_clicked:
            col1, col2 = st.columns([2,2])
            group_df = manipulateData.pivot_df(update_df, option, col_options)
            chart_prep_df = manipulateData.pivot_df(update_df, option, ["Agency", "Department/Program/Unit"])

            chart_df = chart_prep_df.iloc[:-1]
            chart_df.rename(columns={"{}".format(chart_df.columns.to_list()[2]):"Count"}, inplace=True)
            col1.dataframe(group_df, hide_index=True, width=700, height=800)
            if "Agency" in col_options:
                fig = px.bar(chart_df, x="Agency", y="Department/Program/Unit", color="Count",
                 width=1000, height=800)
                fig.update_layout(
                    yaxis_title = "Count",
                    legend_title_text='Department/Program/Unit'
                )
                col2.plotly_chart(fig, use_container_width=True)
            else: 
                col2.bar_chart(chart_df, x="Department/Program/Unit", y="Count")
            
    with tab4:
        # pass
        option = st.selectbox(
                "Choose the question category: ",
                list(data["question_category"].keys())[:-1]
            )
        button_summary_clicked = st.button("Summarize Question")
        if button_summary_clicked:
            st.session_state.button_summary_clicked = True
        tmp_df = manipulateData.get_tmp_df(update_df, data, option)
        if st.session_state.button_summary_clicked:
            df = manipulateData.get_question_df(data, data["question_columns"], tmp_df, option)
            st.subheader("Summary of Responses")
            df["Grand Total"] = df.drop(df.columns.to_list()[0], axis=1).sum(axis=1)
            st.dataframe(df, hide_index=True, width=1500)
            st.session_state["summary_df"] = df
            
            st.subheader("Analysis of Responses")
            df = manipulateData.get_percentage_df(df)
            st.dataframe(df, hide_index=True, width=1500)
            st.session_state["responses_df"] = df
            
            st.subheader("Comments Summary")
            comment_df = manipulateData.get_comment_df(update_df, data, option)
            st.dataframe(comment_df[["Respondent ID", "Response Date", "Comment"]], hide_index=True, width=1500)
            st.session_state["comments_df"] = comment_df
        
        