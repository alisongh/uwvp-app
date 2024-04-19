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
        """
        This method pivots a DataFrame based on the specified columns and question.

        Parameters:
        df (pandas.DataFrame): The input DataFrame to be pivoted.
        question (str): The column name of the question for which the pivot is to be performed.
        cols (list): A list of column names that will be used as the pivot columns.

        Returns:
        pandas.DataFrame: A pivoted DataFrame with the specified question and columns.
        """
        groupby_df = df.groupby(cols)[question].count().reset_index()
        
        groupby_df.loc[len(groupby_df)] = groupby_df.sum(numeric_only=True)
        groupby_df.loc[len(groupby_df)-1, "Department/Program/Unit"] = "Grand Total"
        return groupby_df
    
    @classmethod
    def get_tmp_df(self, df, data, category):
        """
        This method filters the DataFrame based on the specified category and returns a subset of the DataFrame with the 'Respondent ID' and the specified category column.

        Parameters:
        df (pandas.DataFrame): The input DataFrame to be filtered.
        data (dict): A dictionary containing the question categories.
        category (str): The category of questions to be included in the temporary DataFrame.

        Returns:
        pandas.DataFrame: A temporary DataFrame with the 'Respondent ID' and the specified category column.
        """
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
        """
        This method calculates the percentage of each category in the DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            The input DataFrame to be processed.

        Returns
        -------
        pandas.DataFrame
            A DataFrame with the same columns as the input DataFrame, but with the values of the specified columns divided by the "Grand Total" and multiplied by 100, rounded to 2 decimal places and appended with "%". The "Grand Total" column is removed from the DataFrame.

        """
        col = df.columns.difference([df.columns.to_list()[0], "Grand Total"])
        df[col] = (df[col].div(df["Grand Total"], axis=0).mul(100))
        df["Total Percentages"] = df.drop([df.columns.to_list()[0], df.columns.to_list()[-1]], axis=1).sum(axis=1)
        df[col] = df[col].round(2).astype(str) + "%"
        df["Total Percentages"] = df["Total Percentages"].round(2).astype(str) + "%"
        df = df.iloc[:, df.columns != "Grand Total"]
        return df
    
    @classmethod
    def get_comment_df(self, df, json_data, category):
        """
        This method filters the DataFrame based on the specified category and returns a subset of the DataFrame with the 'Respondent ID', 'End Date', and the specified category column.
        The column names are then updated and any empty strings are replaced with NaN values.
        DataFrame rows with NaN values in the 'Respondent ID' or 'End Date' columns are then removed.

        Parameters:
        df (pandas.DataFrame): The input DataFrame to be filtered.
        json_data (dict): A dictionary containing the comment categories.
        category (str): The category of comments to be included in the temporary DataFrame.

        Returns:
        pandas.DataFrame: A temporary DataFrame with the 'Respondent ID', 'Response Date', and the specified category column.
        """
        df = df[["Respondent ID", "End Date", json_data["comment_category"][category][0]]]
        df.columns = ["Respondent ID", "Response Date", "Comment"]
        df.reset_index(inplace=True)    
        df.replace('', np.nan, inplace=True)
        df.dropna(inplace=True)
        return df
    
    @classmethod
    def concat_dfs(self, uploaded_files, data):
        """
        Concatenates multiple DataFrames read from the uploaded Excel files.

        Parameters:
        uploaded_files (list): A list of file paths to the uploaded Excel files.
        data (dict): A dictionary containing the necessary information for transforming the DataFrames.

        Returns:
        pandas.DataFrame: A concatenated DataFrame containing the data from all the uploaded Excel files after transformation.
        """
        df_list = []
        for i in range(len(uploaded_files)):
            df = pd.read_excel(uploaded_files[i])
            trans_df = backend.transform_df(df, data)
            df_list.append(trans_df)
        merged_df = pd.concat(df_list)
        return merged_df