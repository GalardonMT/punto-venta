import os
import sys
import webbrowser
from threading import Timer
from django.core.management import execute_from_command_line

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == '__main__':
    Timer(1, open_browser).start()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aplicacion.settings')  # cambia 'mi_pos' por tu nombre real

    # ⚠️ ¡Importante! NO pongas "manage.py" aquí
    args = ['runserver', '--noreload']

    execute_from_command_line([sys.argv[0]] + args)
