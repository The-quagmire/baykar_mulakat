from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from .models import Team, Personnel, Part, Aircraft, PartType, AircraftType
from .forms import UserRegisterForm, PersonnelForm, PartForm, AircraftAssemblyForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        personnel_form = PersonnelForm(request.POST)

        if user_form.is_valid() and personnel_form.is_valid():
            user = user_form.save()
            personnel = personnel_form.save(commit=False)
            personnel.user = user
            personnel.save()

            login(request, user)
            messages.success(request, f'Hesabınız oluşturuldu! Giriş yapabilirsiniz.')
            return redirect('dashboard')
    else:
        user_form = UserRegisterForm()
        personnel_form = PersonnelForm()

    return render(request, 'baykar/register.html', {'user_form': user_form, 'personnel_form': personnel_form})

def check_session(request):
    return JsonResponse({
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None
    })

@login_required
def dashboard(request):
    try:
        personnel = Personnel.objects.get(user=request.user)
        team = personnel.team

        if team:

            if team.team_type == 'ASSEMBLY':
                # Montaj takımı ise mevcut parçaları ve üretilen uçakları listele
                produced_aircraft = Aircraft.objects.filter(assembled_by=team)
                available_parts = {
                    'WING': Part.objects.filter(part_type='WING', is_used=False),
                    'BODY': Part.objects.filter(part_type='BODY', is_used=False),
                    'TAIL': Part.objects.filter(part_type='TAIL', is_used=False),
                    'AVIONICS': Part.objects.filter(part_type='AVIONICS', is_used=False),
                }
                return render(request, 'baykar/dashboard.html', {
                    'personnel': personnel,
                    'team': team,
                    'produced_aircraft': produced_aircraft,
                    'available_parts': available_parts,
                })
            else:
                # Diğer takımlar için üretilen parçaları listele
                produced_parts = Part.objects.filter(produced_by=team)
                return render(request, 'baykar/dashboard.html', {
                    'personnel': personnel,
                    'team': team,
                    'produced_parts': produced_parts,
                })
        else:
            messages.warning(request, 'Henüz bir takıma atanmadınız.')
            return render(request, 'baykar/dashboard.html')
    except Personnel.DoesNotExist:
        messages.error(request, 'Personel kaydınız bulunamadı.')
        return redirect('register')

@login_required
def produce_part(request):
    try:
        personnel = Personnel.objects.get(user=request.user)
        team = personnel.team

        if not team or team.team_type == 'ASSEMBLY':
            messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
            return redirect('dashboard')

        # Takım-Parça tipi eşleştirmesi
        team_type_to_part_type = {
                'WING': 'WING',
                'BODY': 'BODY',
                'TAIL': 'TAIL',
                'AVIONICS': 'AVIONICS',
            }

        if request.method == 'POST':
            form = PartForm(request.POST, team=team)
            if form.is_valid():
                part = form.save(commit=False)

                # Takımın sadece kendi tipindeki parçaları üretmesini sağla
                expected_part_type = team_type_to_part_type.get(team.team_type)
                if part.part_type != expected_part_type:
                    messages.error(request,
                                   f'Bu takım sadece {Part.PART_TYPE_CHOICES[expected_part_type][1]} üretebilir.')
                    return redirect('dashboard')

                part.produced_by = team
                part.save()
                messages.success(request, f'{part.get_part_type_display()} parçası başarıyla üretildi.')
                return redirect('dashboard')
        else:
            form = PartForm(team=team)

        return render(request, 'baykar/produce_part.html', {'form': form, 'team': team})

    except Personnel.DoesNotExist:
        return redirect('register')

