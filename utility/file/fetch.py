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
        raise ValueError('Depth limit for directory fetch must not be less than 0!')

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
