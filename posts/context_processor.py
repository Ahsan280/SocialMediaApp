from .models import Notification

def user_notification(request):
    try:
        notifications=Notification.objects.filter(receiver=request.user)
    except:
        notifications=None
    return dict(notifications=notifications)