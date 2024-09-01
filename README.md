# Project Summary

## 1. Goal

This data science project aims to improve the detection of fraud in energy consumption. 

## 2. Data 

The data is provided by the company STEG (société tunisienne d'électricité et du gaz) that produces and distributes electricity and gas in Tunisia.

For the data source and description please take a look at the [data description](data/data_description.md).

[insert pie chart for fraud ]

## 3. EDA

A major part of the project is dedicated to the [exploratory data analysis](EDA/EDA_summary.md) and feature engineering with the goal to select variables that can be used to predict fraud. 

## 4. Modelling

Different classification models are compared regarding their performance in predicting fraud.

*   Goal: detect as many fraud cases as possible while keeping the number of wrongfully accused cases low

*   Problem of imbalanced classes
*   Evaluation metric: F1 score


## 5. Best result 

## 6. Ideas

# Set up the virtual environment

## For **`macOS`**: 

-   Install the virtual environment and the required packages by running following commands.

### Option A
-   Make the setup using the [Makefile](Makefile):

     ```BASH
    make setup
    ```
-   After that active your environment:
    ```BASH
    source .venv/bin/activate
    ```
### Option B
- Create and activatethe virtual environment with the following commands:

    ```BASH
    pyenv local 3.11.3
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
    
## For **`WindowsOS`**:

- Install the virtual environment and the required packages by running following commands.

### Option A

-   For `PowerShell` CLI

```PowerShell
pyenv local 3.11.3
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### Option B

-   B For `Git-bash` CLI
  
```BASH
pyenv local 3.11.3
python -m venv .venv
source .venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## **`Note:`**
If you encounter an error when trying to run `pip install --upgrade pip`, try using the following command:
```Bash
python.exe -m pip install --upgrade pip
```

