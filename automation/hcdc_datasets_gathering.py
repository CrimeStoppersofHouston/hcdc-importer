'''
    This module provides functions for scraping HCDC datasets
    from publicly available datasets using playwright.
'''

import re
import zipfile
from playwright.sync_api import sync_playwright

def download_hcdc(directory: str = './data', **kwargs):
    '''executes the HCDC playwright scraper'''
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://www.hcdistrictclerk.com/common/e-services/PublicDatasets.aspx')

        if kwargs.get('historical'):
            with page.expect_download() as download_info:
                page.get_by_role(
                    'row', name=re.compile('Weekly_Historical_Criminal_[0-9]*.zip Download')
                ).locator('a').click()
                download = download_info.value
                download.save_as(f'{directory}/{download.suggested_filename}')

            with zipfile.ZipFile(f'{directory}/{download.suggested_filename}', 'r') as zip_ref:
                zip_ref.extractall(f'{directory}')

        if kwargs.get('dispos_monthly'):
            with page.expect_download() as download1_info:
                page.get_by_role(
                    'row', name=re.compile('.*CrimDisposMonthly_withHeadings.txt Download')
                ).locator('a').click()
                download1 = download1_info.value
                download1.save_as(f'{directory}/{download1.suggested_filename}')

        if kwargs.get('filings_monthly'):
            with page.expect_download() as download2_info:
                page.get_by_role(
                    'row', name=re.compile('.*CrimFilingsMonthly_withHeadings.txt Download')
                ).locator('a').click()
                download2 = download2_info.value
                download2.save_as(f'{directory}/{download2.suggested_filename}')

        if kwargs.get('filings_daily'):
            with page.expect_download() as download3_info:
                page.get_by_role(
                    'row', name=re.compile('.*CrimFilingsDaily_withHeadings.txt Download')
                ).locator('a').click()
                download3 = download3_info.value
                download3.save_as(f'{directory}/{download3.suggested_filename}')

        if kwargs.get('dispos_daily'):
            with page.expect_download() as download4_info:
                page.get_by_role(
                    'row', name=re.compile('.*CrimDisposDaily_withHeadings.txt Download')
                ).locator('a').click()
                download4 = download4_info.value
                download4.save_as(f'{directory}/{download4.suggested_filename}')

        # ---------------------
        context.close()
        browser.close()
