from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Student, Teacher, Attendance, Faculty, Profile
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import UserForm, ProfileForm
from django.db.models import Count, Q
from django.utils.translation import gettext as _
from django.views.i18n import set_language
import requests
import ipaddress
from geopy.distance import geodesic
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from .models import Student, Attendance
from django.db.models.functions import TruncHour  # Для группировки по часам
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Teacher, Attendance, Faculty
from django.db.models import Count, Q

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q
from .models import Student, Teacher, Attendance, Faculty
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Student, Teacher, Attendance, Faculty, Profile
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import UserForm, ProfileForm
from django.db.models import Count, Q
from geopy.distance import geodesic
import requests
import ipaddress
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm, ProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Student, Teacher, Attendance, Faculty, Profile
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.conf import settings
from geopy.distance import geodesic
import requests
import ipaddress





def leaderboard(request):
    student_leaderboard = Student.objects.annotate(
        absent_days=Count('user__attendance', filter=Q(user__attendance__status='absent'))
    ).order_by('-absent_days')

    faculty_filter = request.GET.get('faculty', None)
    student_filter = request.GET.get('student', None)

    if faculty_filter:
        student_leaderboard = student_leaderboard.filter(faculty__id=faculty_filter)

    if student_filter:
        student_leaderboard = student_leaderboard.filter(id=student_filter)

    faculties = Faculty.objects.all()
    students = Student.objects.all()

    context = {
        'student_leaderboard': student_leaderboard,
        'faculties': faculties,
        'students': students,
    }
    return render(request, 'attendance/leaderboard.html', context)

@login_required
def mark_attendance(request):
    if request.method == 'POST':
        user_ip = request.META['REMOTE_ADDR']
        try:
            ipaddress.ip_address(user_ip)
        except ValueError:
            messages.error(request, 'Invalid IP address.')
            return redirect('home')

        try:
            response = requests.get(f'http://ip-api.com/json/{user_ip}').json()
            if response['status'] == 'fail':
                raise ValueError('Failed to get location')
            user_location = {'lat': response['lat'], 'lng': response['lon']}
        except (requests.RequestException, ValueError, KeyError) as e:
            messages.error(request, f'Error getting location: {e}')
            return redirect('home')

        college_location = {'lat': 42.85747034165005, 'lng': 74.59859944086045}
        distance = calculate_distance(user_location, college_location)
        if distance <= 0.1:
            now = timezone.now()
            status = 'present' if now.time() < timezone.time(10, 0) else 'late'
            Attendance.objects.create(user=request.user, status=status)
            messages.success(request, f'Attendance marked as {status}')
        else:
            messages.error(request, 'You are outside the college boundaries.')
    return redirect('home')

def calculate_distance(user_location, college_location):
    return geodesic((user_location['lat'], user_location['lng']), (college_location['lat'], college_location['lng'])).kilometers

