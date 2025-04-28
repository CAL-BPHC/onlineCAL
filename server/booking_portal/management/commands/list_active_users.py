import collections
import csv
import os
from datetime import timedelta

from booking_portal.models import Faculty, FacultyRequest, Student, StudentRequest
from django.core.management.base import BaseCommand
from django.db.models import Count, Max
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Generate a CSV report of active users by department for those with requests in the past two years"

    def handle(self, *args, **options):
        threshold_date = now().date() - timedelta(days=365 * 2)

        faculty_agg = (
            FacultyRequest.objects.filter(slot__date__gte=threshold_date)
            .values("faculty_id")
            .annotate(faculty_reqs=Count("id"), faculty_latest=Max("slot__date"))
        )
        faculty_map = {
            f["faculty_id"]: (f["faculty_reqs"], f["faculty_latest"])
            for f in faculty_agg
        }

        student_agg = (
            StudentRequest.objects.filter(slot__date__gte=threshold_date)
            .values("student_id")
            .annotate(student_reqs=Count("id"), student_latest=Max("slot__date"))
        )
        student_map = {
            s["student_id"]: (s["student_reqs"], s["student_latest"])
            for s in student_agg
        }

        sup_agg = (
            StudentRequest.objects.filter(slot__date__gte=threshold_date)
            .values("student__supervisor_id")
            .annotate(
                supervisor_student_reqs=Count("id"), supervisor_latest=Max("slot__date")
            )
        )
        sup_map = {
            s["student__supervisor_id"]: (
                s["supervisor_student_reqs"],
                s["supervisor_latest"],
            )
            for s in sup_agg
        }

        faculty_ids = set(faculty_map.keys()) | set(sup_map.keys())

        faculties = Faculty.objects.filter(id__in=faculty_ids).select_related(
            "department"
        )
        students = Student.objects.filter(id__in=student_map).select_related(
            "supervisor__department"
        )

        dept_map = collections.defaultdict(lambda: {"faculty": [], "students": []})

        for fac in faculties:
            if not fac.department:
                continue
            fac_reqs, fac_latest = faculty_map.get(fac.id, (0, None))
            stu_under_reqs, sup_latest = sup_map.get(fac.id, (0, None))
            latest = None
            if fac_latest and sup_latest:
                latest = max(fac_latest, sup_latest)
            else:
                latest = fac_latest or sup_latest
            dept_map[fac.department.name]["faculty"].append(
                (fac.name, fac.email, stu_under_reqs, fac_reqs, latest)
            )

        for stu in students:
            sup = stu.supervisor
            if not sup or not sup.department:
                continue
            stu_reqs, stu_latest = student_map.get(stu.id, (0, None))
            dept_map[sup.department.name]["students"].append(
                (stu.name, stu.email, stu_reqs, stu_latest)
            )

        output_path = os.path.join(os.getcwd(), "active_users.csv")
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "Department",
                    "Role",
                    "Name",
                    "Email",
                    "Student Requests",
                    "Faculty Requests",
                    "Latest Request Date",
                ]
            )
            for dept_name, groups in sorted(dept_map.items()):
                for name, email, stu_req_count, fac_req_count, latest in sorted(
                    groups["faculty"], key=lambda x: x[0]
                ):
                    writer.writerow(
                        [
                            dept_name,
                            "Faculty",
                            name,
                            email,
                            stu_req_count,
                            fac_req_count,
                            latest,
                        ]
                    )
                for name, email, stu_req_count, latest in sorted(
                    groups["students"], key=lambda x: x[0]
                ):
                    writer.writerow(
                        [
                            dept_name,
                            "Student",
                            name,
                            email,
                            stu_req_count,
                            0,
                            latest,
                        ]
                    )

        print(f"Report saved to {output_path}")
