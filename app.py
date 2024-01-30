import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from datetime import datetime
import numpy as np

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
    df['month'] = pd.to_datetime(df['end_date']).dt.strftime('%Y-%m')

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
    
    df['scope_description'] = df['scope_description'].astype(str)
    
    # fixing month here. 
    # df['month'] = pd.to_datetime(df['month']).dt.to_period('M')
    df = df[df['month'] < "2024-01"]
    return df




def filter_data_date(df, selection):
    df['month'] = pd.to_datetime(df['month'].astype(str))
    
    max_date = df['month'].max()
    if selection == 'Last 1 Month':
        start_date = (max_date - pd.DateOffset(months=1))
    elif selection == 'Last 3 Months':
        start_date = (max_date - pd.DateOffset(months=2))
    elif selection == 'Last 6 Months':
        start_date = (max_date - pd.DateOffset(months=5))
    elif selection == 'Last 12 Months':
        start_date = (max_date - pd.DateOffset(months=11))
    elif selection == 'All Time':
        return df
    
    start_date_str = start_date.strftime('%Y-%m')
    
    # print("Start Date TY:", start_date)  # Debug print
    # print("End Date TY:", max_date)  # Debug print

    return df[df['month'] >= start_date_str]



def filter_lyear_data(df, selection):
    df['month'] = pd.to_datetime(df['month'].astype(str))

    max_date = df['month'].max()
    # print("Max Date in Data:", max_date)  # Debug

    if selection == 'Last 1 Month':
        start_date = (max_date - pd.DateOffset(months=1)).replace(year=max_date.year - 1)
    elif selection == 'Last 3 Months':
        start_date = (max_date - pd.DateOffset(months=2)).replace(year=max_date.year - 1)
    elif selection == 'Last 6 Months':
        start_date = (max_date - pd.DateOffset(months=5)).replace(year=max_date.year - 1)
    elif selection == 'Last 12 Months':
        start_date = (max_date - pd.DateOffset(months=11)).replace(year=max_date.year - 1)
    elif selection == 'All Time':
        return df
    
    start_date_str = start_date.strftime('%Y-%m')
    end_date_str = max_date.replace(year=max_date.year - 1).strftime('%Y-%m')
    
    
    # print("Start Date LY:", start_date_str)  # Debug print
    # print("End Date LY:", end_date_str)  # Debug print
    return df[(df['month'] >= start_date_str) & (df['month'] <= end_date_str)]


# Function to calculate YoY change safely to ahndle 0 values
def calculate_yoy(current, previous):
    if previous > 0:
        return f"{round(((current / previous) - 1) * 100, 2)}% YoY"
    else:
        return "na" 



# initilizing param
selected_date_range = 'All Time'







# Ensuring data is not already assigned to a session state
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# Assigning the data from the session state to df
df = st.session_state['data']

# Check if the filtered data is already in the session state, if not, filter and store it
if 'filtered_data' not in st.session_state:
    st.session_state['filtered_data'] = filter_data_date(df, selected_date_range)

if 'filtered_ly_data' not in st.session_state:
    st.session_state['filtered_ly_data'] = filter_lyear_data(df, selected_date_range)

# now filterd data assigned to session to avoid recalling
df_filtered = st.session_state['filtered_data']
df_ly_filtered = st.session_state['filtered_ly_data']


### Stremalit begins from this line here ###


# setting page configs
st.set_page_config(page_title='QuantumGrid', layout="wide")



# Title of the dashboard
st.title('QuantumGrid - Energy Usage Tracker')

