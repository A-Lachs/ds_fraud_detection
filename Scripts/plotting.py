################################################################
### This is a collection of functions used for plotting data ###
################################################################


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib


#################
### constants ###
#################


# custom colors for palette
COLOR_1 = 'steelblue'
COLOR_2 =  '#E42A38'
RED_COLORS = ['#e3868d', '#E42A38', '#8a010b']  # bright, middle, dark

# create custom  range function with name in namespace
def max_min_range(x) -> float:
    return x.max() - x.min()

max_min_range.__name__ = 'max_min_range'


################
### pie plot ### - used to show the fraud rate 
################


def get_fraud_proportion(client_data: pd.DataFrame) -> float:
    """ Return the proportion of fraud from a df with the column 'target' 
        in which fraud is coded with 1 and no fraud with 0.

    Args:
        client_data (pd.DataFrame): df with column named 'target' 
                                    that has the categories 0 and 1

    Returns:
        float: proportion of fraud (1)
    """
    df_proportion = client_data.target.value_counts(normalize=True).reset_index()
    fraud_proportion = df_proportion[df_proportion.target == 1].proportion * 100
    
    return fraud_proportion.values[0]


def create_fraud_freq_pieplot(client_data):
    """ Create a pretty pie plot displaying the frequency of fraud
        in energy consumption.

    Args:
        client_data (pd.DataFrame): df with column named 'target' 
                                    that has the categories 0 and 1
    """
    fr = get_fraud_proportion(client_data)
    
    y = [100-fr, fr]                    # percent of normal and fraudulent clients
    pie_labels = ['normal', 'fraud']
    pie_pieces = [0, 0.3]               # cut a piece out of the pie

    plt.pie(y, labels = pie_labels,
            explode = pie_pieces,
            autopct='%1.2f%%',          # format and display percentages
            colors=['steelblue', '#E42A38'],
            )
    
    plt.title('Frequency of gas and electricity fraud in Tunisia')
    plt.show()


##################################################
###  Aggregation function for data exploration ###  -  any categorical feature grouped by target var
##################################################

# is required for subplopts_fraud_risk_per_category() function defined below

def aggregate_feature_by_target(data_df: pd.DataFrame, feature: str, target) -> pd.DataFrame:
    """ This function takes a categorical feature of from data_df and counts it grouped by the target variable.
        It also returns a df with the percentages.

    Args:
        data_df (pd.DataFrame): df that contains feature and target var for each client
        feature (str):          name of feature to aggregate
        target (str, optional): name of target variable to group by. Defaults to 'target'.

    Returns:
        pd.DataFrame: grouped df
    """
    if target:
        grouped_object = data_df.groupby(feature, observed=False, as_index=False, dropna=False)[target]
         # calculate count and proportion
        df_count = grouped_object.value_counts(dropna=False) 
        df_proportion = grouped_object.value_counts(dropna=False, normalize=True)
        # merge count and proportion 
        aggregated_df = df_count.merge(df_proportion, how='inner', on=[feature, target]) 
        aggregated_df.sort_values([target, 'proportion'], ascending=False, inplace=True)
    else:
         # calculate count and proportion
        df_count = data_df[feature].value_counts(dropna=False).reset_index()
        df_proportion = data_df[feature].value_counts(dropna=False, normalize=True).reset_index()
        # merge count and proportion 
        aggregated_df = df_count.merge(df_proportion, how='inner', on=[feature])
        aggregated_df.sort_values(['proportion'], ascending=False, inplace=True)
        
    #  converting to percent
    aggregated_df['proportion']= aggregated_df['proportion']*100
    aggregated_df.rename({'proportion': 'percent'}, axis=1, inplace=True)

    return aggregated_df


#############################################
### subplopts_fraud_risk_per_category()   ### - elaborated plot to explore categorical variables grouped by target 
#############################################

# requires aggregate_feature_by_target() function defined above


