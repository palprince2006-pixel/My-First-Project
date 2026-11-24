from django.db import models

class Student(models.Model):
    roll_number = models.CharField(max_length=50, unique=True, db_index=True)
    student_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    department = models.CharField(max_length=100, default='Computer Science & Engineering')
    section = models.CharField(max_length=20, default='A')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.roll_number} - {self.student_name}"
