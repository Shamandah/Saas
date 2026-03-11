from decimal import Decimal
from django.db import models
from django.utils import timezone
from MasterData.models import Client, Supplier, File, Port, Transport, Currency, Item


class Quotation(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    commodity_desc = models.CharField(max_length=255, blank=True)
    fcl = models.CharField(max_length=100, blank=True)
    pol = models.ForeignKey(Port, related_name="pol_port", on_delete=models.SET_NULL, null=True)
    pod = models.ForeignKey(Port, related_name="pod_port", on_delete=models.SET_NULL, null=True)
    fpod = models.ForeignKey(Port, related_name="fpod_port", on_delete=models.SET_NULL, null=True)
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    vatable = models.BooleanField(default=True)
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=16)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    consignment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_code(self):
        year = timezone.now().year
        last = Quotation.objects.filter(code__startswith=f"QTN-{year}").order_by("id").last()
        if last:
            last_number = int(last.code.split("-")[-1])
            number = last_number + 1
        else:
            number = 1
        return f"QTN-{year}-{number:04d}"

    def calculate_totals(self):
        total = sum([item.total() for item in self.items.all()])
        self.total_amount = total
        self.vat_amount = (total * self.vat_percentage / Decimal(100)) if self.vatable else Decimal(0)
        self.grand_total = self.total_amount + self.vat_amount

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
        self.calculate_totals()
        super().save(update_fields=['total_amount', 'vat_amount', 'grand_total'])

    def __str__(self):
        return self.code


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.item.name} ({self.quantity} x {self.unit_price})"