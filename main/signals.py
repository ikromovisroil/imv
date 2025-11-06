from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Technics, ActivityLog

@receiver(post_save, sender=Technics)
def log_technics_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    ActivityLog.objects.create(
        user=getattr(instance, '_current_user', None),
        action=action,
        model_name='Technics',
        object_name=instance.name,
        description=f"Texnika {'yaratildi' if created else 'tahrirlandi'}: {instance.name}"
    )

@receiver(post_delete, sender=Technics)
def log_technics_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=getattr(instance, '_current_user', None),
        action='delete',
        model_name='Technics',
        object_name=instance.name,
        description=f"Texnika o‘chirildi: {instance.name}"
    )
