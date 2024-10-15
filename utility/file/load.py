'''
    This module contains the functions needed to load various file extensions
    into pandas dataframes. Further cleaning and validations should be 
    handed off to other files. These loads should not do any conversions
    whatsoever, to avoid unforseen problems with data formatting.
 '''

### External Imports ###

import os
import contextlib
import pandas as pd
import numpy as np

### Function Declarations ###

def load_dataframe_csv(filepath, delimiter:str = ',', encoding_type='utf-8') -> pd.DataFrame:
    '''Returns a Dataframe loaded from the given csv filepath'''
    if not os.path.exists(filepath):
        raise ValueError(f'File {filepath} does not exist')
    try:
        with contextlib.closing(open(filepath, 'r', encoding=encoding_type)) as f:
            df = pd.read_csv(f, sep=delimiter, dtype=str, engine='python')
            df = df.replace(np.nan, None)
            return df
    except Exception as e:
        raise AttributeError('Cannot read CSV file: {e}') from e

def load_dataframe_excel(filepath, encoding_type='utf-8') -> pd.DataFrame:
    '''Returns a Dataframe loaded from the given excel filepath'''
    if not os.path.exists(filepath):
        raise ValueError(f'File {filepath} does not exist')
    try:
        with contextlib.closing(open(filepath, 'r', encoding=encoding_type)) as f:
            df = pd.read_excel(f, dtype=str)
            df = df.replace(np.nan, None)
            return df
    except Exception as e:
        raise AttributeError(f'Cannot read excel file: {e}') from e
