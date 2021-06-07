from django.db import models


# class IngestionDataPath(models.Model):
#     path = models.TextField(unique=True)
#     success = models.BooleanField(default=False)
#     interval = models.CharField(max_length=100)
#     date = models.DateField()
#     should_retry = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['-date']
#
#     def __str__(self):
#         return self.path
