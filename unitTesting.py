'''
 # @ Author: Ryan Barnes
 # @ Create Time: 2024-06-20 10:18:23
 # @ Modified by: Ryan Barnes
 # @ Modified time: 2024-06-20 10:19:13
 # @ Description: 
    This file is meant to execute all unittests contained within 
    this directory and its subdirectories
 '''

### Internal Imports ###

import logging

### External Imports ###
import unittest
from datetime import datetime

from tests.test_connection import TestConnection 
from tests.test_file_functions import TestFileFunctions
from tests.test_models import TestModels
from tests.test_state import TestStateHolders

### Execution ###

logging.basicConfig(
   level=logging.DEBUG,
   format='%(asctime)s\t[%(levelname)s]\t%(message)s',
   handlers=[
         logging.FileHandler(f"./logs/{datetime.now().strftime('testing_debug_%Y%m%d_%H%M')}.log"),
   ]
)
unittest.main()