def subplopts_fraud_per_category(your_df:pd.DataFrame, 
                                feature: str,  
                                fraud_baseline: float, 
                                fraud_range: int | float,
                                target='target', 
                                verbose=False) -> pd.DataFrame: 
    """ This function creates 2 subplots of a categorical variable, grouped by the target.
        An new feature "fraud_risk" (low, normal, high) is determined by comparing the fraud risk 
        in all categories to the fraud_baseline.

    Args:
        your_df (pd.DataFrame):     Has column named feature.
        feature (str):              Name of the (categorical!) feature column.
        fraud_baseline (float):     Fraud rate in overall sample. Defaults to FRAUD_BASELINE.
        fraud_range (int | float):  Defaults to FRAUD_RANGE.
                                    Defines range in which fraud rate is considered 
                                    normal or close to baseline. 
        target (str, optional):     Defaults to 'target'.
                                    Column name of grouping variable that contains 
                                    fraud / no fraud destinction.                              
        verbose (bool, optional):   Defaults to False. 
                                    Set to True to print additional info about new risk categories.
                                
    Returns:
        pd.Dataframe:                   Aggregated data frame grouped by target and category, 
                                        with columns "count" and "percent" for each combination.
        tuple([list], [list], [list]):  New fraud risk categories [low], [normal], [high] 
                                        with resprective categories of the feature     
    """
    
    ######################
    ### Aggragate data ###
    ######################

    grouped_df = aggregate_feature_by_target(your_df, feature, target)
    fraud_data = grouped_df[grouped_df[target] == 1].reset_index(drop=True).sort_values('percent', ascending=False)
    
    ### Create 3 new categories according to fraud risk
    
    # low risk: categories with less fraud then fraud baseline - fraud_range
    low_fraud = grouped_df[(grouped_df[target] == 1) & (grouped_df.percent < fraud_baseline - fraud_range)]

    # normal risk: categories with fraud rate within -fraud_range /+ fraud_range of baseline
    normal_fraud = grouped_df[(grouped_df[target] == 1) & (fraud_baseline + fraud_range > grouped_df.percent) & (grouped_df.percent > fraud_baseline - fraud_range)]
    
    # high risk: categories with more fraud then fraud baseline + fraud_range 
    high_fraud = grouped_df[(grouped_df[target] == 1) & (grouped_df.percent > fraud_baseline + fraud_range)]
    # high_fraud.sort_values('percent', ascending=False)
    
    # save in a tuple ([low], [normal], [high])
    fraud_risk_categories = (list(low_fraud[feature]), list(normal_fraud[feature]), list(high_fraud[feature]))

    ###################################
    ### Create plot with 2 subplots ### defined by axes[0] and axes[1]
    ###################################
    
    fig, axes = plt.subplots(1, 2, figsize=(12,5), gridspec_kw={'width_ratios': [1, 1]})
    fig.suptitle(f'Are there {feature}s with a higher risk of fraud?')
    
    ### first subplot: axes[0]

    sns.barplot(ax=axes[0], data=grouped_df, x=feature, y='count', hue=target, palette=[COLOR_1, RED_COLORS[1]])
    axes[0].set_title('Total number of cases')
    
    # change legend labels
    legend_handles, _= axes[0].get_legend_handles_labels()
    axes[0].legend(legend_handles, ['normal', 'fraud'])
    sns.move_legend(axes[0], title='', loc='best')  # remove label title
    
    ### second subplot: axes[1]

    sns.barplot(ax=axes[1], data=fraud_data, x=feature, y='percent')
    axes[1].set_title(f'Fraud rate compared to baseline ({round(fraud_baseline,2)} %)')
    
    # add horizontal lines (indicate baseline fraud rate range)
    axes[1].axhline(fraud_baseline, color='k', linestyle='-')
    axes[1].axhline(fraud_baseline + fraud_range, color='k', linestyle='--')
    axes[1].axhline(fraud_baseline - fraud_range, color='k', linestyle='--')
    
    # color bars according to fraud risk (low, normal, high)
    bar_heights = []
    for bar in axes[1].patches:
        bar_heights.append(bar.get_height())
        if bar.get_height() < fraud_baseline - fraud_range:          
            bar.set_color(RED_COLORS[0])
        elif bar.get_height() > fraud_baseline + fraud_range:
            bar.set_color(RED_COLORS[2])
        else:
            bar.set_color(RED_COLORS[1])
    
    # set y axis limit according to max bar height (to create space for the legend)
    axes[1].set_ylim(0, max(bar_heights) + 5)   
    
    # create custom legend (colors that show fraud risk) with little trick
    # create dummy objects (that are not displayed) with respective colors to add a legend 
    p = matplotlib.patches.Rectangle((0, 0), 1, 1, fc=RED_COLORS[0])
    q = matplotlib.patches.Rectangle((0, 0), 2, 2, fc=RED_COLORS[1])
    r = matplotlib.patches.Rectangle((0, 0), 3, 3, fc=RED_COLORS[2])
    axes[1].legend([p, q, r], ["low", "normal", "high"])
    sns.move_legend(axes[1], title='', loc='best')  # remove label title
    
    # determine appearance of x axis labels (in both subplots)
    if your_df[feature].nunique() > 40:
        # diplay only every second x axis label & rotate label
        for i in range(0,2):
            axes[i].set_xticks(axes[i].get_xticks()[::2])
            axes[i].set_xticks(axes[i].get_xticks(), axes[i].get_xticklabels(), rotation=45, ha='center')
    elif your_df[feature].nunique() > 12:
        # rotate x axis labels
        for i in range(0,2):
            # axes[i].tick_params(axis='x', labelrotation=45)
            axes[i].set_xticks(axes[i].get_xticks(), axes[i].get_xticklabels(), rotation=45, ha='center')

    plt.show()

    #################################
    ### Optional print statements ### showing proportion of new fraud risk categories
    #################################

    if verbose:
        fraud_risk_levels = ['low', 'normal', 'high']            
        print(f'The feature {feature} has {fraud_data[feature].nunique()} categories that are reassigned to the new feature "fraud risk".\n'
              f'"Fraud risk" has 3 levels {fraud_risk_levels[0], fraud_risk_levels[1], fraud_risk_levels[2]}\n'
              f'Normal risk is defined within the dashed lines (baseline of {round(fraud_baseline,2)} +/- {fraud_range}).\n') 
        
        for i,j in enumerate(fraud_risk_categories):
            print(f'{fraud_risk_levels[i]}: {j}')

    return grouped_df, fraud_risk_categories


