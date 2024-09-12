'''
    This module contains the functions needed to handle pyodbc connection cursor
    actions including insertion and merging of data into the database
'''

### External Imports ###

import logging
from contextlib import closing

import pyodbc
import pandas as pd

### Internal Imports ###

from utility.conversion_functions import convert_to_sql
from utility.connection.connection_pool import ConnectionPool
from model.database.database_model import Schema, Table

### Function Declarations ###

def execute_sql(cursor: pyodbc.Cursor, sql: str, max_retries: int = 5, attempt: int = 0):
    '''
        Executes a SQL statement using the given cursor and retries on fail 
        until maximum retries are reached.
    '''
    if attempt > max_retries:
        logging.debug('SQL statement failed!: %s', sql)
        raise RecursionError('Maximum retries reached for SQL statement')
    else:
        try:
            cursor.execute(sql)
        except:
            execute_sql(cursor, sql, max_retries, attempt+1)


def reset_stage_table(cursor:pyodbc.Cursor, schema: Schema, table: Table) -> None:
    '''
        Clears a table's data by dropping and remaking it. This should
        only be done with a prep table as it will not retain foreign relationships
    '''
    logging.debug('Resetting stage table: %s', table.name)
    execute_sql(cursor, f'RENAME table {schema.name}.stage_{table.name} to {schema.name}.t1')
    logging.debug('stage_%s prepared for deletion', table.name)
    execute_sql(cursor, f'create table {schema.name}.stage_{table.name} like {schema.name}.t1')
    logging.debug('Created empty stage_%s', table.name)
    execute_sql(cursor, f'drop table {schema.name}.t1')
    execute_sql(cursor, f'alter table {schema.name}.stage_{table.name} auto_increment = 1')
    logging.debug('stage_%s cleared!', table.name)


def insert_to_stage_table(
    connection_pool: ConnectionPool,
    connection: pyodbc.Connection,
    df: pd.DataFrame,
    schema: Schema,
    table: Table,
    progress_tracker = None,
    limit = 1000
) -> None:
    '''
        Inserts data from a dataframe given a connection object, a schema, 
        and the stage table to insert into. 
        Intended to work with the ConnectionPool object. Frees connection at
        the end of execution.
    '''
    total_rows = len(df)
    column_keys = [column.name for column in table.columns]
    sql = f'INSERT INTO {schema.name}.stage_{table.name} ({",".join(column_keys)}) VALUES '
    
    with closing(connection.cursor()) as cursor:
        reset_stage_table(cursor, schema, table)
        logging.info('Starting insertion for table stage_%s', table.name)
        rows = []
        for index, row in df.iterrows():
            if index % limit == 0 and index != 0:
                if len(rows) != 0:
                    execute_sql(
                        cursor,
                        f'{sql}{",".join(rows)} ON DUPLICATE KEY UPDATE `{column_keys[0]}`=`{column_keys[0]}`;'
                    )
                    # progress tracker update
                rows = []
            insert = [row[col] for col in column_keys]
            if any(insert):
                sql_string = convert_to_sql(insert)
                rows.append(sql_string)
        if len(rows) != 0:
            execute_sql(
                cursor, 
                f'{sql}{",".join(rows)} ON DUPLICATE KEY UPDATE `{column_keys[0]}`=`{column_keys[0]}`;'
            )
        cursor.commit()
        logging.info('Table %s successfully inserted!', table)
        schema.advance_table_state(table)
        connection_pool.free_connection(connection)
