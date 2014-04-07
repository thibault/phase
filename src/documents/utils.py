import zipfile
import tempfile

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


def filter_documents(queryset, data):
    """Filter documents from a queryset given data from DataTables.

    Documentation (lack of is more accurate though):
    http://www.datatables.net/examples/server_side/server_side.html
    """
    model = queryset.model

    # Paging (done at the view level, the whole queryset is still required)

    # Ordering
    queryset = queryset.order_by(data.get('sort_by', 'document_number') or 'document_number')

    # Filtering (search)
    searchable_fields = model.PhaseConfig.searchable_fields
    search_terms = data.get('search_terms', None)
    if search_terms:
        q = Q()
        for field in searchable_fields:

            # does the field belong to the Metadata or the corresponding Revision?
            prefix = ''
            if field not in model._meta.get_all_field_names():
                prefix = 'latest_revision__'

            q.add(Q(**{prefix + '%s__icontains' % field: search_terms}), Q.OR)
        queryset = queryset.filter(q)

    # Filtering (custom fields)
    filter_fields = model.PhaseConfig.filter_fields
    advanced_args = {}
    for parameter_name in filter_fields:

        # does the field belong to the Metadata or the corresponding Revision?
        prefix = ''
        if parameter_name not in model._meta.get_all_field_names():
            prefix = 'latest_revision__'

        parameter = data.get(parameter_name, None)
        if parameter:
            advanced_args[prefix + parameter_name] = parameter

    queryset = queryset.filter(**advanced_args)

    # Special case of advanced filtering with a text field
    cdn = data.get('contractor_document_number', None)
    if cdn:
        queryset = queryset.filter(
            contractor_document_number__icontains=cdn
        )

    return queryset


# HACK to fix http://hg.python.org/cpython/rev/4f0988e8fcb1/
class FixedZipFile(zipfile.ZipFile):
    """Old versions of Python don't have the patch merged."""
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def compress_documents(documents, format='both', revisions='latest'):
    """Compress the given files' documents (or queryset) in a zip file.

    * format can be either 'both', 'native' or 'pdf'
    * revisions can be either 'latest' or 'all'

    Returns the name of the ziped file.
    """
    temp_file = tempfile.TemporaryFile()

    with FixedZipFile(temp_file, mode='w') as zip_file:
        files = []
        for document in documents:
            if revisions == 'latest':
                revs = [document.latest_revision]
            elif revisions == 'all':
                revs = document.get_all_revisions()

            for rev in revs:
                if rev is not None:
                    if format in ('native', 'both'):
                        files.append(rev.native_file)
                    if format in ('pdf', 'both'):
                        files.append(rev.pdf_file)

        for file_ in files:
            if file_.name:
                zip_file.write(
                    file_.path,
                    file_.name,
                    compress_type=zipfile.ZIP_DEFLATED
                )
    return temp_file


def stringify_value(val):
    """Returns a value suitable for display in a document list.

    >>> stringify_value('toto')
    u'toto'

    >>> stringify_value(None)
    u'NC'

    >>> stringify_value(True)
    u'Yes'

    >>> import datetime
    >>> stringify_value(datetime.datetime(2000, 1, 1))
    u'2000-01-01'

    >>> stringify_value(None)
    u'NC'
    """
    if val is None:
        unicode_val = u'NC'
    elif type(val) == bool:
        unicode_val = u'Yes' if val else u'No'
    else:
        unicode_val = unicode(val)

    return unicode_val


def get_all_document_classes():
    """Returns all document classes available."""
    qs = ContentType.objects \
        .filter(app_label__endswith='_documents') \
        .exclude(model__icontains='revision')

    klasses = [content_type.model_class() for content_type in qs]
    return klasses


def get_all_revision_classes():
    """Returns all classes inheriting MetadataRevision."""
    qs = ContentType.objects \
        .filter(app_label__endswith='_documents') \
        .filter(model__icontains='revision')

    klasses = [content_type.model_class() for content_type in qs]
    return klasses
