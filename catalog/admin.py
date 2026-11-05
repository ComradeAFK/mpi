from django.contrib import admin
from .models import Genre, BoardGame, Review, Comment, GameComment

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BoardGame)
class BoardGameAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'year', 'difficulty', 'is_published', 'created_at')
    list_filter = ('difficulty', 'is_published', 'genres', 'year')
    search_fields = ('title', 'publisher', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'publisher', 'year', 'description', 'cover')
        }),
        ('Характеристики', {
            'fields': ('min_players', 'max_players', 'play_time', 'difficulty', 'genres')
        }),
        ('Публикация', {
            'fields': ('is_published', 'created_at', 'updated_at')
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'author', 'rating', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating', 'game')
    search_fields = ('title', 'text', 'author__username')
    readonly_fields = ('created_at', 'author')
    fields = ('game', 'title', 'text', 'rating', 'is_published', 'author', 'created_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'review', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('subject', 'text', 'author__username')
    readonly_fields = ('created_at',)
    fields = ('review', 'author', 'subject', 'text', 'is_published', 'created_at')
    actions = ('publish_comments', 'unpublish_comments')

    @admin.action(description='Опубликовать выбранные комментарии')
    def publish_comments(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'Опубликовано комментариев: {updated}')

    @admin.action(description='Снять с публикации выбранные комментарии')
    def unpublish_comments(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'Снято с публикации: {updated}')

@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display = ('game', 'author', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('text', 'author__username', 'game__title')
    readonly_fields = ('created_at',)
    actions = ('publish_game_comments', 'unpublish_game_comments')

    @admin.action(description='Опубликовать выбранные комментарии')
    def publish_game_comments(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'Опубликовано: {updated}')

    @admin.action(description='Снять с публикации выбранные комментарии')
    def unpublish_game_comments(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'Снято с публикации: {updated}')