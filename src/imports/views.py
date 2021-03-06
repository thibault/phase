from __future__ import unicode_literals

from django.views.generic import CreateView, DetailView, ListView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin

from notifications.models import notify
from imports.models import ImportBatch
from imports.forms import FileUploadForm
from imports.tasks import do_import


class ImportMixin(object):

    def breadcrumb_section(self):
        return _('Import'), reverse('import_list')

    def get_context_data(self, **kwargs):
        context = super(ImportMixin, self).get_context_data(**kwargs)
        context.update({
            'imports_active': True,
        })
        return context


class ImportList(ImportMixin, LoginRequiredMixin, ListView):
    template_name = 'imports/import_list.html'
    model = ImportBatch


class FileUpload(ImportMixin, LoginRequiredMixin, CreateView):
    template_name = 'imports/upload_file.html'
    form_class = FileUploadForm

    def breadcrumb_object(self):
        return _('Upload file'), reverse('import_file')

    def form_valid(self, form):
        response = super(FileUpload, self).form_valid(form)
        do_import.delay(self.object.uid)

        message_text = '''You required the import of a new file. Results
                       <a href="%(url)s">should be available in a few
                       seconds.</a>'''
        message_data = {
            'url': self.object.get_absolute_url(),
        }
        notify(self.request.user, _(message_text) % message_data)
        return response


class ImportStatus(ImportMixin, LoginRequiredMixin, DetailView):
    model = ImportBatch
    pk_url_kwarg = 'uid'
    template_name = 'imports/import_status.html'

    def breadcrumb_object(self):
        return self.object

    def get_context_data(self, **kwargs):
        context = super(ImportStatus, self).get_context_data(**kwargs)

        return context
