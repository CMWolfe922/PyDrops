
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from taggit.models import Tag


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

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
    # URL to pass to the render method:
    URL = 'blog/post/list.html'
    # context dictionary that gets passed to the render function
    context = {
        'posts': posts,
        'tag': tag,
        }
    return render(request, URL, context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Get a list of active comments for this post:
    comments = post.comments.filter(active=True)
    # Now get the form for users to comment
    form = CommentForm()

    # URL that gets passed to the render function
    URL = 'blog/post/detail.html'

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }

    return render(request, URL, context)


# Create a clasd bassed view
class PostListView(ListView):
    """
    This is an alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


# Create a form view
def post_share(request, post_id):
    # retrieve post by ID
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'cmwolfe.dev@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    URL = 'blog/post/share.html'

    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }

    return render(request, URL, context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A Comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Now assign the post to the comment
        comment.post = post
        # Now save the comment to the database
        comment.save()

    URL = 'blog/post/comment.html'

    context = {
        'post': post,
        'form': form,
        'comment': comment,
    }

    return render(request, URL, context)
