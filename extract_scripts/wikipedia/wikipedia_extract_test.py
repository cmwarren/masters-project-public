import unittest
from wikipedia_extract import WikipediaExtract


class WikipediaExtractTestCase(unittest.TestCase):

    ar_test_page_ids = [u'1990882',
                        u'3523120',
                        u'2780771',
                        u'2736705',
                        u'1302290',
                        u'2224560',
                        u'1604357',
                        u'3178772',
                        u'2217913',
                        u'1107860']

    en_test_page_ids = [u'8034831',
                        u'47218950',
                        u'49991095',
                        u'50620817',
                        u'7977203',
                        u'46585289',
                        u'11681106',
                        u'622866',
                        u'48989322',
                        u'25719292']

    es_test_page_ids = [u'7128783',
                        u'7610698',
                        u'5022275',
                        u'1580006',
                        u'849931',
                        u'7470566',
                        u'5353167',
                        u'2084409',
                        u'571367',
                        u'7773244']

    fi_test_page_ids = [u'1164314',
                        u'505635',
                        u'737714',
                        u'683946',
                        u'755899',
                        u'744245',
                        u'1026920',
                        u'1334558',
                        u'837595',
                        u'1126579']

    fr_test_page_ids = [u'1910620',
                        u'570916',
                        u'5247277',
                        u'7178664',
                        u'10719524',
                        u'379076',
                        u'6907468',
                        u'7095288',
                        u'5873468',
                        u'7097838']

    he_test_page_ids = [u'1315066',
                        u'115884',
                        u'937348',
                        u'335312',
                        u'438188',
                        u'1178967',
                        u'940980',
                        u'695047',
                        u'110456',
                        u'435341']

    hu_test_page_ids = [u'517813',
                        u'346317',
                        u'518431',
                        u'1432267',
                        u'32024',
                        u'391921',
                        u'309421',
                        u'417947',
                        u'125301',
                        u'1253766']

    pt_test_page_ids = [u'28055',
                        u'1856102',
                        u'1472678',
                        u'1407692',
                        u'244952',
                        u'3046333',
                        u'813764',
                        u'4967606',
                        u'1413581',
                        u'1086242']

    tr_test_page_ids = [u'1284112',
                        u'1806202',
                        u'2162505',
                        u'40469',
                        u'893521',
                        u'863382',
                        u'192532',
                        u'1282542',
                        u'1107773',
                        u'268579']

    def testReferenceCitation(self):
        markup = """Some text [1] followed by the rest of the sentence.[2] As a discipline, it is focused on the branch of economics known as microeconomics."""
        expected = """Some text  followed by the rest of the sentence. As a discipline, it is focused on the branch of economics known as microeconomics."""
        self.assertEqual(WikipediaExtract().strip_markup(markup), expected)

    def testArPages(self):
        for index, page_id in enumerate(self.ar_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'ar', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testEnPages(self):
        for index, page_id in enumerate(self.en_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'en', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testEsPages(self):
        for index, page_id in enumerate(self.es_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'es', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testFiPages(self):
        for index, page_id in enumerate(self.fi_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'fi', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testFrPages(self):
        for index, page_id in enumerate(self.fr_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'fr', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testHePages(self):
        for index, page_id in enumerate(self.he_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'he', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testHuPages(self):
        for index, page_id in enumerate(self.hu_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'hu', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testPtPages(self):
        for index, page_id in enumerate(self.pt_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'pt', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def testTrPages(self):
        for index, page_id in enumerate(self.tr_test_page_ids):
            content = WikipediaExtract().output_page_id(page_id, 'data/test_pages', 'tr', index, b_output_raw=True, b_debug=True)
            self.content_assertions(content)

    def content_assertions(self, content):
        self.assertFalse('<table>' in content)
        self.assertFalse('<tr>' in content)
        self.assertFalse('<td>' in content)
        self.assertFalse('</td>' in content)
        self.assertFalse('</tr>' in content)
        self.assertFalse('</table>' in content)
        self.assertFalse('## ' in content)
        self.assertFalse('### ' in content)
        self.assertFalse('* ' in content)
        self.assertFalse('. ^' in content)
        self.assertFalse('[1]' in content)


if __name__ == '__main__':
    unittest.main()
