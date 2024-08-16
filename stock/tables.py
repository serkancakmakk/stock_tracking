import django_tables2 as tables
from .models import StockTransactions

import django_tables2 as tables
from .models import StockTransactions

class StockTransactionsTable(tables.Table):
    incoming_bill_number = tables.Column(accessor='incoming_bill.number', verbose_name='Gelen Fatura Numarası')
    product = tables.Column(verbose_name='Ürün')
    incoming_quantity = tables.Column(verbose_name='Giren Miktar')
    outgoing_quantity = tables.Column(verbose_name='Çıkan Miktar')
    outgoing_bill = tables.Column(verbose_name='Çıkış Faturası')
    processing_time = tables.Column(verbose_name='İşlem Zamanı')
    total_amount = tables.Column(verbose_name='Toplam Tutar')

    class Meta:
        model = StockTransactions
        template_name = 'bootstrap5_table.html'
        fields = ('product', 'incoming_quantity', 'outgoing_quantity', 'outgoing_bill', 'incoming_bill_number', 'processing_time', 'total_amount')
