### collection of functions used for preprocessing ###

import pandas as pd


def convert_column_type(df_data: pd.DataFrame, columns: list, type: str) -> pd.DataFrame:
    """ Convert data types of columns in a dataframe.
    Args:
        client_data (pd.DataFrame): Input df
        columns (list):             list of column names (as str) to convert 
        type (str):                 datatype to convert in e.g. ('category', str, int)
    Returns:
        pd.DataFrame: Output df with converted columns
    """
    if isinstance(columns, str):
        # convert co list
        columns = [columns]
    for col in columns:
        df_data[col] = df_data[col].astype(type)

    return df_data