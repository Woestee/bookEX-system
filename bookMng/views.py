# In bookMng/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import MainMenu
from .forms import BookForm

from .models import Book, Comment, Rating

from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
# Create your views here.
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
            #form.save()
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

    # Compute average rating (optional)
    avg_rating = None
    if ratings.exists():
        avg_rating = sum(r.value for r in ratings) / ratings.count()

    return render(request, 'bookMng/book_detail.html', {
        'item_list': MainMenu.objects.all(),
        'book': book,
        'comments': comments,
        'ratings': ratings,
        'avg_rating': avg_rating,
    })



@login_required  # Ensures only logged-in users can comment
def add_comment_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)  # Safer than .get()

    if request.method == 'POST':
        # This new block runs when the user submits the form
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(
                book=book,
                user=request.user,
                text=comment_text
            )
            # Send the user back to the book's detail page
            return redirect('book_detail', book_id=book.id)

    context = {
        'item_list': MainMenu.objects.all(),
        'book': book
    }
    return render(request, 'bookMng/add_comment.html', context)


@login_required  # Ensures only logged-in users can rate
def add_rating_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # This new block runs when the user submits the form
        rating_value = request.POST.get('rating_value')
        if rating_value:
            Rating.objects.update_or_create(
                book=book,
                user=request.user,
                defaults={'value': rating_value}
            )
            # Send the user back to the book's detail page
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


def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
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

from django.contrib import messages

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Only the user who made the comment or a superuser can delete
    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this comment.")

    return redirect('book_detail', book_id=comment.book.id)


@login_required
def delete_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)

    if request.user == rating.user or request.user.is_superuser:
        rating.delete()
        messages.success(request, "Rating deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this rating.")

    return redirect('book_detail', book_id=rating.book.id)
