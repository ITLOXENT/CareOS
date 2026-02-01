from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q

from ..state import CAREGIVER_STATUSES, MEDICATION_STATUSES
from .base import TimestampedModel


class Patient(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    given_name = models.CharField(max_length=120)
    family_name = models.CharField(max_length=120)
    date_of_birth = models.DateField(null=True, blank=True)
    nhs_number = models.CharField(max_length=32, null=True, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=120, blank=True)
    merged_into = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="merged_from"
    )
    merged_at = models.DateTimeField(null=True, blank=True)
    retention_class = models.CharField(max_length=64, blank=True, default="")
    retention_until = models.DateField(null=True, blank=True)
    restricted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "nhs_number"],
                name="unique_patient_nhs_per_org",
                condition=Q(nhs_number__isnull=False),
            )
        ]

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.given_name} {self.family_name}"


class PatientProfile(TimestampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    phone = models.CharField(max_length=32, unique=True)
    email = models.EmailField(blank=True)

    def __str__(self) -> str:
        return f"{self.organization_id}:{self.phone}"


class PatientOTP(TimestampedModel):
    phone = models.CharField(max_length=32)
    code = models.CharField(max_length=8)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.phone}:{self.expires_at.isoformat()}"


class PatientToken(TimestampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.expires_at.isoformat()}"


class MedicationSchedule(TimestampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=120, blank=True)
    instructions = models.TextField(blank=True)
    times = models.JSONField(default=list)
    timezone = models.CharField(max_length=64, default="UTC")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.name}"


class MedicationDoseEvent(TimestampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    schedule = models.ForeignKey(MedicationSchedule, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=MEDICATION_STATUSES)
    scheduled_for = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.status}:{self.scheduled_for.isoformat()}"


class CaregiverInvite(TimestampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    contact = models.CharField(max_length=255)
    channel = models.CharField(max_length=32, default="sms")
    status = models.CharField(max_length=16, choices=CAREGIVER_STATUSES, default="invited")
    permissions = models.JSONField(default=list)

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.contact}:{self.status}"


class Feedback(TimestampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    message = models.TextField()
    category = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.category}"


class PatientIdentifier(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="identifiers")
    kind = models.CharField(max_length=64)
    value = models.CharField(max_length=255)
    system = models.CharField(max_length=120, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.kind}:{self.value}"


class PatientAddress(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=64, default="home")
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=120, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.address_type}:{self.line1}"


class PatientContactMethod(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="contacts")
    kind = models.CharField(max_length=64)
    value = models.CharField(max_length=255)
    notes = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.kind}:{self.value}"


class CareCircleMember(TimestampedModel):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="care_circle")
    person_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=120)
    contact = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"{self.patient_id}:{self.person_name}"
