from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(UserManager):
    # Create a method that will automatically run each time a user object is instantiated
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Valid e-mail address not provided!")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, default='', unique=True, required=True)
    username = models.CharField(max_length=255, blank=True, default='', unique=True, required=True)
    first_name = models.CharField(max_length=50, blank=True, default='', required=True)
    last_name = models.CharField(max_length=50, blank=True, default='', required=True)
    mobile_number = models.CharField(max_length=15, blank=True, default='', required=False)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:

        verbose_name = 'User'
        verbose_name_plural = 'Users'

        def get_full_name(self):
            return self.first_name + self.last_name

        def get_username(self):
            return self.username

        def get_email(self):
            return self.email

        def get_short_email(self):
            return self.name or self.email.split('@')[0]
