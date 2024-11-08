import os
import sys

activate_this = os.path.expanduser('~/treaty/public_html/myenv/bin/activate_this.py')
exec(open(activate_this).read(), {'__file': activate_this})

sys.path.insert(1, os.path.expanduser('~/treaty/public_html/'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treatyproj.settings')

application = get_wsgi_application()