from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache


class Genre(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('Слаг', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class BoardGame(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Очень просто'),
        (2, 'Просто'),
        (3, 'Средне'),
        (4, 'Сложно'),
        (5, 'Очень сложно'),
    ]

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=200, unique=True)
    publisher = models.CharField('Издатель', max_length=200, blank=True)
    year = models.PositiveIntegerField('Год', null=True, blank=True)
    min_players = models.PositiveSmallIntegerField('Мин. игроков', default=1)
    max_players = models.PositiveSmallIntegerField('Макс. игроков', default=4)
    play_time = models.PositiveSmallIntegerField('Время партии (мин)')
    difficulty = models.PositiveSmallIntegerField('Сложность', choices=DIFFICULTY_CHOICES, default=3)
    description = models.TextField('Описание')
    cover = models.ImageField('Обложка', upload_to='covers/', blank=True, null=True)
    genres = models.ManyToManyField(Genre, verbose_name='Жанры', related_name='games', blank=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Настольная игра'
        verbose_name_plural = 'Настольные игры'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.clear()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('game_detail', kwargs={'slug': self.slug})


class Review(models.Model):
    game = models.ForeignKey(BoardGame, verbose_name='Игра', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст обзора')
    rating = models.PositiveSmallIntegerField('Оценка', choices=[(i, str(i)) for i in range(1, 6)])
    is_published = models.BooleanField('Опубликовано', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.game.title}'


class Comment(models.Model):
    review = models.ForeignKey(Review, verbose_name='Обзор', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='comments')
    subject = models.CharField('Тема', max_length=150)
    text = models.TextField('Текст комментария')
    is_published = models.BooleanField('Опубликовано', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} — {self.author.username}'


class GameComment(models.Model):
    game = models.ForeignKey(BoardGame, verbose_name='Игра', on_delete=models.CASCADE, related_name='game_comments')
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='game_comments')
    text = models.TextField('Текст комментария')
    # ТУТ ИЗМЕНЕНИЕ: default=True, чтобы публиковалось сразу
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий к игре'
        verbose_name_plural = 'Комментарии к играм'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} — {self.game.title}'


