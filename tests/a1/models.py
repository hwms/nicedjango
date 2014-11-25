from django.db import models
from django.db.models.query import QuerySet


class Model(models.Model):
    id = models.CharField(max_length=10, primary_key=True)

    class Meta:
        app_label = 'a1'
        abstract = True


class A(Model):
    pass


class B(A):
    pass


class C(B):
    pass


class D(C):
    pass


class E(B):
    pass


class PManager(models.Manager):
    # TODO: make proxies work
    def get_queryset(self):
        return QuerySet(self.model).filter(id__startswith='p_')


class P(A):
    objects = PManager()

    class Meta:
        app_label = 'a1'
        proxy = True


class F(Model):
    a = models.ForeignKey(A, null=True)


class G(Model):
    d = models.ForeignKey(D, null=True)


class O(Model):
    c = models.OneToOneField(C, null=True)
    s = models.OneToOneField('self', null=True)


class M(Model):
    d = models.ManyToManyField(D)
    s = models.ManyToManyField('self')

M_d = getattr(M.d, 'through')
M_s = getattr(M.s, 'through')
