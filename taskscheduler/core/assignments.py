from datetime import timedelta
from core.models import Assignment, Employee, Manager, TaskRequirement, DailyAttendance
from django.utils.timezone import now
from core.models import AssignmentFile

TASKS = [
    "Scanning",
    "Pushing",
    "Unloading",
    "Electric pallet truck",
    "Incoming/outgoing goods",
    "Shipping/handling",
    "DG Check",
    "DG Setup",
    "Forklift Setup",
    "NCY Loading",
    "Forklift Transport",
    "Mulli",
    "Truck Loading",
    "Coupling"
]

REQUIRED_COUNTS_BY_SHIFT = {
    'morning': [8,7,6,5,7,8,6,7,6,5,6,5,7,6],
    'afternoon': [6,5,7,6,5,6,5,7,8,7,8,6,5,7],
    'night': [5,6,5,7,6,5,7,8,7,6,5,7,8,6],
}

def get_yesterday_task_for_employee(employee, shift, date):
    yesterday = date - timedelta(days=1)
    assignment = Assignment.objects.filter(employee=employee, shift=shift, date=yesterday).first()
    return assignment.task if assignment else None

def already_has_assignment(employee, shift, date):
    return Assignment.objects.filter(employee=employee, shift=shift, date=date).exists()

def count_task_assignments(shift, date, task):
    return Assignment.objects.filter(shift=shift, date=date, task=task).count()

def generate_assignments(shift, date):
    today = date

    # Determine present employees for this date and shift using DailyAttendance
    present_ids = DailyAttendance.objects.filter(date=today, status='present').values_list('employee_id', flat=True)
    employees = Employee.objects.filter(id__in=present_ids, shift=shift).select_related('supervisor', 'supervisor__manager')
    assignments = []

    # Prepare task requirements for the shift and date
    # Prefer dated TaskRequirement rows; fallback to static defaults if none found
    dated_reqs = list(TaskRequirement.objects.filter(shift=shift, date=today))
    tasks = []
    if dated_reqs:
        for r in dated_reqs:
            tasks.append({'task': r.task, 'required_count': r.required_count})
    else:
        counts = REQUIRED_COUNTS_BY_SHIFT.get(shift, [])
        for task_name, count in zip(TASKS, counts):
            tasks.append({'task': task_name, 'required_count': count})

    supervisor_employees = {}
    for emp in employees:
        if emp.supervisor:
            supervisor_employees.setdefault(emp.supervisor.id, []).append(emp)

    for sup_id, emp_list in supervisor_employees.items():
        # Derive manager from supervisor relation
        manager = emp_list[0].supervisor.manager if emp_list and emp_list[0].supervisor else None
        if not (manager and manager.shift == shift):
            continue

        for task in tasks:
            # Calculate how many already assigned for this task, shift and date
            assigned_count = count_task_assignments(shift, today, task['task'])

            # Remaining slots for this task
            slots_left = task['required_count'] - assigned_count
            if slots_left <= 0:
                continue  # Already fulfilled required count

            # Filter eligible employees: have skill for task, no assignment today, and not repeated task from yesterday
            eligible_emps = [
                e for e in emp_list
                if task['task'] in e.skills and
                not already_has_assignment(e, shift, today) and
                get_yesterday_task_for_employee(e, shift, today) != task['task']
            ]

            # Select up to available slots
            assigned_emps = eligible_emps[:slots_left]

            for emp in assigned_emps:
                a = Assignment.objects.create(
                    employee=emp,
                    supervisor=emp.supervisor,
                    manager=manager,
                    task=task['task'],
                    shift=shift,
                    date=today
                )
                assignments.append({
                    "employee_id": emp.id,
                    "employee_name": emp.name,
                    "employee_type": emp.employee_type,
                    "supervisor_id": emp.supervisor.id,
                    "supervisor_name": emp.supervisor.name,
                    "manager_id": manager.id,
                    "manager_name": manager.name,
                    "task": task['task'],
                    "shift": shift,
                    "date": str(today)
                })
    save_assignments_file(date, shift, assignments)

    # Compute summary information: total required and present employees
    # Total required employees is the sum of required_count for dated requirements
    # or, if using static defaults, the sum of the static counts
    dated_reqs = list(TaskRequirement.objects.filter(shift=shift, date=today))
    if dated_reqs:
        min_required = sum(r.required_count for r in dated_reqs)
    else:
        counts = REQUIRED_COUNTS_BY_SHIFT.get(shift, [])
        min_required = sum(counts)

    present_count = employees.count()

    return {
        'date': str(today),
        'shift': shift,
        'min_employees_required': min_required,
        'present_employees': present_count,
        'assignments': assignments,
    }

def save_assignments_file(date, shift, assignments):
    file_name = f"assignments_{date.strftime('%Y-%m-%d')}_{shift}.json"
    AssignmentFile.objects.update_or_create(
        file_name=file_name,
        defaults={'content': assignments}
    )
