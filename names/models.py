from django.db import models

class NameVector(models.Model):

    name = models.CharField(max_length=100, unique=True)

    x = models.FloatField()

    y = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name