# Sidebar for filters
st.sidebar.markdown(
    """
    ### How to Use This App
    Adjust the filters above to customize the data and metrics displayed on the dashboard. 
    Select different date ranges, utilities, and emission scopes to explore QuantumGrid's energy usage and CO2 emissions data. 

    ### Understanding the Metrics
    - **Total Energy Consumed (kWh)**: The sum of all energy consumed within the selected filters and date range.
    - **Total Emissions (KgCO2)**: The total CO2 emissions calculated for the selected filters and date range.
    - **Emissions Intensity (KgCO2e per kWh)**: This metric represents the average emissions per unit of energy consumed. It is calculated as the total emissions divided by the total energy consumed.
    - **Renewable Emissions Share in KgCO2e (%)**: This represents the percentage of total emissions that come from renewable energy sources.

    ### Year-over-Year (YoY) Calculation
    The Year-over-Year change indicates how the selected metrics have changed from the same period in the previous year. 
    For example, if 'Last 12 Months' is selected, the app compares the most recent 12-month data with the data from the preceding 12 months.
    """
)
st.sidebar.header('Filters')
st.sidebar.markdown('Use the **selection boxes** below to customize the data and metrics displayed on the dashboard.')

date_options = ['Last 1 Month', 'Last 3 Months', 'Last 6 Months', 'Last 12 Months', 'All Time']
selected_date_range = st.sidebar.selectbox('Select Date Range', date_options, index=date_options.index('Last 12 Months'))




# Function to check selection and reset to default if empty. Otherwise, dashboard breaks... 
def ensure_selection(selected_items, all_items, title):
    if not selected_items:
        st.sidebar.warning(f'At least one {title} must be selected. Resetting to default.')
        return all_items
    return selected_items

# Initialize the selectboxes with all options selected
all_utilities = df['utility'].unique()
selected_utilities = st.sidebar.multiselect('Utility', all_utilities, default=all_utilities)
selected_utilities = ensure_selection(selected_utilities, all_utilities, "utility")

all_scope_types = df['scope_description'].unique()
selected_scope_types = st.sidebar.multiselect('Scope Type', all_scope_types, default=all_scope_types)
selected_scope_types = ensure_selection(selected_scope_types, all_scope_types, "scope type")

all_divisions = df['division'].unique()
selected_divisions = st.sidebar.multiselect('Division', all_divisions, default=all_divisions)
selected_divisions = ensure_selection(selected_divisions, all_divisions, "division")

all_renewable = df['renewable_flag'].unique()
selected_renewable = st.sidebar.multiselect('Renewable Energy', all_renewable, default=all_renewable)
selected_renewable = ensure_selection(selected_renewable, all_renewable, "renewable energy")

# Filter the data based on the sidebar selections - current year dataframe (og df)
df_filtered = filter_data_date(df, selected_date_range)
df_filtered = df_filtered[df_filtered['utility'].isin(selected_utilities)]
df_filtered = df_filtered[df_filtered['scope_description'].isin(selected_scope_types)]
df_filtered = df_filtered[df_filtered['division'].isin(selected_divisions)]
df_filtered = df_filtered[df_filtered['renewable_flag'].isin(selected_renewable)]

# Filter the data based on the sidebar selections for last year data frame.
df_filtered_ly = filter_lyear_data(df, selected_date_range)
df_filtered_ly = df_filtered_ly[df_filtered_ly['utility'].isin(selected_utilities)]
df_filtered_ly = df_filtered_ly[df_filtered_ly['scope_description'].isin(selected_scope_types)]
df_filtered_ly = df_filtered_ly[df_filtered_ly['division'].isin(selected_divisions)]
df_filtered_ly = df_filtered_ly[df_filtered_ly['renewable_flag'].isin(selected_renewable)]


    



## Creating some empty spaces... prob other ways to do it



st.text("""            """) 

st.text("""            """) 

st.text("""            """) 

# Check if the filtered data is empty
if df_filtered.empty or df_ly_filtered.empty:
    st.warning('No data available for those filter selections.')
else:
    # creating comparisons
    start_date_ty = df_filtered['month'].min().strftime('%m-%Y')
    end_date_ty = df_filtered['month'].max().strftime('%m-%Y')
    start_date_ly = df_filtered_ly['month'].min().strftime('%m-%Y')
    end_date_ly = df_filtered_ly['month'].max().strftime('%m-%Y')
    comparison_string = f"(Comparison Period from: {start_date_ly} - {end_date_ly} to {start_date_ty} - {end_date_ty})"
    # Main section for Key KPI Cards
    st.header('Key Performance Metrics - ' + str(selected_date_range))

    # Using Markdown to customize the font size of the subheader
    st.markdown(f'<h3 style="font-size: 16px; font-style: italic;">{comparison_string}</h3>', unsafe_allow_html=True)



