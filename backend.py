import json
import re
import pandas as pd
from decimal import Decimal
import warnings

warnings.filterwarnings('ignore')

class backend():
    def __init__(self):
        print(True)
        
    @classmethod
    def load_data(self, json_file):
        """
        Load data from a json file.

        Parameters
        ----------
        json_file : str
            Path to the json file.

        Returns
        -------
        data : dict
            The data from the json file.
        """
        with open(json_file, "r", encoding="cp866") as file:
            data = json.load(file)
        return data
    
    @classmethod    
    def sjoin(self, x): return ';'.join(x[x.notnull()].astype(str))
    
    @classmethod 
    def remove_mixed_response(self, df, pattern):
        for i in df.columns:
            for j in range(len(df)):
                if re.findall(pattern, df.loc[:, i][j]):
                    # print(i)
                    df.loc[:, i][j] = df.loc[:, i][j].split(pattern)[0]
                    
    @classmethod
    def transform_df(self, df, json_data):
        # Define variables
        agency_list = json_data["agency_list"]
        update_col_list = json_data["update_col_list"]
        unnecessary_columns = json_data["unnecessary_columns"]
        department_col = json_data["department_column"]
        agency_column = json_data["agency_column"]
        respondent_id = json_data["type_change_columns"][0]
        collector_id = json_data["type_change_columns"][1]
        
        print("Manipulating data...")
        # remove unnecessary columns
        df.drop(unnecessary_columns, axis=1, inplace=True)
        print("Unnecessary columns are removed.")
        # move the column Department/Program/Unit to the front of departments
        df.insert(5, department_col, df.pop(department_col))
        non_col_list = []
        discontinuous_col_list = []
        backup_col_list = []
        agency_update_list = []
        comment_col = []
        for i in range(6, len(df.columns)):
            if "Unnamed" in df.columns[i]:
                non_col_list.append(int(df.columns[i][-3:]))
        
        discontinuous_col_list.append(non_col_list[0])
        for i in range(len(non_col_list)-1):
            if non_col_list[i] + 1 != non_col_list[i+1]:
                discontinuous_col_list.append(non_col_list[i+1])
                backup_col_list.append(non_col_list[i])

        backup_col_list.append(non_col_list[-1])
        # rename the column
        df.rename({agency_column:df[agency_column][0]}, axis=1, inplace=True)
        print("Agency columns are renamed.")
        
        
        discontinuous_col_list.append(non_col_list[-1])
        for n in range(len(backup_col_list)):
            for i in range(discontinuous_col_list[n], backup_col_list[n]+1):
                df.rename({"Unnamed: {}".format(str(i)): df["Unnamed: {}".format(str(i))][0]}, axis=1, inplace=True)
        print("Unnamed columns are renamed.")
        
        # Rename columns
        df.columns = json_data["master_col_list"]
        
        pattern_one = r'\s+-\s+'
        pattern_two = "; ; ; ;"
        pattern_three = ";"
        for i in range(5, len(df.columns)):
            if df.iloc[0][i] != df.columns[i]:
                df.rename({"{0}".format(df.columns[i]): "{0}; {1}".format(df.columns[i], df.iloc[0][i])}, axis=1, inplace=True)
                # print(df.columns[i])
            if re.findall(pattern_one, df.columns[i]):
                df.rename({"{0}".format(df.columns[i]): df.columns[i].split(" - ")[0]}, axis=1, inplace=True)
        for i in range(len(df.columns)):
            if re.findall(pattern_two, df.columns[i]):
                df.rename({"{0}".format(df.columns[i]): df.columns[i-1]}, axis=1, inplace=True)
        for i in range(len(df.columns)):
            if re.findall(pattern_three, df.columns[i]):
                df.rename({"{0}".format(df.columns[i]): df.columns[i].split(";")[0]}, axis=1, inplace=True)
        print("Renamed long columns")
        
        temp_df = df.iloc[1:]
        temp_df.reset_index(drop=True, inplace=True)
        
        # Remove columns with all null values
        df.dropna(axis=1, how='all', inplace=True)
        print("Removed all-nan value columns.")
        # Check if any comments columns were removed
        print("Checking any comments columns were removed...")
        df_comment_list = []
        missed_comment_list = []
        for aCol in df.columns:
            if "Comment" in aCol:
                df_comment_list.append(aCol)
        for aComment in json_data["question_category"]["comments"]:
            if aComment not in df_comment_list:
                missed_comment_list.append(aComment)
                
                
        if len(missed_comment_list) > 0:
            df[missed_comment_list] = temp_df[missed_comment_list]
            print("Removed comment columns were resolved.")
        else: 
            df = temp_df
            print("No comment columns were removed")
        
        # Convert column values types
        df[respondent_id] = df[respondent_id].apply(Decimal)
        df[collector_id] = df[collector_id].astype(int)
        
        for aCol in df.columns:
            for anAgency in agency_list:
                if aCol == anAgency:
                    agency_update_list.append(anAgency)

        
        df[agency_column] = df[agency_update_list].apply(
            lambda x: " ".join(x.dropna()),
            axis=1
        )
        
        [df.pop(x) for x in agency_update_list]
        print("Combined all agency columns into one.")
        df.insert(5, agency_column, df.pop(agency_column))
        
        df.set_index(json_data["index_columns"], inplace=True)
        
        
        df = df.groupby(level=0, axis=1).apply(lambda x: x.apply(backend.sjoin, axis=1)).reset_index()
        print("Combined the same name columns")
        
        # self.remove_mixed_response(df, pattern_three)
        update_df = df[update_col_list]
        update_df.fillna("", inplace=True)
        update_df = update_df.loc[:, ~update_df.columns.duplicated()]
        update_df = update_df.replace("N/A - to My Role", "N/A to My Role")
        return update_df
    
    @classmethod
    def get_col_widths(self, dataframe):
        # First we find the maximum length of the index column   
        idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
        # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
        return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

    @classmethod
    def format_excel(self, df):
        writer = pd.ExcelWriter("update_format.xlsx", engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Individual Response", startrow=1, header=False, index=False)
        workbook = writer.book
        worksheet = writer.sheets["Individual Response"]

        header_format = workbook.add_format({"bold": True,
                                            "bottom": 2,
                                            "bg_color": "#d3d3d3"})

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        for i, width in enumerate(self.get_col_widths(df)):
            worksheet.set_column(i-1, i, width)
       
        worksheet.autofilter(0,0,df.shape[0], df.shape[1])
        writer.close()
        workbook.close()