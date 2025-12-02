from django.contrib import admin

# Register your models here.
from .models import MainMenu, Book, Comment, Rating, Favorite

admin.site.register(MainMenu)
admin.site.register(Book)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(Favorite)