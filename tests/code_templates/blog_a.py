from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=80)

    def __unicode__(self):
        return self.title


class Entry(models.Model):
    blog = models.ForeignKey(Blog)
    title = models.CharField(max_length=80, default="", null=True)

    def __unicode__(self):
        return self.title