## Creating some empty spaces... prob other ways to do it

st.text("""            """) 

st.text("""            """) 

st.text("""            """) 




css_metrics = """
<style>
div[data-testid="metric-container"] div[data-testid="stMetricValue"] > div {
   font-size: 180%;
</style>
"""

# Inject custom CSS with Markdown
st.markdown(css_metrics, unsafe_allow_html=True)




# Calculate the KPIs
total_kwh = df_filtered['kwh'].sum() 
total_kgco2e = df_filtered['kgco2e'].sum() 
kgCO2e_per_kWh = (df_filtered['kgco2e'].sum() / df_filtered['kwh'].sum())
renewable_share = ((df_filtered[df_filtered['renewable_flag'] == "Renewable Source"]['kgco2e'].sum()) / (total_kgco2e) *100)

# Differences
# apply(filter_lyear_data)
total_kwh_ly = df_filtered_ly['kwh'].sum() 
total_kgco2e_ly = df_filtered_ly['kgco2e'].sum() 
kgCO2e_per_kWh_ly = (df_filtered_ly['kgco2e'].sum() / df_filtered_ly['kwh'].sum())
renewable_share_ly = ((df_filtered_ly[df_filtered_ly['renewable_flag'] == "Renewable Source"]['kgco2e'].sum()) / (total_kgco2e_ly) *100)


# Display KPIs using st.metric
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

def all_time_flag(selected_date_range, value):
    if selected_date_range == 'All Time':
        return 'na'
    return value

# Use the function to calculate KPI deltas
kpi1delta = all_time_flag(selected_date_range, calculate_yoy(total_kwh, total_kwh_ly))
kpi2delta = all_time_flag(selected_date_range, calculate_yoy(total_kgco2e, total_kgco2e_ly))
kpi3delta = all_time_flag(selected_date_range, calculate_yoy(kgCO2e_per_kWh, kgCO2e_per_kWh_ly))
kpi4delta = all_time_flag(selected_date_range, calculate_yoy(renewable_share, renewable_share_ly))


#C Calling metrics st.cols
kpi1.metric("Total Energy Consumed (kWh)", f"{round(total_kwh):,}", delta=kpi1delta)
kpi2.metric("Total Emissions (KgCO2)", f"{round(total_kgco2e):,}", delta=kpi2delta)
kpi3.metric("Emissions Intensity (KgCO2e per kWh)", f"{round(kgCO2e_per_kWh, 2):,}", delta=kpi3delta)
kpi4.metric("Renewable Emissions Share in KgCO2e (%)", f"{round(renewable_share, 2):,}%", delta=kpi4delta)

# Sidebar for metric and dimension selection
st.sidebar.header('Dashboard Options')

selected_metric = st.sidebar.radio('Select Metric', ['kWh', 'kgCO2e', 'KgCO2e per kWh'])
metric_column = 'kwh' if selected_metric == 'kWh' else 'kgco2e' if selected_metric == 'kgCO2e' else 'kgco2e_per_kwh'
selected_dimension = st.sidebar.radio('Select Dimension for Line Chart', ['No Dimension', 'Utility', 'Scope Type', 'Division', 'Renewable'])

## Creating some empty spaces... prob other ways to do it

st.text("""            """) 

st.text("""            """) 

st.text("""            """) 

st.text("""            """) 

st.text("""            """) 

st.text("""            """) 

st.text("""            """) 


# Dashboard section now 
st.subheader("Dashboard",divider ='gray')

#inserting radio button to flick between chart types.. 
chart_type = st.radio('Select Chart Type', ['Bar Chart','Line Chart'])
st.subheader(chart_type)



