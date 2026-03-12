from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# -----------------------------
# Base Model (Reusable)
# -----------------------------
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


# -----------------------------
# ASSETS
# -----------------------------
class Asset(BaseModel):

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    asset_tag = models.CharField(max_length=100, unique=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiry = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.asset_tag})"


# -----------------------------
# TICKETS
# -----------------------------
class Ticket(BaseModel):

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_created')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_assigned')

    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)

    closed_at = models.DateTimeField(blank=True, null=True)

    def close_ticket(self):
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title


# -----------------------------
# KNOWLEDGE BASE
# -----------------------------
class KnowledgeArticle(BaseModel):

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=100)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# -----------------------------
# MAINTENANCE REPORTS
# -----------------------------
class MaintenanceReport(BaseModel):

    TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('emergency', 'Emergency'),
    ]

    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    related_asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def downtime_duration(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return self.title


# -----------------------------
# EMAIL CONFIGURATION
# -----------------------------
class EmailConfig(BaseModel):

    PURPOSE_CHOICES = [
        ('payroll', 'Payroll System'),
        ('ticket', 'Ticket System'),
    ]

    name = models.CharField(max_length=100)

    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES
    )

    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Encrypt in production
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    default_from_email = models.EmailField()

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"
        unique_together = ('purpose', 'is_active')

    def save(self, *args, **kwargs):
        # Ensure only ONE active config per purpose
        if self.is_active:
            EmailConfig.objects.filter(
                purpose=self.purpose,
                is_active=True
            ).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.purpose})"