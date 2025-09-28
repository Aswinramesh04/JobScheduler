from rest_framework.views import APIView
from rest_framework.response import Response
from .assignments import generate_assignments
from datetime import datetime
from django.utils.timezone import now

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
