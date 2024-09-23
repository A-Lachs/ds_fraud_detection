############################################################################
### collection of functions used for preprocessing & feature engineering ###
############################################################################


import pandas as pd


# create custom  range function with name in namespace

def max_min_range(x) -> float:
    return x.max() - x.min()

max_min_range.__name__ = 'max_min_range'


# change dtype of DF column

def convert_column_type(df_data: pd.DataFrame, columns: list | str, to_type) -> pd.DataFrame:
    """ Convert data types of column(s) in a dataframe.

    Args:
        df_data (pd.DataFrame):     Input df
        columns (list | str):       Column name (str) or list of column names to convert. 
        to_type:                    Data type to convert in e.g. ('category', str, int).
    
    Returns:
        pd.DataFrame:               Input df with converted columns.
    """
    if isinstance(columns, str):
        # convert co list
        columns = [columns]
    for col in columns:
        df_data[col] = df_data[col].astype(to_type)

    return df_data


# the add_feature_to_list() function is used to keep track of features used for modelling 

def add_feature_to_list(feature_name: str | list, feature_list: list) -> list:
    
    """ Add the a feature name (str) or list of feature names 
        to another list named "feature_list". 
        Names in feature_list are unique.

    Args:
        feature_name (str | list):  Str or list of str to be added to feature_list
        feature_list (list):        Name of in- and output list.

    Returns:
        feature_list (list):        Output list = input list with feature_name(s) added,
                                    unless it is already part of it.
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


#######################################
### Create account duration feature ### from the client's invoice data
#######################################


def extract_account_duration(df_by_counter_type: pd.DataFrame, prefix='')-> pd.DataFrame:
    """ From a DF with the columns 'client_id' and 'invoice_date' extract 
        the duration in days between first and last date from 'invoice_date'. 
        Return DF with new column prefix + '_acc_dur_days' with account duration in days.

    Args:
        df_by_counter_type (pd.DataFrame):  DF wih columns 'client_id' and 'invoice_date'.
        prefix (str, optional):             Prefix for the new column 'acc_dur_days'. 
                                            Defaults to '' + '_acc_dur_days.

    Returns:
        pd.DataFrame:   DF with columns client_id' and 'invoice_date' and prefix + '_acc_dur_days.
    """
    df_time_diff = df_by_counter_type.sort_values('invoice_date').groupby('client_id', as_index=False, observed=True)['invoice_date'].agg(['first','last']) 
    df_time_diff[f'{prefix}_acc_dur_days'] = df_time_diff['last'] - df_time_diff['first']
    df_time_diff.drop(['first', 'last'], axis=1, inplace=True)

    return df_time_diff


##################################
#### Create fraud_risk feature ###  - with 3 categories (low, normal, high)
##################################

# from a categorical feature rearrange its categories according to fraud risk 
# compared to baseline rate (low, normal or high) to create a new fraud_risk feature
 
def create_fraud_risk_feature(data_frame: pd.DataFrame, 
                              feature_in: str, 
                              new_categories: tuple | list,                          
                              feature_out_prefix='risk', 
                              verbose=False, 
                              convert=True) -> pd.DataFrame: 
    """ To a data frame add a column with a new fraud_risk feature with recoded categories [0,1] or [0,1,2].
        Higher values indicate higher risk of fraud.
        All categories of the feature "feature in" that are listed in "new_categories" will be set to 1, the rest to 0, 
        except it is a tuple with up to 3 lists (see Args below).
        By default the datatype is set to int, str and category with convert=True.
    
    Args:
        data_frame (pd.DataFrame):          Has column named feature_in.
        feature_in (str):                   Name of the column that contains the original categorical feature.
        new_categories (tuple | list):      List of categories from feature_in that constitute a new category.
                                            Can be a tuple with up to 3 lists, where 
                                            list[0] elements will be recoded as 0 (first list)
                                            list[1] elements will be recoded as 1 (second list)
                                            list[2] elements will be recoded as 2 (third list)
                                            Attention: If only one list is given, members of this list will be recoded as 1, else 0.
                                            Higher values indicate higher risk of fraud.         
        feature_out_prefix (str, optional): Prefix for new column. Defaults to 'risk'.
        verbose (bool, optional):           Defaults to False. Set to True to print additional info. 
        convert (bool, optional):           Defaults to True. Set False to if you don't want the datatype to be set to int, str and category.
    
    Returns:
        pd.DataFrame: has new column with recoded feature 
    """
    ### create column for new feature "risk of fraud" (higher values indicate higher risk)
        # data_frame.loc[data_frame[feature_in].isin(labeled_as_1), f"{feature_out_prefix}_{feature_in}"] = 1
        # data_frame.loc[~data_frame[feature_in].isin(labeled_as_1), f"{feature_out_prefix}_{feature_in}"] = 0

    # check wheter input is a nested list and proceed with recoding accordingly
    if any(isinstance(i, list) for i in new_categories): 
        
        if len(new_categories) == 3: # tuple | list with 3 lists
            # elif statement is expressed as nested if condition in list comprehension (nice!)
            data_frame[f"{feature_out_prefix}_{feature_in}"] = [0 if x in new_categories[0] else 1 if x in new_categories[1] else 2 for x in data_frame[feature_in] ]
        elif len(new_categories) == 2: # tuple | list with 2 lists
            data_frame[f"{feature_out_prefix}_{feature_in}"] = [1 if x in new_categories[1] else 0 for x in data_frame[feature_in] ]
        elif len(new_categories) == 1: # only 1 list: assuming list contains high risk categtory!
            data_frame[f"{feature_out_prefix}_{feature_in}"] = [1 if x in new_categories else 0 for x in data_frame[feature_in] ]
        else:
            print('Error: The number of catogeries for the new feature is invalid (<1 or >3)')
            return
    else:
        # only a list with elements that are recoded as 1 (assuming list contains high risk categtory), all others 0
        data_frame[f"{feature_out_prefix}_{feature_in}"] = [1 if x in new_categories else 0 for x in data_frame[feature_in] ]

    # Option: convert to int (for format), str (for memory), and category using own function
    if convert:
        for data_type in [int, str, 'category']:
            data_frame = convert_column_type(data_frame, f"{feature_out_prefix}_{feature_in}", data_type)

    # Option: print additional information about the new feature (proportion of each category)
    if verbose:
        print(f'\nNew feature "{feature_out_prefix}_{feature_in}" was added to the dataframe.\n'
              f'Higher values indicate a higher risk of fraud.\n')
        proportions = data_frame[f"{feature_out_prefix}_{feature_in}"].value_counts(normalize=True).reset_index().sort_values(f"{feature_out_prefix}_{feature_in}").reset_index()
        for j,i in enumerate(proportions[f"{feature_out_prefix}_{feature_in}"].values):
            print(f' Category {i}: {round(proportions.proportion[j]* 100,2)}%')   
    
    return data_frame


#####################################
### Create mode and count feature ### of categorical variables from the invoice data (clientwise aggregation)
#####################################

# Main function: create_mode_and_count_feature()
# Contains sub functions to create a mode and count feature of a categorical variable 
# for each client_id and merge them in a df


def create_mode_feature(invoice_data: pd.DataFrame, feature: str, renamed_feature=None) -> pd.DataFrame:
    """ Create a new feature with the feature's mode for each client_id in the invoice_data and return it as df.
    
    Args:
        invoice_data (pd.DataFrame):     Has columns 'client_id' and 'feature'
        feature (str):                   Name of input feature
        renamed_feature (str, optional): Name of output feature, same as feature when not given. Default's to None.
    
    Returns:
        pd.DataFrame:                    Has columns client_id and (renamed_feature)_mode.
    """
    if not renamed_feature:
        renamed_feature=feature
     # solution 1: old version with lambda function (takes 13s)
        # feature_mode = invoice_data.groupby('client_id', as_index=False)[feature].agg({'column': lambda x: x.value_counts().index[0]}) # mode return always a series, only return first value
        # feature_mode.rename(columns={'column': f'{renamed_feature}_mode'}, inplace=True)

    # solution 2: nested dict comprehension --> to df (better, but still takes 9s)
        # feature_mode = {client_id: max(df[feature], key=df[feature].tolist().count) for client_id, df in invoice_data.groupby('client_id')}
        # here changed to handle exception:

    feature_mode = {} 
    for client_id, df in invoice_data.groupby('client_id', observed=False):
        try:
            mode_value = max(df[feature], key=df[feature].tolist().count)
            feature_mode[client_id] = mode_value
        except ValueError:  # Handle the case where the sequence max()is empty
            feature_mode[client_id] = None
    
    df_mode = pd.DataFrame(list(feature_mode.items()), columns=['client_id', f'{renamed_feature}_mode'])

    # change data type of mode feature to str/category 
    new_name = f'{renamed_feature}_mode'
    conversions = [str, 'category']
    for i in conversions:
        df_mode = convert_column_type(df_mode, columns=new_name, to_type=i)

    return df_mode


def create_count_feature(invoice_data: pd.DataFrame, feature: str, renamed_feature=None, verbose=1) -> pd.DataFrame:
    """ Create a new feature from the feature's category count per client_id in the invoice_data and return it as df.
    
    Args:
        invoice_data (pd.DataFrame):        Has columns 'client_id' and 'feature'
        feature (str):                      Name of input feature
        renamed_feature (str, optional):    Name of output feature, same as feature when not given. Default's to None.
        verbose (int, optional):            If True print summary, set to False to if not wanted. Defaults to 1.
    
    Returns:
        pd.DataFrame:                       Has columns client_id and (feature)_count.
    """
    df_count = invoice_data.groupby('client_id', observed=False, as_index=False)[feature].nunique().sort_values(feature)
    
    if verbose:
        # Check if there are more than one feature category per client.
        print(f'There are {len(df_count[df_count[feature] == 1])} clients with only 1 {feature}.')
        print(f'There are {len(df_count[df_count[feature] > 1])} clients with more than 1 {feature}.')
        print(f'The max number of different {feature}s per client is {df_count[feature].max()}.')   

    if not renamed_feature:
        renamed_feature=feature

    df_count.rename(columns={feature : f'{renamed_feature}_count'}, inplace=True)

    return df_count


def merge_features(df_mode: pd.DataFrame, df_count : pd.DataFrame) -> pd.DataFrame:
    """ Merge df feature_mode and df feature_count into one data frame based on client_id.
    
    Args:
        feature_mode (pd.DataFrame):    Has columns client_id and (feature)_mode.
        feature_count (pd.DataFrame):   Has columns client_id and (feature)_count.
    
    Returns:
        pd.DataFrame: Has columns client_id, (feature)_mode and (feature)_count.
    """
    df_features = pd.merge(df_mode, df_count, on='client_id', how='outer')
    
    return df_features


def create_mode_and_count_feature(invoice_data: pd.DataFrame, feature: str, renamed_feature=None, verbose=1) -> pd.DataFrame:
    """ Create a new mode and count feature by aggregating the feature from the invoice_data df. 
    
    Args:
        invoice_data (pd.DataFrame):        Has columns client_id and feature
        feature (str):                      Name of input feature
        renamed_feature (str, optional):    Name of output feature, same as feature when not given. Default's to None.
        verbose (optional)                  Default's to 1. If False no information about count feature is printed.
    
    Returns:
        pd.DataFrame: Has columns client_id, (feature)_mode and (feature)_count.
    """
    if not renamed_feature:
        renamed_feature=feature

    feature_mode = create_mode_feature(invoice_data, feature, renamed_feature)
    feature_count = create_count_feature(invoice_data, feature, renamed_feature, verbose)
    
    feature_df = merge_features(feature_mode, feature_count)
    
    return feature_df


#############################################
### Calculate energy consumption features ###  - clientwise aggregation
#############################################

# the wrapper function add_consumption_features() is used to calculate 
# the consumption features of each client for each level 1 to 4 
# and add them to the main_df

# it uses the calculate_energy_consumption() function and
# the columns_exist() function from this section 

def calculate_energy_consumption(data: pd.DataFrame, energy_type: str, consumption_level: int, monthly: bool
                                 ) -> pd.DataFrame:
    """ Form the client's invoice data calculate the client's mean (std, max_min_range) consumption 
        for a specific energy type (electricity or gas) and a consumption level (1, 2, 3 or 4) 
        either over all months or for each month seperately (depending on bool 'monthly').

    Args:
        data (pd.DataFrame):        DF with columns 'client_id' and 'invoice_month'.
        energy_type (str):          Can be 'elec' or 'gas'.
        consumption_level (int):    Can be level 1, 2, 3 or 4.
        monthly (bool, optional):   If True aggregate the data by month.
                                    If False aggregate the data over all months.  

    Returns:
        pd.DataFrame:   DF aggregated by client (rows) with (mean, std, max_min_range) columns 
                        for a specific energy type and level. 
                        Optionally columns for each month.
    """
    
    # create dict with the aggregation methods (operations) 
    operations = ['mean', 'std', max_min_range]  
    aggregations = {}
    aggregations[f'consumption_lvl_{consumption_level}'] = operations

    # example:
    # df.groupby('group').agg({'a':['sum', 'max'], 
    #                         'b':'mean', 
    #                         'c':'sum', 
    #                         'd': max_min_range})

    if monthly:
        # observed=False is used for categorical variables, includes all categories (even when not observed)
        agg_data = data.groupby(['client_id','invoice_month'], observed=False, dropna=False).agg(aggregations)
        
        # reshape df
        #agg_data = agg_data.stack(level=0, future_stack=True).reset_index()
        agg_data = agg_data.stack(level=0).reset_index()
        agg_data.drop(['level_2'], axis=1, inplace=True)
        agg_data = agg_data.pivot(index='client_id', columns=['invoice_month'])
        
        # reduce multiindex using map and reset index
        agg_data.columns = agg_data.columns.map(lambda s: '_'.join(map(str, s)))
        agg_data = agg_data.reset_index()
        
        # rename columns
        agg_data.set_index('client_id', inplace=True)
        agg_data.columns = [f'{energy_type}_{consumption_level}_mon_{column.split("_")[1]}_{column.split("_")[0]}' 
                            if len(column.split("_")) == 2 
                            else f'{energy_type}_{consumption_level}_mon_{column.split("_")[3]}_{column.split("_")[0]}_{column.split("_")[1]}_{column.split("_")[2]}'
                            for column in agg_data.columns
                            ]
        agg_data = agg_data.reset_index()

    else: 
        agg_data = data.groupby(['client_id'], observed=False, dropna=False).agg(aggregations)
        
        # reshape df
        #agg_data= agg_data.stack(level=0, future_stack=True).reset_index()
        agg_data= agg_data.stack(level=0).reset_index()
        agg_data.drop(['level_1'], axis=1, inplace=True)
        
        # rename colums
        for operation in operations:
            if callable(operation): # get the operation name as str
                operation = operation.__name__
            agg_data.rename(columns={f'{operation}': f'{energy_type}_{consumption_level}_{operation}'}, inplace=True)
       
    return agg_data


# (wrapper) functions used to calculate and add new features to the df


def columns_exist(original_df: pd.DataFrame, new_df: pd.DataFrame) -> bool:
    """ Returns True if all columns of the new_df already exist in the original_df,
        otherwise False.
    """
    target_list = list(original_df.columns)
    test_list = list(new_df.columns)
    return all( element in target_list for element in test_list)


def add_consumption_features(to_df: pd.DataFrame, data: pd.DataFrame, energy_type: str, monthly: bool
                             ) -> pd.DataFrame:
    """ Wrapper function: 
        1) Aggregate consumption features by column 'client_id' with calculate_enery_consumption() function 
        2) Add the new consumption features to main DF 'to_df' 
            - only if they do not already exist, otherwise update them
            - main DF has to have to column 'client_id' too
        
        Do this for all consumption levels 1 to 4.

    Args:
        to_df (pd.DataFrame):   main DF with column 'client_id' to which new feature will be added
        data (pd.DataFrame):    feature DF with consumption features  aggregated by column 'client_id' 
        energy_type (str):      Can be 'elec' or 'gas'.
        monthly (bool):         If True aggregate the data by month.
                                If False aggregate the data over all months.

    Returns:
        pd.DataFrame:           Main DF with consumption features added or udated.  
    """

    # calculate and add aggregated consumption features to 'to_df'
    
    for level in range(1,5):
        # aggregate energy consumption features by client_id
        aggregated_features = calculate_energy_consumption(data, energy_type, level, monthly) 

        if not columns_exist(to_df, aggregated_features):
            # add aggregated features to to_df
            to_df = pd.merge(to_df, aggregated_features, on='client_id', how='outer')
        else:
            # update existing features in to_df 
            to_df.update(aggregated_features)

    return to_df