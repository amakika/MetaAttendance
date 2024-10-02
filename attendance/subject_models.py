from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey('attendance.Faculty', on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return self.name