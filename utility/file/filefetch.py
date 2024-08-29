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

def fetchFromDirectory(directoryPath: str, extension: str, recursive: bool = False, depthLimit: int = 3, depth: int = 0) -> list[str]:
    if depthLimit < 0:
        raise ValueError("Depth limit for directory fetch must not be less than 0!")

    fileList = []
    if not os.path.exists(directoryPath):
        raise ValueError(f'Directory does not exist: {directoryPath}')

    # Recursion with depth limit 
    if recursive and depth < depthLimit:
        subDirectories = [f'{directoryPath}\\{d}' for d in os.listdir(directoryPath) if os.path.isdir(f'{directoryPath}\\{d}')]
        for directory in subDirectories:
            fileList += fetchFromDirectory(directory, extension, recursive, depthLimit, depth+1)

    # Fetching file paths
    for f in os.listdir(directoryPath):
        if f.endswith(extension):
            fileList.append(f'{directoryPath}\\{f}')
    
    return fileList

def hcdcFileValidation(directoryPath: str, debug: bool= False):
    todays_date = date.today()
    filepaths = []
    code = 0
    fileList, status = dailyFilingsCheck(directoryPath, todays_date, debug)
    filepaths += fileList
    code += status
    fileList, status = monthlyFilingsCheck(directoryPath, todays_date, debug)
    filepaths += fileList
    code += status
    fileList, status = historicalFilingsCheck(directoryPath, todays_date, debug)
    filepaths += fileList
    code += status
    codeCheck(code)
    return filepaths, code
    
def dailyFilingsCheck(directoryPath: str, date: date):
    fileList = glob.glob(f'{directoryPath}\\*[0-9]-*[0-9]-*[0-9] CrimFilingsDaily_withHeadings.txt')
    status = 0
    latestFile = max(fileList)
    if latestFile:
        status = 1
        logging.info(f'Daily Filing found in {latestFile}')
    
    if FlagParser.instance.args.debug:
        if latestFile.find(f'{date.year}-{date.month:02d}-{date.day:02d}') != -1 :
            logging.debug(f'{latestFile} corresponds to today - {date}')
        else:
            logging.debug(f'Daily file does not correspond to today - {date}')
        
        
    return fileList, status

def monthlyFilingsCheck(directoryPath: str, date: date):
    fileList = glob.glob(f'{directoryPath}\\*[0-9]-*[0-9]-*[0-9] CrimFilingsMonthly_withHeadings.txt')
    status = 0
    latestFile = max(fileList)
    if latestFile:
        status = 2
        logging.info(f'Monthly Filing found in {latestFile}')
    
    if FlagParser.instance.args.debug:
        if latestFile.find(fr'{date.year}-{date.month:02d}') != -1 :
            logging.debug(f'{latestFile} corresponds to this month - {date}')
        else:
            logging.debug(f'Monthly file does not correspond to this month - {date}')
            
    return fileList, status
    
def historicalFilingsCheck(directoryPath: str, date: date):
    fileList = glob.glob(f'{directoryPath}\\Weekly_Historical_Criminal_*[0-9].txt')
    latestFile = max(fileList)
    status = 0
    if latestFile:
        status = 4
        logging.info(f'Historical Filing found in {latestFile}')
        
    if FlagParser.instance.args.debug:
        if latestFile.find(fr'{date.year}{date.month:02d}') != -1 :
            logging.debug(f'{latestFile} corresponds to this month - {date}')
        else:
            logging.debug(f'Historical file does not correspond to this month - {date}') 
        
    return fileList, status

def codeCheck(code: int):
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
            