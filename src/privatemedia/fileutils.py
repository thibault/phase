# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.core.files.storage import FileSystemStorage
from django.conf import settings


# Revision documents
private_storage = FileSystemStorage(location='{}'.format(settings.PRIVATE_ROOT),
                                    base_url='{}'.format(settings.PRIVATE_URL))
