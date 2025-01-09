'''
   Links execution functions to their respective execution stages. This design
   should allow for easy customization of program behavior.
'''

### External Imports ###

import logging
import os
import sys
from datetime import datetime

### Internal Imports ###

from config.flag_parser import FlagParser
from config.states import ProgramStateHolder, ProgramStates
from handler.file_handler import handle_file
from handler.state_handler import change_program_state
from utility.file.fetch import fetch_from_directory

### Function Declarations ###


def execute_program():
    '''Starts the program execution process. Should be called from the main thread.'''
    filepaths = []
    parser = FlagParser()
    program_state = ProgramStateHolder()
    while program_state.get_state() != ProgramStates.END:
        match program_state.get_state():
            case ProgramStates.INITIALIZATION:
                for handler in logging.root.handlers[:]:
                    logging.root.removeHandler(handler)
                logging.basicConfig(
                    level=logging.INFO if not parser.args.debug else logging.DEBUG,
                    format='%(asctime)s\t[%(levelname)s]\t%(message)s',
                    handlers=[
                        logging.FileHandler(
                            f'./logs/{datetime.now().strftime('debug_%Y%m%d_%H%M')}.log'
                        ),
                        logging.StreamHandler(sys.stdout),
                    ],
                )
                logging.debug('Entering debug mode...')
                logging.info('Initialization complete!')

            case ProgramStates.FILE_FETCH:
                logging.info('Fetching filepaths...')
                if parser.args.directory:
                    try:
                        filepaths = fetch_from_directory(
                            parser.args.directory,
                            parser.args.extensions,
                            parser.args.recursive,
                            parser.args.depth,
                        )
                    except ValueError as e:
                        logging.error('Invalid argument supplied: %s', e)
                elif parser.args.file:
                    if os.path.exists(parser.args.file):
                        filepaths.append(parser.args.file)
                    else:
                        logging.error('Invalid filepath supplied: %s', parser.args.file)
                if len(filepaths) == 0:
                    logging.error('No files were found!')
                    sys.exit(1)

                logging.debug('%d files were found: %s', len(filepaths), filepaths)
                logging.info('%d files fetched', len(filepaths))

            case ProgramStates.FILE_PROCESSING:
                handle_file(filepaths)


            case ProgramStates.REPORTING:
                pass

            case _:
                logging.error('Program state %s unaccounted for! Exiting...', program_state.get_state())
                exit(1)

        change_program_state(program_state)
