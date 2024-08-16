#!/usr/bin/env python
"""Django'nun yönetim komutları için komut satırı aracıdır."""
import os
import sys

def main():
    """Yönetim görevlerini çalıştırır."""
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_tracking.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django'yu içe aktaramadık. Django'nun kurulu ve PYTHONPATH ortam değişkeninde mevcut olduğundan emin olun."
            "Bir sanal ortam oluşturmayı unuttunuz mu?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
