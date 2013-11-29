# -*- coding: utf-8 -*-
from django.test import TestCase

from ..pybars_lenker import Lenker, DocChoiceException, DocSelectException, DocVarMismatchException

import logging
logger = logging.getLogger('django.test')


class TestTemplateToDoc(TestCase):
    """ Class tests that the server-side handebars methods are called
    and retur the appropriate values """
    def setUp(self):
        self.subject = Lenker
        self.html_handlers = {
            # Doc Var
            'doc_var': u'{{#doc_var name="monkey"}}Bananarama{{/doc_var}}',
            # Doc Choice
            'doc_choice': u'{{#doc_choice name="animal_farm" choices="pig,horse,duck" is_static=true}}{{/doc_choice}}',
            'doc_choice_custom_not_is_static': u'{{#doc_choice name="animal_farm" choices="pig,horse,duck" is_static=false}}{{/doc_choice}}',
            'doc_choice_custom_unspecified_static': u'{{#doc_choice name="animal_farm" choices="pig,horse,duck"}}{{/doc_choice}}',
            # Doc Select
            'doc_select': u'{{#doc_select name="favourite_monkies" label="What are your favourite Monkies?"}}Gorillas{option}Baboons{option}Chimpanzies{option}Big Hairy Ones{{/doc_select}}',
            'doc_select_custom_join_by': u'{{#doc_select name="favourite_monkies" join_by="-A crazy night out with a Ham-" label="What are your favourite Monkies?"}}Gorillas{option}Baboons{option}Chimpanzies{option}Big Hairy Ones{{/doc_select}}',
            'doc_select_custom_subvariable': u'{{#doc_select name="favourite_monkies" label="What are your favourite Monkies?"}}Gorillas named {{#doc_var name="gorilla_name"}}{{/doc_var}}{option}Baboons{option}Chimpanzies named {{#doc_var name="chimp_name"}}{{/doc_var}}{option}Big Hairy Ones named {{#doc_var name="big_hairy_name"}}{{/doc_var}}{{/doc_select}}',
            'doc_select_custom_multi': u'{{#doc_select multi=true name="best_apes" label="What are the best Apes?"}}Gorillaz{option}Chimpanzies{option}Baboons{{/doc_select}}',
            # Mismatched
            '_custom_mismatched': u'{{#doc_var name="monkey"}}Bananarama{{/doc_choice}}{{#doc_select multi=true name="best_apes" label="What are the best Apes?"}}Gorillaz{option}Chimpanzies{option}Baboons{{/doc_var}}',
        }

    def testDocVar(self):
        subject = self.subject(source=self.html_handlers['doc_var'])
        context = {'monkey': u'This is some kind of Banana!'}
        subject.context = context

        self.assertEqual(subject.render(context), u'This is some kind of Banana!')

    def testDocChoice(self):
        subject = self.subject(source=self.html_handlers['doc_choice'])
        context = {
            'animal_farm': u'pig'
        }
        subject.context = context
        self.assertEqual(subject.render(context), u'pig')

    def testInvalidStaticDocChoice(self):
        with self.assertRaises(DocChoiceException):
            subject = self.subject(source=self.html_handlers['doc_choice'])
            context = {
                'animal_farm': u'monkey'
            }
            subject.context = context
            subject.render(context)

    def testNotStaticDocChoice(self):
        subject = self.subject(source=self.html_handlers['doc_choice_custom_not_is_static'])
        context = {
            'animal_farm': u'gorilla'
        }
        subject.context = context
        self.assertEqual(subject.render(context), u'gorilla')

    def testDefaultDocChoice(self):
        subject = self.subject(source=self.html_handlers['doc_choice_custom_unspecified_static'])
        context = {
            'animal_farm': u'gorilla'
        }
        subject.context = context
        self.assertEqual(subject.render(context), u'gorilla')

    def testDocSelect(self):
        subject = self.subject(source=self.html_handlers['doc_select'])
        context = {
            'favourite_monkies': [u'Gorillas']
        }
        subject.context = context
        self.assertEqual(subject.render(context), u'Gorillas')

    def testDocSelectMulti(self):
        """ When multi=true the method will return a string """
        subject = self.subject(source=self.html_handlers['doc_select'])
        context = {
            'favourite_monkies': [u'Gorillas', 'Big Hairy Ones']
        }
        subject.context = context
        # Joins on new line char
        self.assertEqual(subject.render(context), u'Gorillas\rBig Hairy Ones')

    def testDocSelectInvalidMulti(self):
        """ Elephants are NOT monkies """
        with self.assertRaises(DocSelectException):
            subject = self.subject(source=self.html_handlers['doc_select'])
            context = {
                'favourite_monkies': [u'Elephants', 'Gorillas']
            }
            subject.context = context
            subject.render(context)

    def testDocSelectCustomJoinBy(self):
        """ Join by '-A crazy night out with a Ham-' """
        subject = self.subject(source=self.html_handlers['doc_select_custom_join_by'])
        context = {
            'favourite_monkies': [u'Chimpanzies', 'Baboons']
        }
        subject.context = context
        self.assertEqual(subject.render(context), 'Chimpanzies-A crazy night out with a Ham-Baboons')

    def testDocSelectSubVariable(self):
        """ Test DocSelects that contain sub doc_vars """
        subject = self.subject(source=self.html_handlers['doc_select_custom_subvariable'])
        context = {
            'favourite_monkies': [u'Chimpanzies named George', 'Baboons'],
            'gorilla_name': 'Harald',
            'chimp_name': 'George',
            'big_hairy_name': 'Grumwald',
        }
        subject.context = context
        self.assertEqual(subject.render(context), 'Chimpanzies named George\rBaboons')

    def testComplexMultiDocSelectSubVariable(self):
        subject = self.subject(source=self.html_handlers['doc_select_custom_multi'])
        context = {
            'best_apes[0][selected]': 'true',
            'best_apes[1][selected]': 'false',
            'best_apes[2][selected]': 'true'
        }
        self.assertEqual(subject.render(context), u'Gorillaz\rBaboons')


class TestSimpleSelectHTMLExample(TestTemplateToDoc):
    def testGenericHTML(self):
        handlers = [v for k,v in self.html_handlers.items() if '_custom_' not in k]
        html = '<html><head></head><body> <h1>A Test Title</h1> %s </body></html>'

        subject = self.subject(source=html % ("<br/>".join(handlers),))
        context = {
            'monkey': u'Slurping Schwein on the Train from Mönchengladbach',
            'animal_farm': u'horse',
            'favourite_monkies': [u'Baboons', u'Gorillas']
        }
        subject.context = context

        html_result = subject.render(context)
        expected_html = html % (u'Baboons\rGorillas<br/>horse<br/>Slurping Schwein on the Train from Mönchengladbach')

        self.assertEqual(html_result, expected_html)


class TestMisMatchedTags(TestTemplateToDoc):

    def test_mismatch(self):
        with self.assertRaises(DocVarMismatchException):
            subject = self.subject(source=self.html_handlers["_custom_mismatched"])
            subject.render({})
