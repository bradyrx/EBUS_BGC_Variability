"""
Desc : Really simple script to store various constants (such as colors) for
this project overall. You can simply import the constants at the top line of a
given script so that you don't have to repeat them. To do so, run "from
constants import *" which unpacks everything.
"""
import pandas as pd

EBUS = ['CalCS', 'HumCS', 'CanCS', 'BenCS']

colors = {
    'CalCS': '#80b1d3',
    'calcs': '#80b1d3',
    'HumCS': '#fb8072',
    'humcs': '#fb8072',
    'CanCS': '#fdb462',
    'cancs': '#fdb462',
    'BenCS': '#bc80bd',
    'bencs': '#bc80bd'
}

ens = ['001', '002', '009', '010', '011', '012', '013', '014', '015', '016',
       '017', '018', '019', '020', '021', '022', '023', '024', '025', '026',
       '027', '028', '029', '030', '031', '032', '033', '034', '035', '101',
       '102', '103', '104', '105']

# TAYLOR SERIES EXPANSION
# This makes the buffer values and sensitivity values global.
fileDir = '/glade/u/home/rbrady/projects/EBUS_BGC_Variability/' + \
          'data/processed/all-systems/'
sensitivities = pd.DataFrame.from_csv(fileDir + \
                                      'pCO2_sensitivities_all_systems')
buffers = pd.DataFrame.from_csv(fileDir + \
                                      'pCO2_buffers_all_systems')
