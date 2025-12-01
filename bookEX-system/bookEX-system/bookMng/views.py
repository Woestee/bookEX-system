# In bookMng/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import MainMenu
from .forms import BookForm
from .models import Book, Comment, Rating, Favorite

from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

# Create your views here.

def index(request):
    return render(request,
                  'bookMng/index.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })


def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request,
                  'bookMng/postbook.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'submitted': submitted
                  })


def displaybooks(request):
    books = Book.objects.all()
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books
                  })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.pic_path = book.picture.url[14:]

    comments = book.comments.all().order_by('-created_at')
    ratings = book.ratings.all()

    # Check if the book is in user's favorites
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, book=book).exists()

    # Compute average rating
    avg_rating = None
    if ratings.exists():
        avg_rating = sum(r.value for r in ratings) / ratings.count()

    return render(request, 'bookMng/book_detail.html', {
        'item_list': MainMenu.objects.all(),
        'book': book,
        'comments': comments,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'is_favorite': is_favorite,
    })


@login_required(login_url='login')
def add_comment_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(
                book=book,
                user=request.user,
                text=comment_text
            )
            return redirect('book_detail', book_id=book.id)

    context = {
        'item_list': MainMenu.objects.all(),
        'book': book
    }
    return render(request, 'bookMng/add_comment.html', context)


@login_required(login_url='login')
def add_rating_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        rating_value = request.POST.get('rating_value')
        if rating_value:
            Rating.objects.update_or_create(
                book=book,
                user=request.user,
                defaults={'value': rating_value}
            )
            return redirect('book_detail', book_id=book.id)

    context = {
        'item_list': MainMenu.objects.all(),
        'book': book
    }
    return render(request, 'bookMng/add_rating.html', context)


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def mybooks(request):
    books = Book.objects.filter(username=request.user)

    for b in books:
        if hasattr(b, 'picture') and getattr(b.picture, 'url', None):
            b.pic_path = b.picture.url[14:]

    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books
                  })


def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    return render(request,
                  'bookMng/book_delete.html',
                  {
                      'item_list': MainMenu.objects.all(),
                  })


@login_required(login_url='login')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")

    return redirect('book_detail', book_id=comment.book.id)


@login_required(login_url='login')
def delete_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)

    if request.user == rating.user or request.user.is_superuser:
        rating.delete()
        messages.success(request, "Rating deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this rating.")

    return redirect('book_detail', book_id=rating.book.id)


def about(request):
    return render(request, 'bookMng/about.html', {
        'item_list': MainMenu.objects.all(),
    })


@login_required(login_url='login')
def add_to_favorites(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Favorite.objects.get_or_create(user=request.user, book=book)
    messages.success(request, f'"{book.name}" added to favorites.')
    return redirect('book_detail', book_id=book.id)


@login_required(login_url='login')
def remove_from_favorites(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Favorite.objects.filter(user=request.user, book=book).delete()
    messages.info(request, f'"{book.name}" removed from favorites.')
    return redirect('book_detail', book_id=book.id)

@login_required(login_url='login')
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('book')

    fav_books = [f.book for f in favorites]

    for b in fav_books:
        if hasattr(b, 'picture') and getattr(b.picture, 'url', None):
            b.pic_path = b.picture.url[14:]  # or just b.picture.url if you don’t need slicing

    return render(request, 'bookMng/favorites_list.html', {
        'item_list': MainMenu.objects.all(),
        'books': fav_books,
    })


