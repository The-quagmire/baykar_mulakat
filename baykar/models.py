from django.db import models
from django.contrib.auth.models import User

# Uçak modelleri için enum gibi kullanılacak seçenekler
class AircraftType(models.TextChoices):
    TB2 = 'TB2', 'TB2'
    TB3 = 'TB3', 'TB3'
    AKINCI = 'AKINCI', 'AKINCI'
    KIZILELMA = 'KIZILELMA', 'KIZILELMA'

# Parça türleri için enum gibi kullanılacak seçenekler
class PartType(models.TextChoices):
    WING = 'WING', 'Kanat'
    BODY = 'BODY', 'Gövde'
    TAIL = 'TAIL', 'Kuyruk'
    AVIONICS = 'AVIONICS', 'Aviyonik'

# Takım türleri için enum gibi kullanılacak seçenekler
class TeamType(models.TextChoices):
    WING = 'WING', 'Kanat Takımı'
    BODY = 'BODY', 'Gövde Takımı'
    TAIL = 'TAIL', 'Kuyruk Takımı'
    AVIONICS = 'AVIONICS', 'Aviyonik Takımı'
    ASSEMBLY = 'ASSEMBLY', 'Montaj Takımı'

# Takım modeli
class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="Takım Adı")
    team_type = models.CharField(max_length=20, choices=TeamType.choices, verbose_name="Takım Türü")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Takım"
        verbose_name_plural = "Takımlar"

# Personel modeli - Django'nun User modelini genişletiyoruz
class Personnel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="personnel", verbose_name="Takım")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team}"

    class Meta:
        verbose_name = "Personel"
        verbose_name_plural = "Personeller"

# Parça modeli
class Part(models.Model):
    name = models.CharField(max_length=100, verbose_name="Parça Adı")
    part_type = models.CharField(max_length=20, choices=PartType.choices, verbose_name="Parça Türü")
    aircraft_type = models.CharField(max_length=20, choices=AircraftType.choices, verbose_name="Uyumlu Uçak")
    is_used = models.BooleanField(default=False, verbose_name="Kullanıldı mı?")
    produced_by = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="produced_parts", verbose_name="Üreten Takım")
    production_date = models.DateTimeField(auto_now_add=True, verbose_name="Üretim Tarihi")

    def __str__(self):
        return f"{self.name} ({self.get_aircraft_type_display()}) - {self.get_part_type_display()}"

    class Meta:
        verbose_name = "Parça"
        verbose_name_plural = "Parçalar"

# Üretilen Uçak modeli
class Aircraft(models.Model):
    name = models.CharField(max_length=100, verbose_name="Uçak Adı")
    aircraft_type = models.CharField(max_length=20, choices=AircraftType.choices, verbose_name="Uçak Tipi")
    wing = models.OneToOneField(Part, on_delete=models.PROTECT, related_name="aircraft_wing", verbose_name="Kanat", null=True)
    body = models.OneToOneField(Part, on_delete=models.PROTECT, related_name="aircraft_body", verbose_name="Gövde", null=True)
    tail = models.OneToOneField(Part, on_delete=models.PROTECT, related_name="aircraft_tail", verbose_name="Kuyruk", null=True)
    avionics = models.OneToOneField(Part, on_delete=models.PROTECT, related_name="aircraft_avionics", verbose_name="Aviyonik", null=True)
    assembled_by = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="assembled_aircrafts", verbose_name="Montaj Takımı")
    assembly_date = models.DateTimeField(auto_now_add=True, verbose_name="Montaj Tarihi")

    def __str__(self):
        return f"{self.name} ({self.get_aircraft_type_display()})"

    class Meta:
        verbose_name = "Uçak"
        verbose_name_plural = "Uçaklar"
