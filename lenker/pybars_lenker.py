# -*- coding: utf-8 -*-
from .pybars_plus import PybarsPlus

import re
import logging
logger = logging.getLogger('django.request')


class Lenker(PybarsPlus):
    source = None
    context = {}
    compiler = None
    template = None

    def __init__(self, source, *args, **kwargs):
        self.source = unicode(source)
        super(Lenker, self).__init__(source=source, *args, **kwargs)
        self.context = {}
        self.compiler.register_helper(u'doc_var', self.doc_var)
        self.compiler.register_helper(u'doc_choice', self.doc_choice)
        self.compiler.register_helper(u'doc_select', self.doc_select)
        self.compiler.register_helper(u'help_for', self.help_for)
        self.compiler.register_helper(u'doc_note', self.doc_note)

    def render(self, context):
        self.context = context
        template = self.compiler.compile(self.source)

        if not template:
            logger.error("template was not set from provided source")
            return None
        else:
            html_list = self.validate(template(context))
            return unicode(''.join(html_list))

    def validate(self, html_list):
        match = re.search(r"\{\{\#doc_(.*?)\}\}", self.source)  # match at least one doc_ tag

        if match is not None:
            # we have at least one doc_* variable
            if len(html_list) == 0:
                # if we have at least 1 match then the html_list should NOT
                # be empty! thus we have a tag mismatch. doc_var being closed by doc_select
                # or similar
                raise DocVarMismatchException()
        return html_list

    def doc_var(self, this, *args, **kwargs):
        var_name = kwargs.get('name', None)
        if var_name in self.context:
            return self.context[var_name].strip()
        logger.warn("var_name %s was not found in context" % var_name)
        return None

    def doc_choice(self, this, *args, **kwargs):
        var_name = kwargs.get('name', None)
        choices = kwargs.get('choices', [])
        is_static = kwargs.get('is_static', False)

        if var_name in self.context:
            if self.context[var_name] not in choices:
                # Test for is static
                if is_static is True:
                    logger.error("choice %s was not in the set of valid choices" % self.context[var_name])
                    raise DocChoiceException(self.context[var_name], choices)
            return self.context[var_name].strip()
        logger.warn("var_name %s was not found in context" % var_name)
        return None

    def doc_select(self, this, *args, **kwargs):
        options = args[0]
        var_name = kwargs.get('name', None)
        join_by = str(kwargs.get('join_by', "\r"))
        choices_text = unicode(options['fn'](this))
        choices = [o.strip() for o in choices_text.split('{option}')]
        selected_values = []

        # 1. Complex Multi selector, a json nested nightmare
        for i, value in enumerate(choices):
            c = i + 1

            index_lookup_name = '%s[%d][selected]' % (var_name, i,)
            is_present = self.context.get(index_lookup_name)

            if is_present == 'true':
                # have found the [selected] == true
                logger.info("%d index IS present %s and its index is: %d and its value is %s" % (c, is_present, i, choices[i],))
                #now use the index to get the context name
                selected_values.append(choices[i])
            else:
                logger.info("%d index is not present" % c)

        if len(selected_values) > 0:
            logger.info("var_name: %s is in self.context" % index_lookup_name)
            # Join the selectd options based on the join_by character; that may be custom
            return join_by.join(selected_values)

        logger.info("var_name: %s is not a Complex Multi Select but could be a Simple Select" % index_lookup_name)
        # 2. Simple selector, not a json nested nightmare
        if self.context.get(var_name, None) is not None:
            simple_selected = self.context.get(var_name, [])
            for c in simple_selected:
                if c not in choices:
                    raise DocSelectException(c, choices)
            return join_by.join(simple_selected)

        logger.info("var_name %s was not found in context" % var_name)

        return None

    def help_for(self, this, *args, **kwargs):
        """ No help is provided on the server side render of the doc """
        return None

    def doc_note(self, this, *args, **kwargs):
        """ No note is provided on the server side render of the doc """
        return None


class LenkerRemoval(Lenker):
    """ Class to remove the smoothe handlers
    primarily for document xtml validation where the handlebars
    tags can break xhtml validation """
    def render(self, context=None):
        html = self.source

        # regex = re.compile(r"\{\{\#(.*?)\}\}(.*)\{\{\/(.*?)\}\}", re.I&re.MULTILINE&re.IGNORECASE&re.DOTALL&re.DEBUG)
        # html = re.sub(regex, r"\2", html)

        html = re.sub(r"\{\{\#(.*?)\}\}", "", html)  # remove doc_* start
        html = re.sub(r"\{\{\/(.*?)\}\}", "", html)  # remove /doc_* end
        html = re.sub(r"\{option\}", "", html)
        logger.info(html)
        return html


class DocChoiceException(Exception):
    def __init__(self, value, choices):
        self.value = value
        self.choices = choices
        message = u'The value provided "%s" is not one of [%s]' % (self.value, self.choices,)
        Exception.__init__(self, message)


class DocSelectException(DocChoiceException):
    pass


class DocVarMismatchException(Exception):
    message = u'It looks like there is a variable mismatch. Look for a {{#doc_var}} that is mismatched with its ending token. it may have the wrong closing token i.e. {{/doc_select}} or indeed no ending token'

    def __init__(self):
        logger.critical(self.message)
