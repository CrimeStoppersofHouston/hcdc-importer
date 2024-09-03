'''
    This module contains functions for validating files before
    they are loaded.
'''

### External imports ###

import pandas as pd

from model.database import database_model

### Function Declarations ###

def validate_from_model(df: pd.DataFrame, model: database_model.Schema) -> bool:
    '''Returns True if all columns from the model are present in the given Dataframe'''
    checklist = {column:False for column in model.get_conversion_dict().keys()}
    for column in df.columns:
        if column in checklist:
            checklist[column] = True
    for column in checklist:
        if not checklist[column]:
            return False
    return True
