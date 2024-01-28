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
        return 'Renewable Source'
    else:
        return 'Non-renewable Source'

# Function to call data
def load_data():
    df = pd.read_csv('data.csv')
    
    # Creating new column, a descriptive value for scope instead.       
    df['scope_description'] = df['scope'].apply(label_scope)

    # Adding renewable col flag
    df['renewable_flag'] = df['renewable'].apply(set_renewable_flag)

    # making sure end_date correct format
    df['end_date'] = pd.to_datetime(df['end_date'], dayfirst=True).dt.strftime('%Y-%m')

    df['month'] = pd.to_datetime(df['end_date']).dt.strftime('%Y-%m')  # Ensure month is a string 'YYYY-MM'

    # Ensuring subset cols
    cleaned_data = df[['month', 'division', 'scope_description', 'renewable_flag', 'data_type', 'utility', 'scope_text', 'kwh', 'kgco2e']]

    # Grouping the data agg by the two metrics
    grouped_data = cleaned_data.groupby(
        ['month', 'division', 'scope_description', 'renewable_flag', 'data_type', 'utility', 'scope_text']
    ).agg({
        'kwh': 'sum',
        'kgco2e': 'sum'
    }).reset_index()

    # Replace NaN values with zeros in the 'kwh' and 'kgco2e' columns as it creates issues down the line
    grouped_data['kwh'].fillna(0, inplace=True)
    grouped_data['kgco2e'].fillna(0, inplace=True)    
    
    # calling it df
    df = grouped_data
    
    # renaming to df
    df = df.rename(columns={'data_type': 'utility_type'})
    
    # fixing month here. 
    df['month'] = pd.to_datetime(df['month']).dt.to_period('M')
    df = df[df['month'] < "2024-01"]
    return df

