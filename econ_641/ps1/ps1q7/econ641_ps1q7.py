import pandas as pd
import numpy as np
from requests import get
from os import chdir, mkdir, path, mkdir

# Set main directory
mdir = path.dirname(path.abspath(__file__)).replace('\\', '/')

# Set data directory
ddir = '/data'

# Create the data directory if it doesn't exist
if not path.isdir(mdir+ddir):
    mkdir(mdir+ddir)

# Set up main data file
data_file = 'wiot00_row_apr12'
data_file_ext = '.xlsx'

# Set download flag
download_data = False

# Specify names for index levels
ind_icode = 'industry_code'
ind_iname_fgood = 'industry_name_or_final_good'
ind_country = 'country'
ind_c = 'c_num'

# Make a list of the original order, as well as a reordered index
data_index_orig = [ind_icode, ind_iname_fgood, ind_country, ind_c]
data_index_reorder = [ind_country, ind_c, ind_iname_fgood, ind_icode]

# Change directory to data
chdir(mdir+ddir)

# Check whether to download data
if download_data:
    # Specify WTIOD URL, as well as which spreadsheet to download
    wtiod_url = 'http://www.wiod.org/protected3/data13/wiot_analytic/'
    web_sheet = 'wiot00_row_apr12.xlsx'

    # Access that spreadshett and save it locally
    web_file = get(wtiod_url+web_sheet, stream=True)  # Access file on server
    with open(data_file+data_file_ext, 'wb') as local_file:  # Open local file
        for chunk in web_file.iter_content(chunk_size=128):  # Go through contents on server
            local_file.write(chunk)  # Write to local file

    # Read the downloaded spreadsheet into a DataFrame
    data = pd.read_excel(data_file+data_file_ext, skiprows=[x for x in range(2)],
        header=[x for x in range(4)], index_col=[x for x in range(4)], skipfooter=8)

    # Get rid of the last column, which just contains totals
    data = data.iloc[:, :-1]

    # Specify names for index levels
    data.columns.names = data_index_orig
    data.index.names = data_index_orig

    # Save the DataFrame locally
    data.to_pickle(data_file+'.pkl')
else:
    # Read in the locally saved DataFrame
    data = pd.read_pickle(data_file+'.pkl')

# Reorder the index levels to a more usable order
for x in range(2):
    data = data.reorder_levels(data_index_reorder, axis = x)

# Make a list of a c codes indicating intermediate goods (c1 - c35)
intermediate_c_range = []
for x in range(35):
    intermediate_c_range.append('c'+str(x+1))

# Make a DataFrame containing only intermediate goods, and one containing only final goods
intermediate_flows = data.iloc[:, [x in intermediate_c_range for x in data.columns.get_level_values('c_num')]]
final_flows = data.iloc[:, [x not in intermediate_c_range for x in data.columns.get_level_values('c_num')]]

# Sum both across the country level, across both axes
intermediate_flows = intermediate_flows.sum(axis=0, level='country').sum(axis=1, level='country')
final_flows = final_flows.sum(axis=0, level='country').sum(axis=1, level='country')

# Create vectors of total intermediate goods and final goods imports by country
intermediate_imports = intermediate_flows.sum(axis=0) - np.diag(intermediate_flows)
final_imports = final_flows.sum(axis=0) - np.diag(final_flows)

# Create a vector of the ratio of intermediate to total imports
intermediate_import_ratio = intermediate_imports / (intermediate_imports + final_imports)

# Create a matrix of trade flows, combining intermediate and final goods
total_flows = intermediate_flows + final_flows

# Create vectors of total imports and exports
total_imports = total_flows.sum(axis=0) - np.diag(total_flows)
total_exports = total_flows.sum(axis=1) - np.diag(total_flows)

# Calculate trade deficits
trade_deficit = total_exports - total_imports

# Make a vector of total expenditure
total_expenditure = total_imports + np.diag(total_flows)

# Calculate the ratio of trade deficits to total expenditure
trade_deficit_ratio = trade_deficit / total_expenditure

np.kron( np.array(total_expenditure, ndmin=2), np.ones((41,1)), )
print(np.array(total_expenditure, ndmin=2).shape)
