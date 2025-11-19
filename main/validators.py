import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']

    if ext not in valid_extensions:
        raise ValidationError("Faqat PDF, DOC, DOCX yoki rasm fayllari yuklash mumkin!")
