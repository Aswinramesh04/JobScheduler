from django.urls import path
from .views import AssignmentView, SeedDatabaseView

urlpatterns = [
    path('assignments/', AssignmentView.as_view()),
    path('seed/', SeedDatabaseView.as_view())
]
