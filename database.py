"""Eventually this will be a class created early on that will store
   and track all types of execution, strategy and news data
"""
#TODO: it's writing over files since they are being stored by teh category instead of actual tickers

import os

def write_analysis_to_file(category, date, df):
    filepath=f"/Users/michael.hammond/pythanos-bot/analysis/{date}/{category.upper()}_{date}.csv"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath)

def  process_data_files(category, date, database):
    for db in  database:
        write_analysis_to_file(category, date, db)
    
