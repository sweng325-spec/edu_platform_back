from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransferSerializer, TransactionSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_detail_view(request):
    """Retrieve the current authenticated user's wallet balance."""
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_money_view(request):
    """Transfer funds from the authenticated user's wallet to another user via email."""
    serializer = TransferSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    receiver_email = serializer.validated_data['receiver_email']
    amount = serializer.validated_data['amount']

    try:
        receiver_user = User.objects.get(email=receiver_email)
    except User.DoesNotExist:
        return Response({"error": "Receiver with this email address does not exist."}, status=status.HTTP_404_NOT_FOUND)

    sender_wallet = getattr(request.user, 'wallet', None)
    receiver_wallet = getattr(receiver_user, 'wallet', None)

    if not sender_wallet or not receiver_wallet:
        return Response({"error": "Wallet not found for one or both users."}, status=status.HTTP_400_BAD_REQUEST)

    if sender_wallet == receiver_wallet:
        return Response({"error": "You cannot transfer money to yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if sender_wallet.balance < amount:
        return Response({"error": "Insufficient wallet balance."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Deduct from sender and add to receiver
        sender_wallet.balance -= amount
        receiver_wallet.balance += amount
        sender_wallet.save()
        receiver_wallet.save()

        # Log transaction
        txn = Transaction.objects.create(
            sender=sender_wallet,
            receiver=receiver_wallet,
            amount=amount,
            status=getattr(Transaction.Status, 'COMPLETED', 'COMPLETED')
        )

        return Response({
            "message": "Transfer successful.",
            "transaction_id": str(txn.id),
            "remaining_balance": str(sender_wallet.balance)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history_view(request):
    """Retrieve all sent and received transactions for the authenticated user."""
    user_wallet = getattr(request.user, 'wallet', None)
    if not user_wallet:
        return Response([], status=status.HTTP_200_OK)

    transactions = Transaction.objects.filter(
        Q(sender=user_wallet) | Q(receiver=user_wallet)
    ).order_by('-timestamp')

    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)