###################################################
### 1x4 grid of boxplots for energy consumption ### - grouped by consumption level and target
###################################################


def boxplot_consumption_per_level(data:pd.DataFrame, energy_type: str, feature: str, show_outliers=True):
    """ Create boxplots to display energy consumption grouped by target (fraud, no fraud) 
        and with a subplot for each level 1 to 4. 
    
    Args:
        data (pd.DataFrame):    DF with aggregated energy consumption by client, 
                                energy_type ('elec', 'gas'), feature ('mean', 'std', 'max_min_range') and for each level 1 to 4.
        energy_type (str):      Energy type has to be any of 'elec' or 'gas'
        feature (str):          The aggregated energy consumption feature, e.g. 'mean', 'std', 'max_min_range'.
        show_outliers (bool):   Defaults to True to show ouliers in boxplots, 
                                When False it will not display outliers in boxplots. 

    """

    # energy type has to be chosen from 'elec' or 'gas'
    if energy_type == 'elec':
        consumption_label = 'electricity'
    elif energy_type == 'gas':
        consumption_label = energy_type
    else:
        return f'Type is not any of "elec" or "gas"'
    
    if show_outliers == False:
        title_info = '(outliers not displayed)'
    elif show_outliers == True:
         title_info = ''

    # build plot 

    fig, axes = plt.subplots(1, 4, figsize=(10,5), sharey=True)
    fig.suptitle(f'\n{consumption_label.title()} consumption by level {title_info}', fontsize=16, verticalalignment='center')

    for subplot in range(0,4):
        sns.boxplot(ax=axes[subplot], 
                    data=data, y=f'{energy_type}_{subplot + 1}_{feature}', 
                    hue='target', palette=[COLOR_1, RED_COLORS[1]], 
                    gap=0.2, width=.5, linewidth=1.5, notch=True,
                    showfliers=show_outliers,
                    )
        
        axes[subplot].set_title(f' Level {subplot +1 }', fontsize=9)
        axes[subplot].legend([],[], frameon=False)  # remove legend
        axes[subplot].set_xticks([])                # remove xticks

        if subplot == 0:
            axes[subplot].set_ylabel(f'{consumption_label.title()} consumption [kWh]')
        else:
            axes[subplot].set_ylabel('') 

        if subplot == 3: # add custom legend to last subplot (and dont' forget to adjust plt.tight_layout() accortdingly!)
            legend_handles, _= axes[subplot].get_legend_handles_labels()
            axes[subplot].legend(legend_handles, ['normal (left)', 'fraud (right)'])
            sns.move_legend(axes[subplot], 
                            title='', 
                            bbox_to_anchor=(1, 1.25), 
                            loc='upper right')  # remove label title
        
    plt.tight_layout(rect=[0, 0.03, 1, 1.15]) 
    # tight_layout only considers ticklabels, axis labels, and titles
    # adjustment with [left bottom, right, top] in normalized (0,1) space
    # increase top value to reduce space between top figures and suptitle (that is created when customizing the legend)
    
    plt.show()
    return


