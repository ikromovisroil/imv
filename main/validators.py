import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    # 1. Fayl kengaytmasi
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [
        '.pdf', '.doc', '.docx', '.xlsx', '.xls', '.jpg', '.jpeg', '.png'
    ]
    if ext not in valid_extensions:
        raise ValidationError("Faqat PDF, DOC, DOCX, XLS, XLSX yoki rasm fayllari yuklash mumkin!")

    # 2. MIME TYPES (haqiqiy fayl turi)
    valid_mime = [
        'application/pdf',

        # DOC
        'application/msword',
        'application/vnd.ms-word',

        # DOCX
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',

        # XLS (Excel eski format)
        'application/vnd.ms-excel',

        # XLSX (Excel yangi format)
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',

        # Images
        'image/jpeg',
        'image/jpg',
        'image/png',
    ]

    if value.content_type not in valid_mime:
        raise ValidationError("Fayl formati haqiqiy emas!")

    # 3. Fayl hajmi
    if value.size > 10 * 1024 * 1024:
        raise ValidationError("Fayl 10 MB dan katta bo‘lishi mumkin emas!")
