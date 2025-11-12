from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
from .models import *
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Count, Prefetch
from docx import Document
import os
from django.http import HttpResponse
from django.conf import settings
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor,Inches
from datetime import datetime
from docx.oxml import OxmlElement
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT


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


def get_technics_count(request):
    org_id = request.GET.get('org_id')
    dep_id = request.GET.get('dep_id')
    pos_id = request.GET.get('pos_id')

    # Default: barcha texnikalar
    tec = Technics.objects.all()

    if org_id:
        tec = tec.filter(
            Q(employee__organization_id=org_id) |
            Q(employee__department__organization_id=org_id) |
            Q(employee__position__department__organization_id=org_id)
        )
    if dep_id:
        tec = tec.filter(
            Q(employee__department_id=dep_id) |
            Q(employee__position__department_id=dep_id)
        )
    if pos_id:
        tec = tec.filter(employee__position_id=pos_id)

    count = tec.count()
    return JsonResponse({'count': count})


def document_get(request):
    """GET so‘rovi uchun sahifani ko‘rsatish"""
    context = {
        'departments': Department.objects.filter(is_active=True),
        'positions': Position.objects.filter(is_active=True),
        'categorys': Category.objects.filter(is_active=True),
        'organizations': Organization.objects.filter(is_active=True),
    }
    return render(request, 'main/document.html', context)


def document_post(request):
    """POST so‘rovi uchun dalolatnoma yaratish"""
    oylar = [
        "yanvarda", "fevralda", "martda", "aprelda", "mayda", "iyunda",
        "iyulda", "avgustda", "sentabrda", "oktabrda", "noyabrda", "dekabrda"
    ]

    if request.method != 'POST':
        return redirect('document_get')

    org_id = request.POST.get('organization')
    dep_id = request.POST.get('department')
    pos_id = request.POST.get('position')
    post_id = request.POST.get('post_id')
    fio_id = request.POST.get('fio_id')
    date_id = request.POST.get('date_id')
    namber_id = request.POST.get('namber_id')
    rim_id = request.POST.get('rim_id')

    # 🔍 Model obyektlarini xavfsiz olish
    org = Organization.objects.filter(id=org_id).first() if org_id else None
    dep = Department.objects.filter(id=dep_id).first() if dep_id else None
    pos = Position.objects.filter(id=pos_id).first() if pos_id else None

    # 📅 Sanani formatlash
    formatted_date = ''
    if date_id:
        try:
            dt = datetime.strptime(date_id.strip(), "%Y-%m-%d").date()
            oy_nomi = oylar[dt.month - 1]
            formatted_date = f"{dt.year} yil {dt.day}-{oy_nomi}"
        except (ValueError, TypeError):
            formatted_date = str(date_id)

    # ✅ Qaysi obyekt tanlanganini aniqlash

    full_name = None
    technic_count = 0
    if org:
        full_name = org
        technic_count = Technics.objects.filter(employee__organization=org).count()
    elif dep:
        full_name = dep
        technic_count = Technics.objects.filter(employee__department=dep).count()
    elif pos:
        full_name = pos
        technic_count = Technics.objects.filter(employee__position=pos).count()
    else:
        return HttpResponse("Tashkilot, bo‘lim yoki lavozim tanlanmagan!", status=400)

    print(full_name.name,technic_count)

    # 📂 Shablonni tekshirish
    template_path = os.path.join(settings.MEDIA_ROOT, 'document', 'dalolatnoma1.docx')
    if not os.path.exists(template_path):
        return HttpResponse("Shablon fayl topilmadi!", status=404)

    doc = Document(template_path)

    # 🔁 O‘rniga qo‘yiladigan qiymatlar
    replacements = {
        'DEPARTMENT': full_name.name,
        'POST': post_id or '',
        'FIO': fio_id or '',
        'DATA': formatted_date or '',
        'NAMBER': namber_id or '',
        'RIM': rim_id or '',
        'STYLE': full_name.name or '',
    }

    # ✍️ Oddiy matnni almashtirish
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for old, new in replacements.items():
                if old in run.text:
                    run.text = run.text.replace(old, new)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(12)
                    if old in ['STYLE', 'FIO', 'DATA', 'NAMBER']:
                        run.font.bold = True

    # 🔄 Text box (shape) ichidagi matnni almashtirish
    replace_text_in_textboxes(doc.element.body, replacements)

    # 📄 Faylni qaytarish
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = 'attachment; filename="dalolatnoma_yangi.docx"'
    doc.save(response)
    return response


def hisobot_get(request):
    """GET so‘rovi uchun sahifani ko‘rsatish"""
    context = {
        'departments': Department.objects.filter(is_active=True),
        'positions': Position.objects.filter(is_active=True),
        'categorys': Category.objects.filter(is_active=True),
        'organizations': Organization.objects.filter(is_active=True),
    }
    return render(request, 'main/hisobot.html', context)


