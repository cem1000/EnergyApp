import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings


# Let's create a description of what the scopes are. Found online. 
def label_scope(value):
    if value == 1:
        return "Scope 1: Direct Emmissions"
    elif value == 2:
        return "Scope 2: Indirect Emissions from Electricity"
    elif value == 3:
        return "Scope 3: Other Indirect Emissions"
    else:
        return "Invalid Scope"

def set_renewable_flag(row):
    if row == 'y':
        return True
    else:
        return False

# Function to call data
def load_data():
    df = pd.read_csv('data.csv')
    
    # Creating new column, a descriptive value for scope instead.       
    df['scope_description'] = df['scope'].apply(label_scope)

    # Adding renewable col flag
    df['renewable_flag'] = df['renewable'].apply(set_renewable_flag)

    # making sure end_date correct format
    df['end_date'] = pd.to_datetime(df['end_date'])

    # Ensuring subset cols
    cleaned_data = df[['end_date', 'division', 'scope_description', 'renewable_flag', 'data_type', 'utility', 'scope_text', 'kwh', 'kgco2e']]

    # Grouping the data agg by the two metrics
    grouped_data = cleaned_data.groupby(
        ['end_date', 'division', 'scope_description', 'renewable_flag', 'data_type', 'utility', 'scope_text']
    ).agg({
        'kwh': 'sum',
        'kgco2e': 'sum'
    }).reset_index()

    df = grouped_data
    
    return df