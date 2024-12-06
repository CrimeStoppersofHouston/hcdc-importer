'''
    This module contains the class needed to create,
    maintain, and remove connections with the mysql server
    in order to allow for multi-threaded inserts.
'''

### External Imports ###

import logging

import pyodbc

### Class Declarations ###


class ConnectionPool:
    '''Manages a connection pool of pyodbc connections'''

    def __init__(
        self,
        username: str,
        password: str,
        server: str,
        port: int,
        database: str,
        driver: str,
        max_connections: int = 5,
    ):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.database = database
        self.driver = driver

        self.pool = set()
        self.blocked_connections = set()
        self.available_connections = set()
        self.max_connections = max_connections

    def set_max_connections(self, max_connections: int) -> None:
        '''Sets the meximum number of connections that can be created'''
        if max_connections < len(self.pool):
            logging.warning(
                'Cannot set max connections to %d, %d connections are currently active',
                max_connections,
                len(self.pool),
            )
            return None
        self.max_connections = max_connections

    def all_connections_blocked(self) -> bool:
        '''Returns True if all connections are blocked'''
        return len(self.blocked_connections) == self.max_connections

    def get_connection(self, max_retries: int = 5) -> pyodbc.Connection:
        '''Returns a pyodbc connection object'''
        connection = None
        for tries in range(max_retries):
            try:
                connection = pyodbc.connect(
                    f'Driver={self.driver};'
                    f'Server={self.server};'
                    f'Port={self.port}'
                    f'Database={self.database};'
                    f'Uid={self.username};'
                    f'Pwd={self.password};'
                    'Encrypt=yes;Connection Timeout=100;MULTI_HOST=1;',
                    autocommit=False,
                )
                logging.debug(
                    'Connection to %s established on try %d', self.database, tries + 1
                )
                return connection
            except Exception as e:
                logging.debug('Error getting connection: %s', e)
        if connection is None:
            raise ConnectionError('Failed to establish connection to database')
        return connection

    def set_database(self, database: str):
        '''Sets the database to connect to. Does not change databases of current connections.'''
        self.database = database

    def add_connection(self):
        '''Creates a new connection and adds it to the connection pool'''
        if len(self.pool) >= self.max_connections:
            logging.warning(
                'Cannot add connection to pool, max connections has been reached!'
            )
            return None
        connection = self.get_connection()
        self.pool.add(connection)
        self.available_connections.add(connection)

    def remove_connection(self, connection: pyodbc.Connection) -> None:
        '''Removes the given connection from the pool'''
        if connection not in self.pool:
            logging.error(
                'Connection failed to be removed from pool: not present in pool'
            )
            raise ValueError
        if connection in self.blocked_connections:
            logging.error(
                'Connection cannot be removed from pool: connection blocked for execution'
            )
            raise KeyError
        if connection not in self.available_connections:
            logging.warning(
                'Connection cannot be removed from pool: \
                connection not found in available state or blocked state'
            )
            raise KeyError
        self.available_connections.remove(connection)
        self.pool.remove(connection)
        connection.close()
        logging.debug('Connection successfully removed from pool')

    def get_available_connection(self) -> pyodbc.Connection:
        '''Returns an available connection from the pool'''
        if len(self.available_connections) < 1:
            logging.warning('There are no available connections!')
            return None
        connection = self.available_connections.pop()
        self.blocked_connections.add(connection)
        return connection

    def free_connection(self, connection: pyodbc.Connection) -> None:
        '''Removes the given connection from the set of blocked connections'''
        if connection not in self.blocked_connections:
            logging.error('Connection cannot be freed: connection not in blocked set!')
            raise ValueError
        self.blocked_connections.remove(connection)
        self.available_connections.add(connection)

    def clear(self) -> None:
        '''Closes and removes all connections, regardless of state'''
        self.available_connections.clear()
        self.blocked_connections.clear()
        while len(self.pool) > 0:
            self.pool.pop().close()
