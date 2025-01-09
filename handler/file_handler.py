'''
       This module should contain functions that handle the
       flow of file handling. Additional responisibilities
       should be handed off to other files, such as insertion
       and merging
'''

### External Imports ###

import logging
import os
import threading

### Internal Imports ###

from config.flag_parser import FlagParser
from config.states import FileStateHolder, FileStates
from config.import_type import ImportType
from handler.state_handler import change_file_state
from utility.connection.connection_pool import ConnectionPool
from utility.file.load import load_dataframe_csv, load_dataframe_excel
from utility.progress_tracking import ProgressTracker, Task
from handler.insertion_handler import handle_insert

### Function Declarations ###

def handle_file(filepaths):
    '''Takes a filepath and imports it into the database'''
    parser = FlagParser()
    import_type = ImportType()
    connection_pool = ConnectionPool(
        os.getenv('USERNAME'),
        os.getenv('PASSWORD'),
        os.getenv('SERVER'),
        os.getenv('PORT'),
        os.getenv('DEFAULT_DATABASE'),
        os.getenv('DRIVER'),
    )

    import_type.model.set_name(os.getenv('WORKING_DATABASE'))
    if parser.args.createDatabase:
        connection_pool.add_connection()
        conn = connection_pool.get_available_connection()
        import_type.model.create(conn, connection_pool)
        connection_pool.clear()
    connection_pool.set_database(import_type.model.name)

    for i, current_filepath in enumerate(filepaths):
        file_state = FileStateHolder()
        file_state.set_state(FileStates.INITIALIZATION)
        current_filepath = filepaths[i]
        model = None
        df = None
        logging.info(
            'Handling file %d of %d: %s', i + 1, len(filepaths), current_filepath
        )
        while file_state.get_state() != FileStates.END:
            match file_state.get_state():
                case FileStates.INITIALIZATION:
                    pass

                case FileStates.LOADING:
                    logging.info('Loading file...')
                    tracker = ProgressTracker(
                        f'File {i+1}: {os.path.basename(current_filepath)[:40]}...'
                    )
                    loading_task = Task('Loading', 1)
                    tracker.add_task(loading_task)
                    tracker.update()
                    logging.debug(os.path.splitext(current_filepath)[-1:][0])
                    match os.path.splitext(current_filepath)[-1:][0]:
                        case '.xlsx':
                            df = load_dataframe_excel(current_filepath)
                        case '.csv':
                            df = load_dataframe_csv(
                                current_filepath, parser.args.delimiter, parser.args.encoding
                            )
                        case '.txt':
                            df = load_dataframe_csv(
                                current_filepath, parser.args.delimiter, parser.args.encoding
                            )
                        case _:
                            logging.error(
                                'Unsupported file extension: %s', 
                                os.path.splitext(current_filepath)[1]
                            )
                            file_state.set_state(FileStates.END)
                            break
                    tracker.clear()
                    logging.info('%s loaded successfully!', current_filepath)
                    loading_task.add_progress(1)
                    tracker.update(True)

                case FileStates.SANITIZATION:
                    tracker.clear()
                    logging.info('Sanitizing columns for insertion...')
                    tracker.update(True)

                    sanitization_task = Task('Converting columns', len(import_type.model.get_conversion_dict()))
                    tracker.add_task(sanitization_task)
                    for column, conversion_func in import_type.model.get_conversion_dict().items():
                        df[column] = df[column].apply(conversion_func)
                        sanitization_task.add_progress(1)
                        tracker.update()

                case FileStates.INSERT:
                    handle_insert(df, connection_pool, tracker)

                case _:
                    logging.error('File state %s unaccounted for! Exiting...', file_state.get_state())
                    exit(1)

            change_file_state(file_state)