############################################################
### 2x2 grid of lineplots for montly energy consumption  ### - grouped by consumption level and target
############################################################

#  main function plot_monthly_consumption() for plotting levelwise monthly consumption grouped by target
#  uses subfunctions aggregate_monthly_consumption() and calculate_error_bar_bounds() to draw each subplot


def aggregate_monthly_consumption(data: pd.DataFrame, energy_type: str, consumption_level: int) -> pd.DataFrame:
    """ For plotting aggregate the mean monthly consumption data over all clients for a given energy type ('elec' or 'gas') 
        and level (1, 2, 3 or 4) grouped by month and by target (fraud or no fraud). 

    Args:
        data (pd.DataFrame):        DF that has for each client (rows) columns with levelwise mean monthly consumption data
                                    and a column 'target' (with codes 1 and 0 for fraud/ no fraud)
        energy_type (str):          Has to be 'elec' or 'gas'
        consumption_level (int):    Consumption data are available for level 1 to 4.

    Returns:
        pd.DataFrame:               Df with columns 'target', 'months' and aggregated features (mean, std, max_min_range) 
    """

    operations = ['mean', 'std', max_min_range]     # means of  aggregation 
    aggregations = {}

    for month in range(1,13):
        aggregations[f'{energy_type}_{consumption_level}_mon_{month}_mean'] = operations
        agg_data = data.groupby('target', observed=False).agg(aggregations)
   
    # change format for plotting (using stack)
    # agg_data = agg_data.stack(level=0, future_stack=True).reset_index()
    agg_data = agg_data.stack(level=0).reset_index()

    # rename months  
    agg_data.rename(columns={'level_1': 'months'}, inplace=True)
    agg_data['months'] = [i.split('_')[3] for i in agg_data['months'] ]

    # convert month dtype to ordered category for plotting
    agg_data['months'] = pd.Categorical(agg_data['months'],
                                       categories=[str(i) for i in list(range(1,13))], 
                                       ordered=True
                                       )

    return agg_data


def calculate_error_bar_bounds(y: pd.Series, error: pd.Series, limit=True)->tuple:
    """ From the input y values and corresponding errors compute the lower and upper bound 
        and return it as a tuple (lower, upper). 

    Args:
        y (pd.Series):          y_values, example: data[data.target == 0]['mean']
        error (pd.Series):      Corresponding error values data[data.target == 0]['std']
        limit (bool, optional): Limit the bounds to positive values. Defaults to True.

    Returns:
        tuple:                  Values vor lower, upper boundries.
    """

    # y_data = data[data.target == 0]['mean']
    # error = data[data.target == 0]['std']
    upper = y + error
    lower = y - error 
    if limit: #  set negative values to zero for plotting
        lower.loc[lower <0 ] = 0 
    return lower, upper


