from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Team, Personnel, Part, Aircraft
from .Serializers import TeamSerializer, PersonnelSerializer, PartSerializer, AircraftSerializer

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """Takım bilgilerini görüntüleme API'si"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

class PersonnelViewSet(viewsets.ReadOnlyModelViewSet):
    """Personel bilgilerini görüntüleme API'si"""
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    permission_classes = [permissions.IsAuthenticated]

class PartViewSet(viewsets.ModelViewSet):
    """Parça CRUD işlemleri API'si"""
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        personnel = get_object_or_404(Personnel, user=request.user)
        team = personnel.team

        if not team or team.team_type == 'ASSEMBLY':
            return Response({"error": "Bu işlem için yetkiniz bulunmamaktadır."},
                           status=status.HTTP_403_FORBIDDEN)

        team_type_to_part_type = {
            'WING': 'WING', 'BODY': 'BODY',
            'TAIL': 'TAIL', 'AVIONICS': 'AVIONICS',
        }

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        expected_part_type = team_type_to_part_type.get(team.team_type)
        if serializer.validated_data.get('part_type') != expected_part_type:
            return Response(
                {"error": f"Bu takım sadece {expected_part_type} üretebilir"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save(produced_by=team)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AircraftViewSet(viewsets.ModelViewSet):
    """Uçak CRUD işlemleri API'si"""
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        personnel = get_object_or_404(Personnel, user=request.user)

        if not personnel.team or personnel.team.team_type != 'ASSEMBLY':
            return Response({"error": "Bu işlem için yetkiniz bulunmamaktadır."},
                           status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        aircraft_type = serializer.validated_data.get('aircraft_type')
        wing_id = request.data.get('wing')
        body_id = request.data.get('body')
        tail_id = request.data.get('tail')
        avionics_id = request.data.get('avionics')

        try:
            wing = Part.objects.get(id=wing_id, part_type='WING',
                                  aircraft_type=aircraft_type, is_used=False)
            body = Part.objects.get(id=body_id, part_type='BODY',
                                  aircraft_type=aircraft_type, is_used=False)
            tail = Part.objects.get(id=tail_id, part_type='TAIL',
                                  aircraft_type=aircraft_type, is_used=False)
            avionics = Part.objects.get(id=avionics_id, part_type='AVIONICS',
                                      aircraft_type=aircraft_type, is_used=False)
        except Part.DoesNotExist:
            return Response({"error": "Parçalar bulunamadı veya uyumlu değil"},
                           status=status.HTTP_404_NOT_FOUND)

        aircraft = serializer.save(assembled_by=personnel.team)
        aircraft.wing = wing
        aircraft.body = body
        aircraft.tail = tail
        aircraft.avionics = avionics
        aircraft.save()

        # Parçaları kullanılmış olarak işaretle
        for part in [wing, body, tail, avionics]:
            part.is_used = True
            part.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_compatible_parts_api(request):
    """Belirli bir uçak tipiyle uyumlu parçaları getiren API"""
    aircraft_type = request.query_params.get('aircraft_type')

    if not aircraft_type:
        return Response({"error": "Uçak tipi belirtilmedi"},
                       status=status.HTTP_400_BAD_REQUEST)

    parts = {
        'wings': PartSerializer(
            Part.objects.filter(part_type='WING', aircraft_type=aircraft_type, is_used=False),
            many=True
        ).data,
        'bodies': PartSerializer(
            Part.objects.filter(part_type='BODY', aircraft_type=aircraft_type, is_used=False),
            many=True
        ).data,
        'tails': PartSerializer(
            Part.objects.filter(part_type='TAIL', aircraft_type=aircraft_type, is_used=False),
            many=True
        ).data,
        'avionics': PartSerializer(
            Part.objects.filter(part_type='AVIONICS', aircraft_type=aircraft_type, is_used=False),
            many=True
        ).data
    }

    missing_parts = []
    for part_type, parts_list in parts.items():
        if not parts_list:
            part_type_tr = {
                'wings': 'Kanat', 'bodies': 'Gövde',
                'tails': 'Kuyruk', 'avionics': 'Aviyonik'
            }
            missing_parts.append(part_type_tr.get(part_type))

    return Response({
        'parts': parts,
        'inventory_status': {'missing_parts': missing_parts}
    })