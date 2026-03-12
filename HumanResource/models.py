from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group, Permission

class Department(models.Model):
    name = models.ForeignKey(Group, on_delete=models.CASCADE, max_length=255, help_text="Department Name")
    description = models.TextField(max_length=255, help_text='Description', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}  {self.is_active}"
    
class ContractType(models.Model):
    name = models.CharField(max_length=255, help_text="Contract Name")
    description = models.CharField(max_length=255, help_text="Description")
    duration_month = models.DurationField(max_length=20, help_text="Duration in months")
    is_permanent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}  {self.is_active}"
    
class LeaveType(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=255, help_text="Leave Name")
    description = models.CharField(max_length=255, help_text="Description")
    duration = models.DurationField(max_length=20, help_text="Duration in Days")
    is_paid = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}  {self.is_active}"
    
class Employee(models.Model):
    payroll = models.IntegerField(unique=True, blank=False, help_text='Payroll no')

    name = models.CharField(max_length=255, help_text="Employee Name")
    contact_email = models.EmailField(max_length=255, unique=True, help_text='Email address')
    contact_phone = models.CharField(max_length=12, validators=[RegexValidator(r'^07\d{8}$', message='invalid phone number')], help_text='format: 07xxxxx')
    gender = models.CharField(max_length=255, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], blank=False)
    nok_Name= models.CharField(max_length=255, help_text="Next Of kin Name")
    nok_phone_number = models.CharField(max_length=12, validators=[RegexValidator(r'^07\d{8}$', message='invalid phone number')], help_text='Next Of kin Phone Number')
    nok_relationship = models.CharField(max_length=255, help_text="Relationship")

    department = models.ForeignKey(Department, on_delete=models.CASCADE, help_text='Department')
    designation = models.CharField(max_length=255, help_text="Designation")
    is_HOD = models.BooleanField(default=False)
    
    contract_info = models.ForeignKey(ContractType, on_delete=models.CASCADE)
    applicable_leave_type = models.ManyToManyField(LeaveType, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
    
class Allowance(models.Model):
    ALLOWANCE_TYPE = [
        ('amount','Amount'),
        ('percentage', 'Percentage'),
    ]
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=10, choices=ALLOWANCE_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}  {self.is_active}"
    
class Deduction(models.Model):
    DEDUCTION_TYPE = [
        ('amount','Amount'),
        ('percentage', 'Percentage'),
    ]
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=10, choices=DEDUCTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}  {self.is_active}"
    
class SalaryStructure(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.ManyToManyField(Allowance, blank=True)
    deductions = models.ManyToManyField(Deduction, blank=True)
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_allowances(self):
        total_allowances = 0
        for allowance in self.allowances.all():
            if allowance.type == 'amount':
                total_allowances += allowance.amount
            elif allowance.type == 'percentage':
                total_allowances += self.basic_salary * (allowance.amount / 100)
        return total_allowances
    
    @property
    def total_deductions(self):
        total_deductions = 0
        for deduction in self.deductions.all():
            if deduction.type == 'amount':
                total_deductions += deduction.amount
            elif deduction.type == 'percentage':
                total_deductions += (self.basic_salary + self.total_allowances) * (deduction.amount / 100)
        return total_deductions

    @property
    def gross_salary(self):
        return self.basic_salary + self.total_allowances
    
    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions - (self.gross_salary * self.tax_rate / 100)
    
from django.db import models
from datetime import date

class ProcessedSalary(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    salary_structure = models.ForeignKey('SalaryStructure', on_delete=models.CASCADE)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    date_processed = models.DateField(default=date.today)
    pdf_file = models.FileField(upload_to='salary_pdfs/', blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'salary_structure', 'date_processed')

    def __str__(self):
        return f"{self.employee} - {self.date_processed}"