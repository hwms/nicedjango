from django.db import models


class Model(models.Model):
    id = models.CharField(max_length=10, primary_key=True)

    class Meta:
        app_label = 'a4'
        abstract = True


class Question(Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Response(Model):
    question = models.ForeignKey(Question)
    response_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class Sample(Model):
    bool = models.BooleanField()
    nullbool = models.NullBooleanField()
    date = models.DateField()
    time = models.TimeField()
    dec = models.DecimalField(decimal_places=2, max_digits=5)
    float = models.FloatField()
    text = models.TextField()
    comma = models.CommaSeparatedIntegerField(max_length=10)
    slug = models.SlugField()
