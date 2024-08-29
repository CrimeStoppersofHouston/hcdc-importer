'''
        This module contains the classes and enums for the
        states that the program can enter. This file should
        only contain responsibilities that are related to
        switching and reading the states of these classes
'''

### External Imports ###

from enum import Enum
import logging

### Class Declarations ###

class State(Enum):
    '''State class to provide common parent type for validation purposes'''

class ProgramStates(State):
    '''Enumerator class that holds all program states'''
    INITIALIZATION = 100
    FILE_FETCH = 101
    FILE_PROCESSING = 102
    REPORTING = 103
    END = 110

class FileStates(State):
    '''Enumerator class that holds all file states'''
    INITIALIZATION = 200
    LOADING = 201
    SANITIZATION = 202
    STAGING = 203
    MERGE = 204
    END = 210

class StateHolder():
    '''Class that holds an enumerated state'''
    current_state = None

    def __init__(self, state_type:State):
        self.state_type = state_type 

    def set_state(self, state:State):
        '''Sets the current state to provided state'''
        if state not in self.state_type:
            raise ValueError(f'Invalid State: {state}')
        logging.debug('Entering state: %s', state)
        self.current_state = state

    def get_state(self):
        '''Returns the current state'''
        return self.current_state

class FileStateHolder(StateHolder):
    '''Child class of StateHolder that holds file states'''
    # Singleton instance to avoid creating multiple instances
    @classmethod
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FileStateHolder, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(FileStates)
        self.set_state(FileStates.INITIALIZATION)

class ProgramStateHolder(StateHolder):
    '''Child class of StateHolder that holds program states'''
    # Singleton instance to avoid creating multiple instances
    @classmethod
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ProgramStateHolder, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(ProgramStates)
        self.set_state(ProgramStates.INITIALIZATION)
