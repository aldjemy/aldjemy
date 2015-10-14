try:
    import pundle
    pundle.activate()
except:
    pass
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.core.wsgi import get_wsgi_application
from sample.models import StaffAuthor
application = get_wsgi_application()

import datetime
StaffAuthor(role='manager', date=datetime.datetime.utcnow()).save()
print(StaffAuthor.objects.all())

print(StaffAuthor.sa.query().all())
