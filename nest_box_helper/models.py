from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import pre_save
import random
import string


class Park(models.Model):
    park_name = models.CharField(max_length=50, default="None", unique=False)

    def __str__(self):
            return self.park_name


class UserParks(models.Model):
    park_name = models.ForeignKey(Park, on_delete=models.SET_NULL, null=True, unique=False)
    monitor_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.park_name)

    class Meta:
        verbose_name_plural = "User Parks"


class Box(models.Model):
    monitor_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    park_name = models.ForeignKey(Park, on_delete=models.SET_NULL, null=True)
    box_number = models.PositiveIntegerField(default=1)
    box_description = models.CharField(max_length=100, default="None")

    class Meta:
        verbose_name_plural = "Boxes"

    def __str__(self):
        return str(self.box_number)


class Attempt(models.Model):
    attempt_number = models.PositiveIntegerField()
    monitor_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    box_number = models.ForeignKey(Box, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.attempt_number)

    def get_year(self):
        return self.timestamp.year


def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))


class Sheet(models.Model):
    NEST_STATUS_CODES = (
        ('NO', 'No nest'),
        ('IN', 'Incomplete nest'),
        ('AN', 'New nest built on top of old'),
        ('CN', 'Complete nest'),
        ('DN', 'Damaged nest'),
        ('FN', 'Flattened nest'),
        ('NN', 'Non-avian nest'),
        ('RN', 'Nest gone'),
    )

    ADULT_ACTIVITY_CODES= (
        ('NO', 'No adult activity'),
        ('AA', 'At or on nest, then flushed'),
        ('BA', 'Building nest/carrying material'),
        ('DA', 'Dead adults at nest'),
        ('FA', 'Feeding young at the nest'),
        ('RA', 'Stayed on nest while box checked'),
        ('VA', 'Parents in vicinity during check'),
    )

    YOUNG_STATUS_CODES= (
        ('NO', 'No young - presumed dead'),
        ('FY', 'Fully feathered young'),
        ('HY', 'Hatchling young'),
        ('NY', 'Naked young'),
        ('PY', 'Partially feathered'),
        ('VY', 'Vocal young - you could not see them'),
        ('YY', 'Young presumed to have fledged'),
    )

    MANAGEMENT_CODES = (
        ('NO', 'No management done'),
        ('AM', 'Removed house sparrow nest/eggs'),
        ('EM', 'Unhatched host eggs removed'),
        ('NM', 'Cleaned nest box for next inhabitant'),
        ('PM', 'Removed pests from box'),
    )

    attempt_number = models.ForeignKey(Attempt, blank=False, on_delete=models.SET_NULL, null=True)
    monitor_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateField(blank=False)
    species = models.CharField(max_length=50, blank=True)
    eggs = models.PositiveIntegerField(default="0")
    live_young = models.PositiveIntegerField(default="0")
    dead_young = models.PositiveIntegerField(default="0")
    nest_status = models.CharField(max_length=2, choices=NEST_STATUS_CODES, default="NO")
    adult_activity = models.CharField(max_length=2, choices=ADULT_ACTIVITY_CODES, default="NO")
    young_status = models.CharField(max_length=2, choices= YOUNG_STATUS_CODES, blank=True)
    management_activity = models.CharField(max_length=2, choices= MANAGEMENT_CODES, default="NO")
    cowbird_evidence = models.CharField(max_length=50, default="None")
    comments = models.TextField(max_length=300, blank=True)
    slug = models.SlugField(blank=True, unique=True)


def __str__(self):
        return self.box_number

def pre_save_sheet_receiver(sender, instance, *args, **kwargs):
        if not instance.slug:
            instance.slug = slugify(rand_slug())

pre_save.connect(pre_save_sheet_receiver, sender=Sheet)


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("An email address is required")
        if not username:
            raise ValueError("A username is required")

        user = self.model(
                email=self.normalize_email(email),
                username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )

        user.is_admin=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_Label):
        return True
