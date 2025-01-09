'''
    This file should handle the insertion process for all
    import types and ideally be the main area where connections
    are created for the database in the import process
'''

### External Imports ###

import logging
import threading
import pandas as pd

### Internal Imports ###

from config.import_type import ImportType
from config.states import InsertionStates, InsertionStateHolder
from utility.connection.connection_pool import ConnectionPool
from utility.connection.cursor_actions import insert_to_table, insert_to_stage_table, merge_from_stage_table
from utility.progress_tracking import ProgressTracker
from handler.state_handler import change_insertion_state


### Function Declarations ###

def handle_insert(df: pd.DataFrame, connection_pool: ConnectionPool, tracker: ProgressTracker):
    import_type = ImportType()
    insertion_state = InsertionStateHolder()
    while insertion_state.get_state() != InsertionStates.END:
        match insertion_state.get_state():
            case InsertionStates.INITIALIZATION:
                pass

            # If staging is not required, stage will skip down to INSERTION
            case InsertionStates.STAGING:
                tracker.clear()
                logging.info('Inserting to stage tables')
                tracker.update(True)
                threads = []
                while not import_type.model.is_completed():
                    table = import_type.model.get_available_table()
                    # If there are no tables or all connections are blocked,
                    # join the thread at the front of the queue and loop around
                    if (
                        table is None or
                        connection_pool.all_connections_blocked()
                    ):
                        if len(threads) > 0:
                            threads.pop().join()
                        continue

                    # If there are no connections and there is still room for one,
                    # create a connection
                    if (
                        len(connection_pool.available_connections) == 0
                        and len(connection_pool.pool) < connection_pool.max_connections
                    ):
                        connection_pool.add_connection()

                    # If there is an available connection, handle the table retrieved earlier
                    if len(connection_pool.available_connections) > 0:
                        connection = connection_pool.get_available_connection()
                        t = threading.Thread(
                            target=insert_to_stage_table,
                            args=[connection_pool, connection, df, import_type.model, table, tracker]
                        )
                        threads.insert(0, t)
                        t.start()

                connection_pool.clear()
                tracker.clear()
                logging.info('Finished inserting to stage tables')
                tracker.update(True)
                import_type.model.reset_schema()

            case InsertionStates.MERGING:
                tracker.clear()
                logging.info('Merging to final tables')
                tracker.update(True)

                threads = []
                while not import_type.model.is_completed():
                    table = import_type.model.get_available_table()
                    # If there are no tables or all connections are blocked,
                    # join the thread at the front of the queue and loop around
                    if (
                        table is None or
                        connection_pool.all_connections_blocked()
                    ):
                        if len(threads) > 0:
                            threads.pop().join()
                        continue

                    # If there are no connections and there is still room for one,
                    # create a connection
                    if (
                        len(connection_pool.available_connections) == 0
                        and len(connection_pool.pool) < connection_pool.max_connections
                    ):
                        connection_pool.add_connection()

                    # If there is an available connection, handle the table retrieved earlier
                    if len(connection_pool.available_connections) > 0:
                        connection = connection_pool.get_available_connection()
                        t = threading.Thread(
                            target = merge_from_stage_table,
                            args=[connection_pool, connection, import_type.model, table, tracker]
                        )
                        threads.insert(0, t)
                        t.start()

                connection_pool.clear()
                tracker.clear()
                logging.info('Finished merging into final tables')
                import_type.model.reset_schema()

            case InsertionStates.INSERTION:
                tracker.clear()
                logging.info('Inserting data into tables')
                tracker.update(True)

                threads = []
                while not import_type.model.is_completed():
                    table = import_type.model.get_available_table()
                    # If there are no tables or all connections are blocked,
                    # join the thread at the front of the queue and loop around
                    if (
                        table is None or
                        connection_pool.all_connections_blocked()
                    ):
                        if len(threads) > 0:
                            threads.pop().join()
                        continue

                    # If there are no connections and there is still room for one,
                    # create a connection
                    if (
                        len(connection_pool.available_connections) == 0
                        and len(connection_pool.pool) < connection_pool.max_connections
                    ):
                        connection_pool.add_connection()

                    # If there is an available connection, handle the table retrieved earlier
                    if len(connection_pool.available_connections) > 0:
                        connection = connection_pool.get_available_connection()
                        t = threading.Thread(
                            target = insert_to_table,
                            args=[connection_pool, connection, df, import_type.model, table, tracker]
                        )
                        threads.insert(0, t)
                        t.start()

                connection_pool.clear()
                tracker.clear()
                logging.info('Finished insertion into all tables')
                import_type.model.reset_schema()

            case _:
                logging.error('Insertion state %s unaccounted for! Exiting...')
                exit(1)
        
        change_insertion_state(insertion_state, import_type.model)
        