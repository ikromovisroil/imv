from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *


# =======================
# EMPLOYEE INLINE
# =======================
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    fk_name = "user"
    extra = 0
    verbose_name = "Xodim"
    verbose_name_plural = "Xodim ma'lumotlari"

    # Admin’da ko‘rinadigan maydonlar:
    fields = [
        "division",
        "directorate",
        "department",
        "organization",
        "rank",
        "phone",
        "is_active",
    ]


# =======================
# USER ADMIN OVERRIDE
# =======================
class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)

    def save_model(self, request, obj, form, change):
        """User saqlanganda Employee avtomatik yaraladi"""
        super().save_model(request, obj, form, change)

        # avtomatik Employee yaratish
        Employee.objects.get_or_create(user=obj)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# =======================
# ORGANIZATION ADMIN
# =======================
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "author", "date_creat")
    list_filter = ("is_active", "date_creat")
    search_fields = ("name",)


# =======================
# STRUCTURE ADMIN
# =======================
@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "author", "date_creat")
    list_filter = ("is_active", "date_creat")
    search_fields = ("name",)


# =======================
# DEPARTMENT ADMIN
# =======================
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("organization", "structure", "name", "is_active", "author", "date_creat")
    list_filter = ("organization", "structure", "is_active", "date_creat")
    search_fields = ("name",)


# =======================
# DIRECTORATE ADMIN
# =======================
@admin.register(Directorate)
class DirectorateAdmin(admin.ModelAdmin):
    list_display = ("department", "name", "is_active", "author", "date_creat")
    list_filter = ("department", "is_active", "date_creat")
    search_fields = ("name",)


# =======================
# DIVISION ADMIN
# =======================
@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("directorate", "name", "is_active", "author", "date_creat")
    list_filter = ("directorate", "is_active", "date_creat")
    search_fields = ("name",)


# =======================
# RANK ADMIN
# =======================
@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "author", "date_creat")
    list_filter = ("is_active",)
    search_fields = ("name",)


# =======================
# EMPLOYEE ADMIN
# =======================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("user", "division", "directorate", "department", "organization", "rank", "is_active")
    list_filter = ("division", "directorate", "department", "organization", "rank", "is_active")
    search_fields = ("user__first_name", "user__last_name", "phone")


# =======================
# CATEGORY ADMIN
# =======================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "author", "date_creat")
    search_fields = ("name",)


# =======================
# CONDITION ADMIN
# =======================
@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "author", "date_creat")
    search_fields = ("name",)


# =======================
# TECHNICS ADMIN
# =======================
@admin.register(Technics)
class TechnicsAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "employee", "status", "is_active")
    list_filter = ("category", "status", "is_active")
    search_fields = ("name", "inventory", "serial")


# =======================
# DEED ADMIN
# =======================
@admin.register(Deed)
class DeedAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "status", "date_creat")
    list_filter = ("status", "date_creat")
    search_fields = ("sender__user__first_name", "receiver__user__first_name")


# =======================
# DEED FILE ADMIN
# =======================
@admin.register(DeedFile)
class DeedFileAdmin(admin.ModelAdmin):
    list_display = ("deed", "file")
