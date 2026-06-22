import pandas as pd

def read_excel(file_path: str):
    df = pd.read_excel(file_path)

    return df

def read_csv(file_path: str):
    df = pd.read_csv(file_path)

    return df

def dataframe_to_dict(df):
    return df.to_dict(orient="records")