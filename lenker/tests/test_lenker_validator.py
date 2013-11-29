# -*- coding: utf-8 -*-
from django.test import TestCase

from ..services import LenkerValidateService

import logging
logger = logging.getLogger('django.test')


class TestSmootheValidator(TestCase):
    def setUp(self):
        self.valid = [
            #('doc_var', '{{#doc_var name="principal_name"}} PRINCIPAL {{/doc_var}}')
            ('doc_select', u'{{#doc_select name="test"}} A {option} B {{/doc_select}}')
        ]
        self.invalid = [
            ('doc_var', u'{{#doc_var name="principal_name"}} PRINCIPAL'),  # expnd to include
            ('doc_var', u'{{#doc_var name="principal_name"}} PRINCIPAL {{/doc_select}}'),
            ('doc_choice', u'{{#doc_choice name="principal_name"}} PRINCIPAL {{/doc_var}}'),
            ('doc_select', u'{{#doc_select name="principal_name"}} PRINCIPAL {{/doc_choice}}'),
        ]

        self.subject = LenkerValidateService

    def testValidSetup(self):
        for k, i in self.valid:
            s = self.subject(source=i, ident='valid-test')
            self.assertEqual(s.is_valid(), True)

    def testInvalidSetup(self):
        for k, i in self.invalid:
            s = self.subject(source=i, ident='invalid-test')
            self.assertEqual(s.is_valid(), False)
            self.assertEqual(len(s.errors), 1)
            self.assertEqual(s.error_msg, u"Unclosed tags: %s" % k)