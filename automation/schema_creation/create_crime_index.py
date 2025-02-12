'''
This module is meant to be used to create a new instance of the crime index database.
It includes a creation statement and a creation function for this purpose.
'''

### External Imports ###

import contextlib

import pyodbc

### Internal Imports ###

from utility.connection.connection_pool import ConnectionPool

### Variable Declarations ###

CREATE_STMT = """
create table data if not exists (
	year int,
    month int, 
    type varchar(20),
    reportingYear int,
    reportingMonth int,
    category varchar(50),
    count int,
    primary key (year, month, type, reportingYear, reportingMonth, category)
);
"""

def create(
    schema_name: str, connection: pyodbc.Connection, connection_pool: ConnectionPool
) -> None:
    '''Creates a new crim eindex database with a predefined creation statement'''
    with contextlib.closing(connection.cursor()) as cursor:
        cursor.execute(f'create database if not exists {schema_name}')
        cursor.commit()

        old_database = connection_pool.database
        connection_pool.set_database(schema_name)
        new_connection = connection_pool.get_connection()
        new_cursor = new_connection.cursor()
        new_cursor.execute(f'use {schema_name};')
        new_cursor.commit()
        for statement in CREATE_STMT.split(';'):
            if statement.strip() == '':
                continue
            new_cursor.execute(statement)
        new_cursor.commit()
        new_connection.close()

        connection_pool.set_database(old_database)
        connection_pool.free_connection(connection)