from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('medium', 'Medium'),
        ('pro', 'Pro'),
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    score = models.IntegerField(default=0)
    groups = models.ManyToManyField('auth.Group', related_name='math_users_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='math_users_permissions')
    first_login = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    correct_answer = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text


class UserScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='score_info')
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Score: {self.score}"
