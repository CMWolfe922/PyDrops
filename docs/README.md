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

The related_name attribute allows you to name the attribute that you use for the relationship from the related object back to this one. We can retrieve the post of a comment object using comment.post and retrieve all comments associated with a post object using post.comments.all(). If you don’t define the related_name attribute, Django will use the name of the model in lowercase, followed by _set (that is, comment_set) to name the relationship of the related object to the object of the model, where this relationship has been defined.

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
{% extends "blog/base.html" %}
{% block title %}Add a comment{% endblock %}
{% block content %}
  {% if comment %}
    <h2>Your comment has been added.</h2>
    <p><a href="{{ post.get_absolute_url }}">Back to the post</a></p>
  {% else %}
    {% include "blog/post/includes/comment_form.html" %}
  {% endif %}
{% endblock %}
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
