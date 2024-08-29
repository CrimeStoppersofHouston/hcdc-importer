import unittest
import os
import pyodbc
from dotenv import load_dotenv

from utility.connection.connectionPool import ConnectionPool
from automation.schema_creation import create_hcdc_snapshot

class TestConnection(unittest.TestCase):
    def setUp(self):
        load_dotenv(override=True)
        self.connectionPool = ConnectionPool(
            os.getenv('USERNAME'),
            os.getenv('PASSWORD'),
            os.getenv('SERVER'),
            os.getenv('PORT'),
            os.getenv('DATABASE'),
            os.getenv('DRIVER')
        )


    def testClear(self):
        self.connectionPool.addConnection()
        self.connectionPool.addConnection()
        self.connectionPool.getAvailableConnection()
        self.connectionPool.clear()
        self.assertEqual(len(self.connectionPool.availableConnections), 0)
        self.assertEqual(len(self.connectionPool.blockedConnections), 0)
        self.assertEqual(len(self.connectionPool.pool), 0)


    def testConnect(self):
        conn = self.connectionPool.getConnection()
        self.assertIsNotNone(conn)
        conn.close()


    def testConnectionPoolAddition(self):
        self.connectionPool.addConnection()
        self.assertEqual(len(self.connectionPool.pool), 1)
        self.connectionPool.clear()


    def testConnectionPoolBlocking(self):
        self.connectionPool.addConnection()
        conn = self.connectionPool.getAvailableConnection()
        self.assertEqual(len(self.connectionPool.blockedConnections), 1)
        self.connectionPool.clear()


    def testConnectionPoolBlockFail(self):
        self.connectionPool.addConnection()
        conn = self.connectionPool.getAvailableConnection()
        self.assertIsNone(self.connectionPool.getAvailableConnection())
        self.connectionPool.clear()


    def testConnectionPoolOverload(self):
        self.connectionPool.setMaxConnections(1)
        self.connectionPool.addConnection()
        self.connectionPool.addConnection()
        self.assertEqual(len(self.connectionPool.pool), 1)
        self.connectionPool.setMaxConnections(5)
        self.connectionPool.clear()


    def testSetMaxConnectionsFail(self):
        initialMax = self.connectionPool.max_connections
        self.connectionPool.addConnection()
        self.connectionPool.addConnection()
        self.connectionPool.setMaxConnections(1)
        self.assertEqual(initialMax, self.connectionPool.max_connections)
        self.connectionPool.clear()
        self.connectionPool.setMaxConnections(initialMax)


    def testGetAvailableConnection(self):
        self.connectionPool.addConnection()
        conn = self.connectionPool.getAvailableConnection()
        self.assertIsNotNone(conn)
        self.connectionPool.clear()


    def testFreeConnection(self):
        self.connectionPool.addConnection()
        conn = self.connectionPool.getAvailableConnection()
        self.assertIn(conn, self.connectionPool.blockedConnections)
        self.connectionPool.freeConnection(conn)
        self.assertIn(conn, self.connectionPool.availableConnections)
        self.connectionPool.clear()

    def testSchemaCreation(self):
        self.connectionPool.addConnection()
        conn = self.connectionPool.getAvailableConnection()

        create_hcdc_snapshot.create('testHCDC', conn, self.connectionPool)

        afterConn = self.connectionPool.getAvailableConnection()

        cleanupCursor = afterConn.cursor()
        cleanupCursor.execute("show databases like 'testHCDC'")
        creationCheck = cleanupCursor.fetchall()
        cleanupCursor.execute('drop database if exists testHCDC')
        self.assertEqual(conn, afterConn)
        self.assertNotEqual(self.connectionPool.database, 'testHCDC')
        self.assertNotEqual(0, len(creationCheck))

        cleanupCursor.close()