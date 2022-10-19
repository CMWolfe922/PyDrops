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
