from queue import Empty
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm
from django.views.generic import ListView
from django.core.mail import send_mail

def post_list(request):
    post_list = Post.published.all()

    # ------------------------------------------------ #
    # Create a paginator for the list view html page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # if page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page_number is out of range deliver the last page of results.
        posts = paginator.page(paginator.num_pages)

    # ------------------------------------------------ #
    # context dictionary that gets passed to the render function
    context = {
        'posts': posts,
        }

    return render(request,
                 'blog/post/list.html',
                 context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    context = {
        'post': post,

    }

    return render(request,
                  'blog/post/detail.html',
                  context)

# Create a clasd bassed view
class PostListView(ListView):
    """
    This is an alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    # Create a sent equals false variable
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'cmwolfe.dev@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }

    return render(request, 'blog/post/share.html', context)
