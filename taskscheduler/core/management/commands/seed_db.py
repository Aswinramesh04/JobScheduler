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
from core.models import Employee, Manager, Supervisor, TaskRequirement
import random

SKILLS = [
    "Scanning", "Pushing", "Unloading", "Electric pallet truck", "Incoming/outgoing goods",
    "Shipping/handling", "DG Check", "DG Setup", "Forklift Setup", "NCY Loading",
    "Forklift Transport", "Mulli", "Truck Loading", "Coupling"
]
SHIFTS = ["morning", "afternoon", "night"]
STATUSES = ["present", "sick", "vacation", "seminar", "leave"]
PLACES = ["A", "B", "C", "D"]

REQUIRED_COUNTS_BY_SHIFT = {
    'morning': [8,7,6,5,7,8,6,7,6,5,6,5,7,6],
    'afternoon': [6,5,7,6,5,6,5,7,8,7,8,6,5,7],
    'night': [5,6,5,7,6,5,7,8,7,6,5,7,8,6],
}

class Command(BaseCommand):
    help = 'Seed supervisors, managers, employees, and tasks'

    def handle(self, *args, **options):
        Employee.objects.all().delete()
        Manager.objects.all().delete()
        Supervisor.objects.all().delete()
        TaskRequirement.objects.all().delete()

        # Create supervisors
        supervisors = []
        for i in range(5):
            sup = Supervisor.objects.create(
                name=f"Supervisor {i+1}",
                place_work=random.choice(PLACES),
                shift=random.choice(SHIFTS)
            )
            supervisors.append(sup)

        # Create one manager per supervisor
        managers = []
        for sup in supervisors:
            mgr = Manager.objects.create(
                name=f"Manager for {sup.name}",
                shift=sup.shift,
                supervisor=sup
            )
            managers.append(mgr)

        # Create employees linked to random supervisors
        for i in range(100):
            sup = random.choice(supervisors)
            Employee.objects.create(
                name=f"Employee {i+1}",
                skills=random.sample(SKILLS, k=random.randint(2, 4)),
                shift=sup.shift,
                employee_type=random.choice(["permanent", "temporary", "contract"]),
                supervisor=sup,
                status=random.choices(STATUSES, weights=[8,1,1,1,1], k=1)[0]
            )

        # Create task requirements for all shifts and tasks
        for shift in SHIFTS:
            taskobjs = []
            for task_name, count in zip(SKILLS, REQUIRED_COUNTS_BY_SHIFT[shift]):
                taskobjs.append(TaskRequirement(
                    task=task_name,
                    required_count=count,
                    shift=shift
                ))
            TaskRequirement.objects.bulk_create(taskobjs)

        self.stdout.write(self.style.SUCCESS('Database seeded with supervisors, managers, employees, and tasks'))
