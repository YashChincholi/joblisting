import scrapy


class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["dice.com"]
    start_urls = ["https://dice.com"]

    def parse(self, response):
        pass
