from django.db import models


class A(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        app_label = 'a1'


class B(A):
    pass


class C(B):
    pass
