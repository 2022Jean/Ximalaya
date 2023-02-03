from typing import List

import requests
from lxml import html
from requests import Response
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from utils import log_print


class StaticRequests:

    def __init__(self,
                 url: str,
                 timeout: int = 10,
                 headers: dict = None,
                 ) -> None:

        if headers is None:
            headers = {}
        self.url = url
        self.timeout = timeout
        self.headers = headers

    def _request(self) -> Response:
        try:
            response = requests.get(url=self.url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error_http:
            log_print("HTTP Error:", error_http)
        except requests.exceptions.ConnectionError as error_conn:
            log_print("Error Connecting:", error_conn)
        except requests.exceptions.Timeout as error_time:
            log_print("Timeout Error:", error_time)
        except requests.exceptions.RequestException as err:
            log_print("Something Else:", err)
        else:
            return response

    def xpath(self, path: str) -> List[str]:
        try:
            tree = html.fromstring(self.text)
            elements = tree.xpath(path + '/text()')
        except html.etree.ParserError as e:
            log_print("ParserError:", e)
        except ValueError as e:
            log_print("ValueError:", e)
        else:
            return elements

    @property
    def media_content(self) -> Response.content:
        content = self._request().content
        if content:
            return content
        else:
            log_print('Fail to get media:', self.url)
            return

    @property
    def text(self) -> str:
        return self._request().text


class DynamicRequests:

    def __init__(self,
                 url: str,
                 timeout: int = 10,
                 headless: bool = False,
                 eager: bool = False,
                 none: bool = False,
                 ) -> None:

        self.url = url
        self.timeout = timeout
        self.headless = headless
        self.eager = eager
        self.none = none
        self.wait = None
        self.driver = self._set_driver()

    def _set_driver(self) -> WebDriver:
        options = ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        if self.eager:
            options.page_load_strategy = 'eager'
        if self.none:
            options.page_load_strategy = 'none'
        driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(driver=driver, timeout=self.timeout)
        return driver

    def _request(self) -> WebDriver:
        try:
            self.driver.get(self.url)
        except WebDriverException as error:
            log_print("WebDriverException caught:", error)
        return self.driver

    def xpath(self, path: str) -> List[str]:
        try:
            elements = self._request().find_elements(by='xpath', value=path)
        except NoSuchElementException as e:
            log_print('NoSuchElementException:', e)
        except TimeoutException as e:
            log_print('TimeoutException:', e)
        except WebDriverException as e:
            log_print("WebDriverException caught:", e)
        else:
            return [element.text for element in elements]

    @property
    def text(self) -> str:
        return self._request().page_source
