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
