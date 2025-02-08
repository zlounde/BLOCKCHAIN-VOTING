from rest_framework import serializers
from .models import Department, ElectionTitle, Candidate

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class ElectionTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionTitle
        fields = '__all__'

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'
