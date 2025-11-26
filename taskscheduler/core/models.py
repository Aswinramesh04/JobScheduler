from django.db import models

class Supervisor(models.Model):
    name = models.CharField(max_length=64)
    place_work = models.CharField(max_length=16)  # A, B, C, D etc.
    shift = models.CharField(max_length=16)
    # Supervisor belongs to a Manager
    manager = models.ForeignKey('Manager', on_delete=models.PROTECT, null=True, blank=True)

class Manager(models.Model):
    name = models.CharField(max_length=64)
    shift = models.CharField(max_length=16)

class Employee(models.Model):
    name = models.CharField(max_length=64)
    skills = models.JSONField()
    shift = models.CharField(max_length=16)
    employee_type = models.CharField(max_length=16)  # permanent, contract etc.
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=16, default='present', choices=[
        ('present', 'Present'),
        ('sick', 'Sick'),
        ('vacation', 'Vacation'),
        ('seminar', 'Seminar'),
        ('leave', 'Casual Leave')
    ])


class DailyAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('sick', 'Sick'),
        ('vacation', 'Vacation'),
        ('seminar', 'Seminar'),
        ('leave', 'Casual Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_attendance')
    date = models.DateField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = ('employee', 'date')

class TaskRequirement(models.Model):
    task = models.CharField(max_length=64)
    required_count = models.PositiveIntegerField()
    shift = models.CharField(max_length=16)
    # Date when this requirement applies; allows per-day, per-shift planning
    date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('task', 'shift', 'date')

class Assignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    task = models.CharField(max_length=64)
    shift = models.CharField(max_length=16)
    date = models.DateField()

    class Meta:
        unique_together = ('employee', 'shift', 'date')

class AssignmentFile(models.Model):
    file_name = models.CharField(max_length=128, unique=True)
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)        
