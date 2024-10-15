'''
    Test suite for the ConnectionPool object and other connection related methods
'''

import unittest
import os
from dotenv import load_dotenv

from utility.connection.connection_pool import ConnectionPool
from automation.schema_creation import create_hcdc_snapshot

class TestConnection(unittest.TestCase):
    '''Tests functionality of the ConnectionPool object'''
    def setUp(self):
        load_dotenv(override=True)
        self.connection_pool = ConnectionPool(
            os.getenv('USERNAME'),
            os.getenv('PASSWORD'),
            os.getenv('SERVER'),
            os.getenv('PORT'),
            os.getenv('DATABASE'),
            os.getenv('DRIVER')
        )


    def test_clear(self):
        '''Tests clearing of connection pool'''
        self.connection_pool.add_connection()
        self.connection_pool.add_connection()
        self.connection_pool.get_available_connection()
        self.connection_pool.clear()
        self.assertEqual(len(self.connection_pool.available_connections), 0)
        self.assertEqual(len(self.connection_pool.blocked_connections), 0)
        self.assertEqual(len(self.connection_pool.pool), 0)


    def test_connect(self):
        '''Tests creating a connection'''
        conn = self.connection_pool.get_connection()
        self.assertIsNotNone(conn)
        conn.close()


    def test_connection_pool_addition(self):
        '''Tests adding a connection to the pool'''
        self.connection_pool.add_connection()
        self.assertEqual(len(self.connection_pool.pool), 1)
        self.connection_pool.clear()


    def test_connection_pool_blocking(self):
        '''Tests blocking a connection via get_available_connection()'''
        self.connection_pool.add_connection()
        self.connection_pool.get_available_connection()
        self.assertEqual(len(self.connection_pool.blocked_connections), 1)
        self.connection_pool.clear()


    def test_connection_pool_overload(self):
        '''Tests adding connections past max_connections'''
        self.connection_pool.set_max_connections(1)
        self.connection_pool.add_connection()
        self.connection_pool.add_connection()
        self.assertEqual(len(self.connection_pool.pool), 1)
        self.connection_pool.set_max_connections(5)
        self.connection_pool.clear()


    def test_set_max_connections_fail(self):
        '''Tests setting max_connections to a value lower than # of current connections'''
        initial_max = self.connection_pool.max_connections
        self.connection_pool.add_connection()
        self.connection_pool.add_connection()
        self.connection_pool.set_max_connections(1)
        self.assertEqual(initial_max, self.connection_pool.max_connections)
        self.connection_pool.clear()
        self.connection_pool.set_max_connections(initial_max)


    def test_get_available_connection(self):
        '''Tests getting an available connection from the pool'''
        self.connection_pool.add_connection()
        conn = self.connection_pool.get_available_connection()
        self.assertIsNotNone(conn)
        self.connection_pool.clear()


    def test_free_connection(self):
        '''Tests freeing a connection in the blocked state'''
        self.connection_pool.add_connection()
        conn = self.connection_pool.get_available_connection()
        self.assertIn(conn, self.connection_pool.blocked_connections)
        self.connection_pool.free_connection(conn)
        self.assertIn(conn, self.connection_pool.available_connections)
        self.connection_pool.clear()

    def test_schema_creation(self):
        '''Tests creating a schema using a connection object'''
        self.connection_pool.add_connection()
        conn = self.connection_pool.get_available_connection()

        create_hcdc_snapshot.create('testHCDC', conn, self.connection_pool)

        after_conn = self.connection_pool.get_available_connection()

        cleanup_cursor = after_conn.cursor()
        cleanup_cursor.execute("show databases like 'testHCDC'")
        creation_check = cleanup_cursor.fetchall()
        cleanup_cursor.execute('drop database if exists testHCDC')
        self.assertEqual(conn, after_conn)
        self.assertNotEqual(self.connection_pool.database, 'testHCDC')
        self.assertNotEqual(0, len(creation_check))

        cleanup_cursor.close()


    def test_detect_all_blocked_connections(self):
        '''Tests if connection pool will detect if all connections are blocked'''
        self.connection_pool.set_max_connections(1)
        self.connection_pool.add_connection()
        self.connection_pool.get_available_connection()
        self.assertTrue(self.connection_pool.all_connections_blocked())
        self.connection_pool.clear()
        self.connection_pool.set_max_connections(5)
