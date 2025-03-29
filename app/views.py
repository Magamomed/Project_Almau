from django.shortcuts import render, redirect, get_object_or_404
from .models import  Candidate, Education, Relative, WorkExperience
from django.views.decorators.http import require_POST
import os
from django.conf import settings
from .utils.ocr import extract_text
from .utils.parser import extract_all 

from datetime import datetime

# Загрузка анкеты (страница /)

def upload_view(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')

        for file in files:
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file.name)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Используем Google Cloud Vision OCR
            raw_text = extract_text(upload_path)
            print("==== RAW TEXT ====")
            print(raw_text)

            data = extract_all(raw_text)
            general = data['general']
            education_list = data['education']
            relatives_list = data['relatives']
            work_list = data['work']

            # Дата рождения
            birth_date = None
            try:
                birth_date = datetime.strptime(general.get('birth_date'), '%Y-%m-%d').date()
            except Exception:
                pass

            candidate = Candidate.objects.create(
                full_name=general.get('full_name', ''),
                birth_date=birth_date,
                birth_place=general.get('birth_place', ''),
                citizenship=general.get('citizenship', ''),
                iin=general.get('iin', ''),
                filename=file.name
            )

            # Образование
            for edu in education_list:
                Education.objects.create(
                    candidate=candidate,
                    institution=edu.get('institution', ''),
                    period=edu.get('period', ''),
                    specialization=edu.get('specialization', ''),
                    diploma=edu.get('diploma', '')
                )

            # Родственники
            for rel in relatives_list:
                Relative.objects.create(
                    candidate=candidate,
                    full_name=rel.get('full_name', ''),
                    birth_date=None,
                    relation=rel.get('relation', ''),
                    job=rel.get('job', '')
                )

            # Опыт работы
            for work in work_list:
                WorkExperience.objects.create(
                    candidate=candidate,
                    start_date=work.get('start_date'),
                    end_date=work.get('end_date'),
                    organization=work.get('organization', ''),
                    position=work.get('position', ''),
                    disciplinary=work.get('disciplinary', ''),
                    reason=work.get('reason', ''),
                    notes=work.get('notes', '')
                )

            return redirect('edit', candidate_id=candidate.id)

    return render(request, 'app/upload.html')

# Список анкет
def list_view(request):
    candidates = Candidate.objects.order_by('-uploaded_at')
    return render(request, 'app/list.html', {'candidates': candidates})


# Редактирование анкеты
def edit_view(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        # Сохраняем общие сведения
        candidate.full_name = request.POST.get('full_name')
        candidate.birth_date = request.POST.get('birth_date')
        candidate.birth_place = request.POST.get('birth_place')
        candidate.citizenship = request.POST.get('citizenship')
        candidate.iin = request.POST.get('iin')
        candidate.save()

        # Очистим предыдущие записи
        candidate.education.all().delete()
        candidate.relatives.all().delete()
        candidate.work_experience.all().delete()

        # Сохраняем образование
        i = 0
        while request.POST.get(f'education_{i}_institution'):
            Education.objects.create(
                candidate=candidate,
                institution=request.POST.get(f'education_{i}_institution'),
                period=request.POST.get(f'education_{i}_period'),
                specialization=request.POST.get(f'education_{i}_specialization'),
                diploma=request.POST.get(f'education_{i}_diploma')
            )
            i += 1

        # Сохраняем родственников
        i = 0
        while request.POST.get(f'relative_{i}_full_name'):
            Relative.objects.create(
                candidate=candidate,
                full_name=request.POST.get(f'relative_{i}_full_name'),
                birth_date=request.POST.get(f'relative_{i}_birth_date') or None,
                relation=request.POST.get(f'relative_{i}_relation'),
                job=request.POST.get(f'relative_{i}_job')
            )
            i += 1

        # Сохраняем трудовую деятельность
        i = 0
        while request.POST.get(f'work_{i}_org'):
            WorkExperience.objects.create(
                candidate=candidate,
                start_date=request.POST.get(f'work_{i}_start') or None,
                end_date=request.POST.get(f'work_{i}_end') or None,
                organization=request.POST.get(f'work_{i}_org'),
                position=request.POST.get(f'work_{i}_position'),
                disciplinary=request.POST.get(f'work_{i}_disciplinary'),
                reason=request.POST.get(f'work_{i}_reason'),
                notes=request.POST.get(f'work_{i}_notes'),
            )
            i += 1

        return redirect('list')

    return render(request, 'app/edit.html', {'candidate': candidate})


# Удаление анкеты
@require_POST
def delete_view(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.delete()
    return redirect('list')


# Успешное сохранение (если нужно отдельная страница)
def success_view(request):
    return render(request, 'app/success.html')
