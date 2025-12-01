from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('postbook', views.postbook, name='postbook'),
    path('displaybooks', views.displaybooks, name='displaybooks'),
    path('book_detail/<int:book_id>', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/comment/', views.add_comment_view, name='add_comment'),
    path('book/<int:book_id>/rate/', views.add_rating_view, name='add_rating'),
    path('mybooks', views.mybooks, name='mybooks'),
    path('book_delete/<int:book_id>', views.book_delete, name='book_delete'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('rating/<int:rating_id>/delete/', views.delete_rating, name='delete_rating'),
    path('aboutus', views.about, name='about'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('book/<int:book_id>/favorite', views.add_to_favorites, name='add_to_favorites'),
    path('book/<int:book_id>/unfavorite', views.remove_from_favorites, name='remove_from_favorites'),
]