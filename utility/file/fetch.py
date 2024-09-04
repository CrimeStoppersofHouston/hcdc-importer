'''
 # @ Author: Ryan Barnes
 # @ Create Time: 2024-05-29 15:48:01
 # @ Modified by: Ryan Barnes
 # @ Modified time: 2024-05-30 12:14:30
 # @ Description: 
        This file contains all of the functions needed to fetch file names
        for use in the main execution of the program.
 '''

### External Imports ###

import os
import glob
from datetime import date
import logging
from config.flag_parser import FlagParser

### Function Declarations ###

def fetch_from_directory(
    directory_path: str,
    extension: str,
    recursive: bool = False,
    depth_limit: int = 3,
    depth: int = 0
) -> list[str]:
    '''Gets a list of files in the given directory with optional recursion'''
    if depth_limit < 0:
        raise ValueError("Depth limit for directory fetch must not be less than 0!")

    file_list = []
    if not os.path.exists(directory_path):
        raise ValueError(f'Directory does not exist: {directory_path}')

    # Recursion with depth limit
    if recursive and depth < depth_limit:
        subdirectories = [
            f'{directory_path}\\{d}'
            for d in os.listdir(directory_path) if os.path.isdir(f'{directory_path}\\{d}')
        ]
        for directory in subdirectories:
            file_list += fetch_from_directory(directory, extension, recursive, depth_limit, depth+1)

    # Fetching file paths
    for f in os.listdir(directory_path):
        if f.endswith(extension):
            file_list.append(f'{directory_path}\\{f}')

    return file_list


def hcdc_file_validation(directory_path: str, debug: bool= False):
    todays_date = date.today()
    filepaths = []
    code = 0
    file_list, status = daily_filings_check(directory_path, todays_date)
    filepaths += file_list
    code += status
    file_list, status = monthly_filings_check(directory_path, todays_date)
    filepaths += file_list
    code += status
    file_list, status = historical_filings_check(directory_path, todays_date)
    filepaths += file_list
    code += status
    code_check(code)
    return filepaths


def daily_filings_check(directory_path: str, check_date: date):
    '''Checks for daily filings file'''
    file_list = glob.glob(
        f'{directory_path}\\*[0-9]-*[0-9]-*[0-9] CrimFilingsDaily_withHeadings.txt'
    )
    status = 0
    latest_file = max(file_list)
    if latest_file:
        status = 1
        logging.info('Daily Filing found in %s', latest_file)

    if FlagParser.instance.args.debug:
        if latest_file.find(f'{check_date.year}-{check_date.month:02d}-{check_date.day:02d}') != -1 :
            logging.debug('%s corresponds to today - %s', latest_file, check_date)
        else:
            logging.debug('Daily file does not correspond to today - %s', check_date)

    return file_list, status


def monthly_filings_check(directory_path: str, check_date: date):
    '''Checks for monthly filings file'''
    file_list = glob.glob(
        f'{directory_path}\\*[0-9]-*[0-9]-*[0-9] CrimFilingsMonthly_withHeadings.txt'
    )
    status = 0
    latest_file = max(file_list)
    if latest_file:
        status = 2
        logging.info('Monthly Filing found in %s', latest_file)

    if FlagParser.instance.args.debug:
        if latest_file.find(fr'{check_date.year}-{check_date.month:02d}') != -1 :
            logging.debug('%s corresponds to this month - %s', latest_file, check_date)
        else:
            logging.debug('Monthly file does not correspond to this month - %s', check_date)

    return file_list, status


def historical_filings_check(directory_path: str, check_date):
    '''Checks for historical file'''
    file_list = glob.glob(f'{directory_path}\\Weekly_Historical_Criminal_*[0-9].txt')
    latest_file = max(file_list)
    status = 0
    if latest_file:
        status = 4
        logging.info('Historical Filing found in %s', latest_file)
        
    if FlagParser.instance.args.debug:
        if latest_file.find(fr'{check_date.year}{check_date.month:02d}') != -1 :
            logging.debug('%s corresponds to this month - %s', latest_file, check_date)
        else:
            logging.debug('Historical file does not correspond to this month - %s', check_date) 

    return file_list, status


def code_check(code: int):
    '''Returns a status code based on the files found'''
    match code:
        case 0:
            logging.info("No HCDC files found")
        case 1:
            logging.info("MISSING FILES: Monthly Filings, Historical Files")
        case 2:
            logging.info("MISSING FILES: Daily Filings, Historical Filings")
        case 3:
            logging.info("MISSING FILES: Historical Files")
        case 4:
            logging.info("MISSING FILES: Daily Filings, Monthly Filings")
        case 5:
            logging.info("MISSING FILES: Monthly Filings")
        case 6:
            logging.info("MISSING FILES: Daily Filings")
        case 7:
            logging.info("All HCDC files found") 
