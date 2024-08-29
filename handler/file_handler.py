"""
# @ Author: Ryan Barnes
# @ Create Time: 2024-05-30 12:17:51
# @ Modified by: Ryan Barnes
# @ Modified time: 2024-05-30 12:18:17
# @ Description:
       This file should contain functions that handle the
       flow of the program. Additional responisibilities
       should be handed off to other files, such as insertion
       and sanitization.
"""

### External Imports ###

import logging
import os

### Internal Imports ###

from config.flag_parser import FlagParser
from config.states import FileStateHolder, FileStates
from handler.state_handler import change_file_state
from model.database import hcdc_snapshot
from utility.connection.connectionPool import ConnectionPool
from utility.file.fileload import loadDataframeCSV, loadDataframeXLSX
from automation.schema_creation import create_hcdc_snapshot

### Function Declarations ###


def handle_file(filepaths):
    """Takes a filepath and imports it into the database"""
    parser = FlagParser()
    connection_pool = ConnectionPool(
        os.getenv("USERNAME"),
        os.getenv("PASSWORD"),
        os.getenv("SERVER"),
        os.getenv("PORT"),
        os.getenv("DATABASE"),
        os.getenv("DRIVER"),
    )
    match parser.args.type:
        case "hcdc":
            connection_pool.addConnection()
            conn = connection_pool.getAvailableConnection()
            create_hcdc_snapshot.create(os.getenv("DATABASE"), conn, connection_pool)
            connection_pool.clear()

    for i, current_filepath in enumerate(filepaths):
        file_state = FileStateHolder()
        file_state.set_state(FileStates.INITIALIZATION)
        current_filepath = filepaths[i]
        model = None
        df = None
        logging.info(
            "Handling file %d of %d: %s", i + 1, len(filepaths), current_filepath
        )
        while file_state.get_state() != FileStates.END:
            match file_state.get_state():
                case FileStates.INITIALIZATION:
                    pass

                case FileStates.LOADING:
                    logging.info("Loading file...")
                    match os.path.splitext(current_filepath)[1]:
                        case "xlsx":
                            df = loadDataframeXLSX(current_filepath)
                        case "csv":
                            df = loadDataframeCSV(
                                current_filepath, parser.args.delimiter
                            )
                        case "txt":
                            df = loadDataframeCSV(
                                current_filepath, parser.args.delimiter
                            )
                        case _:
                            logging.error(
                                "Unsupported file extension: %s", 
                                os.path.splitext(current_filepath)[1]
                            )
                            file_state.set_state(FileStates.END)
                    logging.info("%s loaded successfully!", current_filepath)

                case FileStates.SANITIZATION:
                    logging.info("Sanitizing columns for insertion...")
                    match parser.args.type:
                        case "hcdc":
                            conversion_dict = hcdc_snapshot.database.getConversionDict()
                            for column, conversion_func in conversion_dict.items():
                                df[column] = df[column].apply(conversion_func)
                            model = hcdc_snapshot.database
                        case _:
                            raise ValueError(
                                f"Unimplemented format: {parser.args.type}"
                            )
                    logging.info("All columns sanitized!")

                case FileStates.STAGING:
                    while not model.isCompleted():
                        table = model.getAvailableTable()
                        if table is None:
                            continue

                        if (
                            len(connection_pool.availableConnections) == 0
                            and len(connection_pool.pool) < connection_pool.max_connections
                        ):
                            connection_pool.addConnection()

                        if connection_pool.availableConnections > 0:
                            pass
                            # connection = connection_pool.getAvailableConnection()
                            # threading.run(insert(df, table, conneciton, connection_pool))

                    connection_pool.clear()

                case FileStates.MERGE:
                    while not model.isCompleted():
                        table = model.getAvailableTable()
                        if table is None:
                            continue

                        if (
                            len(connection_pool.availableConnections) == 0
                            and len(connection_pool.pool) < connection_pool.max_connections
                        ):
                            connection_pool.addConnection()

                        if connection_pool.availableConnections > 0:
                            pass
                            # connection = connection_pool.getAvailableConnection()
                            # threading.run(merge(df, table, conneciton, connection_pool))

                    connection_pool.clear()

            change_file_state(file_state)
