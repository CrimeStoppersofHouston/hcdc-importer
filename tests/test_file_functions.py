"""
    Test suite file fetching functions
"""

import unittest
import os
from datetime import date

from utility.file.fetch import (
    fetch_from_directory,
    daily_filings_check,
    monthly_filings_check,
    historical_filings_check
)
from utility.file.validate import validate_from_model
from utility.file.load import load_dataframe_csv
from model.database import hcdc_snapshot


class TestFileFunctions(unittest.TestCase):
    '''Tests file fetching functions'''

    ### File Fetching ###

    def test_get_directory_single(self):
        '''Tests getting files in a directory'''
        files = {
            [
                os.path.basename(x)
                for x in fetch_from_directory(
                    "./tests/test_setups/directorySearch", ".txt"
                )
            ]
        }
        expected = {"1.txt"}

        self.assertEqual(files, expected)

    def test_get_directory_one_depth(self):
        '''Tests getting files in directories recursively with a depth of 1'''
        files = {
            os.path.basename(x)
            for x in fetch_from_directory("./tests/test_setups/directorySearch", ".txt", True, 1)
        }
        expected = {"1.txt", "2.txt", "3.txt", "4.txt", "6.txt"}

        self.assertEqual(files, expected)

    def test_get_directory_ten_depth(self):
        '''Tests getting files in directories recursively with a depth of 1'''
        files = {
            os.path.basename(x)
            for x in fetch_from_directory("./tests/test_setups/directorySearch", ".txt", True, 10)
        }
        expected = {"1.txt", "2.txt", "3.txt", "4.txt", "6.txt", "9.txt", "10.txt"}

        self.assertEqual(files, expected)

    def test_extension_adherence(self):
        '''Tests getting files with a specific extension'''
        files = {
            os.path.basename(x)
            for x in fetch_from_directory("./tests/test_setups/directorySearch", ".pdf")
        }
        expected = {"document.pdf"}

        self.assertEqual(files, expected)

    def test_hcdc_daily_filings(self):
        '''Tests hcdc daily filings fetch'''
        files, code = daily_filings_check("./data", date.today())

        self.assertEqual(code, 1)

    def test_hcdc_monthly_filings(self):
        '''Tests hcdc monthly filings fetch'''
        files, code = monthly_filings_check("./data", date.today())

        self.assertEqual(code, 2)

    def test_hcdc_historical_filings(self):
        '''Tests hcdc historical filings fetch'''
        files, code = historical_filings_check("./data", date.today())

        self.assertEqual(code, 4)

    @unittest.expectedFailure
    def test_negative_depth_fail(self):
        '''Tests error catch on setting a negative depth'''
        fetch_from_directory("./tests/test_setups/directorySearch", ".pdf", True, -1)

    ### File Validation ###

    def test_hcdc_validation(self):
        '''Tests valiation of file based on model'''
        df = load_dataframe_csv(
            "./tests/test_setups/sampleFile/HCDC_sample_chunk.txt", "\t"
        )
        self.assertTrue(validate_from_model(df, hcdc_snapshot))