@login_required
def recycle_part(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    personnel = get_object_or_404(Personnel, user=request.user)

    # Parçayı üreten takım mı kontrol et
    if part.produced_by != personnel.team:
        messages.error(request, 'Bu parçayı geri dönüşüme gönderme yetkiniz yok.')
        return redirect('dashboard')

    # Parça zaten kullanıldıysa geri dönüşüme gönderilemesin
    if part.is_used:
        messages.error(request, 'Bu parça zaten bir uçakta kullanıldı, geri dönüşüme gönderilemez.')
        return redirect('dashboard')

    part.delete()
    messages.success(request, 'Parça başarıyla geri dönüşüme gönderildi.')
    return redirect('dashboard')

@login_required
def assemble_aircraft(request):
    personnel = get_object_or_404(Personnel, user=request.user)

    # Montaj takımı değilse yönlendir
    if not personnel.team or personnel.team.team_type != 'ASSEMBLY':
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AircraftAssemblyForm(request.POST)
        if form.is_valid():
            aircraft = form.save(commit=False)

            # POST'tan parça ID'lerini al
            wing_id = request.POST.get('wing')
            body_id = request.POST.get('body')
            tail_id = request.POST.get('tail')
            avionics_id = request.POST.get('avionics')

            # Parçaları bul ve uçak tipiyle uyumluluğunu kontrol et
            wing = get_object_or_404(Part, id=wing_id, part_type='WING', aircraft_type=aircraft.aircraft_type, is_used=False)
            body = get_object_or_404(Part, id=body_id, part_type='BODY', aircraft_type=aircraft.aircraft_type, is_used=False)
            tail = get_object_or_404(Part, id=tail_id, part_type='TAIL', aircraft_type=aircraft.aircraft_type, is_used=False)
            avionics = get_object_or_404(Part, id=avionics_id, part_type='AVIONICS', aircraft_type=aircraft.aircraft_type, is_used=False)

            # Parçaları uçağa ekle
            aircraft.wing = wing
            aircraft.body = body
            aircraft.tail = tail
            aircraft.avionics = avionics
            aircraft.assembled_by = personnel.team
            aircraft.save()

            # Parçaları kullanılmış olarak işaretle
            wing.is_used = True
            body.is_used = True
            tail.is_used = True
            avionics.is_used = True
            wing.save()
            body.save()
            tail.save()
            avionics.save()

            messages.success(request, f'{aircraft.get_aircraft_type_display()} uçağı başarıyla montajlandı!')
            return redirect('dashboard')
    else:
        form = AircraftAssemblyForm()

    # Kullanılabilir parçaları getir
    available_parts = {
        'wings': Part.objects.filter(part_type='WING', is_used=False),
        'bodies': Part.objects.filter(part_type='BODY', is_used=False),
        'tails': Part.objects.filter(part_type='TAIL', is_used=False),
        'avionics': Part.objects.filter(part_type='AVIONICS', is_used=False),
    }

    return render(request, 'baykar/assemble_aircraft.html', {
        'form': form,
        'available_parts': available_parts,
    })

@login_required
def get_compatible_parts(request):
    """AJAX isteği ile uyumlu parçaları getiren view"""
    aircraft_type = request.GET.get('aircraft_type')

    if not aircraft_type:
        return JsonResponse({'error': 'Uçak tipi belirtilmedi'}, status=400)

    parts = {
        'wings': list(Part.objects.filter(
            part_type='WING', aircraft_type=aircraft_type, is_used=False
        ).values('id', 'name')),
        'bodies': list(Part.objects.filter(
            part_type='BODY', aircraft_type=aircraft_type, is_used=False
        ).values('id', 'name')),
        'tails': list(Part.objects.filter(
            part_type='TAIL', aircraft_type=aircraft_type, is_used=False
        ).values('id', 'name')),
        'avionics': list(Part.objects.filter(
            part_type='AVIONICS', aircraft_type=aircraft_type, is_used=False
        ).values('id', 'name')),
    }

    # Her parça tipinden en az bir tane var mı kontrol et
    inventory_status = {
        'missing_parts': []
    }

    for part_type, parts_list in parts.items():
        if not parts_list:
            # Türkçe karşılıkları
            part_type_tr = {
                'wings': 'Kanat',
                'bodies': 'Gövde',
                'tails': 'Kuyruk',
                'avionics': 'Aviyonik'
            }
            inventory_status['missing_parts'].append(part_type_tr.get(part_type))

    response = {
        'parts': parts,
        'inventory_status': inventory_status
    }

    return JsonResponse(response)

# Özelleştirilmiş logout view
class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Tüm oturum verilerini temizle
        request.session.flush()
        # Tarayıcı önbelleğinin yenilenmesini sağlayalım
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response