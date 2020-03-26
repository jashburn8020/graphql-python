from django.db import models
from django.conf import settings


class Link(models.Model):
    url = models.URLField()
    description = models.TextField(blank=True)
    # Integrate the Links and Users models
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE
    )
