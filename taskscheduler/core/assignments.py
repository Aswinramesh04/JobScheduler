from datetime import timedelta
from core.models import Assignment, Employee, Manager, TaskRequirement
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
    managers = Manager.objects.filter(shift=shift).select_related('supervisor')
    employees = Employee.objects.filter(shift=shift, status='present').select_related('supervisor')
    
    assignments = []
    supervisor_to_manager = {m.supervisor.id: m for m in managers}

    # Prepare task requirements for the shift
    tasks = []
    counts = REQUIRED_COUNTS_BY_SHIFT.get(shift, [])
    for task_name, count in zip(TASKS, counts):
        tasks.append({'task': task_name, 'required_count': count})

    supervisor_employees = {}
    for emp in employees:
        if emp.supervisor:
            supervisor_employees.setdefault(emp.supervisor.id, []).append(emp)

    for sup_id, emp_list in supervisor_employees.items():
        manager = supervisor_to_manager.get(sup_id)
        if not manager:
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

    return assignments

def save_assignments_file(date, shift, assignments):
    file_name = f"assignments_{date.strftime('%Y-%m-%d')}_{shift}.json"
    AssignmentFile.objects.update_or_create(
        file_name=file_name,
        defaults={'content': assignments}
    )
