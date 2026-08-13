from django.urls import path
from .views import (
    wallet_detail_view,
    transfer_money_view,
    transaction_history_view,
)

app_name = 'wallets'

urlpatterns = [
    path('', wallet_detail_view, name='wallet-detail'),
    path('transfer/', transfer_money_view, name='wallet-transfer'),
    path('transactions/', transaction_history_view, name='transaction-history'),
]