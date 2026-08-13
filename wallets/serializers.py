from decimal import Decimal
from rest_framework import serializers
from .models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Wallet
        fields = ('id', 'user_email', 'balance', 'created_at')
        read_only_fields = ('id', 'user_email', 'balance', 'created_at')


class TransferSerializer(serializers.Serializer):
    receiver_email = serializers.EmailField()
    # Use Decimal(Decimal('0.01')) instead of float (0.01)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))


class TransactionSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.user.email', read_only=True)
    receiver_email = serializers.EmailField(source='receiver.user.email', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'sender_email', 'receiver_email', 'amount', 'transaction_type', 'status', 'timestamp')