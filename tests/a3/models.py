"""
Multiple inheritance sample 2 from docs.

Notes:
* not more than one review per book looks like a wrong example.
* have to define review differently for 1.7, despite docs say this is for 1.7
"""
from django import VERSION
from django.db import models


class Piece(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        app_label = 'a3'


class Article(Piece):
    pass


class Book(Piece):
    pass


if VERSION[:2] == (1, 7):
    class BookReview(Book):
        article_ptr = models.OneToOneField(Article)
        book_ptr = models.OneToOneField(Book)
else:
    class BookReview(Book, Article):
        pass
