from django.db import models


class User(models.Model):
    email = models.EmailField()
    uuid = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    invitor = models.CharField(max_length=100)
    invited_count = models.IntegerField(default=0)
    expire_date = models.DateTimeField('expire date')


class Magazine(models.Model):
    title = models.CharField(max_length=100)
    titleAndDate = models.CharField(max_length=100, default='')
    thumbnailPath = models.CharField(max_length=100, default='')
    todayUpdated = models.BooleanField(default=False)


class Subscribe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE)
