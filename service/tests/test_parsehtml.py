# coding=utf-8
"""
This File is part of Pinyto
"""

from django.test import TestCase
from service.parsehtml import ParseHtml


class TestParseHtml(TestCase):
    def test_contains(self):
        html = """
        <html>
        <head><title>Just a Test</title></head>
        <body>
            <h1>Heading</h1>
            <div data-custom="special">Te<i>x</i>t</div>
        </body>
        </html>"""
        soup = ParseHtml(html)
        self.assertTrue(soup.contains([{'tag': "div", 'attrs': {'data-custom': "special"}}]))
        self.assertTrue(soup.contains({'tag': "div", 'attrs': {'data-custom': "special"}}))
        self.assertTrue(soup.contains([{'tag': "div", 'attrs': {'data-custom': "special"}}, {'tag': "i"}]))
        self.assertFalse(soup.contains({'tag': "div", 'attrs': {'style': "something"}}))
        self.assertFalse(soup.contains({'tag': "span"}))

    def test_find_element_and_get_attribute_value(self):
        html = """
        <html>
        <head><title>Just a Test</title></head>
        <body>
            <h1>Heading</h1>
            <div data-custom="special" style="width: 20px;" class="inline">
                Text
                <span>Thing</span>
                <a href="location">Link</a>
                <a href="somewhere">another Link</a>
            </div>
        </body>
        </html>"""
        soup = ParseHtml(html)
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                [{'tag': "div", 'attrs': {'data-custom': "special"}}],
                'style'),
            'width: 20px;')
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                {'tag': "div", 'attrs': {'data-custom': "special"}},
                'style'),
            'width: 20px;')
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                [{'tag': "div", 'attrs': {'data-custom': "special"}}],
                'class'),
            ['inline'])
        self.assertEqual(
            soup.find_element_and_get_attribute_value(
                [{'tag': "div", 'attrs': {'data-custom': "special"}}],
                'id'),
            '')
        self.assertEqual(
            soup.find_element_and_get_attribute_value([{'tag': "span"}], 'id'),
            '')
        self.assertEqual(
            soup.find_element_and_get_attribute_value([
                    {'tag': "div", 'attrs': {'data-custom': "special"}},
                    {'tag': "a"}],
                'href'),
            'location')

    def test_find_element_and_collect_table_like_information_dnb(self):
        html = """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
              "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="de" lang="de" dir="ltr">
        <head>
            <title>DNB, Katalog der Deutschen Nationalbibliothek</title>
             <meta http-equiv="content-type" content="text/html;charset=utf-8" />
        </head>
        <body>
            <h1>Katalog der Deutschen Nationalbibliothek </h1>
            <h2>Ergebnis der Suche nach: <em>&quot;978-3-943176-24-7&quot;</em></h2>
            <div class="searchdisplay">
                <span class="amount">Treffer 1 von 1</span>
            </div>
            <table id="fullRecordTable" valign="bottom" cellpadding="3" cellspacing="0" class="yellow" width="100%" summary="Vollanzeige des Suchergebnises">
                <tr>
                    <td width="25%" >
                        <strong>Link zu diesem Datensatz</strong>
                    </td>
                    <td >http://d-nb.info/1022135384</td>
                </tr>
                <tr>
                    <td width="25%" class='yellow'><strong>Titel/Bezeichnung</strong></td>
                    <td class='yellow'>
                        <a href="./opac.htm?method=simpleSearch&cqlMode=true&reset=true&referrerPosition=0&referrerResultId=%22978-3-943176-24-7%22%26any&query=idn%3D1001317165" >Fettnäpfchenführer. - Meerbusch : Conbook-Verl.</a> [Mehrteiliges Werk]<br/>Teil: Japan : die Axt im Chrysanthemenwald / Kerstin und Andreas Fels
                    </td>
                </tr>
                <tr>
                    <td width="25%" ><strong>Person(en)</strong></td>
                    <td >
                        <a href="./opac.htm?method=simpleSearch&cqlMode=true&reset=true&referrerPosition=0&referrerResultId=%22978-3-943176-24-7%22%26any&query=idn%3D129857165" >Fels, Kerstin</a><br/>Fels, Andreas
                    </td>
                </tr>
                <tr>
                    <td width="25%" class='yellow'><strong>Ausgabe</strong></td>
                    <td class='yellow'>6. Aufl., Ausg. 2012</td>
                </tr>
                <tr>
                    <td width="25%" ><strong>Erscheinungsjahr</strong></td>
                    <td >2012</td>
                </tr>
                <tr>
                    <td width="25%" class='yellow'><strong>Umfang/Format</strong></td>
                    <td class='yellow'>279 S. ; 300 g</td>
                </tr>
                <tr>
                    <td width="25%" ><strong>ISBN/Einband/Preis</strong></td>
                    <td >978-3-943176-24-7 kart. : EUR 10.95 (DE), EUR 11.30 (AT), ca. sfr 16.50 (freier Pr.)</td>
                </tr>
                <tr>
                    <td width="25%" class='yellow'><strong>EAN</strong></td>
                    <td class='yellow'>9783943176247</td>
                </tr>
                <tr>
                    <td width="25%" ><strong>Sprache(n)</strong></td>
                    <td >Deutsch (ger)</td>
                </tr>
                <tr>
                    <td width="25%" class='yellow'><strong>Weiterführende Informationen</strong></td>
                    <td class='yellow'>
                        <a href="http://d-nb.info/1022135384/04" title="Inhaltsverzeichnis" onclick="window.open(this.href); return false;" onfocus="titleAnpassen(this);" onmouseover="titleAnpassen(this);">Inhaltsverzeichnis</a><br/><a href="http://deposit.d-nb.de/cgi-bin/dokserv?id=4030376&prov=M&dok_var=1&dok_ext=htm" title="Inhaltstext" onclick="window.open(this.href); return false;" onfocus="titleAnpassen(this);" onmouseover="titleAnpassen(this);">Inhaltstext</a>
                    </td>
                </tr>
            </table>
            <table valign="bottom" cellpadding="3" cellspacing="0" class="yellow" width="100%" summary="Vollanzeige der Exemplardaten">
                <tr>
                    <td width="25%" ><strong>Frankfurt</strong></td>
                    <td >Signatur: 2012 A 63624</td>
                </tr>
                <tr>
                    <td width="25%" class='yellow'><strong>Leipzig</strong></td>
                    <td class='yellow'>Signatur: 2012 A 77850</td>
                </tr>
            </table>
        </body>
        </html>"""
        soup = ParseHtml(html)
        infos = soup.find_element_and_collect_table_like_information(
            [{'tag': 'table', 'attrs': {'summary': 'Vollanzeige des Suchergebnises'}}, {'tag': 'tr'}],
            {'author': {'search tag': 'td', 'captions': ['Person(en)'], 'content tag': 'td'},
             'title': {'search tag': 'td',
                       'captions': ['Mehrteiliges Werk', 'Titel', 'Titel/Bezeichnung'],
                       'content tag': 'td'},
             'uniform title': {'search tag': 'td', 'captions': ['Einheitssachtitel'], 'content tag': 'td'},
             'year': {'search tag': 'td', 'captions': ['Erscheinungsjahr'], 'content tag': 'td'},
             'languages': {'search tag': 'td', 'captions': ['Sprache(n)'], 'content tag': 'td'},
             'category': {'search tag': 'td', 'captions': ['Sachgruppe(n)'], 'content tag': 'td'},
             'publisher': {'search tag': 'td', 'captions': ['Verleger'], 'content tag': 'td'},
             'edition': {'search tag': 'td', 'captions': ['Ausgabe'], 'content tag': 'td'},
             'isbn': {'search tag': 'td', 'captions': ['ISBN/Einband/Preis'], 'content tag': 'td'},
             'ean': {'search tag': 'td', 'captions': ['EAN'], 'content tag': 'td'}})
        self.assertEqual(infos['author'], u'Fels, Kerstin Fels, Andreas')
        self.assertEqual(infos['title'], u'Fettnäpfchenführer. - Meerbusch : Conbook-Verl. [Mehrteiliges Werk] ' +
                         u'Teil: Japan : die Axt im Chrysanthemenwald / Kerstin und Andreas Fels')
        self.assertNotIn('uniform title', infos)
        self.assertEqual(infos['year'], u'2012')
        self.assertEqual(infos['languages'], u'Deutsch (ger)')
        self.assertNotIn('category', infos)
        self.assertNotIn('publisher', infos)
        self.assertEqual(infos['edition'], u'6. Aufl., Ausg. 2012')
        self.assertEqual(unicode(infos['isbn']).split(' ', 1)[0], u'978-3-943176-24-7')
        self.assertEqual(infos['ean'], u'9783943176247')