# Metric handling in the bar chart
if selected_dimension == 'No Dimension':
    df_filtered['month'] = pd.to_datetime(df_filtered['month']).dt.strftime('%Y-%m')
    df_filtered = df_filtered.sort_values('month')
    
    # Calculations and metric assignment
    df_filtered_grouped = df_filtered.groupby('month').agg({'kwh': 'sum', 'kgco2e': 'sum'}).reset_index()
    if metric_column == 'kgco2e_per_kwh':
        df_filtered_grouped['kgco2e_per_kwh'] = df_filtered_grouped['kgco2e'] / df_filtered_grouped['kwh']
        df_filtered_grouped['kgco2e_per_kwh'] = round(df_filtered_grouped['kgco2e_per_kwh'], 2)

    # Using metric to widen the format
    wide_format_data = df_filtered_grouped.set_index('month')[metric_column]

else:
    df_filtered['month'] = pd.to_datetime(df_filtered['month']).dt.strftime('%Y-%m')
    df_filtered = df_filtered.sort_values('month')
    dimension_column = 'utility' if selected_dimension == 'Utility' else 'scope_description' if selected_dimension == 'Scope Type' else 'renewable_flag' if selected_dimension == 'Renewable' else 'division'

    # Calculating sum of metrics per montha and selected col
    df_filtered_grouped = df_filtered.groupby(['month', dimension_column]).agg({'kwh': 'sum', 'kgco2e': 'sum'}).reset_index()
    if metric_column == 'kgco2e_per_kwh':
        # Avoid division by zero by using np.where to only perform division where kwh is not zero
        df_filtered_grouped['kgco2e_per_kwh'] = np.where(df_filtered_grouped['kwh'] != 0,
                                                         df_filtered_grouped['kgco2e'] / df_filtered_grouped['kwh'],
                                                         np.nan)  
        df_filtered_grouped['kgco2e_per_kwh'] = round(df_filtered_grouped['kgco2e_per_kwh'], 2)
        df_filtered_grouped['kgco2e_per_kwh'].fillna(0, inplace=True)  # Fill NaN values with 0 again at end to avoid issues with calc

    # Pivot using the correct metric_column +   Using metric to widen the format
    wide_format_data = df_filtered_grouped.pivot(index='month', columns=dimension_column, values=metric_column).sort_index()

    
    

# Create a bar chart or line chart based on the selected type (bar or line chart selection)
if chart_type == 'Line Chart':
    st.line_chart(wide_format_data)
else:
    # Create a bar chart with selected dimension
    st.bar_chart(wide_format_data)
    
# Getting current date for naming
current_date = datetime.now().strftime("%Y%m%d")

# Concatenate the date with the string for file naming
file_name = f"data_{current_date}.csv"

# Data exporting options
csv_export_button = st.download_button(
    label="Download Data as CSV",
    data=df.to_csv(index=False),
    file_name=file_name,
    mime='text/csv',
    key="download_button"
)

# Section to debug values.. keeping in code if needed 



# st.write("LY KWH:", total_kwh_ly)
# print("LY KgCO2e:", total_kgco2e_ly)
# print("LY KgCO2e per KWh:", kgCO2e_per_kWh_ly)
# # print("LY Renewable Share:", renewable_share_ly)



# print("Current Year kWh:", total_kwh)
# print("Last Year kWh:", total_kwh_ly)
# print("Current Year KgCO2e:", total_kgco2e)
# print("Last Year KgCO2e:", total_kgco2e_ly)
# print("Current Year KgCO2e per kWh:", kgCO2e_per_kWh)
# print("Last Year KgCO2e per kWh:", kgCO2e_per_kWh_ly)
# print("Current Year Renewable Share:", renewable_share)
# print("Last Year Renewable Share:", renewable_share_ly)



# print("Start Date TY:", start_date)  # Debug print
# print("End Date TY:", max_date)  # Debug print
# print("Start Date LY:", start_date_str)  # Debug print
# print("End Date LY:", end_date_str)  # Debug print
