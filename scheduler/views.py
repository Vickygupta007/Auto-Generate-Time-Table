from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import *
from collections import defaultdict
import csv

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# ===================== ADMIN DASHBOARD =====================
@login_required
def dashboard(request):
    return render(request, "dashboard.html", {
        "teacher_count": Teacher.objects.count(),
        "subject_count": Subject.objects.count(),
        "room_count": Room.objects.count(),
        "classes": Class.objects.all(),
    })


# ===================== TIMETABLE GENERATION =====================
@login_required
def generate(request):

    ALL_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    holiday_map = {h.day: h.reason for h in Holiday.objects.all()}

    class_id = request.GET.get("class_id")
    classes = Class.objects.filter(id=class_id)

    if not class_id:
        return HttpResponse("Class not selected", status=400)

    # Delete only selected class timetable
    Timetable.objects.filter(class_name_id=class_id).delete()

    rows = []

    for c in classes:

        weekly_theory_count = defaultdict(int)
        weekly_practical_used = set()
        weekly_theory_extra_used = set()

        allowed_subjects = Subject.objects.filter(
            id__in=ClassSubject.objects.filter(class_name=c)
            .values_list('subject_id', flat=True)
        )

        theory_subjects = [s for s in allowed_subjects if not s.is_lab]
        practical_subjects = [s for s in allowed_subjects if s.is_lab]

        rotation, _ = WeeklyRotation.objects.get_or_create(class_name=c)

        for day_index, d in enumerate(ALL_DAYS):

            # ---------- HOLIDAY ----------
            if d in holiday_map:
                rows.append({
                    "day": d,
                    "holiday": True,
                    "reason": holiday_map[d]
                })
                continue

            daily_subject_used = set()

            # ================= PERIOD 1 → PRACTICAL =================
            practical = None
            for offset in range(len(practical_subjects)):
                idx = (rotation.last_practical_index + day_index + offset) % len(practical_subjects)
                candidate = practical_subjects[idx]
                if candidate.id not in weekly_practical_used:
                    practical = candidate
                    break

            if not practical:
                practical = practical_subjects[
                    (rotation.last_practical_index + day_index) % len(practical_subjects)
                ]

            ts = TeacherSubject.objects.filter(subject=practical).select_related('teacher').first()
            lab = Room.objects.filter(room_type='LAB').order_by('?').first()

            Timetable.objects.create(
                class_name=c, day=d, period=1,
                subject=practical, teacher=ts.teacher, room=lab
            )

            rows.append({
                "day": d, "period": 1,
                "subject": practical, "teacher": ts.teacher, "room": lab
            })

            weekly_practical_used.add(practical.id)
            daily_subject_used.add(practical.id)

            # ================= PERIOD 2 & 3 → THEORY =================
            for p in [2, 3]:
                theory = None

                for offset in range(len(theory_subjects)):
                    idx = (rotation.last_theory_index + day_index + offset) % len(theory_subjects)
                    candidate = theory_subjects[idx]
                    if (
                        weekly_theory_count[candidate.id] < 2 and
                        candidate.id not in daily_subject_used
                    ):
                        theory = candidate
                        break

                if theory is None:
                    for candidate in theory_subjects:
                        if candidate.id not in weekly_theory_extra_used:
                            theory = candidate
                            weekly_theory_extra_used.add(candidate.id)
                            break

                ts = TeacherSubject.objects.filter(subject=theory).select_related('teacher').first()
                room = Room.objects.filter(room_type='CLASS').order_by('?').first()

                Timetable.objects.create(
                    class_name=c, day=d, period=p,
                    subject=theory, teacher=ts.teacher, room=room
                )

                rows.append({
                    "day": d, "period": p,
                    "subject": theory, "teacher": ts.teacher, "room": room
                })

                weekly_theory_count[theory.id] += 1
                daily_subject_used.add(theory.id)

        rotation.last_practical_index += 1
        rotation.last_theory_index += 1
        rotation.save()

    return render(request, "timetable.html", {
        "rows": rows,
        "selected_class": c,
        "holidays": Holiday.objects.all()
    })


# ===================== STUDENT VIEW (READ ONLY) =====================
def student_timetable(request):
    class_id = request.GET.get('class_id')

    classes = Class.objects.all()
    selected_class = None

    if class_id:
        selected_class = Class.objects.get(id=class_id)
        rows_qs = Timetable.objects.filter(class_name=selected_class)
    else:
        rows_qs = Timetable.objects.none()

    DAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    rows = sorted(
        rows_qs,
        key=lambda x: (DAY_ORDER.index(x.day), x.period)
    )

    return render(request, "student_timetable.html", {
        "rows": rows,
        "classes": classes,
        "selected_class": selected_class,
        "holidays": Holiday.objects.all()
    })


# ===================== DOWNLOAD CSV =====================
@login_required
def download_timetable_csv(request):
    class_id = request.GET.get('class_id')

    if not class_id:
        return HttpResponse("Class not selected", status=400)

    timetable = Timetable.objects.filter(class_name_id=class_id)

    DAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    timetable = sorted(timetable, key=lambda x: (DAY_ORDER.index(x.day), x.period))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timetable.csv"'

    writer = csv.writer(response)
    writer.writerow(['Day', 'Time', 'Subject', 'Teacher', 'Room'])

    time_map = {
        1: "10:00 AM - 12:00 PM",
        2: "12:00 PM - 02:00 PM",
        3: "03:00 PM - 05:00 PM",
    }

    for t in timetable:
        writer.writerow([
            t.day,
            time_map[t.period],
            t.subject,
            t.teacher,
            t.room
        ])

    return response


# ===================== DOWNLOAD PDF =====================
@login_required
def download_timetable_pdf(request):
    class_id = request.GET.get('class_id')

    if not class_id:
        return HttpResponse("Class not selected", status=400)

    timetable = Timetable.objects.filter(class_name_id=class_id)

    DAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    timetable = sorted(timetable, key=lambda x: (DAY_ORDER.index(x.day), x.period))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="timetable.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "College Timetable")
    y -= 30

    current_day = None
    c.setFont("Helvetica", 10)

    time_map = {
        1: "10:00 AM - 12:00 PM",
        2: "12:00 PM - 02:00 PM",
        3: "03:00 PM - 05:00 PM",
    }

    for t in timetable:
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 40

        if t.day != current_day:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, t.day)
            y -= 18
            c.setFont("Helvetica", 10)
            current_day = t.day

        line = f"{time_map[t.period]} | {t.subject} | {t.teacher} | {t.room}"
        c.drawString(60, y, line)
        y -= 14

    c.save()
    return response
