from django.db import models
from apps.results.models import Exam

class ImportHistory(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('PARTIAL', 'Partial Success'),
        ('FAILED', 'Failed'),
    ]

    filename = models.CharField(max_length=255)
    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True, related_name='imports')
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
    error_summary = models.TextField(blank=True, null=True)
    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-imported_at']
        verbose_name = 'Import History'
        verbose_name_plural = 'Import Histories'

    def __str__(self):
        return f"{self.filename} ({self.status}) - {self.imported_at.strftime('%Y-%m-%d %H:%M')}"
