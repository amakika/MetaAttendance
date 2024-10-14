from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Student, Parent  # Замените 'myapp' на ваше фактическое имя приложения
import random

def generate_random_digits(length):
    return ''.join(random.choices('0123456789', k=length))

class Command(BaseCommand):
    help = 'Add parents to students with random usernames and passwords'

    def handle(self, *args, **kwargs):
        # Удаляем всех существующих родителей и их пользователей
        Parent.objects.all().delete()

        students = Student.objects.all()
        for student in students:
            # Генерация случайного username и password из цифр
            username = generate_random_digits(8)
            password = generate_random_digits(6)

            # Создание пользователя для родителя
            user = User.objects.create_user(username=username, password=password)

            # Создание родителя и связь его со студентом
            Parent.objects.create(student=student, name=f"Parent of {student.first_name}", user=user)
            
            self.stdout.write(f"Created parent for {student.user.username},{user.username} with username: {username} and password: {password}")