def set_cell_border(cell, **kwargs):
    """Word jadval hujayrasi atrofida chiziq (border) chizish uchun."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge)
        if edge_data:
            element = OxmlElement(f"w:{edge}")
            for key in ['val', 'sz', 'space', 'color']:
                val = edge_data.get(key)
                if val:
                    element.set(qn(f"w:{key}"), str(val))
            tcPr.append(element)


def set_cell_text(cell, text, bold=False, size_pt=11, center=False):
    """Hujayraga matn yozish va font o‘rnatish."""
    cell.text = text or ''
    for p in cell.paragraphs:
        if center:
            p.alignment = 1  # markazlash
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(size_pt)
            run.font.bold = bold


def create_table(doc, title, data, headers):
    """Sarlavha va jadval yaratish (masofa va format bilan)."""
    # 📌 Bo‘lim sarlavhasi
    heading_para = doc.add_paragraph()
    heading_para.alignment = 0  # chapda
    run = heading_para.add_run(title)
    run.bold = True
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)

    # 🔹 Jadval yaratish
    table = doc.add_table(rows=1, cols=len(headers))
    try:
        table.style = 'Table Grid'
    except KeyError:
        table.style = None

    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Ustun kengliklari (inchlarda)
    widths = [Inches(0.3), Inches(1.2), Inches(1.2), Inches(1.2)]

    # Jadval sarlavhalari
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].width = widths[i]
        set_cell_text(hdr_cells[i], h, bold=True, center=True)
        set_cell_border(hdr_cells[i],
                        top={"val": "single", "sz": "8", "color": "000000"},
                        left={"val": "single", "sz": "8", "color": "000000"},
                        bottom={"val": "single", "sz": "8", "color": "000000"},
                        right={"val": "single", "sz": "8", "color": "000000"})

    # 🔹 Ma’lumotlarni to‘ldirish
    for idx, item in enumerate(data, start=1):
        row = table.add_row()
        row.height = Inches(0.25)
        row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        cells = row.cells
        values = [
            f"{idx}.",  # raqam va nuqta
            item.name or '',
            item.serial or '',
            getattr(item, 'moc', '') or '',
        ]
        for i, val in enumerate(values):
            set_cell_text(cells[i], val, center=(i == 0))  # 1-ustun markazda
            set_cell_border(cells[i],
                            top={"val": "single", "sz": "6", "color": "000000"},
                            left={"val": "single", "sz": "6", "color": "000000"},
                            bottom={"val": "single", "sz": "6", "color": "000000"},
                            right={"val": "single", "sz": "6", "color": "000000"})

    # Jadvaldan keyin bo‘sh satr qo‘shish
    doc.add_paragraph()

    return heading_para, table


def hisobot_post(request):
    if request.method != 'POST':
        return redirect('hisobot_get')

    org_id = request.POST.get('organization')
    dep_id = request.POST.get('department')
    pos_id = request.POST.get('position')

    org = Organization.objects.filter(id=org_id).first() if org_id and org_id.isdigit() else None
    dep = Department.objects.filter(id=dep_id).first() if dep_id and dep_id.isdigit() else None
    pos = Position.objects.filter(id=pos_id).first() if pos_id and pos_id.isdigit() else None

    template_path = os.path.join(settings.MEDIA_ROOT, 'document', 'dalolatnoma2.docx')
    if not os.path.exists(template_path):
        return HttpResponse("Shablon fayl topilmadi!", status=404)

    doc = Document(template_path)

    # 🔹 1. Matnli markerlarni almashtirish
    replacements = {
        'DEPARTMENT': dep.name if dep else '',
        'ORGANIZATION': org.name if org else '',
    }
    for p in doc.paragraphs:
        for old, new in replacements.items():
            if old in p.text:
                p.text = p.text.replace(old, new)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)

    # 🔹 2. TABLE joyini topish
    target_paragraph = None
    for p in doc.paragraphs:
        if 'TABLE' in p.text:
            target_paragraph = p
            p.text = ''
            break

    # 🔹 3. Texnikalarni ajratish
    kompyuterlar = Technics.objects.select_related('employee').filter(category_id=1)
    printerlar = Technics.objects.select_related('employee').filter(category_id=2)
    if org:
        kompyuterlar = kompyuterlar.filter(employee__organization=org)
        printerlar = printerlar.filter(employee__organization=org)
    if dep:
        kompyuterlar = kompyuterlar.filter(employee__department=dep)
        printerlar = printerlar.filter(employee__department=dep)
    if pos:
        kompyuterlar = kompyuterlar.filter(employee__position=pos)
        printerlar = printerlar.filter(employee__position=pos)

    # 🔹 4. Jadval sarlavhalari
    headers = ['№', 'Rusumi', 'Kompyuter SR:', 'Monitor SR:']

    heading1, table1 = create_table(
        doc,
        "Kompyuterlar (shaxsiy kompyuter, monoblok, noutbuk, planshet va infokioskalar)",
        kompyuterlar,
        headers
    )
    heading2, table2 = create_table(
        doc,
        "Printerlar (lazer, MFU, siyohli va boshqa printerlar)",
        printerlar,
        headers
    )

    # 🔹 5. TABLE joyiga qo‘yish
    if target_paragraph is not None:
        target_paragraph._p.addnext(heading1._p)
        heading1._p.addnext(table1._tbl)
        table1._tbl.addnext(heading2._p)
        heading2._p.addnext(table2._tbl)
    else:
        doc.add_paragraph()
        doc._body._body.append(heading1._p)
        doc._body._body.append(table1._tbl)
        doc._body._body.append(heading2._p)
        doc._body._body.append(table2._tbl)

    # 🔹 6. Hujjatni jo‘natish
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = 'attachment; filename="hisobot_yangi.docx"'
    doc.save(response)
    return response




