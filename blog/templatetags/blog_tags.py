from django import template
from django.db.models import Count
from ..models import Post

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

# Creating an inclusion template tag. This will display the latest posts in
# the sidebar of the blog
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


# Create a QuerySet template_tag that shows the top 5 Posts with the most comments
# this will show all the posts with most comments.
@register.simple_tag
def get_most_commented_posts(count=5):
    """Retrieves the top 5 most commented on posts"""
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]
