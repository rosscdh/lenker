# -*- coding: utf-8 -*-
import re
from django.utils.encoding import smart_unicode


class LenkerValidateService(object):
    """
    Service used to validate the handlebars template objects
    """
    def __init__(self, ident, source, **kwargs):
        self.preprocessors = kwargs.pop('preprocessors') if 'preprocessors' in kwargs else []
        self.ident = ident
        self.source = self.preprocess(source)
        self.errors = set()
        self.error_msg = u''

    def preprocess(self, source):
        for c in self.preprocessors:
            instance = c(source_source=source)
            source = instance.render({})
        return source

    def rex_tag(self, tag_name):
        rex = re.compile(r"(?P<tag>\{\{\#%s (?P<tag_attribs>.*?)\}\}(?P<tag_contents>.*?)\{\{\/%s\}\}.*?)" % (tag_name, tag_name,), re.MULTILINE&re.IGNORECASE&re.DOTALL)
        return rex.findall(self.source)

    def gen_sets(self):
        tag_names = set()
        tag_ends = set()

        tag_name_rex = re.compile(r"\{\{\#(?P<tag_name>.*?) (?P<tag_attribs>.*?)\}\}") # remove doc_* start
        end_tag_rex = re.compile(r"\{\{\/(?P<end_tag_name>.*?)\}\}") # remove /doc_* end
        option_rex = re.compile(r"\{option\}")

        #rex = re.compile(r"(?P<tag>\{\{\#(?P<tag_name>.*?) (?P<tag_attribs>.*?)\}\}(?P<tag_contents>.*?)\{\{\/(?P<end_tag_name>.*?)\}\}.*?)", re.MULTILINE&re.IGNORECASE&re.DOTALL)

        for i in tag_name_rex.findall(self.source):
            tag_name, tag_attribs = i
            tag_names.add(tag_name)

        for tag_end in end_tag_rex.findall(self.source):
            tag_ends.add(tag_end)

        return (tag_names, tag_ends,)

    def validate(self):
        """ extract all of the {{#doc_var}}content{{/doc_var}}
        where doc_var is a doc_* tag
        """
        is_valid = True
        # sets for comparison
        tag_names, tag_ends = self.gen_sets()

        # ensure that the sets are the same
        assert tag_names.issubset(tag_ends), 'Unclosed tags: %s' % ', '.join([name for name in tag_names])

        # ensure all doc_selects have an options
        # NOT REQRUIED: as a doc select can have only 1 value.. 
        # if 'doc_select' in tag_names:
        #     doc_selects = self.rex_tag('doc_select')
        #     for s in doc_selects:
        #         tag, attribs, content = s
        #         assert '{option}' in content, 'doc_select must contain at least 2 items seperated by "{option}", error at: %s' % attribs


    def is_valid(self):
        try:
            self.validate()
        except AssertionError as e:
            self.errors.add(e.message)
            self.error_msg += '; '.join(self.errors)
            return False
        return True