@login_required
def faculty_attendance(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    students = Student.objects.filter(faculty=faculty)
    attendance_records = Attendance.objects.filter(user__student__faculty=faculty)

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(str(student.id), 'absent')
            Attendance.objects.create(user=student.user, status=status)
            messages.success(request, f'Attendance for {student.user.username} marked as {status}')

    context = {
        'faculty': faculty,
        'students': students,
        'attendance_records': attendance_records,
    }
    return render(request, 'attendance/faculty_attendance.html', context)

@login_required
def home(request):
    user = request.user

    if hasattr(user, 'student'):
        attendance_streak = user.student.get_attendance_streak()

        male_students = Student.objects.filter(profile__gender='male').annotate(
            present_days=Count('user__attendance', filter=Q(user__attendance__status='present'))
        ).order_by('-present_days')

        female_students = Student.objects.filter(profile__gender='female').annotate(
            present_days=Count('user__attendance', filter=Q(user__attendance__status='present'))
        ).order_by('-present_days')

        faculty_attendance = Faculty.objects.annotate(
            present_days=Count('students__user__attendance', filter=Q(students__user__attendance__status='present'))
        ).order_by('-present_days')

        context = {
            'attendance_streak': attendance_streak,
            'male_students': male_students,
            'female_students': female_students,
            'faculty_attendance': faculty_attendance,
        }
        return render(request, 'attendance/student_home.html', context)

    elif hasattr(user, 'teacher'):
        student_leaderboard = Student.objects.annotate(
            present_days=Count('user__attendance', filter=Q(user__attendance__status='present'))
        ).order_by('-present_days')

        faculty_attendance = Faculty.objects.annotate(
            present_days=Count('students__user__attendance', filter=Q(students__user__attendance__status='present'))
        ).order_by('-present_days')

        context = {
            'student_leaderboard': student_leaderboard,
            'faculty_attendance': faculty_attendance,
        }
        return render(request, 'attendance/teacher_home.html', context)

    elif user.is_staff:
        return redirect('admin_dashboard')

    else:
        return render(request, 'attendance/error.html', {'message': 'User type not recognized'})

@login_required
def all_teachers(request):
    teachers = Teacher.objects.all()
    context = {
        'teachers': teachers,
    }
    return render(request, 'attendance/all_teachers.html', context)

# Ensure this is not duplicated in your code
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    teachers = Teacher.objects.all().annotate(
        total_days=Count('user__attendance', distinct=True),
        present_days=Count('user__attendance', filter=Q(user__attendance__status='present')),
        absent_days=Count('user__attendance', filter=Q(user__attendance__status='absent')),
    )

    faculty_attendance = Faculty.objects.annotate(
        present_days=Count('students__user__attendance', filter=Q(students__user__attendance__status='present'))
    ).order_by('-present_days')

    context = {
        'teachers': teachers,
        'faculties': Faculty.objects.all(),
        'faculty_attendance': faculty_attendance,
    }
    return render(request, 'attendance/admin_dashboard.html', context)

# Other functions unchanged...

# Профиль студента




@login_required
def faculty_attendance(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    students = Student.objects.filter(faculty=faculty)
    attendance_records = Attendance.objects.filter(user__student__faculty=faculty)

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(str(student.id), 'absent')  # 'absent' по умолчанию
            Attendance.objects.create(user=student.user, status=status)
            messages.success(request, f'Посещаемость для {student.user.username} отмечена как {status}')

    context = {
        'faculty': faculty,
        'students': students,
        'attendance_records': attendance_records,
    }
    return render(request, 'attendance/faculty_attendance.html', context)

# Other views...
@login_required
def all_teachers(request):
    teachers = Teacher.objects.all()
    context = {
        'teachers': teachers,
    }
    return render(request, 'attendance/all_teachers.html', context)


class AttendanceFilter(SimpleListFilter):
    title = _('Attendance Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('present', _('Present')),
            ('absent', _('Absent')),
            ('late', _('Late')),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__attendance__status=self.value())
        else:
            return queryset


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty', 'present_days')
    list_filter = ('faculty', AttendanceFilter)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            present_days=Count('user__attendance', filter=Q(user__attendance__status='present'))
        )
        return qs

    def present_days(self, obj):
        return obj.user.attendance_set.filter(status='present').count()
    present_days.short_description = _('Present Days')





@login_required
def profile(request):
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else None

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'attendance/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'attendance/login.html')




@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    # Получение общего количества студентов, преподавателей и факультетов
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_faculties = Faculty.objects.count()

    teachers = Teacher.objects.all().annotate(
        total_days=Count('user__attendance', distinct=True),
        present_days=Count('user__attendance', filter=Q(user__attendance__status='present')),
        absent_days=Count('user__attendance', filter=Q(user__attendance__status='absent')),
    )

    faculty_attendance = Faculty.objects.annotate(
        present_days=Count('students__user__attendance', filter=Q(students__user__attendance__status='present'))
    ).order_by('-present_days')

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_faculties': total_faculties,
        'teachers': teachers,
        'faculties': Faculty.objects.all(),
        'faculty_attendance': faculty_attendance,
    }
    return render(request, 'attendance/admin_dashboard.html', context)


# Добавление статистики посещаемости по часам
@login_required
def attendance_by_hour(request):
    """Группировка посещаемости по часам"""
    attendance_by_hour = Attendance.objects.annotate(
        hour=TruncHour('time')
    ).values('hour').annotate(count=Count('id')).order_by('hour')

    context = {
        'attendance_by_hour': attendance_by_hour
    }
    return render(request, 'attendance/attendance_by_hour.html', context)


# Добавление фильтрации по полу и факультету
@login_required
def filter_attendance(request):
    gender = request.GET.get('gender')
    faculty_id = request.GET.get('faculty')

    queryset = Attendance.objects.all()

    if gender:
        queryset = queryset.filter(user__student__gender=gender)

    if faculty_id:
        queryset = queryset.filter(user__student__faculty_id=faculty_id)

    context = {
        'attendance_records': queryset,
        'faculties': Faculty.objects.all(),
        'selected_gender': gender,
        'selected_faculty': faculty_id,
    }

    return render(request, 'attendance/filter_attendance.html', context)


