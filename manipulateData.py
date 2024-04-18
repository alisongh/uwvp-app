from backend import *
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

class manipulateData():
    def __init__(self):
        pass
    def read_files(self, json_file, excel_file):
        """
        Reads data from a JSON file and an Excel file.

        Parameters
        ----------
        json_file : str
            Path to the JSON file.
        excel_file : str
            Path to the Excel file.

        Returns
        -------
        Tuple[Dict, pd.DataFrame]
            A tuple containing the data from the JSON file and the Excel file.
        """
        print("Reading json data...")
        # Load data from JSON file
        data = backend.load_data(json_file)
        print("Json data is loaded.")
        print("Reading excel data...")
        # Load data from Excel file
        df = pd.read_excel(excel_file)
        print("Excel data is loaded.")
        return data, df
    
    @classmethod
    def pivot_df(self, df, question, cols):
        groupby_df = df.groupby(cols)[question].count().reset_index()
        
        groupby_df.loc[len(groupby_df)] = groupby_df.sum(numeric_only=True)
        groupby_df.loc[len(groupby_df)-1, "Department/Program/Unit"] = "Grand Total"
        return groupby_df
    
    @classmethod
    def get_tmp_df(self, df, data, category):
        tmp_col = data["question_category"][category]
        tmp_col.insert(0, "Respondent ID")
        tmp_df = df[tmp_col]
        return tmp_df
    
    @classmethod
    def get_question_df(self, data, columns, df, category):
        """
        This function takes in a dataframe df, a list of columns, and a category, and returns a dataframe with the count of unique responses for each question in the given category.

        Parameters:
        columns (list): a list of column names, where the first element is the question number
        df (pandas.DataFrame): a dataframe containing the responses
        category (str): the category of questions to be included in the summary

        Returns:
        pandas.DataFrame: a dataframe with the question number, question text, and count of unique responses for each question in the given category

        """
        new_data = []
        for i in range(1, len(data["question_category"][category])):
            tmp_df = df.groupby(data["question_category"][category][i])["Respondent ID"].count().reset_index(name="Count")
            col_qlist = tmp_df.columns.to_list()
            for aCol in columns[1:]:
                if aCol not in list(tmp_df[col_qlist[0]]):
                    tmp_df.loc[-1] = [aCol, 0]
                    tmp_df.index = tmp_df.index + 1
                    tmp_df = tmp_df.reset_index(drop=True)
                    tmp_df = tmp_df.sort_values(col_qlist[0])
                # If a user skipped the question
                # then the answer should be N/A to My Role
                if tmp_df.iloc[0][0] == "":
                    tmp_df.loc[0, tmp_df.columns[0]] = "N/A to My Role"
                    tmp_df = tmp_df.groupby(tmp_df.columns[0])["Count"].sum().reset_index()

            question_data = [col_qlist[0]] + list(tmp_df["Count"])
            new_data.append(question_data)
        question_summary_df = pd.DataFrame(new_data, columns=columns)
        question_summary_df = question_summary_df.loc[:, ~question_summary_df.columns.duplicated()]
        return question_summary_df
    
    @classmethod
    def get_percentage_df(self, df):
        col = df.columns.difference([df.columns.to_list()[0], "Grand Total"])
        df[col] = (df[col].div(df["Grand Total"], axis=0).mul(100))
        df["Total Percentages"] = df.drop([df.columns.to_list()[0], df.columns.to_list()[-1]], axis=1).sum(axis=1)
        df[col] = df[col].round(2).astype(str) + "%"
        df["Total Percentages"] = df["Total Percentages"].round(2).astype(str) + "%"
        df = df.iloc[:, df.columns != "Grand Total"]
        return df
    
    @classmethod
    def get_comment_df(self, df, json_data, category):
        df = df[["Respondent ID", "End Date", json_data["comment_category"][category][0]]]
        df.columns = ["Respondent ID", "Response Date", "Comment"]
        df.reset_index(inplace=True)    
        df.replace('', np.nan, inplace=True)
        df.dropna(inplace=True)
        return df
    
    @classmethod
    def concat_dfs(self, uploaded_files, data):
        df_list = []
        for i in range(len(uploaded_files)):
            df = pd.read_excel(uploaded_files[i])
            trans_df = backend.transform_df(df, data)
            df_list.append(trans_df)
        merged_df = pd.concat(df_list)
        return merged_df