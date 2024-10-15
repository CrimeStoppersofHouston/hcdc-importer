'''
    This module contains the handler functions needed
    to change the states of program and file holder
    classes.
'''

### Internal Imports ###

from config.states import FileStates, ProgramStates, FileStateHolder, ProgramStateHolder

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
            fstate.set_state(FileStates.STAGING)

        case FileStates.STAGING:
            fstate.set_state(FileStates.MERGE)

        case FileStates.MERGE:
            fstate.set_state(FileStates.END)
