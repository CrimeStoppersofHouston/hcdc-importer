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
    match pstate.getState():
        case ProgramStates.INITIALIZATION:
            pstate.setState(ProgramStates.FILE_FETCH)

        case ProgramStates.FILE_FETCH:
            pstate.setState(ProgramStates.FILE_PROCESSING)

        case ProgramStates.FILE_PROCESSING:
            pstate.setState(ProgramStates.REPORTING)

        case ProgramStates.REPORTING:
            pstate.setState(ProgramStates.END)


def change_file_state(fstate: FileStateHolder):
    '''Progresses the file state of the given FileStateHolder'''
    match fstate.getState():
        case FileStates.INITIALIZATION:
            fstate.setState(FileStates.SANITIZATION)

        case FileStates.LOADING:
            fstate.setState(FileStates.SANITIZATION)

        case FileStates.SANITIZATION:
            fstate.setState(FileStates.STAGING)

        case FileStates.STAGING:
            fstate.setState(FileStates.MERGE)

        case FileStates.MERGE:
            fstate.setState(FileStates.END)
