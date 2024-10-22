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
import threading

### Internal Imports ###

from automation.schema_creation import create_hcdc_snapshot
from config.flag_parser import FlagParser
from config.states import FileStateHolder, FileStates
from handler.state_handler import change_file_state
from model.database import hcdc_snapshot
from utility.connection.connection_pool import ConnectionPool
from utility.connection.cursor_actions import insert_to_stage_table, insert_to_final_table
from utility.file.load import load_dataframe_csv, load_dataframe_excel
from utility.progress_tracking import ProgressTracker, Task

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
    if not parser.args.skipCreation:
        match parser.args.type:
            case "hcdc":
                connection_pool.add_connection()
                conn = connection_pool.get_available_connection()
                create_hcdc_snapshot.create(os.getenv("DATABASE"), conn, connection_pool)
                connection_pool.clear()
            case _:
                logging.error('Unimplemented type : %s', parser.args.type)
                raise ValueError(f"Unimplemented type :{parser.args.type}")

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
                    tracker = ProgressTracker(
                        f'File {i+1}: {os.path.basename(current_filepath)[:40]}...'
                    )
                    loading_task = Task('Loading', 1)
                    tracker.add_task(loading_task)
                    tracker.update()

                    match os.path.splitext(current_filepath)[1]:
                        case ".xlsx":
                            df = load_dataframe_excel(current_filepath)
                        case ".csv":
                            df = load_dataframe_csv(
                                current_filepath, parser.args.delimiter, parser.args.encoding
                            )
                        case ".txt":
                            df = load_dataframe_csv(
                                current_filepath, parser.args.delimiter, parser.args.encoding
                            )
                        case _:
                            logging.error(
                                "Unsupported file extension: %s", 
                                os.path.splitext(current_filepath)[1]
                            )
                            file_state.set_state(FileStates.END)
                    tracker.clear()
                    logging.info("%s loaded successfully!", current_filepath)
                    loading_task.add_progress(1)
                    tracker.update(True)

                case FileStates.SANITIZATION:
                    tracker.clear()
                    logging.info("Sanitizing columns for insertion...")
                    tracker.update(True)
                    match parser.args.type:
                        case "hcdc":
                            conversion_dict = hcdc_snapshot.database.get_conversion_dict()
                            sanitization_task = Task('Converting columns', len(conversion_dict))
                            tracker.add_task(sanitization_task)
                            for column, conversion_func in conversion_dict.items():
                                df[column] = df[column].apply(conversion_func)
                                sanitization_task.add_progress(1)
                                tracker.update()
                            model = hcdc_snapshot.database
                            model.name = os.getenv("DATABASE")
                        case _:
                            raise ValueError(
                                f"Unimplemented format: {parser.args.type}"
                            )
                    tracker.clear()
                    logging.info("All columns sanitized!")
                    tracker.update(True)

                case FileStates.STAGING:
                    tracker.clear()
                    logging.info("Inserting to stage tables")
                    tracker.update(True)
                    threads = []
                    while not model.is_completed():
                        table = model.get_available_table()
                        if (
                            table is None or
                            connection_pool.all_connections_blocked()
                        ):
                            if len(threads) > 0:
                                threads.pop().join()
                            continue

                        if (
                            len(connection_pool.available_connections) == 0
                            and len(connection_pool.pool) < connection_pool.max_connections
                        ):
                            connection_pool.add_connection()

                        if len(connection_pool.available_connections) > 0:
                            connection = connection_pool.get_available_connection()
                            t = threading.Thread(
                                target=insert_to_stage_table,
                                args=[connection_pool, connection, df, model, table, tracker]
                            )
                            threads.insert(0, t)
                            t.start()

                    connection_pool.clear()
                    tracker.clear()
                    logging.info("Finished inserting to stage tables")
                    tracker.update(True)
                    model.reset_schema()

                case FileStates.MERGE:
                    tracker.clear()
                    logging.info("Merging to final tables, blocked conns")
                    tracker.update(True)

                    threads = []
                    while not model.is_completed():
                        table = model.get_available_table()
                        if (
                            table is None or
                            connection_pool.all_connections_blocked()
                        ):
                            if len(threads) > 0:
                                threads.pop().join()
                            continue

                        if (
                            len(connection_pool.available_connections) == 0
                            and len(connection_pool.pool) < connection_pool.max_connections
                        ):
                            connection_pool.add_connection()

                        if len(connection_pool.available_connections) > 0:
                            connection = connection_pool.get_available_connection()
                            t = threading.Thread(
                                target = insert_to_final_table,
                                args=[connection_pool, connection, model, table, tracker]
                            )
                            threads.insert(0, t)
                            t.start()

                    connection_pool.clear()
                    model.reset_schema()
                    tracker.clear()
                    logging.info("Finished merging into final tables")

            change_file_state(file_state)
