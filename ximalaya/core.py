import json
import logging
import re
from typing import List

import requests
from lxml import html
from requests import Response
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

URL1 = 'https://www.ximalaya.com/revision/album/v1/getTracksList?albumId=%d&pageNum=1&pageSize=2000'
URL2 = 'https://www.ximalaya.com/revision/play/v1/audio?id=%d&ptype=1'

RE1 = re.compile(r"{\"index\":\d*,.*?\"joinXimi\":false}", re.MULTILINE)
RE2 = re.compile(r"(https://.*?\.m4a)", re.MULTILINE)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='ximalaya.log',
                    filemode='w',
                    encoding='UTF-8'
                    )


def log_print(message: str, *args, **kwargs) -> None:
    logging.info(message, *args, **kwargs)
    print(message, *args, **kwargs)


class StaticRequests:
    """
    request static web page.
    """

    def __init__(self, url: str, timeout: int = 10, headers: dict = None, ) -> None:

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
    """
    request dynamic web page.
    """

    def __init__(
            self, url: str,
            timeout: int = 10,
            headless: bool = True,
            eager: bool = False,
            none: bool = False, ) -> None:

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

    def click_element(self, path: str):
        element = self._request().find_element('xpath', path)
        element.click()

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


def save(directory: str, content: bytes) -> None:
    """
    save audio file to somewhere
    """
    try:
        file_name = directory.rsplit('/')[-1]
        log_print(f'Downloading file {file_name}')
        with open(file=directory, mode='wb') as f:
            f.write(content)
    except FileExistsError as exi_error:
        log_print(f"FileExistsError: {exi_error}")
    except PermissionError as exi_error:
        log_print(f"PermissionError: {exi_error}")
    except IOError as exi_error:
        log_print(f"IOError: {exi_error}")
    else:
        log_print(f'Successfully save {directory}')


def main(album_id: int, directory: str):
    album_url: str = URL1 % album_id
    resp1: str = DynamicRequests(album_url).text
    items: List[dict] = [json.loads(item) for item in RE1.findall(resp1)]

    for item in items:
        title: str = item['title']
        track_url: str = URL2 % item['trackId']
        resp2: str = DynamicRequests(url=track_url).text
        src: str = RE2.search(resp2).group(1)
        resp3: bytes = StaticRequests(src).media_content
        file_name: str = title + '.m4a'

        if directory[-1] != '/':
            path: str = directory + '/' + file_name
        else:
            path: str = directory + file_name

        save(path, resp3)


if __name__ == '__main__':
    pass

# todo: 多线程下载文件
