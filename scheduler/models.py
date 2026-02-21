from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    ROOM_TYPES = (
        ('CLASS', 'Classroom'),
        ('LAB', 'Laboratory'),
    )
    name = models.CharField(max_length=50)
    room_type = models.CharField(max_length=5, choices=ROOM_TYPES)

    def __str__(self):
        return f"{self.name} ({self.room_type})"


class Teacher(models.Model):
    name = models.CharField(max_length=50)
    max_hours = models.IntegerField(default=16)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=50)
    is_lab = models.BooleanField(default=False)
    weekly_limit = models.IntegerField(default=4)

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher} → {self.subject}"



class ClassSubject(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.class_name} → {self.subject}"


class TeacherLeave(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.teacher} - {self.day}"


class Timetable(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    period = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

class Holiday(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
    ]

    day = models.CharField(max_length=3, choices=DAY_CHOICES, unique=True)
    reason = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.day} - {self.reason}"
    
class WeeklyRotation(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    last_practical_index = models.IntegerField(default=0)
    last_theory_index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.class_name} rotation"


