from django.db import models
from django.conf import settings


class Payment(models.Model):
    """Payment record for bookings."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
        PARTIALLY_REFUNDED = 'partial_refund', 'Partially Refunded'

    class PaymentMethod(models.TextChoices):
        SUMUP = 'sumup', 'SumUp'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        CASH = 'cash', 'Cash'

    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Amount (in pence)
    amount = models.PositiveIntegerField(help_text='Amount in pence')
    currency = models.CharField(max_length=3, default='GBP')

    # Payment details
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.SUMUP
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # SumUp specific fields
    sumup_checkout_id = models.CharField(max_length=100, blank=True)
    sumup_transaction_id = models.CharField(max_length=100, blank=True)
    sumup_checkout_url = models.URLField(blank=True)

    # Metadata
    description = models.CharField(max_length=200, blank=True)
    receipt_email = models.EmailField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.user} - {self.amount_display}"

    @property
    def amount_display(self):
        """Return amount in pounds."""
        return f"£{self.amount / 100:.2f}"


class Refund(models.Model):
    """Refund records."""

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.PositiveIntegerField(help_text='Refund amount in pence')
    reason = models.TextField()

    # SumUp specific
    sumup_refund_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund {self.id} - {self.amount / 100:.2f}"


class Invoice(models.Model):
    """Invoice generation for payments."""

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)

    # Billing details
    billing_name = models.CharField(max_length=200)
    billing_email = models.EmailField()
    billing_address = models.TextField(blank=True)

    # PDF
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number: TH-YYYYMM-XXXX
            from django.utils import timezone
            import random
            now = timezone.now()
            self.invoice_number = f"TH-{now.strftime('%Y%m')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
