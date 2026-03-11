# HumanResource/utils.py

from django.core.mail import EmailMessage, get_connection
from IT.models import EmailConfig


def get_payroll_email_connection():
    """
    Fetch active payroll email configuration from IT app
    and return (connection, from_email)
    """
    config = EmailConfig.objects.filter(
        purpose='payroll',
        is_active=True
    ).first()

    if not config:
        return None, None

    connection = get_connection(
        backend='django.core.mail.backends.smtp.EmailBackend',
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        use_tls=config.use_tls,
        use_ssl=config.use_ssl,
    )

    return connection, config.default_from_email


def send_payslip_email(employee_email, employee_name, pdf_file, payroll_month, payroll_year):
    """
    Send a payslip PDF to an employee via dynamic Payroll email configuration.
    """

    if not pdf_file:
        return False

    connection, from_email = get_payroll_email_connection()

    if not connection:
        print("No active Payroll email configuration found.")
        return False

    subject = f"Payslip for {payroll_month}/{payroll_year}"
    body = f"""
Dear {employee_name},

Please find attached your payslip for {payroll_month}/{payroll_year}.

Best regards,
HR
"""

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[employee_email],
        connection=connection
    )

    email.attach(
        pdf_file.name,
        pdf_file.read(),
        'application/pdf'
    )

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send payslip to {employee_email}: {e}")
        return False

def test_payroll_email_configuration(test_email):
    """
    Send a test email using the active payroll configuration.
    Returns (True, message) or (False, error)
    """

    connection, from_email = get_payroll_email_connection()

    if not connection:
        return False, "No active Payroll email configuration found."

    subject = "Payroll Email Configuration Test"
    body = "This is a test email to verify Payroll SMTP configuration."

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[test_email],
            connection=connection
        )
        email.send()
        return True, "Test email sent successfully."
    except Exception as e:
        return False, str(e)