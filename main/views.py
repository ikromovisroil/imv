from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
from .models import *
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Count, Prefetch


# technics ni categoriya bo'yicha qidirish .
def technics(request, pk=None):
    if pk:
        category = get_object_or_404(Category, pk=pk)
        technics = Technics.objects.filter(category=category, is_active=True)
    else:
        category = None
        technics = Technics.objects.filter(is_active=True)

    org_id = request.GET.get('organization')
    dep_id = request.GET.get('department')
    pos_id = request.GET.get('position')

    organizations = Organization.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)
    positions = Position.objects.filter(is_active=True)

    if org_id:
        technics = technics.filter(employee__position__department__organization_id=org_id)
        departments = departments.filter(organization_id=org_id)
    if dep_id:
        technics = technics.filter(employee__position__department_id=dep_id)
        positions = positions.filter(department_id=dep_id)
    if pos_id:
        technics = technics.filter(employee__position_id=pos_id)

    context = {
        'category': category,
        'categorys': Category.objects.filter(is_active=True),
        'technics': technics.select_related('employee', 'category'),
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






