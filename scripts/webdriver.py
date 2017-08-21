# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from selenium import webdriver
import selenium.common.exceptions

class WebDriver:
    """Use a Selenium web driver to ease login, navigation, and access of
    HTTPS sites.

    WARNING: Always use a dummy Firefox profile for scraping, never
    your main profile! This avoids possibility of corrupting your main
    profile.
    """
    def __init__(self, firefox_profile,
                 download_path=None, download_types=None):
        self.fp = webdriver.FirefoxProfile(firefox_profile)
        if download_path:
            self._configure_downloads(download_path, download_types)
        self.driver = webdriver.Firefox(self.fp)
        self.driver.set_page_load_timeout(5)

    def _configure_downloads(self, path, types):
        """WARNING: Changes profile settings.
        Examples of types include audio/mpeg and text/csv. See Firefox options for complete list."""
        self.fp.set_preference('media.play-stand-alone', False)
        self.fp.set_preference('browser.download.folderList', 2)
        self.fp.set_preference('browser.download.manager.showWhenStarting', False)
        self.fp.set_preference('browser.download.dir', path)
        types = ', '.join(types)
        self.fp.set_preference('browser.helperApps.neverAsk.saveToDisk', types)

    def get_html(self, url):
        self.driver.get(url)
        html_source = self.driver.page_source
        return html_source

    def __getattr__(self, name):
        '''Forward undefined fields to underlying driver.'''
        return getattr(self.driver, name)
