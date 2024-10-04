from django.core.management.base import BaseCommand
import timeit
from views import toggle_error_status

class Command(BaseCommand):
    help = 'Performans testi komutu'

    def handle(self, *args, **kwargs):
        def test_toggle_error_status():
            toggle_error_status(1)  # id'si 1 olan bir kayıt üzerinde test yapılıyor

        sure = timeit.timeit(test_toggle_error_status, number=1000)
        self.stdout.write(self.style.SUCCESS(f"Fonksiyonun 1000 tekrarındaki ortalama çalışma süresi: {sure:.6f} saniye"))