from selenium import webdriver
from selenium.webdriver import ChromeOptions


class SeleniumRequests:

    def __init__(self, url: str, headless=False):
        self.url = url
        self.headless = headless
        self.driver = self._set_driver()

    def _set_driver(self):
        if self.headless:
            options = ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            return driver
        else:
            driver = webdriver.Chrome()
            return driver

    def _request(self):
        self.driver.get(self.url)
        return self.driver

    @property
    def text(self):
        return self._request().page_source


u = 'https://www.ximalaya.com/album/73602960'
response = SeleniumRequests(url=u, headless=True)
if response.text:
    print(response.text)
