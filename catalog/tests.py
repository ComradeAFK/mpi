from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Genre, BoardGame, Review, Comment, GameComment


class ModelTests(TestCase):
    """Тесты для проверки правильности работы моделей"""

    def setUp(self):
        # Этот метод запускается перед каждым тестом (создает тестовые данные)
        self.genre = Genre.objects.create(name="Стратегия", slug="strategiya")
        self.game = BoardGame.objects.create(
            title="Тестовая игра",
            slug="test-game",
            play_time=60,
            description="Описание",
        )
        self.user = User.objects.create_user(username="tester", password="password123")

    def test_genre_str(self):
        """Проверяем, что __str__ у жанра возвращает его название"""
        self.assertEqual(str(self.genre), "Стратегия")

    def test_game_str(self):
        """Проверяем, что __str__ у игры возвращает название игры"""
        self.assertEqual(str(self.game), "Тестовая игра")

    def test_game_get_absolute_url(self):
        """Проверяем, что метод get_absolute_url ведет на правильный URL"""
        # reverse() берет имя маршрута из urls.py и подставляет slug
        expected_url = reverse('game_detail', kwargs={'slug': 'test-game'})
        self.assertEqual(self.game.get_absolute_url(), expected_url)


class ViewTests(TestCase):
    """Тесты для проверки открытия страниц (Views)"""

    def setUp(self):
        self.game = BoardGame.objects.create(
            title="Catan",
            slug="catan",
            play_time=90,
            description="Классика",
            is_published=True  # Важно: игра должна быть опубликована, чтобы отображаться
        )

    def test_home_page_status_code(self):
        """Главная страница должна открываться (код 200)"""
        response = self.client.get(reverse('game_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catan")  # Ищем название на странице

    def test_game_detail_status_code(self):
        """Страница игры должна открываться (код 200)"""
        response = self.client.get(reverse('game_detail', kwargs={'slug': 'catan'}))
        self.assertEqual(response.status_code, 200)

    def test_game_detail_404(self):
        """Страница несуществующей игры должна выдавать ошибку 404"""
        response = self.client.get(reverse('game_detail', kwargs={'slug': 'non-existent-game'}))
        self.assertEqual(response.status_code, 404)


class AuthTests(TestCase):
    """Тесты для проверки прав доступа (может ли гость оставить коммент)"""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password123")
        self.game = BoardGame.objects.create(
            title="Catan",
            slug="catan",
            play_time=90,
            description="Классика",
            is_published=True
        )

    def test_anonymous_user_cannot_comment(self):
        """Анонимный (незалогиненный) юзер не может отправить комментарий к игре.
        Его должно перекинуть на страницу логина (код 302)"""
        url = reverse('game_detail', kwargs={'slug': 'catan'})
        response = self.client.post(url, {'text': 'Привет'})

        # Проверяем, что был редирект (302)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что редирект ведет на страницу логина
        self.assertIn('/accounts/login/', response.url)
        # Проверяем, что комментарий НЕ создался в БД
        self.assertEqual(GameComment.objects.count(), 0)

    def test_logged_in_user_can_comment(self):
        """Залогиненный юзер МОЖЕТ отправить комментарий к игре,
        и он создается в БД"""
        # Логинимся
        self.client.login(username='tester', password='password123')

        url = reverse('game_detail', kwargs={'slug': 'catan'})
        response = self.client.post(url, {'text': 'Отличная игра!'})

        # Проверяем, что редирект (302) обратно на страницу игры
        self.assertEqual(response.status_code, 302)
        # Проверяем, что в БД появился 1 комментарий
        self.assertEqual(GameComment.objects.count(), 1)
        # Проверяем, что текст правильный и опубликован сразу (is_published=True)
        comment = GameComment.objects.first()
        self.assertEqual(comment.text, 'Отличная игра!')
        self.assertTrue(comment.is_published)