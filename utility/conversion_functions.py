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

from typing import Iterable
import logging
from datetime import datetime

import pandas as pd
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


def convert_to_datetime(value, none_value = None) -> datetime:
    '''
        Converts a value to a datetime object. If blank or none, returns provided none_value.
        Default date_format is YYYYMMDD.
    '''
    if value is None or str(value).strip() == '':
        return none_value
    # Trim whitespace in order to avoid conversion errors
    value = str(value).strip()
    formats = ['%Y%m%d', '%Y-%m-%d %H:%M:%S']
    for date_format in formats:
        try:
            return datetime.strptime(value, date_format)
        except:
            continue
    logging.error('Cannot convert value %s to datetime!', value)
    raise ValueError(f'Cannot convert value {value} to datetime!')


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

def convert_to_sql(items: Iterable) -> str:
    '''Takes in an iterable and returns a sql string encompassing all items in it.'''
    ret = '('
    for item in items:
        if pd.isna(item):
            item = None
        match item:
            case str():
                ret += f"'{item.replace("'", "''")}',"
            case int():
                ret += f'{int(item)},'
            case float():
                ret += f'{float(item)},'
            case datetime():
                ret += f"'{datetime.strftime(item, '%Y-%m-%d')}',"
            case None:
                ret += 'NULL,'
            case _:
                logging.error('uncaught type %s | %s', str(type(item)), item)
                raise ValueError()
    return ret[:-1] + ')'
