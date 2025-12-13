import requests
from django.conf import settings
from django.urls import reverse


class SumUpService:
    """Service for SumUp payment integration."""

    def __init__(self):
        self.api_key = settings.SUMUP_API_KEY
        self.merchant_code = settings.SUMUP_MERCHANT_CODE
        self.base_url = settings.SUMUP_API_URL

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def create_checkout(self, payment):
        """Create a SumUp checkout session."""
        if not self.api_key:
            # Return mock data for development
            return {
                'id': f'demo-checkout-{payment.id}',
                'checkout_url': None,  # Will use demo flow
            }

        url = f'{self.base_url}/checkouts'

        # Build callback URLs
        from django.contrib.sites.models import Site
        try:
            domain = Site.objects.get_current().domain
        except:
            domain = 'localhost:8000'

        success_url = f'https://{domain}{reverse("payments:success", args=[payment.id])}'
        cancel_url = f'https://{domain}{reverse("payments:cancel", args=[payment.id])}'

        payload = {
            'checkout_reference': f'TH-{payment.id}',
            'amount': payment.amount / 100,  # Convert pence to pounds
            'currency': payment.currency,
            'pay_to_email': self.merchant_code,
            'description': payment.description,
            'redirect_url': success_url,
            'return_url': success_url,
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"SumUp API error: {e}")
            return None

    def get_checkout_status(self, checkout_id):
        """Get the status of a checkout."""
        if not self.api_key or checkout_id.startswith('demo-'):
            return 'PAID'  # Demo mode

        url = f'{self.base_url}/checkouts/{checkout_id}'

        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get('status', 'UNKNOWN')
        except requests.RequestException:
            return 'UNKNOWN'

    def process_refund(self, payment, amount=None):
        """Process a refund for a payment."""
        if not self.api_key:
            return {'status': 'refunded'}  # Demo mode

        if not payment.sumup_transaction_id:
            return None

        url = f'{self.base_url}/me/refund'
        payload = {
            'transaction_id': payment.sumup_transaction_id,
            'amount': (amount or payment.amount) / 100,
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
