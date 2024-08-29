'''
    This module provides functions for scraping HCDC datasets
    from publicly available datasets using playwright.
'''

import re
import zipfile
from playwright.sync_api import Playwright, sync_playwright


def run(playwright: Playwright) -> None:
    '''executes the HCDC playwright scraper'''
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.hcdistrictclerk.com/common/e-services/PublicDatasets.aspx")
    with page.expect_download() as download_info:
        page.get_by_role(
            "row", name=re.compile("Weekly_Historical_Criminal_[0-9]*.zip Download")
        ).locator("a").click()
        download = download_info.value
        download.save_as(f"./data/{download.suggested_filename}")

    with page.expect_download() as download1_info:
        page.get_by_role(
            "row", name=re.compile(".*CrimDisposMonthly_withHeadings.txt Download")
        ).locator("a").click()
        download1 = download1_info.value
        download1.save_as(f"./data/{download1.suggested_filename}")

    with page.expect_download() as download2_info:
        page.get_by_role(
            "row", name=re.compile(".*CrimFilingsMonthly_withHeadings.txt Download")
        ).locator("a").click()
        download2 = download2_info.value
        download2.save_as(f"./data/{download2.suggested_filename}")

    with page.expect_download() as download3_info:
        page.get_by_role(
            "row", name=re.compile(".*CrimFilingsDaily_withHeadings.txt Download")
        ).locator("a").click()
        download3 = download3_info.value
        download3.save_as(f"./data/{download3.suggested_filename}")

    with page.expect_download() as download4_info:
        page.get_by_role(
            "row", name=re.compile(".*CrimDisposDaily_withHeadings.txt Download")
        ).locator("a").click()
        download4 = download4_info.value
        download4.save_as(f"./data/{download4.suggested_filename}")

    # ---------------------
    context.close()
    browser.close()

    with zipfile.ZipFile(f"./data/{download.suggested_filename}", "r") as zip_ref:
        zip_ref.extractall("./data")


def run_playwright():
    '''Invokes the HCDC playwright scraper function with the sync_playwright function'''
    with sync_playwright() as playwright:
        run(playwright)
