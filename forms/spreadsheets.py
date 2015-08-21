from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import simplejson as json

DATA_JSON_STATIC = 0
DATA_JSON_AJAX = 1

#================= Data Validation =========================
# The goal with data validation is to create a series of validators
# that work both client-side, so errors can be seen and remedied live
# and server-side in case someone disables JavaScript, and generally 
# to ensure data cleanliness.  Right now this essentially means 
# writing a mini-language, which I don't really love the idea of.

class Validator(object):
    """
    Simplest base class, allows arbitrary client-side js scripts and 
    server-side rules
    """

    def client_side(self):
        return mark_safe(self.script)

    def server_side(self, value):
        if self.validator(value):
            return True
        else: 
            raise ValidationError("The value {} did not pass validation".format(value))

    def __init__(self, validator, script):
        self.script = script
        self.validator = validator


class NumeralValidator(Validator):
    """
    Validator to ensure data is a valid number
    """
    @staticmethod
    def numeral_check(value):
        if not value:
            return True
        try:
            float(value)
            return True
        except ValueError as v:
            return False

    def __init__(self, allow_blank=True):
        self.allow_blank = allow_blank
        script = """
        function(value, callback){
            callback(!isNaN(value));
        }
        """
        validator = self.numeral_check
        super(NumeralValidator, self).__init__(validator, script)
# TODO: RegEx validator and Assertion Validator

#======================== DataSource objects ===========================
# Spreadsheet shouldn't have to care what kind of DataSource object it has,
# it will accept any of them.

class DataSource(object):
    # simplest version
    def render_block(self):
        needed_string = json.dumps(self.data)
        return mark_safe(needed_string)

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data', None)
        self.ajax = kwargs.pop('ajax', False)
    
class QuerysetDataSource(DataSource):
    # Best for static dataset generation, this will take any django
    # QuerySet object.
    def render_block(self):
        data = []
        for record in self.data.values():
            row = []
            for field in self.display_fields:
                row.append(record[field])
            data.append(row)
        return mark_safe(json.dumps(data))

    def __init__(self, *args, **kwargs):
        self.display_fields = kwargs.pop('display_fields', None)
        super(QuerysetDataSource, self).__init__(*args, **kwargs)

# TODO: Ajax and API data sources

#=======================================================================
class ColumnOption(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.verbose_name = kwargs.get("verbose_name", self.name)
        self.hidden = kwargs.get("hidden", False)
        self.editable = kwargs.get("editable", True)
        self.validator = kwargs.get("validator", None)

class Spreadsheet(object):

    def get_headers(self):
        return mark_safe(str([\
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
        self.column_options = kwargs.get('column_options', None)
        self.data_source = kwargs['data_source']
        self.headers = kwargs.pop('headers', self.data_source.display_fields)
        self.ajax_save_url = kwargs.pop('ajax_save_url', '#')


