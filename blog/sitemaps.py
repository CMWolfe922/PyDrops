from django.contrib.sitemaps import Sitemap
from .models import Post

# create a PostSitemap class
class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    # create an item method
    def items(self):
        return Post.objects.all()

    # create a method that shows the last modified posts
    def lastmod(self, obj):
        return obj.updated
