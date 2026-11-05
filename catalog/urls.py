from django.urls import path
from . import views

urlpatterns = [
    path('', views.BoardGameListView.as_view(), name='game_list'),
    path('game/<slug:slug>/', views.BoardGameDetailView.as_view(), name='game_detail'),
    path('review/<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('comment/<int:pk>/toggle/', views.toggle_comment_publication, name='comment_toggle'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
path('game/<slug:slug>/review/add/', views.ReviewCreateView.as_view(), name='review_add'),

]