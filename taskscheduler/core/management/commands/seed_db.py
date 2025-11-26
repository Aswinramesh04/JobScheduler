# from django.core.management.base import BaseCommand
# from core.models import Employee, Manager, TaskRequirement
# import random

# SKILLS = ["scanning", "truck", "dg_check", "pushen", "entladen", "transport"]
# SHIFTS = ["morning", "afternoon", "night"]
# STATUSES = ["present", "sick", "vacation", "seminar", "leave"]

# class Command(BaseCommand):
#     help = 'Seed DB with dummy managers, employees, tasks'

#     def handle(self, *args, **options):
#         Employee.objects.all().delete()
#         Manager.objects.all().delete()
#         TaskRequirement.objects.all().delete()
#         managers = [Manager.objects.create(name=f"Manager {i+1}", shift=SHIFTS[i % 3]) for i in range(6)]
#         for i in range(50):
#             Employee.objects.create(
#                 name=f"Employee {i+1}",
#                 skills=random.sample(SKILLS, k=random.randint(2, 4)),
#                 shift=random.choice(SHIFTS),
#                 employee_type=random.choice(["permanent", "temporary", "contract"]),
#                 manager=random.choice(managers),
#                 status=random.choices(STATUSES, weights=[8,1,1,1,1], k=1)[0]
#             )
#         TaskRequirement.objects.bulk_create([
#             TaskRequirement(task="scanning", required_count=14, shift="morning"),
#             TaskRequirement(task="truck", required_count=6, shift="afternoon"),
#             TaskRequirement(task="dg_check", required_count=4, shift="night"),
#             TaskRequirement(task="pushen", required_count=5, shift="morning")
#         ])

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Deprecated: seeding is disabled. Use the API endpoints to create real data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('seed_db is deprecated and does nothing. Create data via /api endpoints.'))