@login_required
def add_student(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        faculty_id = request.POST['faculty']
        try:
            user = User.objects.create_user(username=username, password=password)
            faculty = Faculty.objects.get(id=faculty_id)
            Student.objects.create(user=user, faculty=faculty)
            messages.success(request, 'Student added successfully.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding student: {e}')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/add_student.html', {'faculties': faculties})


@login_required
def edit_student(request, student_id):
    if not request.user.is_staff:
        return redirect('home')
    student = Student.objects.get(id=student_id)
    if request.method == 'POST':
        student.user.username = request.POST['username']
        student.user.save()
        student.faculty = Faculty.objects.get(id=request.POST['faculty'])
        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('admin_dashboard')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/edit_student.html', {
        'student': student,
        'faculties': faculties,
    })


@login_required
def delete_student(request, student_id):
    if not request.user.is_staff:
        return redirect('home')
    student = Student.objects.get(id=student_id)
    student.delete()
    messages.success(request, 'Student deleted successfully.')
    return redirect('admin_dashboard')


@login_required
def add_teacher(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.create_user(username=username, password=password)
            Teacher.objects.create(user=user)
            messages.success(request, 'Teacher added successfully.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding teacher: {e}')
    return render(request, 'attendance/add_teacher.html')


@login_required
def edit_teacher(request, teacher_id):
    if not request.user.is_staff:
        return redirect('home')
    teacher = Teacher.objects.get(id=teacher_id)
    if request.method == 'POST':
        teacher.user.username = request.POST['username']
        teacher.user.save()
        teacher.faculty = Faculty.objects.get(id=request.POST['faculty'])
        teacher.save()
        messages.success(request, 'Teacher updated successfully.')
        return redirect('admin_dashboard')
    faculties = Faculty.objects.all()
    return render(request, 'attendance/edit_teacher.html', {
        'teacher': teacher,
        'faculties': faculties
    })


@login_required
def delete_teacher(request, teacher_id):
    if not request.user.is_staff:
        return redirect('home')
    teacher = Teacher.objects.get(id=teacher_id)
    teacher.delete()
    messages.success(request, 'Teacher deleted successfully.')
    return redirect('admin_dashboard')


@login_required
def add_faculty(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        name = request.POST['name']
        try:
            Faculty.objects.create(name=name)
            messages.success(request, 'Faculty added successfully.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding faculty: {e}')
    return render(request, 'attendance/add_faculty.html', {})


@login_required
def edit_faculty(request, faculty_id):
    if not request.user.is_staff:
        return redirect('home')
    faculty = Faculty.objects.get(id=faculty_id)
    if request.method == 'POST':
        faculty.name = request.POST['name']
        faculty.save()
        messages.success(request, 'Faculty updated successfully.')
        return redirect('admin_dashboard')
    return render(request, 'attendance/edit_faculty.html', {
        'faculty': faculty
    })


@login_required
def delete_faculty(request, faculty_id):
    if not request.user.is_staff:
        return redirect('home')
    faculty = Faculty.objects.get(id=faculty_id)
    faculty.delete()
    messages.success(request, 'Faculty deleted successfully.')
    return redirect('admin_dashboard')


@login_required
def faculty_attendance(request, faculty_id):
    try:
        faculty = Faculty.objects.get(id=faculty_id)
        attendance_records = Attendance.objects.filter(user__student__faculty=faculty)

        context = {
            'faculty': faculty,
            'attendance_records': attendance_records
        }
        return render(request, 'attendance/faculty_attendance.html', context)

    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty not found.')
        return redirect('home')


@login_required
def delete_attendance(request, attendance_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete attendance records.")
        return redirect('home')

    attendance_record = get_object_or_404(Attendance, id=attendance_id)
    
    try:
        attendance_record.delete()
        messages.success(request, 'Attendance record deleted successfully.')
    except Exception as e:
        messages.error(request, f"Error deleting attendance record: {e}")
    
    return redirect('admin_dashboard')




@login_required
def set_language_view(request):
    next = request.POST.get('next', request.GET.get('next'))
    language = request.POST.get('language')
    if language:
        response = HttpResponseRedirect(next)
        response.set_cookie(
            key=settings.LANGUAGE_COOKIE_NAME,
            value=language,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        request.session[settings.LANGUAGE_SESSION_KEY] = language
        return response
    return HttpResponseBadRequest()
