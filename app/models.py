from django.db import models

class Candidate(models.Model):
    full_name = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=255, blank=True)
    citizenship = models.CharField(max_length=255, blank=True)
    iin = models.CharField(max_length=20, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or f"Анкета #{self.pk}"


class Education(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255, blank=True)
    period = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    diploma = models.CharField(max_length=255, blank=True)


class Relative(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='relatives')
    full_name = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    relation = models.CharField(max_length=100, blank=True)
    job = models.CharField(max_length=255, blank=True)


class WorkExperience(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='work_experience')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    disciplinary = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True)
