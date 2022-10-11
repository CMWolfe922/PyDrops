from queue import Empty
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
