from django.db import models
from django.contrib.auth.models import User

class Faculty(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos', blank=True)
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Not Specified')

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='students')
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_attendance_streak(self):
        attendance_records = Attendance.objects.filter(user=self.user).order_by('-date')
        streak = 0
        for record in attendance_records:
            if record.status == 'present':
                streak += 1
            else:
                break
        return streak

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers')
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent')
    ])
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return self.name