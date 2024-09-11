# Data description 

The data can be [downloaded](https://zindi.africa/competitions/fraud-detection-in-electricity-and-gas-consumption-challenge/data) from a Zindi competition as `train.zip` file that contains the following csv files:

1. [Client data](#client-data):  `train_client.csv` includes information about the client and the target variable (fraud or no fraud)
2. [Invoice data](#invoice-data): `train_invoice.csv` includes each client's billing history from 2005 to 2019 

In the exploratory data analysis ([EDA](../EDA/EDA_summary.md)) the variables from both csv files are analysed regarding their relation to the target variable (fraud/ no fraud). Based on this analysis and some feature engineering the variables are selected to predict fraud. 


## Client data 

| Column name | Column values| Description |
| --- | ----------- |---|
| Client_id || Unique identifier for client |
| District |60, 62, 63, 69| District number associated to the location of a client ||
| Client_catg |11, 12, 51| Category the client belongs to|
| Region |101, 103, 104, 105, 106, 107, 199, 206, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 371, 372, 379, 399| Region number associated to the location of a client|
| Creation_date | Format: YYYY-MM-DD| Date when a client became customer of STEG |
| Target | 0, 1| Category indicating normal (0) or fraudulent (1) energy consumption of a client|

## Invoice data 

| Column name | Column values| Description |
| --- | ----------- |---|
| Client_id || Unique identifier for client |
| Invoice_date || Date of issue of the invoice relating to a given quarter due date for a client |
| Tarif_type |10, 11, 12, 13, 14, 15, 21, 24, 29, 9, 30, 40, 45, None| Type of tarif determines how a client is charged for electricity and gas copnsumption by the company STEG|
| Counter_number || Serial number identifing the counter materialized by a series of numbers written on the counting device and unique for each client|
| Counter_statue |0, 1, 2, 3, 4, 5, 269375, 618| Working status of the device measuring the amount of energy consumed by a client|
| Counter_code || Registration number identifing the device made up of three digits located within the serial number of the meter |
| Counter_coefficient || Coefficient used to convert the raw meter readings from the meter into actual consumption values |
| Consommation_level_1 || Energy consumption is less than 2.400 kwh per year <br> at the  [cost of 181 millimes per kwh](https://kapitalis.com/tunisie/2022/05/12/tunisie-les-nouveaux-tarifs-de-la-steg/) |
| Consommation_level_2 || Energy consumption is between 2.401 and 3.600 kwh per year <br> at the [cost of 223 millimes per kwh](https://kapitalis.com/tunisie/2022/05/12/tunisie-les-nouveaux-tarifs-de-la-steg/) |
| Consommation_level_3 || Energy consumpution is between 3.601 et 6.000 kwh per year <br> at the [cost of 338 millimes per kwh](https://kapitalis.com/tunisie/2022/05/12/tunisie-les-nouveaux-tarifs-de-la-steg/) |
| Consommation_level_4 || Energy consumption exceeds 6.000 kWh per year <br> at the [cost of 419 millimes per kwh](https://kapitalis.com/tunisie/2022/05/12/tunisie-les-nouveaux-tarifs-de-la-steg/) |
| Old_index || Old counter meter reading |
| New_index || New counter meter reading |
| Months_number |1 to 12| Number of the month  |
| Counter_type |'ELEC', 'GAZ'| Type of device measuring the amount of energy consumed <br> 'ELEC' = electricity consumption <br> 'GAZ' =  gas consumption|