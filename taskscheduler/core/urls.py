from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssignmentView,
    SupervisorViewSet,
    ManagerViewSet,
    EmployeeViewSet,
    TaskRequirementViewSet,
    DailyAttendanceViewSet,
    DailyAttendanceMarkView,
    DailyAttendanceSummaryView,
)

router = DefaultRouter()
router.register(r'supervisors', SupervisorViewSet, basename='supervisor')
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'tasks', TaskRequirementViewSet, basename='task')
router.register(r'attendance', DailyAttendanceViewSet, basename='attendance')

urlpatterns = [
    path('assignments/', AssignmentView.as_view()),
    path('', include(router.urls)),
    path('attendance/mark/', DailyAttendanceMarkView.as_view(), name='attendance-mark'),
    path('attendance/summary/', DailyAttendanceSummaryView.as_view(), name='attendance-summary'),
]
