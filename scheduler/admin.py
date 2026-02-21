from django.contrib import admin
from .models import *
admin.site.register(Department)
admin.site.register(Room)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(TeacherSubject)
admin.site.register(TeacherLeave)
admin.site.register(Timetable)
admin.site.register(ClassSubject)
admin.site.register(Holiday)


