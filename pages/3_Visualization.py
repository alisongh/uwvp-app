import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from backend import *
from manipulateData import *
import warnings

warnings.filterwarnings('ignore')

config_data = backend.load_data(r"config.json")
data = backend.load_data(r"data_update.json")
st.set_page_config(page_title="Visualization", layout="wide")

st.sidebar.markdown(config_data["made_by"])

if "update_df" not in st.session_state:
    st.warning("Please go to Explore page and explore the data first.", icon="🚨")
else:
    update_df = st.session_state.update_df
    tab1, tab2 = st.tabs(["Comments WordCloud", "Charts"])
    with tab1:
        option_list = list(data["comment_category"].keys())
        option = st.columns((1,2,1))[1].selectbox(
            "Choose the comment you want to display",
            option_list
        )
        comment_df = update_df[data["question_category"]["comments"]]
        sub_comment_df = comment_df[data["comment_category"][option][0]]
        comment_string = "".join(sub_comment_df)
        print(len(comment_string))
        if len(comment_string) != 0:
            fig, ax = plt.subplots()
            wc = WordCloud(width = 600,
                        height = 300,
                        background_color = "white", 
                        colormap = "magma",
                        max_words=55)
            
            wc.generate(comment_string)
            
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            plt.show()
            
            st.columns((1,2,1))[1].pyplot(fig)
        else: 
            st.columns((1,2,1))[1].warning("There is no comment in this category.", icon="🚨")
    with tab2:
        option = st.selectbox(
                "Choose the question category: ",
                list(data["question_category"].keys())[:-1]
            )
        tmp_df = manipulateData.get_tmp_df(update_df, data, option)
        question_df = manipulateData.get_question_df(data, data["question_columns"], tmp_df, option)
        questions = question_df["Questions"]
        categories = question_df.columns[1:-1]
        fig = go.Figure()
        fig = make_subplots(rows=1, cols=len(question_df))

        # Adding traces for each question
        for i, question in enumerate(question_df['Questions']):
            values = question_df.loc[question_df['Questions'] == question, categories].values.flatten()
            text_values = [str(val) if val != 0 else "0" for val in values]  # Replace zero values with "0"
            trace = go.Bar(
                x=categories,
                y=values,
                text=text_values,
                textposition='auto',
                name=question
            )
            fig.add_trace(trace, row=1, col=i+1)

        fig.update_layout(
            title='Grouped Bar Chart',
            barmode='group',
            autosize=False,
            legend=dict(x=0, y=-1, font=dict(size=14)),
            width=1800,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
