# importing the required modules
import glob
import pandas as pd

# specifying the path to csv files
path = r"BLABLABLA"

#example
#r"C:\Users\taylan\trade bot\sql"
# csv files in the path
file_list = glob.glob(path + "/*.xlsx")

# list of excel files we want to merge.
# pd.read_excel(file_path) reads the 
# excel data into pandas dataframe.
excl_list = []

for file in file_list:
	excl_list.append(pd.read_excel(file))

# concatenate all DataFrames in the list
# into a single DataFrame, returns new DataFrame.
# 
excl_merged = pd.concat(excl_list, ignore_index=True)

# exports the dataframe into excel file
# change the file path
excl_merged.to_excel( r'C:\BLABLABLA\SQL_results.xlsx', index=False)
