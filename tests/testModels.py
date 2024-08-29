import unittest
import numpy as np

from model.database.database_model import Schema, Table, Column
from utility.conversionFunctions import convertToInteger, convertToString, convertToDatetime, convertSPN
from datetime import datetime


class TestModels(unittest.TestCase):
    def setUp(self):
        pass

    
    def testAddTable(self):
        schema = Schema('Sample Schema')
        table = Table('Sample Table')
        schema.addTable(table)
        self.assertIn(table, schema.tables)
        self.assertIn(table, schema.pendingTables)


    def testAddColumn(self):
        table = Table('Sample Table')
        col = Column('Sample Column', 'Sample Name', int)
        table.addColumn(col)
        self.assertIn(col, table.columns)


    def testPrerequisites(self):
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        table2.addPrereq(table1)

        schema.addTable(table1)
        schema.addTable(table2)

        result = schema.getAvailableTable()
        self.assertIs(result, table1)

    
    def testAdvanceTable(self):
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        table2.addPrereq(table1)

        schema.addTable(table1)
        schema.addTable(table2)

        currentTable = schema.getAvailableTable()
        self.assertIn(currentTable, schema.processingTables)
        self.assertIsNone(schema.getAvailableTable())

        schema.advanceTableState(currentTable)
        self.assertIn(currentTable, schema.completedTables)
        self.assertIs(schema.getAvailableTable(), table2)


    def testCompletionOfTable(self):
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')

        schema.addTable(table1)

        currentTable = schema.getAvailableTable()
        schema.advanceTableState(currentTable)
        self.assertTrue(schema.isCompleted())


    def testMultiplePrereqs(self):
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')
        table3 = Table('Sample Table 3')

        prereqs = {table1, table3}

        table2.addPrereq(table1)
        table2.addPrereq(table3)

        schema.addTable(table1)
        schema.addTable(table2)
        schema.addTable(table3)

        handled1 = schema.getAvailableTable()
        handled2 = schema.getAvailableTable()
        self.assertSetEqual(schema.processingTables, prereqs)
        self.assertIsNone(schema.getAvailableTable())

        schema.advanceTableState(handled1)
        schema.advanceTableState(handled2)

        self.assertSetEqual(schema.completedTables, prereqs)
        handled3 = schema.getAvailableTable()
        self.assertIs(handled3, table2)

        
    def testResetSchema(self):
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        schema.addTable(table1)
        schema.addTable(table2)

        handled1 = schema.getAvailableTable()
        handled2 = schema.getAvailableTable()

        schema.advanceTableState(handled1)
        schema.advanceTableState(handled2)

        schema.resetSchema()

        self.assertSetEqual(schema.tables, schema.pendingTables)


    def testSearchTable(self):
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        schema.addTable(table1)
        schema.addTable(table2)

        self.assertEqual(schema.getTablebyName('Sample Table 1'), table1)
        self.assertEqual(schema.getTablebyName('Sample Table 2'), table2)
        
        
    def testGetTableConversionDict(self):
        table1 = Table('Sample Table 1').addColumn(
            Column('int', 'intnew', int)
        ).addColumn(
            Column('string', 'stringnew', str)   
        ).addColumn(
            Column('datetime', 'datetimenew', np.datetime64)
        )
        
        expected = {
            'int': convertToInteger,
            'string': convertToString,
            'datetime': convertToDatetime
        }
        
        self.assertDictEqual(table1.getConversionDict(), expected)
        
    
    def testGetSchemaConversionDict(self):
        schema = Schema('Sample Schema').addTable(
            Table('Sample Table 1').addColumn(
                Column('int', 'intnew', int)
            ).addColumn(
                Column('string', 'stringnew', str)   
            ).addColumn(
                Column('datetime', 'datetimenew', np.datetime64)
            )
        ).addTable(
            Table('Sample Table 1').addColumn(
                Column('int', 'intnew', int)
            ).addColumn(
                Column('spn', 'spnnew', str, conversionFunction= convertSPN)   
            ).addColumn(
                Column('datetime', 'datetimenew', np.datetime64)
            )
        )
        
        expected = {
            'int': convertToInteger,
            'string': convertToString,
            'spn': convertSPN,
            'datetime': convertToDatetime
        }
        
        self.assertDictEqual(schema.getConversionDict(),expected)
        
    @unittest.expectedFailure
    def testSharedColumnConflict(self):
        schema = Schema('Sample Schema').addTable(
            Table('Sample Table 1').addColumn(
                Column('int', 'intnew', int)
            ).addColumn(
                Column('string', 'stringnew', str)   
            ).addColumn(
                Column('datetime', 'datetimenew', np.datetime64)
            )
        ).addTable(
            Table('Sample Table 1').addColumn(
                Column('int', 'intnew', int)
            ).addColumn(
                Column('spn', 'spnnew', str, conversionFunction= convertSPN)   
            ).addColumn(
                Column('datetime', 'datetimenew', int)
            )
        )
        
        schema.getConversionDict()