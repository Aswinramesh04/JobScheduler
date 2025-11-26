from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from .assignments import generate_assignments
from datetime import datetime
from django.utils.timezone import now
from .models import Supervisor, Manager, Employee, TaskRequirement, DailyAttendance
from .serializers import (
    SupervisorSerializer,
    ManagerSerializer,
    EmployeeSerializer,
    TaskRequirementSerializer,
    DailyAttendanceSerializer,
    DailyAttendanceSummarySerializer,
)

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
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        else:
            date = now().date()

        data = generate_assignments(shift, date)
        return Response(data)


class SupervisorViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = SupervisorSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        qs = Supervisor.objects.all().order_by('id')
        manager_id = self.request.query_params.get('manager')
        if manager_id:
            qs = qs.filter(manager_id=manager_id)
        return qs


class ManagerViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Manager.objects.all().order_by('id')
    serializer_class = ManagerSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post']


class EmployeeViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    queryset = Employee.objects.select_related('supervisor_id').all().order_by('id')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post']


class TaskRequirementViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             viewsets.GenericViewSet):
    queryset = TaskRequirement.objects.all().order_by('id')
    serializer_class = TaskRequirementSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post']


class DailyAttendanceViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    queryset = DailyAttendance.objects.select_related('employee').all().order_by('date', 'employee_id')
    serializer_class = DailyAttendanceSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        qs = super().get_queryset()
        date = self.request.query_params.get('date')
        employee_id = self.request.query_params.get('employee')
        if date:
            qs = qs.filter(date=date)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs

    # @action(detail=False, methods=['post'], url_path='bulk')
    # def bulk(self, request):
    #     """Create DailyAttendance rows (status=present) for all employees for a given date."""
        # date_str = request.data.get('date')
        # if not date_str:
        #     return Response({'error': 'date is required (YYYY-MM-DD)'}, status=400)
    # @action(detail=False, methods=['get'], url_path='summary')
    # def summary(self, request):
    #     """Return counts of attendance statuses for a given date."""
    #     date_str = request.query_params.get('date')
    #     if not date_str:
    #         return Response({'error': 'date is required (YYYY-MM-DD)'}, status=400)
    #     try:
    #         target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    #     except ValueError:
    #         return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    #     qs = DailyAttendance.objects.filter(date=target_date)

    #     total_employees = qs.count()
    #     counts = {key: qs.filter(status=key).count() for key, _ in DailyAttendance.STATUS_CHOICES}

    #     data = {
    #         'date': target_date,
    #         'total_employees': total_employees,
    #         **counts,
    #     }

    #     serializer = DailyAttendanceSummarySerializer(data)
    #     return Response(serializer.data)
    #     try:
    #         target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    #     except ValueError:
    #         return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    #     employees = Employee.objects.all()
    #     created_count = 0

    #     for emp in employees:
    #         _, created = DailyAttendance.objects.get_or_create(
    #             employee=emp,
    #             date=target_date,
    #             defaults={'status': 'present'},
    #         )
    #         if created:
    #             created_count += 1

    #     return Response({
    #         'date': str(target_date),
    #         'created_count': created_count,
    #     })
    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk(self, request):
        """Create DailyAttendance rows (status=present) for all employees for a given date."""
        date_str = request.data.get('date')
        if not date_str:
            return Response({'error': 'date is required (YYYY-MM-DD)'}, status=400)
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        employees = Employee.objects.all()
        created_count = 0

        for emp in employees:
            _, created = DailyAttendance.objects.get_or_create(
                employee=emp,
                date=target_date,
                defaults={'status': 'present'},
            )
            if created:
                created_count += 1

        return Response({
            'date': str(target_date),
            'created_count': created_count,
        })
    
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """Return counts of attendance statuses for a given date."""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'date is required (YYYY-MM-DD)'}, status=400)
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        qs = DailyAttendance.objects.filter(date=target_date)

        total_employees = qs.count()
        counts = {key: qs.filter(status=key).count() for key, _ in DailyAttendance.STATUS_CHOICES}

        data = {
            'date': target_date,
            'total_employees': total_employees,
            **counts,
        }

        serializer = DailyAttendanceSummarySerializer(data)
        return Response(serializer.data)


class DailyAttendanceMarkView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        employee_id = request.data.get('employee')
        date_str = request.data.get('date')
        status_value = request.data.get('status')

        if not employee_id or not date_str or not status_value:
            return Response({'error': 'employee, date and status are required'}, status=400)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)

        if status_value not in dict(DailyAttendance.STATUS_CHOICES):
            return Response({'error': f'Invalid status. Allowed: {list(dict(DailyAttendance.STATUS_CHOICES).keys())}'}, status=400)

        attendance, _ = DailyAttendance.objects.update_or_create(
            employee=employee,
            date=target_date,
            defaults={'status': status_value},
        )

        serializer = DailyAttendanceSerializer(attendance)
        return Response(serializer.data)


class DailyAttendanceSummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'detail': 'Use /api/attendance/summary/?date=YYYY-MM-DD instead.'}, status=404)
