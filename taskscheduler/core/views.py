from rest_framework.views import APIView
from rest_framework.response import Response
from .assignments import generate_assignments
from datetime import datetime
from django.utils.timezone import now
from django.core.management import call_command
from django.http import JsonResponse

# class AssignmentView(APIView):
#     def get(self, request):
#         shift = request.query_params.get('shift', 'morning')
#         date = request.query_params.get('date', '2025-09-28')
#         data = generate_assignments(shift=shift, date=date)
#         return Response(data)

class AssignmentView(APIView):
    def get(self, request):
        shift = request.query_params.get('shift', 'morning')
        date_str = request.query_params.get('date', None)
        force_regenerate = request.query_params.get('force', 'false').lower() == 'true'
        
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            date = now().date()

        # First, check if assignments already exist for this date/shift
        from .models import Assignment
        existing_assignments = Assignment.objects.filter(shift=shift, date=date).select_related(
            'employee', 'supervisor', 'manager'
        )
        
        if existing_assignments.exists() and not force_regenerate:
            # Return existing assignments
            data = [{
                "employee_id": a.employee.id,
                "employee_name": a.employee.name,
                "employee_type": a.employee.employee_type,
                "supervisor_id": a.supervisor.id,
                "supervisor_name": a.supervisor.name,
                "manager_id": a.manager.id,
                "manager_name": a.manager.name,
                "task": a.task,
                "shift": a.shift,
                "date": str(a.date)
            } for a in existing_assignments]
        else:
            # If force=true, delete existing assignments first
            if force_regenerate:
                existing_assignments.delete()
            # Generate new assignments
            data = generate_assignments(shift, date)
        
        return Response(data)

class SeedDatabaseView(APIView):
    def post(self, request):
        try:
            call_command('seed_db')
            return Response({'message': 'Database seeded successfully!'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def get(self, request):
        from .models import Employee, Manager, Supervisor
        return Response({
            'message': 'Database status',
            'employees': Employee.objects.count(),
            'managers': Manager.objects.count(),
            'supervisors': Supervisor.objects.count()
        })
