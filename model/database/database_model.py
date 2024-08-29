'''
    This module contains base classes for creating a model for a
    generic column-based database.
'''

### External Imports ###

import builtins
import logging
from enum import Enum
from typing import Self, Type, Dict, Callable

import numpy as np

### Internal Imports ###
from utility import conversionFunctions

### Class Declarations ###

class Column:
    '''Represents a column for mapping file columns to database columns'''
    def __init__(self, raw_name: str, name: str, data_type: Type, **kwargs):
        self.raw_name = raw_name
        self.name = name
        self.data_type = data_type
        if kwargs.get('conversion_function'):
            self.conversion_function = kwargs.get('conversion_function')
        else:
            match data_type:
                case builtins.str:
                    self.conversion_function = conversionFunctions.convertToString
                case builtins.int:
                    self.conversion_function = conversionFunctions.convertToInteger
                case np.datetime64:
                    self.conversion_function = conversionFunctions.convertToDatetime
                case builtins.float:
                    self.conversion_function = conversionFunctions.convertToFloat
                case _:
                    self.conversion_function = None
                    logging.error(
                        'There is not an automatic implementation for %s type', 
                        data_type.__name__
                    )
                    raise ValueError()

class TableStatus(Enum):
    '''Helper class for marking table handling status'''
    PENDING = 1
    INPROGRESS = 2
    COMPLETED = 3

class Table:
    '''Represents a table containing rows'''
    def __init__(self, name: str):
        self.name = name
        self.columns = set()
        self.prereqs = set()
        self.status = TableStatus.PENDING


    def add_column(self, column: Column) -> Self:
        '''Adds a column to the columns dict'''
        self.columns.add(column)
        return self


    def add_prereq(self, table: Self) -> Self:
        '''Adds a prerequisite table to be handled before this one'''
        self.prereqs.add(table)
        return self


    def advance_state(self):
        '''Advances the state of this table'''
        match self.status:
            case TableStatus.PENDING:
                self.status = TableStatus.INPROGRESS
            case TableStatus.INPROGRESS:
                self.status = TableStatus.COMPLETED
            case TableStatus.COMPLETED:
                logging.warning("Advancing table status when already completed!")


    def get_conversion_dict(self) -> Dict[str, Callable]:
        '''Returns a dictionary containing each column name with its conversion function'''
        return_dict = {}
        for column in self.columns:
            return_dict[column.rawName] = column.conversion_function
        return return_dict


class Schema:
    '''Contains table objects and maintains information about their progress'''
    def __init__(self, name: str):
        self.name = name
        self.completed_tables = set()
        self.processing_tables = set()
        self.pending_tables = set()
        self.tables = set()


    def get_conversion_dict(self) -> Dict[str, Callable]:
        '''Returns a merged dictionary of conversion functions of all columns in the schema'''
        return_dict = {}
        for table in self.tables:
            conversion_dict = table.get_conversion_dict()
            for duplicate in set(conversion_dict.keys()).intersection(return_dict.keys()):
                if return_dict[duplicate] != conversion_dict[duplicate]:
                    logging.error(
                        'Table %s caused conversion function conflict on column %s', 
                        table.name, duplicate
                    )
                    raise ValueError(f'Conversion function conflict on column {duplicate}')
            return_dict.update(table.get_conversion_dict())
        return return_dict


    def reset_schema(self):
        '''Resets the schema to the default state'''
        self.completed_tables = set()
        self.processing_tables = set()
        self.pending_tables = self.tables.copy()


    def get_table_by_name(self, name: str) -> Table:
        '''returns a Table object if it exists in the Schema object'''
        return next((table for table in self.tables if table.name == name), None)


    def add_table(self, table: Table) -> Self:
        '''Adds a table to this schema and returns it for later use'''
        self.tables.add(table)
        self.pending_tables.add(table)
        return self


    def is_completed(self):
        '''Returns True if all tables are marked as completed'''
        return self.completed_tables.issubset(self.tables)


    def advance_table_state(self, table: Table):
        '''Advances the given table's state'''
        table.advanceState()
        match table.status:
            case TableStatus.INPROGRESS:
                self.pending_tables.remove(table)
                self.processing_tables.add(table)
            case TableStatus.COMPLETED:
                self.processing_tables.remove(table)
                self.completed_tables.add(table)
            case _:
                logging.warning('Unaccounted table status %s in %s', table.status, table.name)


    def get_available_table(self) -> Table:
        '''
            Returns a table which is has all prereq fulfilled and is ready for processing. 
            Returns None if no tables are available
        '''
        if not self.pending_tables:
            logging.debug("There are no pending tables")
            return None
        for table in self.pending_tables:
            if table.prereqs.issubset(self.completed_tables):
                self.advance_table_state(table)
                return table
            logging.debug('Cannot handle %s, not all prerequisites are completed', table.name)
        logging.debug("There are no tables that can be handled")
        return None
