from django.contrib import admin
from .models import Payment, Refund, Invoice


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'booking', 'amount_display',
        'payment_method', 'status', 'created_at', 'paid_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'sumup_checkout_id', 'sumup_transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'amount_display')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Payment', {
            'fields': ('user', 'booking', 'amount', 'amount_display', 'currency')
        }),
        ('Method', {
            'fields': ('payment_method', 'status')
        }),
        ('SumUp', {
            'fields': ('sumup_checkout_id', 'sumup_transaction_id', 'sumup_checkout_url'),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('description', 'receipt_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'amount', 'created_at', 'processed_at')
    list_filter = ('created_at',)
    search_fields = ('payment__user__email', 'reason')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment', 'billing_name', 'created_at', 'sent_at')
    list_filter = ('created_at',)
    search_fields = ('invoice_number', 'billing_name', 'billing_email')
    readonly_fields = ('invoice_number', 'created_at')
