from .models import Comment, GameComment


def admin_notifications(request):
    if request.user.is_authenticated and request.user.is_superuser:
        pending_comments = Comment.objects.filter(is_published=False).count()
        pending_game_comments = GameComment.objects.filter(is_published=False).count()

        total = pending_comments + pending_game_comments
        return {'pending_moderation_count': total}

    return {'pending_moderation_count': 0}