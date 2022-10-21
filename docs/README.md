# Building PyDrops' Social Blog with Django:

---

> Notes, Tips, and Tricks for building a social python community for building a community of developers that post tutorials, HowTos and new projects that are being developed.

---

## COMMENTS:

> (This is where notes and and tips and tricks go regarding the site's commenting system)

================================

### Creating a Comment System:

---

- a comment model to store user comments on posts
- a form that allows users to submit comments and manages the data validation
- a view that processes the form and saves a new comment to the database
- a list of comments and a form to add a new comment that can be included in the post detail template.

#### > Create a Model for Comments

Let's start by building a model to store user comments on posts

```python

class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

        def __str__(self):
            return f'Comment by {self.name} on {self.post}'
```

This is the Comment model. We have added a ForeignKey field to associate each comment with a single post. This many-to-one relationship is defined in the Comment model because each comment will be made on one post, and each post may have multiple comments.

The related_name attribute allows you to name the attribute that you use for the relationship from the related object back to this one. We can retrieve the post of a comment object using comment.post and retrieve all comments associated with a post object using post.comments.all(). If you don’t define the related_name attribute, Django will use the name of the model in lowercase, followed by \_set (that is, comment_set) to name the relationship of the related object to the object of the model, where this relationship has been defined.

You can learn more about many-to-one relationships at [this link](https://docs.djangoproject.com/en/4.1/topics/db/examples/many_to_one/)

We have defined the active Boolean field to control the status of the comments. This field will allow us to manually deactivate inappropriate comments using the administration site. We use default=True to indicate that all comments are active by default.

We have defined the created field to store the date and time when the comment was created. By using auto_now_add, the date will be saved automatically when creating an object. In the Meta class of the model, we have added ordering = ['created'] to sort comments in chronological order by default, and we have added an index for the created field in ascending order. This will improve the performance of database lookups or ordering results using the created field.

The Comment model that we have built is not synchronized into the database. We need to generate a new database migration to create the corresponding database table.

### ADDING COMMENTS TO THE ADMINISTRATION SITE

---

Now I need to add this new model to the admin site to manage comments through a simple interface.

in `admin.py` file in the `blog` app I need to import the `Comment` model and add the `ModelAdmin` class.

```python

from .models import Post, Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']
```

Now we can manage Comment instances using the administration site.

### CREATING FORMS FROM MODELS

---

We need to build a form to let users comment on `blog` posts. Remember that Django has two base classes that can be used to create forms: `Form` and `ModelForm`. We used the `Form` class to allow users to share posts by email. Now we will use `ModelForm` to take advantage of the existing Comment model and build a form dynamically for it.

Edit the `forms.py` file of your `blog` application and add the following lines:

```python
from .models import Comment
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

```

To create a form from a model, we just indicate which model to build the form for in the `Meta` class of the form. Django will introspect the model and build the corresponding form dynamically.

Each model field type has a corresponding default `form` field type. The attributes of model fields are taken into account for form validation. By default, Django creates a form field for each field contained in the model. However, we can explicitly tell Django which fields to include in the form using the `fields` attribute or define which fields to exclude using the `exclude` attribute. In the `CommentForm` form, we have explicitly included the `name`, `email`, and `body` fields. These are the only fields that will be included in the form.

You can find more information about creating forms from models at [This Link](https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/)

### HANDLING MODEL FORMS IN VIEWS:

---

For sharing posts by email, we used the same view to display the form and manage its submission. We used the `HTTP` method to differentiate between both cases; `GET` to display the form and `POST` to submit it. In this case, we will add the comment form to the post detail page, and we will build a separate view to handle the form submission. The new view that processes the form will allow the user to return to the post detail view once the comment has been stored in the database.

Edit the `views.py` file of the `blog` application and add the following code:

```python
# Also add CommentForm in the imports for .forms
from .forms import EmailPostForm, `CommentForm`
from django.views.decorators.http import require_POST
# ...
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html',
                           {'post': post,
                            'form': form,
                            'comment': comment})
```

We have defined the post_comment view that takes the request object and the post_id variable as parameters. We will be using this view to manage the post submission. We expect the form to be submitted using the HTTP POST method. We use the require_POST decorator provided by Django to only allow POST requests for this view. Django allows you to restrict the HTTP methods allowed for views. Django will throw an HTTP 405 (method not allowed) error if you try to access the view with any other HTTP method.

In this view, we have implemented the following actions:

    1. We retrieve a published post by its id using the get_object_or_404() shortcut.
    2. We define a comment variable with the initial value None. This variable will be used to store the comment object when it gets created.
    3. We instantiate the form using the submitted POST data and validate it using the is_valid() method. If the form is invalid, the template is rendered with the validation errors.
    4. If the form is valid, we create a new Comment object by calling the form’s save() method and assign it to the new_comment variable, as follows:
        - `comment = form.save(commit=False)`

- The `save()` method method is available for `ModelForm` but NOT for `Form`

- We also need to assign the `Post` to the `Comment` we created.
  `comment.post = post`

##### Creating a URL pattern for the Comment view

```python
from django.urls import path
from . import views
app_name = 'blog'

urlpattterns = [
    ...
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
]
```

### CREATING TEMPLATES FOR THE COMMENT FORM:

---

We will create a template for the comment form that we will use in two places:

1. In the post detail template associated with the `post_detail` view to let users publish comments.
2. In the post comment template associated with the `post_comment` vieww to display the form again if there are any form errors.

So I will create the comment template and use the `{% include %}` template tag to include the comment template in the other two templates.

- So in the `template/blog/post/` directory I will create a directory called `includes/`. Here I will add the `comment_form.html` file.

> So now I need to edit the new `blog/post/includes/comment_form.html` template with this code:

```html

<h2>Add a new comment</h2>
<form action="{% url "blog:post_comment" post.id %}" method="post">
  {{ form.as_p }}
  {% csrf_token %}
  <p><input type="submit" value="Add comment"></p>
</form>
```

In this template, we build the `action` URL of the HTML `<form>` element dynamically using the `{% url %}` template tag. We build the URL of the `post_comment` view that will process the form. We display the form rendered in paragraphs and we include `{% csrf_token %}` for CSRF protection because this form will be submitted with the `POST` method.

Create a new file in the `templates/blog/post/` directory of the blog application and name it `comment.html`.

In that file add this code:

```html
{% extends "blog/base.html" %} {% block title %}Add a comment{% endblock %} {%
block content %} {% if comment %}
<h2>Your comment has been added.</h2>
<p><a href="{{ post.get_absolute_url }}">Back to the post</a></p>
{% else %} {% include "blog/post/includes/comment_form.html" %} {% endif %} {%
endblock %}
```

This is the template for the post comment view. In this view, we expect the form to be submitted via the `POST` method. The template covers two different scenarios:

    > 1. If the form data submitted is valid, the comment variable will contain the comment object that was created, and a success message will be displayed.
    > 2. If the form data submitted is not valid, the comment variable will be None. In this case we will display the comment form. We use the {% include %} template tag to include the comment_form.html template that we have previously created.

#### Now I need to add comments to the post detail view:

> For this I will have to edit the views.py file and edit the post_detail view with the following changes:

```python

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    #===========================================#
    # ================ NEW ADDITION ============#
    #===========================================#
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    #==========================================#
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                  # ================== #
                  # === NEW ADDITION = #
                  # ================== #
                   'comments': comments,
                   'form': form})
```

##### HERE ARE SOME MORE RESOURCES THAT PROVIDE ADDITIONAL INFORMATION ABOUT SOME OF THE TOPICS ABOVE:

[PACKT PUB CHAPTER 2 GITHUB PAGE](https://github.com/PacktPublishing/Django-4-by-example/tree/main/Chapter02)
[URL UTILITY FUNCTIONS](https://docs.djangoproject.com/en/4.1/ref/urlresolvers/)
[URL PATH CONVERTERS](https://docs.djangoproject.com/en/4.1/topics/http/urls/#path-converters)
[DJANGO PAGINATOR CLASS](https://docs.djangoproject.com/en/4.1/ref/paginator/)
[INTRO TO CLASS BASED VIEWS](https://docs.djangoproject.com/en/4.1/topics/class-based-views/intro/)
[SENDING EMAILS WITH DJANGO](https://docs.djangoproject.com/en/4.1/topics/email/)
[DJANGO FORM FIELD TYPES](https://docs.djangoproject.com/en/4.1/ref/forms/fields/)
[WORKING WITH FORMS](https://docs.djangoproject.com/en/4.1/topics/forms/)
[CREATING FORMS FROM MODELS](https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/)
[MANY-TO-ONE MODEL RELATIONSHIPS](https://docs.djangoproject.com/en/4.1/topics/db/examples/many_to_one/)

---

#### SUMMARY

In this chapter, you learned how to define canonical URLs for models. You created SEO-friendly URLs for blog posts, and you implemented object pagination for your post list. You also learned how to work with Django forms and model forms. You created a system to recommend posts by email and created a comment system for your blog.

In the next chapter, you will create a tagging system for the blog. You will learn how to build complex QuerySets to retrieve objects by similarity. You will learn how to create custom template tags and filters. You will also build a custom sitemap and feed for your blog posts and implement a full-text search functionality for your posts.

============================================================

## EXTENDING THE BLOG APP:

---

### Adding Tagging Functionality

> `pip install django-taggit==3.0.0` then once that is complete, hr eill be going

---

#### Implementing custom template tags

> Django provides the following helper functions that allow you to easily create template tags:

- `simple_tag`: Processes the given data and returns a string
- `inclusion_tag`: Processes the given data and returns a rendered template
- Template tags must live inside Django applications.

Inside your blog application directory, create a new directory, name it `templatetags`, and add an empty `__init__.py` file to it. Create another file in the same folder and name it `blog_tags.py`. The file structure of the blog application should look like the following:

```
blog/
    __init__.py
    models.py
    ...
    templatetags/
        __init__.py
        blog_tags.py

```

> The way you name the file is important. You will use the name of this module to load tags in templates.

#### Creating a simple template tag

---

> Let’s start by creating a simple tag to retrieve the total posts that have been published on the blog.

- Edit the `templatetags/blog_tags.py` file you just created and add the following code:

```python

from django import template
from ..models import Post
register = template.Library()
@register.simple_tag
def total_posts():
    return Post.published.count()

```

- We have created a simple template tag that returns the number of posts published in the blog.

Each module that contains template tags needs to define a variable called `register` to be a valid tag library. This variable is an instance of `template.Library`, and it’s used to register the template tags and filters of the application.

In the preceding code, we have defined a tag called `total_posts` with a simple Python function. We have added the `@register.simple_tag` decorator to the function, to register it as a simple tag. Django will use the function’s name as the tag name. If you want to register it using a different name, you can do so by specifying a `name` attribute, such as `@register.simple_tag(name='my_tag')`.

> **After adding a new template tags module, you will need to restart the Django development server in order to use the new tags and filters in templates**.

Before using custom template tags, we have to make them available for the template using the `{% load %}` tag. As mentioned before, we need to use the name of the Python module containing your template tags and filters.

Edit the `blog/templates/base.html` template and add `{% load blog_tags %}` at the top of it to load your template tags module. Then, use the tag you created to display your total posts, as follows. The new lines are highlighted in bold:

```html
{% load blog_tags %} {% load static %}
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}{% endblock %}</title>
    <link href="{% static "css/blog.css" %}" rel="stylesheet">
  </head>
  <body>
    <div id="content">{% block content %} {% endblock %}</div>
    <div id="sidebar">
      <h2>My blog</h2>
      <p>This is my blog. I've written {% total_posts %} posts so far.</p>
    </div>
  </body>
</html>
```

### Creating an inclusion template tag

---

> We will create another tag to display the latest posts in the sidebar of the blog. This time, we will implement an inclusion tag. Using an inclusion tag, you can render a template with context variables returned by your template tag.

- Edit the templatetags/blog_tags.py file and add the following code:

```python
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
```

In the preceding code, we have registered the template tag using the `@register.inclusion_tag` decorator. We have specified the template that will be rendered with the returned values using `blog/post/latest_posts.html`. The template tag will accept an optional `count` parameter that defaults to 5. This parameter will allow us to specify the number of posts to display. We use this variable to limit the results of the query `Post.published.order_by('-publish')[:count]`.

Note that the function returns a dictionary of variables instead of a simple value. Inclusion tags have to return a dictionary of values, which is used as the context to render the specified template. The template tag we just created allows us to specify the optional number of posts to display as `{% show_latest_posts 3 %}`.

Now, create a new template file under `blog/post/` and name it `latest_posts.html`.

Edit the new `blog/post/latest_posts.html` template and add the following code to it:

```html
<ul>
  {% for post in latest_posts %}
  <li>
    <a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
  </li>
  {% endfor %}
</ul>
```

In the preceding code, you display an unordered list of posts using the `latest_posts` variable returned by your template tag. Now, edit the `blog/base.html` template and add the new template tag to display the last three posts, as follows. The new lines are highlighted in bold:

```html
{% load blog_tags %} {% load static %}
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}{% endblock %}</title>
    <link href="{% static 'css/blog.css' %}" rel="stylesheet" />
  </head>

  <body>
    <div id="content">{% block content %} {% endblock %}</div>
    <div id="sidebar">
      <h2>PyDrops:</h2>
      <p>
        A social community for python developers to come and drop knowledge for
        other developers.
      </p>
      <p class="blog-count">Total Blogs: {% total_posts %}</p>
      <!-- The newly added piece to the base template file -->
      <h3>Latest Posts:</h3>
      <!-- Adding the number after the show_latest_posts tag, tells the template how many posts to render -->
      {% show_latest_posts 3 %}
    </div>
  </body>
</html>
```

### Creating a Template Tag That Returns a QuerySet:

---

> Finally, we will create a simple template tag that returns a value. We will store the result in a variable that can be reused, rather than outputting it directly. We will create a tag to display the most commented posts.

- Edit the `templatetags/blog_tags.py` file and add the following import and template tag to it:

```python
from django.db.models import Count
@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
               total_comments=Count('comments')
           ).order_by('-total_comments')[:count]

```

In the preceding template tag, you build a QuerySet using the `annotate()` function to aggregate the total number of comments for each post. You use the `Count` aggregation function to store the number of comments in the computed `total_comments` field for each `Post` object. You order the QuerySet by the computed field in descending order. You also provide an optional `count` variable to limit the total number of objects returned.

In addition to `Count`, Django offers the aggregation functions `Avg`, `Max`, `Min`, and `Sum`. You can read more about aggregation functions at [Click Here for information on db aggregation](https://docs.djangoproject.com/en/4.1/topics/db/aggregation/)

Next, edit the `blog/base.html` template and add the following code highlighted in bold:

```html
{% load blog_tags %} {% load static %}
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}{% endblock %}</title>
    <link href="{% static 'css/blog.css' %}" rel="stylesheet" />
  </head>

  <body>
    <div id="content">{% block content %} {% endblock %}</div>
    <div id="sidebar">
      <h2>PyDrops:</h2>
      <p>
        A social community for python developers to come and drop knowledge for
        other developers.
      </p>
      <p class="blog-count">Total Blogs: {% total_posts %}</p>
      <!-- The newly added piece to the base template file -->
      <h3>Latest Posts:</h3>
      <!-- Adding the number after the show_latest_posts tag, tells the template how many posts to render -->
      {% show_latest_posts 3 %}
      <!-- Show the most commented on posts -->
      <h3>Most Commented Posts:</h3>
      {% get_most_commented_posts as most_commented_posts %}
      <ul>
        {% for post in most_commented_posts %}
        <li>
          <a href="{{ post.get_absolute_url  }}">{{ post.title }}</a>
        </li>
        {% endfor %}
      </ul>
      <p class="back-home">
        <a href="{% url 'blog:post_list' %}">Back to Home</a>
      </p>
    </div>
  </body>
</html>
```

In the preceding code, we store the result in a custom variable using the `as` argument followed by the variable name. For the template tag, we use `{% get_most_commented_posts as most_commented_posts %}` to store the result of the template tag in a new variable named `most_commented_posts`. Then, we display the returned posts using an HTML unordered list element.

> You have now a clear idea about how to build custom template tags. You can read more about them at [Link to Docs on Custom Template Tags](https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/)

### Implementing custom template filters

---

Django has a variety of built-in template filters that allow you to alter variables in templates. These are Python functions that take one or two parameters, the value of the variable that the filter is applied to, and an optional argument. They return a value that can be displayed or treated by another filter.

A filter is written like `{{ variable|my_filter }}`. Filters with an argument are written like `{{ variable|my_filter:"foo" }}`. For example, you can use the `capfirst` filter to capitalize the first character of the value, like `{{ value|capfirst }}`. If `value` is `django`, the output will be `Django`. You can apply as many filters as you like to a variable, for example, `{{ variable|filter1|filter2 }}`, and each filter will be applied to the output generated by the preceding filter.

[You can find the list of Django’s built-in template filters at](https://docs.djangoproject.com/en/4.1/ref/templates/builtins/#built-in-filter-reference).

### Creating a template filter to support Markdown syntax

---

> _We will create a custom filter to enable the use of Markdown syntax in your blog posts and then convert the post body to HTML in the templates._

Markdown is a plain text formatting syntax that is very simple to use, and it’s intended to be converted into HTML. You can write posts using simple Markdown syntax and get the content automatically converted into HTML code. Learning Markdown syntax is much easier than learning HTML. By using Markdown, you can get other non-tech savvy contributors to easily write posts for your blog. You can learn the basics of the Markdown syntax. [Link to learn Markdown syntax:](https://daringfireball.net/projects/markdown/basics)

First, install the Python `markdown` module via `pip` using the following command in the shell prompt:

`pip install markdown==3.4.1`

Then edit the `templatetags/blog_post.py` file and then create this function:

```python
from django.utils.safestring import mark_safe
import markdown
...

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
```

We register template filters in the same way as template tags. To prevent a name clash between the function name and the `markdown` module, we have named the function `markdown_format` and we have named the filter `markdown` for use in templates, such as `{{ variable|markdown }}`.

Django escapes the HTML code generated by filters; characters of HTML entities are replaced with their HTML encoded characters. For example, `<p>` is converted to `&lt;p&gt;` (less than symbol, p character, greater than symbol).

We use the `mark_safe` function provided by Django to mark the result as safe HTML to be rendered in the template. By default, Django will not trust any HTML code and will escape it before placing it in the output. The only exceptions are variables that are marked as safe from escaping. This behavior prevents Django from outputting potentially dangerous HTML and allows you to create exceptions for returning safe HTML.

Edit the `blog/post/detail.html` template and add the following new code highlighted in bold:

```html
{% extends "blog/base.html" %}
<!-- ADDED THE LOAD BLOG_TAGS TAG -->
{% load blog_tags %}
{% block title %}{{ post.title }}{% endblock %}
{% block content %}
  <h1>{{ post.title }}</h1>
  <p class="date">
    Published {{ post.publish }} by {{ post.author }}
  </p>
  <!-- CHANGED THE VARIABLE BELOW FROM HAVING linebreaks TO markdown -->
  {{ post.body|markdown }}
  <p>
    <a href="{% url "blog:post_share" post.id %}">
      Share this post
    </a>
  </p>
  <h2>Similar posts</h2>
  {% for post in similar_posts %}
    <p>
      <a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
    </p>
  {% empty %}
    There are no similar posts yet.
  {% endfor %}
  {% with comments.count as total_comments %}
    <h2>
      {{ total_comments }} comment{{ total_comments|pluralize }}
    </h2>
  {% endwith %}
  {% for comment in comments %}
    <div class="comment">
      <p class="info">
        Comment {{ forloop.counter }} by {{ comment.name }}
        {{ comment.created }}
      </p>
      {{ comment.body|linebreaks }}
    </div>
  {% empty %}
    <p>There are no comments yet.</p>
  {% endfor %}
  {% include "blog/post/includes/comment_form.html" %}
{% endblock %}

```

> We have replaced the `linebreaks` filter of the `{{ post.body }}` template variable with the `markdown` filter. This filter will not only transform line breaks into `<p>` tags; it will also transform Markdown formatting into HTML.

- Edit the `blog/post/list.html` template and add the following new code highlighted in bold:

```html

{% extends "blog/base.html" %}
<!-- ADD THE LOAD BLOG_TAGS TAG -->
{% load blog_tags %}
<!-- -------------------------- -->
{% block title %}My Blog{% endblock %}
{% block content %}
  <h1>My Blog</h1>
  {% if tag %}
    <h2>Posts tagged with "{{ tag.name }}"</h2>
  {% endif %}
  {% for post in posts %}
    <h2>
      <a href="{{ post.get_absolute_url }}">
        {{ post.title }}
      </a>
    </h2>
    <p class="tags">
      Tags:
      {% for tag in post.tags.all %}
        <a href="{% url "blog:post_list_by_tag" tag.slug %}">
          {{ tag.name }}
        </a>
        {% if not forloop.last %}, {% endif %}
      {% endfor %}
    </p>
    <p class="date">
      Published {{ post.publish }} by {{ post.author }}
    </p>
    <!-- CHANGE THESE VARIABLE FILTERS BELOW -->
    {{ post.body|markdown|truncatewords_html:30 }}
    <!-- ----------------------------------- -->
  {% endfor %}
  {% include "pagination.html" with page=posts %}
{% endblock %}
```

> We have added the new `markdown` filter to the `{{ post.body }}` template variable. This filter will transform the Markdown content into HTML. Therefore, we have replaced the previous `truncatewords` filter with the `truncatewords_html` filter. This filter truncates a string after a certain number of words avoiding unclosed HTML tags.

- Then open `http://127.0.0.1:8000/admin/blog/post/add/` in your browser and create a new post with the following body:

```md
## This is a post formatted with markdown

_This is emphasized_ and **this is more emphasized**.
Here is a list:

- One
- Two
- Three
  And a [link to the Django website](https://www.djangoproject.com/).
```


### Adding a sitemap to the site
---

> Django comes with a sitemap framework, which allows you to generate sitemaps for your site dynamically. A sitemap is an XML file that tells search engines the pages of your website, their relevance, and how frequently they are updated. Using a sitemap will make your site more visible in search engine rankings because it helps crawlers to index your website’s content.

The Django sitemap framework depends on `django.contrib.sites`, which allows you to associate objects to particular websites that are running with your project. This comes in handy when you want to run multiple sites using a single Django project. To install the sitemap framework, we will need to activate both the sites and the sitemap applications in your project.

Edit the `settings.py` file of the project and add `django.contrib.sites` and `django.contrib.sitemaps` to the `INSTALLED_APPS` setting. Also, define a new setting for the site ID, as follows. New code is highlighted in bold:

```python
# ...
# ADD THE SITE_ID AND SET IT TO 1
SITE_ID = 1
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog.apps.BlogConfig',
    'taggit',

    # THEN ADD THESE TWO DJANGO GENERIC APPS
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

```

> Now, run the following command from the shell prompt to create the tables of the Django site application in the database:

`python manage.py migrate`

I will see:
```
Applying sites.0001_initial... OK
Applying sites.0002_alter_domain_unique... OK

```

The sites application is now synced with the database.

Next, create a new file inside your blog application directory and name it sitemaps.py. Open the file and add the following code to it:

```python
from django.contrib.sitemaps import Sitemap
from .models import Post
class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9
    def items(self):
        return Post.published.all()
    def lastmod(self, obj):
        return obj.updated

```

I have defined a custom sitemap by inheriting the `Sitemap` class of the `sitemaps` module. The `changefreq` and `priority` attributes indicate the change frequency of your post pages and their relevance in your website (the maximum value is 1).

The `items()` method returns the QuerySet of objects to include in this sitemap. By default, Django calls the `get_absolute_url()` method on each object to retrieve its URL. Remember that we implemented this method in Chapter 2, Enhancing Your Blog with Advanced Features, to define the canonical URL for posts. If you want to specify the URL for each object, you can add a location method to your sitemap class.

The lastmod method receives each object returned by `items()` and returns the last time the object was modified.

Both the changefreq and priority attributes can be either methods or attributes. [You can take a look at the complete sitemap reference in the official Django documentation located at](https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/)

We have created the sitemap. Now we just need to create an URL for it.

Edit the main urls.py file of the mysite project and add the sitemap, as follows. New lines are highlighted in bold:

```python
from django.urls import path, include
from django.contrib import admin

# THIS WAS ADDED:
# ----------------------------------------------- #
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap
sitemaps = {
    'posts': PostSitemap,
}
# ----------------------------------------------- #
urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    # AND THIS
    # ----------------------------------------------- #
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
    # ----------------------------------------------- #
]

```
In the preceding code, we have included the required imports and have defined a sitemaps dictionary. Multiple sitemaps can be defined for the site. We have defined a URL pattern that matches with the sitemap.xml pattern and uses the sitemap view provided by Django. The sitemaps dictionary is passed to the sitemap view.

Start the development from the shell prompt with the following command:
`python manage.py runserver`


Open http://127.0.0.1:8000/sitemap.xml in your browser. You will see an XML output including all of the published posts like this:

```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>http://example.com/blog/2022/1/22/markdown-post/</loc>
    <lastmod>2022-01-22</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>http://example.com/blog/2022/1/3/notes-on-duke-ellington/</loc>
    <lastmod>2022-01-03</lastmod>
    <changefreq>weekly</changefreqa>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>http://example.com/blog/2022/1/2/who-was-miles-davis/</loc>
    <lastmod>2022-01-03</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>http://example.com/blog/2022/1/1/who-was-django-reinhardt/</loc>
    <lastmod>2022-01-03</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>http://example.com/blog/2022/1/1/another-post/</loc>
    <lastmod>2022-01-03</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>

```

The URL for each Post object is built by calling its get_absolute_url() method.

The lastmod attribute corresponds to the post updated date field, as you specified in your sitemap, and the changefreq and priority attributes are also taken from the PostSitemap class.

The domain used to build the URLs is example.com. This domain comes from a Site object stored in the database. This default object was created when you synced the site’s framework with your database. [You can read more about the sites framework at](https://docs.djangoproject.com/en/4.1/ref/contrib/sites/).

Open http://127.0.0.1:8000/admin/sites/site/

Here, you can set the domain or host to be used by the site’s framework and the applications that depend on it. To generate URLs that exist in your local environment, change the domain name to localhost:8000

Open http://127.0.0.1:8000/sitemap.xml in your browser again. The URLs displayed in your feed will now use the new hostname and look like http://localhost:8000/blog/2022/1/22/markdown-post/. Links are now accessible in your local environment. In a production environment, you will have to use your website’s domain to generate absolute URLs.


### Creating feeds for blog posts
---

Django has a built-in syndication feed framework that you can use to dynamically generate RSS or Atom feeds in a similar manner to creating sitemaps using the site’s framework. A web feed is a data format (usually XML) that provides users with the most recently updated content. Users can subscribe to the feed using a feed aggregator, a software that is used to read feeds and get new content notifications.

Create a new file in your blog application directory and name it feeds.py. Add the following lines to it:

```python
import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post
class LatestPostsFeed(Feed):
    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog.'
    def items(self):
        return Post.published.all()[:5]
    def item_title(self, item):
        return item.title
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)
    def item_pubdate(self, item):
        return item.publish

```

In the preceding code, we have defined a feed by subclassing the Feed class of the syndication framework. The title, link, and description attributes correspond to the <title>, <link>, and <description> RSS elements, respectively.

We use reverse_lazy() to generate the URL for the link attribute. The reverse() method allows you to build URLs by their name and pass optional parameters. We used reverse() in Chapter 2, Enhancing Your Blog with Advanced Features.

The reverse_lazy() utility function is a lazily evaluated version of reverse(). It allows you to use a URL reversal before the project’s URL configuration is loaded.

The items() method retrieves the objects to be included in the feed. We retrieve the last five published posts to include them in the feed.

The item_title(), item_description(), and item_pubdate() methods will receive each object returned by items() and return the title, description and publication date for each item.

In the item_description() method, we use the markdown() function to convert Markdown content to HTML and the truncatewords_html() template filter function to cut the description of posts after 30 words, avoiding unclosed HTML tags.

Now, edit the blog/urls.py file, import the LatestPostsFeed class, and instantiate the feed in a new URL pattern, as follows:

```python

from django.urls import path
from . import views
# ---------------------------------------------- #
# NEW IMPORT
# ---------------------------------------------- #
from .feeds import LatestPostsFeed


app_name = 'blog'
urlpatterns = [
    # Post views
    path('', views.post_list, name='post_list'),
    # path('', views.PostListView.as_view(), name='post_list'),
    path('tag/<slug:tag_slug>/',
         views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail,
         name='post_detail'),
    path('<int:post_id>/share/',
         views.post_share, name='post_share'),
    path('<int:post_id>/comment/',
         views.post_comment, name='post_comment'),
         # ---------------------------------------------- #
         # NEW PATH
         # ---------------------------------------------- #
    path('feed/', LatestPostsFeed(), name='post_feed'),
]

```
