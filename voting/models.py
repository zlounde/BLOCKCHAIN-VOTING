from django.db import models
from datetime import date
from django.utils.timezone import now
from django.db import models
from django.utils import timezone


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
    start_time = models.DateTimeField(null=True, blank=True)  # Allow null values
    end_time = models.DateTimeField(null=True, blank=True)    # Allow null values

    def __str__(self):
        return self.title

    @property
    def status(self):
        """
        Dynamically calculate the status based on the current time.
        """
        now = timezone.now()

        if self.start_time is None or self.end_time is None:
            return "Not Scheduled"
        elif now < self.start_time:
            return "Upcoming"
        elif self.start_time <= now <= self.end_time:
            return "Ongoing"
        else: 
            return "Completed"

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
