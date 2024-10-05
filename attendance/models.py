from django.db import models
from django.contrib.auth.models import User
from .subject_models import Subject

class Faculty(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Profile(models.Model):
  

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(blank=True, upload_to='profile_photos')
    bio = models.TextField(blank=True)
   

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='students')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    status = models.CharField(max_length=500, choices=[
        ('present', 'Present'), 
        ('absent', 'Absent'), 
        ('late', 'Late')
    ], blank=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
    check_in_time = models.TimeField(null=True, blank=True)

    def get_attendance_streak(self):
        attendance_records = Attendance.objects.filter(user=self.user).order_by('-date')
        streak = 0
        for record in attendance_records:
            if record.status == 'present':
                streak += 1
            else:
                break
        return streak

    def get_attendance_duration(self):
        # Implement duration calculation logic here
        pass

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
    status = models.CharField(max_length=500, choices=[
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent')
    ])
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"