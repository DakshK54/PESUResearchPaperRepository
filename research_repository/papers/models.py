# papers/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLES = [
        ('Researcher', 'Researcher'),
        ('Student', 'Student'),
        ('Admin', 'Admin')
    ]
    role = models.CharField(max_length=20, choices=ROLES)
    affiliation = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)

class ResearchArea(models.Model):
    area_id = models.AutoField(primary_key=True)
    area_name = models.CharField(max_length=100, default='Student')
    description = models.TextField()

class ResearchPaper(models.Model):
    paper_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, default='NewResearchPaper')
    abstract = models.TextField()
    doi = models.CharField(max_length=50, unique=True, null=True, blank=True)
    citation_count = models.IntegerField(default=0)
    journal_name = models.CharField(max_length=100, default='Journal')
    publication_year = models.IntegerField()
    APPROVAL_STATUS = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default='Pending')
    version = models.IntegerField(default=1)
    pdf_data = models.FileField(upload_to='pdfs/')

class PaperReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField()
    review_date = models.DateField(default=timezone.now)

class PaperKeyword(models.Model):
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('paper', 'keyword')

class PaperAuthor(models.Model):
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paper', 'author')

class PaperResearchArea(models.Model):
    paper = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE)
    area = models.ForeignKey(ResearchArea, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('paper', 'area')

class UserAccessRights(models.Model):
    RESOURCE_TYPES = [
        ('Paper', 'Paper'),
        ('User', 'User'),
        ('Review', 'Review')
    ]
    ACCESS_LEVELS = [
        ('Read', 'Read'),
        ('Write', 'Write'),
        ('Admin', 'Admin')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVELS)