from django.db import models
from datetime import date
from django.utils.timezone import now

# Election Model
class Election(models.Model):
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Upcoming')

    def countdown(self):
        """Returns the number of days left for an upcoming election."""
        days_left = (self.date - date.today()).days
        return f"{days_left} days left" if days_left > 0 else "Election Day!"

    def __str__(self):
        return self.title

class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ElectionTitle(models.Model):
    title = models.CharField(max_length=255, default='all')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(default=now)

    def __str__(self):
        return self.title

# Candidate Model
class Candidate(models.Model):
    election_title = models.ForeignKey(ElectionTitle, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="candidates", null=True, blank=True)
    agenda = models.TextField()
    image = models.ImageField(upload_to='candidates/', blank=True, null=True)

    def __str__(self):
        return self.name

# Vote Model
class Vote(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    election_title = models.ForeignKey(ElectionTitle, on_delete=models.CASCADE, default=1)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} -> {self.candidate.name} ({self.election_title.title})"
