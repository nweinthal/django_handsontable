from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import simplejson as json

DATA_JSON_STATIC = 0
DATA_JSON_AJAX = 1

class DataSource(object):
    def render_block(self):
        needed_string = json.dumps(self.data)
        return mark_safe(needed_string)

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data', None)
        self.ajax = kwargs.pop('ajax', False)
    
class QuerysetDataSource(DataSource):
    def render_block(self):
        data = []
        for record in self.data.values():
            row = []
            row.append(record['id'])
            for field in self.display_fields:
                row.append(record[field])
            data.append(row)
        return mark_safe(json.dumps(data))

    def __init__(self, *args, **kwargs):
        self.display_fields = kwargs.pop('display_fields', None)
        super(QuerysetDataSource, self).__init__(*args, **kwargs)

class Spreadsheet(object):

    def get_headers(self):
        return mark_safe(str(['id'] + [\
                header.capitalize().replace('_', ' ') \
                for header in self.headers]))

    def render(self):
        context_dict = {}
        context_dict['data'] = self.data_source.render_block()
        context_dict['headers'] = self.get_headers() # replace with template tag
        context_dict['raw_headers'] = mark_safe(str(["id"] + list(self.headers))) # TODO better
        context_dict['ajax_save_url'] = self.ajax_save_url
        context_dict['key'] = "id678_" #TODO make this unique n' stuff
        print context_dict['headers']
        return render_to_string("spreadsheets/main.html", context_dict)

    def __init__(self, *args, **kwargs):
        self.data_source = kwargs['data_source']
        self.headers = kwargs.pop('headers', self.data_source.display_fields)
        self.ajax_save_url = kwargs.pop('ajax_save_url', '#')

class ModelSpreadsheet(Spreadsheet):
    pass

class AjaxModelSpreadsheet(ModelSpreadsheet):
    pass

