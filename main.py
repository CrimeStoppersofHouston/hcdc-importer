'''
 # @ Author: Ryan Barnes
 # @ Create Time: 2024-05-20 13:53:12
 # @ Modified by: Ryan Barnes
 # @ Modified time: 2024-05-29 16:24:05
 # @ Description: 
        This is the main entrypoint for this program.
        Very little scripting should be included in this file, 
        all functions and objects should be referenced from other
        locations. This file will pass on the execution responsibility
        to the appropriate handler functions.
 '''

### Internal Imports ###
from handler.execution_handler import execute_program

### Execution ###

execute_program()
