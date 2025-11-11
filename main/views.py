from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
from .models import *
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Count, Prefetch
from docx import Document
from django.conf import settings
import os
from django.http import HttpResponse
from django.conf import settings
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.shared import Pt, RGBColor
from datetime import datetime, date


def technics(request, pk=None):
    # Category filter
    if pk:
        category = get_object_or_404(Category, pk=pk)
        technics_qs = Technics.objects.filter(category=category, is_active=True)
    else:
        category = None
        technics_qs = Technics.objects.filter(is_active=True)

    # Filter parameters
    org_id = request.GET.get('organization')
    dep_id = request.GET.get('department')
    pos_id = request.GET.get('position')

    # Dropdown data
    organizations = Organization.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)
    positions = Position.objects.filter(is_active=True)

    # --- Filtering logic ---
    if org_id:
        technics_qs = technics_qs.filter(
            Q(employee__organization_id=org_id) |
            Q(employee__department__organization_id=org_id) |
            Q(employee__position__department__organization_id=org_id)
        )
    if dep_id:
        technics_qs = technics_qs.filter(
            Q(employee__department_id=dep_id) |
            Q(employee__position__department_id=dep_id)
        )
    if pos_id:
        technics_qs = technics_qs.filter(employee__position_id=pos_id)

    # Context for template
    context = {
        'category': category,
        'categorys': Category.objects.filter(is_active=True),
        'technics': technics_qs.select_related('employee', 'category'),
        'organizations': organizations,
        'departments': departments,
        'positions': positions,
        'selected_org': org_id,
        'selected_dep': dep_id,
        'selected_pos': pos_id,
    }

    return render(request, 'main/technics.html', context)



def ajax_load_departments(request):
    org_id = request.GET.get('organization')

    if not org_id or org_id == "None" or org_id == "":
        return JsonResponse([], safe=False)

    departments = Department.objects.filter(
        organization_id=org_id, is_active=True
    ).values('id', 'name')
    return JsonResponse(list(departments), safe=False)


def ajax_load_positions(request):
    dep_id = request.GET.get('department')

    if not dep_id or dep_id == "None" or dep_id == "":
        return JsonResponse([], safe=False)

    positions = Position.objects.filter(
        department_id=dep_id, is_active=True
    ).values('id', 'name')
    return JsonResponse(list(positions), safe=False)


def organization(request, pk):
    organization = get_object_or_404(Organization, pk=pk)

    # Bo‘limlar (Position) uchun texnika sonini hisoblash
    positions_qs = Position.objects.annotate(
        technics_count=Count('employee__technics')
    ).prefetch_related(
        'employee_set__technics_set'
    )

    # Boshqarma (Department) bo‘yicha texnika soni va bo‘limlarni ulash
    departments = Department.objects.filter(organization=organization) \
        .annotate(
        technics_count=Count('position__employee__technics', distinct=True)+Count('employee__technics', distinct=True),
    ) \
        .prefetch_related(
        Prefetch('position_set', queryset=positions_qs)
    )

    context = {
        'organization': organization,
        'departments': departments,
        'categorys': Category.objects.all(),
        'organizations': Organization.objects.all(),
    }
    return render(request, 'main/organization.html', context)


def replace_text_in_textboxes(element, replacements):
    """
    DOCX fayldagi barcha text box (shape) ichidagi matnlarni almashtiradi.
    """
    for child in element.iter():
        if child.tag == qn('w:t'):  # w:t -> Word text node
            text = child.text
            if text:
                for old, new in replacements.items():
                    if old in text:
                        child.text = text.replace(old, new)


def document(request):
    oylar = [
        "yanvarda", "fevralda", "martda", "aprelda", "mayda", "iyunda",
        "iyulda", "avgustda", "sentabrda", "oktabrda", "noyabrda", "dekabrda"
    ]

    if request.method == 'POST':
        org_id = request.POST.get('organization')
        dep_id = request.POST.get('department')
        pos_id = request.POST.get('position')
        post_id = request.POST.get('post_id')
        fio_id = request.POST.get('fio_id')
        date_id = request.POST.get('date_id')
        namber_id = request.POST.get('namber_id')
        rim_id = request.POST.get('rim_id')

        # Modeldan tanlangan obyektlarni olish
        org = Organization.objects.filter(id=org_id).first() if org_id else None
        dep = Department.objects.filter(id=dep_id).first() if dep_id else None
        pos = Position.objects.filter(id=pos_id).first() if pos_id else None

        org_name = org.name if org else ''
        dep_name = dep.name if dep else ''
        pos_name = pos.name if pos else ''

        # ✅ Sanani formatlash (2025-03-04 -> 2025 yil 4-mart)
        formatted_date = ''
        if date_id:
            dt = datetime.strptime(date_id, "%Y-%m-%d").date()
            oy_nomi = oylar[dt.month - 1]
            formatted_date = f"{dt.year} yil {dt.day}-{oy_nomi}"

        full_name = ""
        if pos_name != "":
            full_name = pos_name
        elif dep_name != "":
            full_name = dep_name
        elif org_name != "":
            full_name = org_name

        if full_name:
            template_path = os.path.join(settings.MEDIA_ROOT, 'document', 'dalolatnoma1.docx')
            if not os.path.exists(template_path):
                return HttpResponse("Shablon fayl topilmadi!", status=404)

            doc = Document(template_path)

            # 🔁 O‘rniga qo‘yiladigan qiymatlar
            replacements = {
                'DEPARTMENT': full_name,
                'POST': post_id,
                'FIO': fio_id,
                'DATA': formatted_date,
                'NAMBER': namber_id,
                'RIM': rim_id,
                'STYLE': full_name,
            }

            # 🔄 Oddiy matnni almashtirish + formatlash
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    for old, new in replacements.items():
                        if old in run.text:
                            run.text = run.text.replace(old, new)

                            # 🎨 Formatlash — faqat DEPARTMENTS uchun
                            if old == 'STYLE':
                                run.font.bold = True
                                run.font.size = Pt(12)
                                run.font.name = 'Times New Roman'

                            if old == 'FIO':
                                run.font.bold = True
                                run.font.name = 'Times New Roman'

                            if old == 'DATA':
                                run.font.bold = True
                                run.font.name = 'Times New Roman'

                            if old == 'NAMBER':
                                run.font.bold = True
                                run.font.name = 'Times New Roman'

            # 🔄 Text box (shape) ichidagi matnni almashtirish
            replace_text_in_textboxes(doc.element.body, replacements)

            # 📄 Yaratilgan faylni qaytarish
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename="dalolatnoma_yangi.docx"'
            doc.save(response)
            return response

        # Agar department tanlanmagan bo‘lsa
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # GET so‘rovi uchun context
    context = {
        'departments': Department.objects.filter(is_active=True),
        'positions': Position.objects.filter(is_active=True),
        'categorys': Category.objects.filter(is_active=True),
        'organizations': Organization.objects.filter(is_active=True),
    }
    return render(request, 'main/document.html', context)


