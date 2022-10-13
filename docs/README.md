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
