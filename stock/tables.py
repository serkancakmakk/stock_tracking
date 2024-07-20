import django_tables2 as tables
from .models import StockTransactions

class StockTransactionsTable(tables.Table):
    incoming_bill_number = tables.Column(accessor='incoming_bill.number', verbose_name='Incoming Bill Number')

    class Meta:
        model = StockTransactions
        template_name = 'django_tables2/bootstrap5.html'  # Bootstrap4 şablonunu kullanın
        fields = ('product', 'incoming_quantity', 'outgoing_quantity', 'outgoing_bill', 'incoming_bill_number', 'processing_time')