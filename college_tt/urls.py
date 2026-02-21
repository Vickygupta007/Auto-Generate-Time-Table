from django.contrib import admin
from django.urls import path
from scheduler import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),      # Admin dashboard
    path('generate/', views.generate, name='generate'),
    path('timetable/', views.student_timetable, name='student_timetable'),  # Student
  
    path('download/csv/', views.download_timetable_csv, name='download_timetable_csv'),
    path('download/pdf/', views.download_timetable_pdf, name='download_timetable_pdf'),


]
