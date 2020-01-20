from scrapy import Spider


class MockSpider(Spider):
    """
    MockSpider used for testing.
    """
    name = 'mock'

    def parse(self, response):
        pass
