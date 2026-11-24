from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.students.models import Student

class Subject(models.Model):
    subject_code = models.CharField(max_length=50, unique=True, db_index=True)
    subject_name = models.CharField(max_length=150)
    maximum_marks = models.FloatField(default=100.0)
    passing_marks = models.FloatField(default=40.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject_code']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code})"


class Exam(models.Model):
    exam_name = models.CharField(max_length=150)
    academic_year = models.CharField(max_length=50, default='2024-2025')
    semester = models.CharField(max_length=30, default='Sem IV')
    department = models.CharField(max_length=100, default='Computer Science & Engineering')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'

    def __str__(self):
        return f"{self.exam_name} ({self.academic_year} - {self.semester})"


class StudentMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_marks')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_marks')
    marks_obtained = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'exam'],
                name='unique_student_subject_exam_mark'
            )
        ]
        indexes = [
            models.Index(fields=['exam', 'subject']),
            models.Index(fields=['student', 'exam']),
        ]
        verbose_name = 'Student Mark'
        verbose_name_plural = 'Student Marks'

    def __str__(self):
        return f"{self.student.roll_number} | {self.subject.subject_code}: {self.marks_obtained}"

    @property
    def is_passed(self):
        return self.marks_obtained >= self.subject.passing_marks
