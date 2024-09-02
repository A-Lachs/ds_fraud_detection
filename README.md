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
...

## 6. Ideas
...


# How to set up the virtual environment

-   The following examples are based on the assumption that you have installed [pyenv](https://github.com/pyenv-win/pyenv?tab=readme-ov-file) to handle different python versions. 
-   Create the virtual environment and install the required packages by running following commands for [macOS](#for-macos) or [windowsOS](#for-windowsos).

## For **`macOS`**: 

### Option A

-   Create the virtual environment using a [Makefile](Makefile) and activate it with the following commands

    ```BASH
    make setup
    source .venv/bin/activate
    ```

### Option B

- Create and activate the virtual environment with the following commands

    ```BASH
    pyenv local 3.11.3
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
    
## For **`WindowsOS`**:

- Here is a helpful guide on how to install [pyenv for windows](https://pyenv-win.github.io/pyenv-win/)

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

## **`Notes`:**
- If you encounter an error when trying to run `pip install --upgrade pip`, try:
    ```BASH
    python.exe -m pip install --upgrade pip
    ```


- Check installed packages (and versions) with `pip freeze` or  `pip list`


