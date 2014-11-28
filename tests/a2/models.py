"""
Multiple inheritance sample 1 from docs.

Note: not more than one review per book looks like a wrong example.
"""
from django.db import models


class Model(models.Model):

    class Meta:
        app_label = 'a2'
        abstract = True


class Article(Model):
    article_id = models.AutoField(primary_key=True)
    headline = models.CharField(max_length=10)


class Book(Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=10)


class BookReview(Book, Article):
    pass
