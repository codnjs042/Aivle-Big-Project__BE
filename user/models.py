from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, nickname, password, selectedGenres, selectedArtist):
        if not email:
            raise ValueError('must have user email')
        if not nickname:
            raise ValueError('must have user nickname')
        if not password:
            raise ValueError('must have user password')
        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
            selectedGenres=selectedGenres,
            selectedArtist=selectedArtist
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password):
        user = self.create_user(
            email=self.normalize_email(email),
            nickname=nickname,
            password=password,
            selectedGenres=0,
            selectedArtist=0
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    selectedGenres = models.PositiveBigIntegerField(default=0)
    selectedArtist = models.PositiveBigIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin
