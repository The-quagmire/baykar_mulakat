from rest_framework import serializers
from .models import Team, Personnel, Part, Aircraft

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class PersonnelSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Personnel
        fields = ['id', 'team', 'user_details']

    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = '__all__'

class AircraftSerializer(serializers.ModelSerializer):
    wing_details = PartSerializer(source='wing', read_only=True)
    body_details = PartSerializer(source='body', read_only=True)
    tail_details = PartSerializer(source='tail', read_only=True)
    avionics_details = PartSerializer(source='avionics', read_only=True)

    class Meta:
        model = Aircraft
        fields = '__all__'