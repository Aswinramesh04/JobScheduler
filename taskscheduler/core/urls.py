from django.urls import path
from .views import AssignmentView

urlpatterns = [
    path('assignments/', AssignmentView.as_view())
]
