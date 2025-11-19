from .models import Deed

def deed_notifications(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user

    # RECEIVER uchun: yangi kelgan (viewed)
    receiver_notes = Deed.objects.filter(
        receiver__user=user,
        status="viewed"
    )

    # SENDER uchun: tasdiqlangan yoki rad etilgan (faqat ko‘rilmagan)
    sender_notes = Deed.objects.filter(
        sender__user=user,
        sender_seen=False,
        status__in=["approved", "rejected"]
    )

    all_notes = (receiver_notes | sender_notes).order_by("-date_creat")[:10]
    unread = all_notes.count()

    return {
        "deed_notifications": all_notes,
        "deed_notification_count": unread
    }
