"""
Multiple inheritance sample 1 from docs.

Note: not more than one review per book looks like a wrong example.
"""
from django.db import models


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)

    class Meta:
        app_label = 'a2'


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=10)

    class Meta:
        app_label = 'a2'


class BookReview(Book, Article):
    pass
