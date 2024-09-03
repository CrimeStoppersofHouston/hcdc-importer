'''
 # @ Author: Ryan Barnes
 # @ Create Time: 2024-05-23 14:38:08
 # @ Modified by: Ryan Barnes
 # @ Modified time: 2024-05-29 11:06:16
 # @ Description:
        This file contains all of the functions used in
        converting dataframe columns to their correct
        data types.
 '''

### External Imports ###

from datetime import datetime
from sqlescapy import sqlescape

### Function Declarations ###

def convert_to_string(value, none_value = None) -> str:
    '''Converts a value to a string. If blank or none, returns provided none_value'''
    if value is None or str(value).strip() == '':
        return none_value
    return sqlescape(str(value).strip())


def convert_to_integer(value, none_value = None) -> int:
    '''Converts a value to an int. If blank or none, returns provided none_value'''
    if value is None or str(value).strip() == '':
        return none_value
    return int(float(value))


def convert_to_datetime(value, none_value = None, date_format:str = "%Y%m%d") -> datetime:
    '''
        Converts a value to a datetime object. If blank or none, returns provided none_value.
        Default date_format is YYYYMMDD.
    '''
    if value is None or str(value).strip() == '':
        return none_value
    # Trim whitespace in order to avoid conversion errors
    value = str(value).strip()
    return datetime.strptime(value, date_format)


def convert_to_float(value, none_value = None):
    '''Converts a value to a string. If blank or none, returns provided none_value'''
    if value is None or str(value).strip() == '':
        return none_value
    return float(value)


def convert_to_spn(value, none_value = None):
    '''Converts a value to a string. If blank or none, returns provided none_value'''
    if value is None or str(value).strip() == '':
        return none_value
    return str(value).strip().zfill(8)
