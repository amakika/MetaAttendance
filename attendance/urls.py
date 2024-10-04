from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('update-location/', views.update_location, name='update_location'),
    path('all-teachers/', views.all_teachers, name='all_teachers'),
    path('faculty/<int:faculty_id>/attendance/', views.faculty_attendance, name='faculty_attendance'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('add-faculty/', views.add_faculty, name='add_faculty'),
    path('edit-faculty/<int:faculty_id>/', views.edit_faculty, name='edit_faculty'),
    path('delete-faculty/<int:faculty_id>/', views.delete_faculty, name='delete_faculty'),
    path('attendance-by-hour/', views.attendance_by_hour, name='attendance_by_hour'),
    path('filter-attendance/', views.filter_attendance, name='filter_attendance'),
    path('delete-attendance/<int:attendance_id>/', views.delete_attendance, name='delete_attendance'),
    path('set-language/', views.set_language_view, name='set_language'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
