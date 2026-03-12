from django.contrib import admin
from .models import (
    Asset,
    Ticket,
    KnowledgeArticle,
    MaintenanceReport,
    EmailConfig
)


# -----------------------------
# ASSET ADMIN
# -----------------------------
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_tag', 'category', 'status', 'assigned_to')
    list_filter = ('status', 'category')
    search_fields = ('name', 'asset_tag', 'serial_number')


# -----------------------------
# TICKET ADMIN
# -----------------------------
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('priority', 'status', 'category')
    search_fields = ('title', 'description')
    readonly_fields = ('closed_at',)


# -----------------------------
# KNOWLEDGE BASE ADMIN
# -----------------------------
@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_by', 'created_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}


# -----------------------------
# MAINTENANCE REPORT ADMIN
# -----------------------------
@admin.register(MaintenanceReport)
class MaintenanceReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'related_asset', 'performed_by', 'start_time', 'end_time')
    list_filter = ('report_type',)
    search_fields = ('title', 'description')


# -----------------------------
# EMAIL CONFIG ADMIN
# -----------------------------
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage, get_connection
from .models import (
    Asset,
    Ticket,
    KnowledgeArticle,
    MaintenanceReport,
    EmailConfig
)

# -----------------------------
# EMAIL CONFIG ADMIN
# -----------------------------
@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'host')

    change_form_template = "admin/it/emailconfig/change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:config_id>/test-smtp/',
                self.admin_site.admin_view(self.test_smtp_view),
                name='it_emailconfig_test_smtp',
            ),
        ]
        return custom_urls + urls

    def test_smtp_view(self, request, config_id):
        config = EmailConfig.objects.get(pk=config_id)

        if request.method == "POST":
            test_email = request.POST.get("test_email")

            try:
                connection = get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host=config.host,
                    port=config.port,
                    username=config.username,
                    password=config.password,
                    use_tls=config.use_tls,
                    use_ssl=config.use_ssl,
                )

                email = EmailMessage(
                    subject="SMTP Configuration Test",
                    body="This is a test email from Payroll SMTP configuration.",
                    from_email=config.default_from_email,
                    to=[test_email],
                    connection=connection,
                )

                email.send()

                self.message_user(
                    request,
                    f"Test email sent successfully to {test_email}",
                    level=messages.SUCCESS,
                )

            except Exception as e:
                self.message_user(
                    request,
                    f"SMTP Test Failed: {str(e)}",
                    level=messages.ERROR,
                )

            return redirect(f"../../{config_id}/change/")

        context = {
            "config": config,
        }

        return render(request, "admin/it/emailconfig/test_smtp.html", context)