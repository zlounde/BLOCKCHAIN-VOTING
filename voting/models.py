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


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, reg_number, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(reg_number=reg_number, email=email, **extra_fields)
        user.set_password(password)  # Hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, reg_number=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(reg_number='superuser', email=email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    reg_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100, null=True, blank=True)
    has_voted = models.ManyToManyField(ElectionTitle, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Use email for authentication
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
    election = models.ForeignKey(ElectionTitle, on_delete=models.CASCADE, null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.fullname} voted for {self.candidate.name} in {self.election.title}"

