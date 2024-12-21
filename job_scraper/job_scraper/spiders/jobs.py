import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["dice.com"]
    start_urls = [
        'https://www.dice.com/jobs?q=Software&radius=30&radiusUnit=mi&page=1&pageSize=20&filters.postedDate=ONE&filters.workplaceTypes=Remote&filters.employmentType=CONTRACTS&currencyCode=USD&language=en'
    ]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 900,
        },
        'RETRY_HTTP_CODES': [403, 500, 502, 503, 504, 408],
        'HTTPERROR_ALLOWED_CODES': [403],
        'LOG_FILE': 'scrapy_log.txt',
    }

    def start_requests(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        chrome_service = Service(ChromeDriverManager().install())

        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=10,
                screenshot=True,
                script='window.scrollTo(0, document.body.scrollHeight);',
                wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.title-container')),
                dont_filter=True,
                service=chrome_service
            )

    def parse(self, response):
        if response.status == 403:
            self.log("403 Forbidden error encountered")
        else:
            self.log("Page accessed successfully.")
            self.log("Response body (first 5000 characters): \n" + response.text[:5000])  # Log the first 5000 characters of the response body

            # Save the rendered HTML content for debugging
            with open('response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.log("Response body saved to response.html")

            # Save a screenshot for verification if available
            if 'screenshot' in response.meta:
                screenshot_path = 'screenshot.png'
                with open(screenshot_path, 'wb') as f:
                    f.write(response.meta['screenshot'])
                self.log(f"Screenshot saved to {screenshot_path}")

            # Wait for elements explicitly using Selenium
            driver = response.meta['driver']
            wait = WebDriverWait(driver, 10)
            title_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.title-container')))

            self.log(f"Found {len(title_elements)} job elements.")

            job_elements = response.css('div.title-container')
            self.log(f"Job elements: {len(job_elements)}")

            # Debugging: Log job elements
            for job in job_elements:
                self.log("Job element HTML: \n" + job.get())

            job_ids = job_elements.css('a[data-cy="card-title-link"]::attr(id)').getall()
            self.log(f"Found {len(job_ids)} job IDs.")

            # Yield requests to job detail pages
            for job_id in job_ids:
                job_detail_url = f"https://www.dice.com/job-detail/{job_id}"
                self.log(f"Navigating to job detail page: {job_detail_url}")
                yield SeleniumRequest(url=job_detail_url, callback=self.parse_job_details)

    def parse_job_details(self, response):
        self.log("Accessed job detail page successfully.")
        
        # Extract job details using refined selectors
        title = response.css('h1[data-cy="jobTitle"]::text').get()
        company = response.css('a[data-cy="companyNameLink"]::text').get()
        location = response.css('li[data-cy="location"]::text').get()
        posted_date = response.css('li[data-cy="postedDate"]::text').get()

        self.log(f"Extracted job details: {title}, {company}, {location}, {posted_date}")

        data = {
            'title': title,
            'company': company,
            'location': location,
            'posted_date': posted_date,
        }

        self.log(f"Scraped data: {data}")

        # Save the extracted data or send to your backend as needed
        # For now, let's print the extracted data
        print(data)