def plot_monthly_consumption(data_df: pd.DataFrame, energy_type: str, metric: str, error_metric='std'):
    """ In a 2x2 grid of subplots display the energy consumption (of a specific type 'elec' or 'gas') 
        for each level 1 to 4. Data is gropued by month and target (fraud/ no fraud).

    Args:
        data_df (pd.DataFrame):         DF that has for each client (rows) columns with levelwise mean monthly consumption data
                                        and a column 'target' (with codes 1 and 0 for fraud/ no fraud)
        energy_type (str):              Has to be 'elec' or 'gas'.
        metric (str):                   Metric used for data aggregation: 'mean'
        error_metric (str, optional):   Metric used to create error bands. Defaults to 'std'.
    """
    #  energy type 'elec' or 'gas' has to be chosen

    if energy_type == 'elec':
        consumption_label = 'electricity'
    elif energy_type == 'gas':
        consumption_label = energy_type
    else:
        return f'Energy type is not any of "elec" or "gas"'
    
    # construct the plot 

    fig, axes = plt.subplots(2, 2, figsize=(8, 7), sharex=True, sharey=True)
    fig.suptitle(f'Monthly {consumption_label} consumption', fontsize=14, verticalalignment='center')

    axes_ref = ([0, 0], [0, 1], [1, 0], [1, 1]) # to address the axes of each subplot in a 2x2 grid
    level_descriptions = ['< 2.400 kWh', 
                          '2.401 - 3.600 kWh', 
                          '3.401 - 6.000 kWh', 
                          '> 6.000 kWh',]

    for subplot in range(0,4):

        # aggregate the data
        data = aggregate_monthly_consumption(data_df, energy_type, consumption_level=subplot+1)

        sns.lineplot(ax=axes[axes_ref[subplot][0]][axes_ref[subplot][1]], 
                    data=data, x='months', y=metric, 
                    hue='target', palette=[COLOR_1, RED_COLORS[1]], 
                    linewidth=2,
                    )
        
        # change subplot titles/labels
        axes[axes_ref[subplot][0]][axes_ref[subplot][1]].set_title(f'Consumption level {subplot+1}', fontsize=9)
        if error_metric:
            axes[axes_ref[subplot][0]][axes_ref[subplot][1]].set_ylabel(f'{metric.title()} ({error_metric}) consumption [kWh]')
        else:
            axes[axes_ref[subplot][0]][axes_ref[subplot][1]].set_ylabel(f'{metric.title()} consumption [kWh]')
        axes[axes_ref[subplot][0]][axes_ref[subplot][1]].set_xlabel('Months')
    
        # remove legends
        axes[axes_ref[subplot][0]][axes_ref[subplot][1]].legend([],[], frameon=False)  

        # add custom legend to specific subplot (and dont' forget to adjust plt.tight_layout() accortdingly!)
        if subplot == 1:                   
            legend_handles, _= axes[axes_ref[subplot][0]][axes_ref[subplot][1]].get_legend_handles_labels()
            axes[axes_ref[subplot][0]][axes_ref[subplot][1]].legend(legend_handles, ['normal', 'fraud'])
            sns.move_legend(axes[axes_ref[subplot][0]][axes_ref[subplot][1]], 
                            title='',       # remove legend title
                            bbox_to_anchor=(1.02, 1.29), 
                            loc='upper right')  
        
        ### Optional:  Add custom error bars for each group 

        if error_metric:    
            
            # calculate error bar bounds
            normal_error = calculate_error_bar_bounds(y=data[data.target == 0][metric],
                                                    error=data[data.target == 0][error_metric])
            fraud_error = calculate_error_bar_bounds(y=data[data.target == 1][metric], 
                                                    error=data[data.target == 1][error_metric])
            
            #x = data['months'].unique() # does not have the correct order
            x=[str(i) for i in list(range(1,13))]

            #  fill space in between upper and lower error range
            axes[axes_ref[subplot][0]][axes_ref[subplot][1]].fill_between(x, normal_error[0], normal_error[1], color=COLOR_1, alpha=0.2)
            axes[axes_ref[subplot][0]][axes_ref[subplot][1]].fill_between(x, fraud_error[0], fraud_error[1], color=RED_COLORS[1], alpha=0.2)

    # layout 

    plt.tight_layout(rect=[0, 0.03, 1, 1.05]) 

    # tight_layout() only considers ticklabels, axis labels, and titles
    # adjustment with [left bottom, right, top] in normalized (0,1) space
    # increase top to reduce space between top figures and suptitle (that is created when customizing the legend)
    
    plt.show()
    return