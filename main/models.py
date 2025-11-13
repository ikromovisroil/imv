from django.contrib.auth.models import User
from django.db import models

# Tashkilot.
class Organization(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'organization'


# Viloyat.
class Region(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'region'


# bo'lim.
class Department(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL,null=True,blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'department'


# Shtat.
class Position(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'position'


# Lavozim.
class Rank(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'rank'


# Xodim.
class Employee(models.Model):
    position = models.ForeignKey(Position, on_delete=models.SET_NULL,null=True,blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL,null=True,blank=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100,null=True,blank=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Avtomatik pog‘ona ketma-ketligi
        if self.position and self.position.department:
            self.department = self.position.department

        if self.department and self.department.organization:
            self.organization = self.department.organization

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'employee'


# Category.
class Category(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)


    def __str__(self):
        return self.name

    class Meta:
        db_table = 'category'


# texnika.
class Technics(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True,blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=100)
    inventory = models.CharField(max_length=100,null=True,blank=True)
    serial = models.CharField(max_length=100,null=True,blank=True)
    moc = models.CharField(max_length=100, null=True, blank=True)
    ip = models.CharField(max_length=100,null=True,blank=True)
    year = models.CharField(max_length=50,null=True,blank=True)
    body = models.CharField(max_length=500,null=True,blank=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'technics'



class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Qo‘shildi'),
        ('update', 'O‘zgartirildi'),
        ('delete', 'O‘chirildi'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=50)
    object_name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.model_name} - {self.object_name}"
