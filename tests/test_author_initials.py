import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lxml import html


DOCUMENT = """\
<rfc version="3" docName="draft-example-initials-00"
     ipr="trust200902" category="info" submissionType="IETF">
  <front>
    <title>Author Initials Example</title>
    <author fullname="jane morgan Doe" />
    <author fullname="Rita Roe" initials="r" surname="Roe" />
    <author fullname="j Solo" />
    <author fullname="Mary Major" />
    <author fullname="田中 太郎" asciiFullname="taro Tanaka" />
    <date year="2026" month="11" day="24" />
    <abstract><t>A small rendering example.</t></abstract>
  </front>
  <middle><section><name>Example</name><t>Demonstration.</t></section></middle>
  <back/>
</rfc>
"""


class AuthorInitialsTest(unittest.TestCase):
    def test_author_name_case_is_preserved_when_initials_are_derived(self):
        expected = ['j. m. Doe', 'r. Roe', 'j Solo', 'M. Major', '田中 太郎 (t. Tanaka)']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'authors.xml'
            source.write_text(DOCUMENT, encoding='utf-8')
            for output_format in ('text', 'html'):
                with self.subTest(output_format=output_format):
                    output = root / f'authors.{output_format}'
                    args = [
                        sys.executable, '-m', 'xml2rfc.run',
                        '--skip-config-files', '--no-network', '--cache', str(root / 'cache'),
                        f'--{output_format}', '--out', str(output), str(source),
                    ]
                    if output_format == 'text':
                        args.append('--no-pagination')
                    result = subprocess.run(
                        args, capture_output=True, text=True, encoding='utf-8', timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if output_format == 'text':
                        front, _, _ = output.read_text(encoding='utf-8').partition('\nAbstract\n')
                        for name in expected:
                            self.assertIn(name, front)
                    else:
                        document = html.parse(str(output)).getroot()
                        authors = [
                            ' '.join(node.text_content().split())
                            for node in document.find_class('author-name')
                        ]
                        self.assertEqual(authors, expected)
