"""
   Links execution functions to their respective execution stages. This design
   should allow for easy customization of program behavior.
"""

### External Imports ###

import logging
from datetime import datetime
import sys
import os

### Internal Imports ###

from automation.hcdc_datasets_gathering import download_hcdc
from config.flag_parser import FlagParser
from config.states import ProgramStateHolder, ProgramStates
from handler.state_handler import change_program_state
from utility.file.fetch import fetch_from_directory
from utility.file.fetch import hcdc_file_validation

### Function Declarations ###


def execute_program():
    """Starts the program execution process. Should be called from the main thread."""
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
                    format="%(asctime)s\t[%(levelname)s]\t%(message)s",
                    handlers=[
                        logging.FileHandler(
                            f"./logs/{datetime.now().strftime('debug_%Y%m%d_%H%M')}.log"
                        ),
                        logging.StreamHandler(sys.stdout),
                    ],
                )
                logging.debug("Entering debug mode...")
                logging.info("Initialization complete!")

            case ProgramStates.FILE_FETCH:
                logging.info("Fetching filepaths...")
                if parser.args.directory:
                    try:
                        filepaths = fetch_from_directory(
                            parser.args.directory,
                            parser.args.extension,
                            parser.args.recursive,
                            parser.args.depth,
                        )
                    except ValueError as e:
                        logging.error("Invalid argument supplied: %s", e)
                elif parser.args.file:
                    if os.path.exists(parser.args.file):
                        filepaths.append(parser.args.file)
                    else:
                        logging.error("Invalid filepath supplied: %s", parser.args.file)
                elif parser.args.hcdc:
                    try:
                        if parser.args.collect:
                            download_hcdc(
                                './data',
                                filings_daily=False,
                                dispos_daily=False,
                                filings_monthly=False,
                                dispos_monthly=False,
                                historical=True
                            )
                        filepaths = hcdc_file_validation(
                            parser.args.hcdc, parser.args.debug
                        )
                    except ValueError as e:
                        logging.error("Invalid argument supplied: %s", e)
                if len(filepaths) == 0:
                    logging.error("No files were found!")
                    sys.exit(1)

                logging.debug("%d files were found: %s", len(filepaths), filepaths)
                logging.info("%d files fetched", len(filepaths))

            case ProgramStates.FILE_PROCESSING:
                pass

            case ProgramStates.REPORTING:
                pass

        change_program_state(program_state)
