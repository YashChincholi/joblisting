from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    location_type = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=100)
    skills = models.TextField()
    compensation = models.CharField(max_length=100)
    job_details = models.TextField()
    posted_date = models.DateField()
    updated_date = models.DateField()

    def __str__(self):
        return self.title
