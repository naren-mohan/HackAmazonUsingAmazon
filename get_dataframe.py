from sqlalchemy import create_engine
import pandas as pd
import os
import time


def store_df(table_name = "items_large"):
    engine = create_engine('sqlite:///database.db')
    df = pd.read_sql('SELECT * FROM '+ table_name +';', engine)
    engine.dispose()

    cwd = os.getcwd()
    folder_name = cwd + "/csv_dumps"
    if not(os.path.isdir(folder_name)):
        os.mkdir(folder_name)

    count = 1
    timestr = time.strftime("%Y%m%d-%H%M")
    filename = timestr + "_" + table_name
    
    while(1):
        if os.path.exists(filename):
            filename += "("+count+")"
            count += 1
        else:
            break
    
    df.to_csv(folder_name+"/"+filename)
    
if __name__ == "__main__":
    store_df()
    