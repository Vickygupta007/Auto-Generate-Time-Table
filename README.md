PROJECT: College Timetable Generator 

Features:
- Multiple departments & classes
- Teacher–Subject specialization
- Fixed periods/day with breaks
- Teacher weekly hour limits
- Teacher leave handling
- Labs scheduled in consecutive periods
- Room allocation (classroom/lab)
- No teacher/room/class clashes
- No subject more than once per day per class
- Balanced workload (rule-based)

Run:
1) python -m venv venv
2) venv\Scripts\activate
3) pip install django
4) python manage.py makemigrations
5) python manage.py migrate
6) python manage.py createsuperuser
7) python manage.py runserver
# Auto-Generate-Time-Table
