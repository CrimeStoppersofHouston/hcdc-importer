'''
    This module contains the handler functions needed
    to change the states of program and file holder
    classes.
'''

### Internal Imports ###

from config.states import (
    FileStates, FileStateHolder, 
    ProgramStates, ProgramStateHolder,
    InsertionStates, InsertionStateHolder
)
from model.database.database_model import Schema

### Function Declarations ###


def change_program_state(pstate: ProgramStateHolder):
    '''Progresses the program state of the given ProgramStateHolder'''
    match pstate.get_state():
        case ProgramStates.INITIALIZATION:
            pstate.set_state(ProgramStates.FILE_FETCH)

        case ProgramStates.FILE_FETCH:
            pstate.set_state(ProgramStates.FILE_PROCESSING)

        case ProgramStates.FILE_PROCESSING:
            pstate.set_state(ProgramStates.REPORTING)

        case ProgramStates.REPORTING:
            pstate.set_state(ProgramStates.END)


def change_file_state(fstate: FileStateHolder):
    '''Progresses the file state of the given FileStateHolder'''
    match fstate.get_state():
        case FileStates.INITIALIZATION:
            fstate.set_state(FileStates.LOADING)

        case FileStates.LOADING:
            fstate.set_state(FileStates.SANITIZATION)

        case FileStates.SANITIZATION:
            fstate.set_state(FileStates.INSERT)

        case FileStates.INSERT:
            fstate.set_state(FileStates.END)

def change_insertion_state(istate: InsertionStateHolder, model: Schema):
    '''Progresses the insertion state of the given InsertionStateHolder'''
    match istate.get_state():
        case InsertionStates.INITIALIZATION:
            if model.staging_required:
                istate.set_state(InsertionStates.STAGING)
            else:
                istate.set_state(InsertionStates.INSERTION)

        case InsertionStates.STAGING:
            istate.set_state(InsertionStates.MERGING)

        case InsertionStates.MERGING:
            istate.set_state(InsertionStates.END)

        case InsertionStates.INSERTION:
            istate.set_state(InsertionStates.END)
