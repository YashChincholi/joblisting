import scrapy
import requests
from datetime import datetime

class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["dice.com"]
    start_urls = [
        'https://www.dice.com/jobs?q=Software&radius=30&radiusUnit=mi&page=1&pageSize=20&filters.postedDate=ONE&filters.workplaceTypes=Remote&filters.employmentType=CONTRACTS&currencyCode=USD&language=en'
    ]

    def parse(self, response):
        jobs = response.css('div.job')
        for job in jobs:
            title = job.css('h2.jobTitle::text').get()
            company = job.css('span.companyName::text').get()
            location = job.css('div.jobLocation::text').get()
            location_type = job.css('span.locationType::text').get()
            employment_type = job.css('span.employmentType::text').get()
            skills = job.css('div.skills::text').getall()
            compensation = job.css('span.compensation::text').get()
            job_details = job.css('div.jobDetails::text').get()
            posted_date = job.css('span.postedDate::text').get()
            updated_date = job.css('span.updatedDate::text').get()

            # Convert posted_date and updated_date to datetime objects
            if posted_date:
                posted_date = datetime.strptime(posted_date, '%B %d, %Y').date()
            if updated_date:
                updated_date = datetime.strptime(updated_date, '%B %d, %Y').date()

            data = {
                'title': title,
                'company': company,
                'location': location,
                'location_type': location_type,
                'employment_type': employment_type,
                'skills': ', '.join(skills),
                'compensation': compensation,
                'job_details': job_details,
                'posted_date': posted_date,
                'updated_date': updated_date
            }

            # Send POST request to the Django backend
            response = requests.post('http://localhost:8000/api/jobs/', json=data)
            self.log(f'Status: {response.status_code}, Reason: {response.reason}')

        # Handle pagination
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
