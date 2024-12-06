'''
    Test suite for schema models
'''

import unittest
import numpy as np

from model.database.database_model import Schema, Table, Column
from utility.conversion_functions import (
    convert_to_datetime,
    convert_to_integer,
    convert_to_string,
    convert_to_spn,
)


class TestModels(unittest.TestCase):
    '''Tests functionality of schema, table, and row ojects'''
    def test_add_table(self):
        '''Tests adding a Table to a Schema'''
        schema = Schema('Sample Schema')
        table = Table('Sample Table')
        schema.add_table(table)
        self.assertIn(table, schema.tables)
        self.assertIn(table, schema.pending_tables)


    def test_add_column(self):
        '''Tests adding a Column to a Table'''
        table = Table('Sample Table')
        col = Column('Sample Column', 'Sample Name', int)
        table.add_column(col)
        self.assertIn(col, table.columns)


    def test_prerequisites(self):
        '''Tests prerequisite blocking'''
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        table2.add_prereq(table1)

        schema.add_table(table1)
        schema.add_table(table2)

        result = schema.get_available_table()
        self.assertIs(result, table1)


    def test_advance_table(self):
        '''Tests advancing a table to completion with prereqs'''
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        table2.add_prereq(table1)

        schema.add_table(table1)
        schema.add_table(table2)

        current_table = schema.get_available_table()
        self.assertIn(current_table, schema.processing_tables)
        self.assertIsNone(schema.get_available_table())

        schema.advance_table_state(current_table)
        self.assertIn(current_table, schema.completed_tables)
        self.assertIs(schema.get_available_table(), table2)


    def test_multiple_prereqs(self):
        '''Tests advancing tables with multiple prereqs'''
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')
        table3 = Table('Sample Table 3')

        prereqs = {table1, table3}

        table2.add_prereq(table1)
        table2.add_prereq(table3)

        schema.add_table(table1)
        schema.add_table(table2)
        schema.add_table(table3)

        handled1 = schema.get_available_table()
        handled2 = schema.get_available_table()
        self.assertSetEqual(schema.processing_tables, prereqs)
        self.assertIsNone(schema.get_available_table())

        schema.advance_table_state(handled1)
        schema.advance_table_state(handled2)

        self.assertSetEqual(schema.completed_tables, prereqs)
        handled3 = schema.get_available_table()
        self.assertIs(handled3, table2)

    def test_reset_schema(self):
        '''Tests resetting a schema to its default state'''
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        schema.add_table(table1)
        schema.add_table(table2)

        schema_copy = Schema('Sample Schema')
        table1_copy = Table('Sample Table 1')
        table2_copy = Table('Sample Table 2')

        schema_copy.add_table(table1_copy)
        schema_copy.add_table(table2_copy)

        handled1 = schema.get_available_table()
        handled2 = schema.get_available_table()

        schema.advance_table_state(handled1)
        schema.advance_table_state(handled2)

        schema.reset_schema()

        self.assertSetEqual(schema.tables, schema.pending_tables)
        self.assertSetEqual(
            {x.name for x in schema.tables}, {x.name for x in schema_copy.tables}
        )
        self.assertSetEqual(
            {x.name for x in schema.pending_tables}, {x.name for x in schema_copy.pending_tables}
        )
        self.assertSetEqual(
            {x.name for x in schema.processing_tables},
            {x.name for x in schema_copy.processing_tables}
        )
        self.assertSetEqual(
            {x.name for x in schema.completed_tables},
            {x.name for x in schema_copy.completed_tables}
        )

    def test_search_table(self):
        '''Tests searching for a table given a name'''
        schema = Schema('Sample Schema')
        table1 = Table('Sample Table 1')
        table2 = Table('Sample Table 2')

        schema.add_table(table1)
        schema.add_table(table2)

        self.assertEqual(schema.get_table_by_name('Sample Table 1'), table1)
        self.assertEqual(schema.get_table_by_name('Sample Table 2'), table2)

    def test_get_table_conversion_dict(self):
        '''Tests getting a table's conversion dict'''
        table1 = (
            Table('Sample Table 1')
            .add_column(Column('int', 'intnew', int))
            .add_column(Column('string', 'stringnew', str))
            .add_column(Column('datetime', 'datetimenew', np.datetime64))
        )

        expected = {
            'int': convert_to_integer,
            'string': convert_to_string,
            'datetime': convert_to_datetime,
        }

        self.assertDictEqual(table1.get_conversion_dict(), expected)

    def test_get_schema_conversion_dict(self):
        '''Tests getting a schema's conversion dict'''
        schema = (
            Schema('Sample Schema')
            .add_table(
                Table('Sample Table 1')
                .add_column(Column('int', 'intnew', int))
                .add_column(Column('string', 'stringnew', str))
                .add_column(Column('datetime', 'datetimenew', np.datetime64))
            )
            .add_table(
                Table('Sample Table 1')
                .add_column(Column('int', 'intnew', int))
                .add_column(
                    Column('spn', 'spnnew', str, conversion_function=convert_to_spn)
                )
                .add_column(Column('datetime', 'datetimenew', np.datetime64))
            )
        )

        expected = {
            'int': convert_to_integer,
            'string': convert_to_string,
            'spn': convert_to_spn,
            'datetime': convert_to_datetime,
        }

        self.assertDictEqual(schema.get_conversion_dict(), expected)

    @unittest.expectedFailure
    def test_shared_column_conflict(self):
        '''Tests that shared columns ensure their conversion funcitons are the same'''
        schema = (
            Schema('Sample Schema')
            .add_table(
                Table('Sample Table 1')
                .add_column(Column('int', 'intnew', int))
                .add_column(Column('string', 'stringnew', str))
                .add_column(Column('datetime', 'datetimenew', np.datetime64))
            )
            .add_table(
                Table('Sample Table 1')
                .add_column(Column('int', 'intnew', int))
                .add_column(
                    Column('spn', 'spnnew', str, conversion_function=convert_to_spn)
                )
                .add_column(Column('datetime', 'datetimenew', int))
            )
        )

        schema.get_conversion_dict()
