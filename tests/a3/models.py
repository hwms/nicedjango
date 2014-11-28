"""
Multiple inheritance sample 2 from docs.

Notes:
* not more than one review per book looks like a wrong example.
* have to define review differently for 1.7, despite docs say this is for 1.7:

    CommandError: System check identified some issues:

    ERRORS:
    a3.BookReview: (models.E005) The field 'piece_ptr' from parent model 'a3.book' clashes with the
    field 'piece_ptr' from parent model 'a3.article'.

"""
from django import VERSION
from django.db import models


class Piece(models.Model):
    class Meta:
        app_label = 'a3'


class Article(Piece):
    headline = models.CharField(max_length=10)


class Book(Piece):
    title = models.CharField(max_length=10)


if VERSION[:2] == (1, 7):
    class BookReview(Book):
        article_ptr = models.OneToOneField(Article)
        book_ptr = models.OneToOneField(Book)
else:
    class BookReview(Book, Article):
        pass
