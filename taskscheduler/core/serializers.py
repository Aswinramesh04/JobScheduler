from rest_framework import serializers
from .models import Employee, Manager, Supervisor, TaskRequirement, DailyAttendance


class SupervisorSerializer(serializers.ModelSerializer):
    # manager = serializers.PrimaryKeyRelatedField(
    #     queryset=Manager.objects.all(), allow_null=True, required=False
    # )
    class Meta:
        model = Supervisor
        fields = '__all__'

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):

    # supervisor = serializers.PrimaryKeyRelatedField(
    #     queryset=Supervisor.objects.all(), allow_null=True, required=False
    # )

    class Meta:
        model = Employee
        fields = '__all__'

    def validate_skills(self, value):
       
        if isinstance(value, list):
            if not all(isinstance(v, str) for v in value):
                raise serializers.ValidationError("Each skill must be a string.")
        elif isinstance(value, dict):
            if not all(isinstance(k, str) and isinstance(v, (bool, int)) for k, v in value.items()):
                raise serializers.ValidationError("Skills dict must be {string: bool}.")
        else:
            raise serializers.ValidationError("Skills must be a list of strings or a {string: bool} dict.")
        return value

class TaskRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskRequirement
        fields = '__all__'


class DailyAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAttendance
        fields = '__all__'


class DailyAttendanceSummarySerializer(serializers.Serializer):
    date = serializers.DateField()
    total_employees = serializers.IntegerField()
    present = serializers.IntegerField()
    sick = serializers.IntegerField()
    vacation = serializers.IntegerField()
    seminar = serializers.IntegerField()
