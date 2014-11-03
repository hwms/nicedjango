from django.db import models


class Abstract(models.Model):
    class Meta:
        app_label = 'testapp'
        abstract = True


class Real(Abstract):
    a = models.CharField(max_length=1)


class Proxy(Real):
    class Meta:
        app_label = 'testapp'
        proxy = True


class Sub(Real):
    b = models.BooleanField()


class SubSub(Sub):
    c = models.CharField(max_length=1)


class OneToOne(Abstract):
    r = models.OneToOneField(Real, null=True)
    s = models.OneToOneField('self', null=True)
    d = models.DecimalField(decimal_places=2, max_digits=6)


class ManyToMany(Abstract):
    m = models.ManyToManyField(Real)
    s = models.ManyToManyField('self')
    e = models.PositiveIntegerField()


class Foreign(Abstract):
    f = models.ForeignKey(Real, null=True)
    i = models.IntegerField()
