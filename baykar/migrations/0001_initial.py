# Generated by Django 5.1.7 on 2025-03-10 06:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Takım Adı')),
                ('team_type', models.CharField(choices=[('WING', 'Kanat Takımı'), ('BODY', 'Gövde Takımı'), ('TAIL', 'Kuyruk Takımı'), ('AVIONICS', 'Aviyonik Takımı'), ('ASSEMBLY', 'Montaj Takımı')], max_length=20, verbose_name='Takım Türü')),
            ],
            options={
                'verbose_name': 'Takım',
                'verbose_name_plural': 'Takımlar',
            },
        ),
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Kullanıcı')),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='personnel', to='baykar.team', verbose_name='Takım')),
            ],
            options={
                'verbose_name': 'Personel',
                'verbose_name_plural': 'Personeller',
            },
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Parça Adı')),
                ('part_type', models.CharField(choices=[('WING', 'Kanat'), ('BODY', 'Gövde'), ('TAIL', 'Kuyruk'), ('AVIONICS', 'Aviyonik')], max_length=20, verbose_name='Parça Türü')),
                ('aircraft_type', models.CharField(choices=[('TB2', 'TB2'), ('TB3', 'TB3'), ('AKINCI', 'AKINCI'), ('KIZILELMA', 'KIZILELMA')], max_length=20, verbose_name='Uyumlu Uçak')),
                ('is_used', models.BooleanField(default=False, verbose_name='Kullanıldı mı?')),
                ('production_date', models.DateTimeField(auto_now_add=True, verbose_name='Üretim Tarihi')),
                ('produced_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='produced_parts', to='baykar.team', verbose_name='Üreten Takım')),
            ],
            options={
                'verbose_name': 'Parça',
                'verbose_name_plural': 'Parçalar',
            },
        ),
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Uçak Adı')),
                ('aircraft_type', models.CharField(choices=[('TB2', 'TB2'), ('TB3', 'TB3'), ('AKINCI', 'AKINCI'), ('KIZILELMA', 'KIZILELMA')], max_length=20, verbose_name='Uçak Tipi')),
                ('assembly_date', models.DateTimeField(auto_now_add=True, verbose_name='Montaj Tarihi')),
                ('avionics', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aircraft_avionics', to='baykar.part', verbose_name='Aviyonik')),
                ('body', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aircraft_body', to='baykar.part', verbose_name='Gövde')),
                ('tail', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aircraft_tail', to='baykar.part', verbose_name='Kuyruk')),
                ('wing', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aircraft_wing', to='baykar.part', verbose_name='Kanat')),
                ('assembled_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assembled_aircrafts', to='baykar.team', verbose_name='Montaj Takımı')),
            ],
            options={
                'verbose_name': 'Uçak',
                'verbose_name_plural': 'Uçaklar',
            },
        ),
    ]
