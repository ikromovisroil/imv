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


# Lavozim.
class Structure(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'structure'

# Departament.
class Department(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL,null=True,blank=True)
    structure = models.ForeignKey(Structure, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'department'


# Boshqarma.
class Directorate(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'directorate'


# Bo'lim.
class Division(models.Model):
    directorate = models.ForeignKey(Directorate, on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'division'



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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user')

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    directorate = models.ForeignKey(Directorate, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=50,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True, related_name='author')
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Agar division tanlangan bo‘lsa → directorate avtomatik to‘lsin
        if self.division and self.division.directorate:
            self.directorate = self.division.directorate

        # Agar directorate tanlangan bo‘lsa → department avtomatik to‘lsin
        if self.directorate and self.directorate.department:
            self.department = self.directorate.department

        # Agar department tanlangan bo‘lsa → organization avtomatik to‘lsin
        if self.department and self.department.organization:
            self.organization = self.department.organization

        super().save(*args, **kwargs)

    def __str__(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return "Employee"


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

# Lavozim.
class Condition(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)


    def __str__(self):
        return self.name

    class Meta:
        db_table = 'condition'



# texnika.
class Technics(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True,blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,null=True,blank=True)
    STATUS = (
        ('active', 'Aktiv'),
        ('free', "Bo'sh"),
        ('defect', 'Brak'),
        ('repair', 'Ta’mirda'),
    )
    status = models.CharField(max_length=20, choices=STATUS, default='free')
    name = models.CharField(max_length=50)
    inventory = models.CharField(max_length=50,null=True,blank=True)
    serial = models.CharField(max_length=50,null=True,blank=True)
    moc = models.CharField(max_length=50, null=True, blank=True)
    ip = models.CharField(max_length=50,null=True,blank=True)
    year = models.CharField(max_length=50,null=True,blank=True)
    parametr = models.CharField(max_length=100,null=True,blank=True)
    body = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True)
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.employee and self.status == "free":
            self.status = "active"

        if not self.employee:
            self.status = "free"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'technics'


class Deed(models.Model):
    sender = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='sent_docs')
    receiver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='received_docs')
    file = models.FileField(upload_to='deed/')
    message = models.CharField(max_length=200, null=True, blank=True)
    STATUS = (
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
        ('viewed', 'Kutulmoqda'),
    )
    status = models.CharField(max_length=20, choices=STATUS, default='viewed')
    date_creat = models.DateField(auto_now_add=True)
    date_edit = models.DateField(auto_now=True)

    def __str__(self):
        return f"Dalolatnoma #{self.id} → {self.receiver}"
