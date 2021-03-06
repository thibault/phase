Management tasks and cronjobs
#############################

Reindex all
-----------

Documents can be reindexed so that elastic search can stay in synch with actual
document data. There is a dedicated task for it::

    python manage.py reindex_all

.. WARNING::
   This task will completely delete the index and recreate it from scratch.


Clear private media
-------------------

Since Django 1.3, FileFields instances are not automaticaly deleted upon's
the mode deletion anymore.

This is to preserve data integrity in case of transactions rollbacks.

The drawback is that cleaning file is our responsability.

This tasks cleans the private storage directory by removing all files that
are not present in db anymore.

::

    python manage.py clearmedia


Exports cleanup
---------------

Exported files are kept on disk for a certain duration. There is a dedicated
task to clean old exported file.

::

    python manage.py exports_cleanup


Crontab
-------

Setup a crontab to run scheduled tasks regularly. You must use your phase user
to run the tasks. Here is a sample crontab file::

    PYTHON="/home/phase/.virtualenvs/phase/bin/python"
    DJANGO_PATH="/home/phase/phase/src/"
    LOGS_PATH="/home/phase/django_logs/"
    DJANGO_SETTINGS_MODULE="core.settings.production"

    # m h  dom mon dow   command
    # 42 0 * * * cd $DJANGO_PATH && $PYTHON manage.py reindex_all --noinput &>"$LOGS_PATH/reindex.log"
    42 1 * * * cd $DJANGO_PATH && $PYTHON manage.py clearmedia  &>"$LOGS_PATH/clearmedia.log"
    42 2 * * * cd $DJANGO_PATH && $PYTHON manage.py exports cleanup  &>"$LOGS_PATH/export_cleanup.log"

.. WARNING::
   Make sure you create the path pointed by the `$LOGS_PATH` variable.
