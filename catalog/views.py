from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse

# ИМПОРТЫ МОДЕЛЕЙ И ФОРМ (Именно их не хватало!)
from .models import BoardGame, Review, Comment, GameComment
from .forms import CommentForm, RegisterForm, GameCommentForm, ReviewForm


class BoardGameListView(ListView):
    model = BoardGame
    template_name = 'catalog/game_list.html'
    context_object_name = 'games'
    paginate_by = 10

    def get_queryset(self):
        return BoardGame.objects.filter(is_published=True)


class BoardGameDetailView(DetailView):
    model = BoardGame
    template_name = 'catalog/game_detail.html'
    context_object_name = 'game'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BoardGame.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game_form'] = GameCommentForm()
        context['game_comments'] = self.object.game_comments.filter(is_published=True)
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        form = GameCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.game = self.object
            comment.author = request.user
            comment.is_published = True
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('game_detail', slug=self.object.slug)

        context = self.get_context_data()
        context['game_form'] = form
        return self.render_to_response(context)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'catalog/review_form.html'

    def get_success_url(self):
        return reverse('game_detail', kwargs={'slug': self.object.game.slug})

    def form_valid(self, form):
        form.instance.game = get_object_or_404(BoardGame, slug=self.kwargs['slug'])
        form.instance.author = self.request.user
        form.instance.is_published = False
        messages.success(self.request, 'Обзор успешно отправлен на модерацию!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = get_object_or_404(BoardGame, slug=self.kwargs['slug'])
        return context


class ReviewDetailView(DetailView):
    model = Review
    template_name = 'catalog/review_detail.html'
    context_object_name = 'review'

    def get_queryset(self):
        return Review.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.filter(is_published=True)
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.review = self.object
            comment.author = request.user
            comment.is_published = False
            comment.save()
            messages.success(request, 'Комментарий отправлен на модерацию.')
            return redirect('review_detail', pk=self.object.pk)

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


@login_required
def toggle_comment_publication(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if not (request.user == comment.author or request.user.is_staff):
        messages.error(request, 'У вас нет прав на это действие.')
        return redirect('review_detail', pk=comment.review.pk)

    if request.method == 'POST':
        comment.is_published = not comment.is_published
        comment.save()
        status = 'опубликован' if comment.is_published else 'снят с публикации'
        messages.success(request, f'Комментарий {status}.')
        return redirect('review_detail', pk=comment.review.pk)

    return redirect('review_detail', pk=comment.review.pk)


def register(request):
    if request.user.is_authenticated:
        return redirect('game_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('game_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def about(request):
    return render(request, 'about.html')