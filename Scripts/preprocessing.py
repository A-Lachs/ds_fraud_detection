### collection of functions used for preprocessing  & feature engineering ###

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


def add_feature_to_list(feature_name: str | list, feature_list: list) -> list:
    """ Add the a feature name (str) or list of feature names 
        to another list named "feature_list". 
        Items in feature_list are non-duplicates.

    Args:
        feature_name (str | list):  Str or list of str to be added to feature_list
        feature_list (list):        Name of in- and output list.

    Returns:
        list: Output list = input list with feature_name added, unless it is already part of it.
    """

    if isinstance(feature_name, str):
        if feature_name not in feature_list:
            feature_list.append(feature_name) 

    elif isinstance(feature_name, list):
        for element in feature_name:
            if element not in feature_list:
                feature_list.append(element)
    else:
        # Invalid input raises a TypeError
        raise TypeError(f"Invalid feature type: {type(feature_name).__name__}. 'feature_name' must be a str or list of strings.")
    
    return feature_list


##################################
#### create fraud_risk feature ###  - with 3 categories (low, normal, high)
##################################


def create_fraud_risk_feature(data_frame: pd.DataFrame, 
                              feature_in: str, 
                              new_categories: tuple | list,                          
                              feature_out_prefix='risk', 
                              verbose=False, 
                              convert=True) -> pd.DataFrame: 
    """ To a data frame add a column with a new feature with recoded categories [0,1] or [0,1,2].
        Higher values indicated higher risk.
        All categories of the feature "feature in" that are listed in "new_categories" will be set to 1, the rest to 0, 
        except it is a tuple with up to 3 lists (see Args below).
        By default the datatype is set to int and category with convert=True.
    
    Args:
        data_frame (pd.DataFrame):          Has column named feature_in.
        feature_in (str):                   Name of the column that contains the feature.
        new_categories (tuple |list):       List of categories from feature_in that constitute a new category.
                                            Can be a tuple with up to 3 lists, where 
                                            tuple[0] will be recoded as 0 
                                            tuple[1] will be recoded as 1
                                            tuple[2] will be recoded as 2
                                            Attention: If only one list, members of this list will be recoded as 1, else 0.
                                            Higher values indicate higher risk of fraud.         
        feature_out_prefix (str, optional): Prefix for new column. Defaults to 'risk'.
        verbose (bool, optional):           Defaults to False. Set to True to print additional info. 
        convert (bool, optional):           Defaults to True. Set False to if you don't want the datatype to be set to int, str and category.
    
    Returns:
        pd.DataFrame: has new column with recoded feature 
    """
    ### create column for new feature "risk of fraud" (higher values indicate heigher risk)
        #data_frame.loc[data_frame[feature_in].isin(labeled_as_1), f"{feature_out_prefix}_{feature_in}"] = 1
        #data_frame.loc[~data_frame[feature_in].isin(labeled_as_1), f"{feature_out_prefix}_{feature_in}"] = 0

    # check wheter input is a nested list and proceed with recoding accordingly
    if any(isinstance(i, list) for i in new_categories): 
        
        if len(new_categories) == 3: # tuple/list with 3 lists
            # elif statement expressed as nested if condition in list comprehension (nice!)
            data_frame[f"{feature_out_prefix}_{feature_in}"] = [0 if x in new_categories[0] else 1 if x in new_categories[1] else 2 for x in data_frame[feature_in] ]
        elif len(new_categories) == 2: # tuple/list with 2 lists
            data_frame[f"{feature_out_prefix}_{feature_in}"] = [1 if x in new_categories[1] else 0 for x in data_frame[feature_in] ]
        elif len(new_categories) == 1: # assuming list contains high risk categtory
            data_frame[f"{feature_out_prefix}_{feature_in}"] = [1 if x in new_categories else 0 for x in data_frame[feature_in] ]
        else:
            print('Error: The number of catogeries for the new feature exceeds 3')
            return
    else:
        # only a list with elements that are recoded as 1 (assuming list contains high risk categtory), all others 0
        data_frame[f"{feature_out_prefix}_{feature_in}"] = [1 if x in new_categories else 0 for x in data_frame[feature_in] ]

    # option: convert to int (for format), str, and category using own function
    if convert:
        for data_type in [int, str, 'category']:
            data_frame = convert_column_type(data_frame, f"{feature_out_prefix}_{feature_in}", data_type)

    # option: print additional information about the new feature (proportion of each category)
    if verbose:
        print(f'\nNew feature "{feature_out_prefix}_{feature_in}" was added to the dataframe.\n'
              f'Higher values indicate a higher risk of fraud.\n')
        proportions = data_frame[f"{feature_out_prefix}_{feature_in}"].value_counts(normalize=True).reset_index().sort_values(f"{feature_out_prefix}_{feature_in}").reset_index()
        for j,i in enumerate(proportions[f"{feature_out_prefix}_{feature_in}"].values):
            print(f' Category {i}: {round(proportions.proportion[j]* 100,2)}%')   
    
    return data_frame




