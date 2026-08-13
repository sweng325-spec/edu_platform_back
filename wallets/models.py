import uuid
from django.conf import settings
from django.db import models, transaction
from rest_framework.exceptions import ValidationError

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s Wallet - Balance: {self.balance}"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        TRANSFER = 'TRANSFER', 'Transfer'
        DEPOSIT = 'DEPOSIT', 'Deposit'
        COURSE_PURCHASE = 'PURCHASE', 'Course Purchase'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_transactions')
    receiver = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def execute_transfer(cls, sender_wallet, receiver_wallet, amount):
        if sender_wallet.balance < amount:
            raise ValidationError("Insufficient wallet balance.")

        with transaction.atomic():
            sender_wallet.balance -= amount
            receiver_wallet.balance += amount
            sender_wallet.save()
            receiver_wallet.save()

            txn = cls.objects.create(
                sender=sender_wallet,
                receiver=receiver_wallet,
                amount=amount,
                transaction_type=cls.TransactionType.TRANSFER,
                status=cls.Status.COMPLETED
            )
            return txn