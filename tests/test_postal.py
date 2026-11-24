import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lxml import html


DOCUMENT = """\
<rfc version="3" docName="draft-example-country-00"
     ipr="trust200902" category="info" submissionType="IETF">
  <front>
    <title>Country Address Example</title>
    <author initials="A." surname="Example" fullname="A. Example">
      <address>
        <postal>
          <street>123 Example Street</street>
          <city>Amsterdam</city>
          <country>The Netherlands</country>
        </postal>
      </address>
    </author>
    <date year="2026" month="11" day="24" />
    <abstract><t>A small rendering example.</t></abstract>
  </front>
  <middle><section><name>Example</name><t>Demonstration.</t></section></middle>
  <back/>
</rfc>
"""


class PostalAddressTest(unittest.TestCase):
    def test_unknown_country_remains_in_rendered_address(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'country.xml'
            source.write_text(DOCUMENT, encoding='utf-8')
            for output_format in ('text', 'html'):
                with self.subTest(output_format=output_format):
                    output = root / f'country.{output_format}'
                    result = subprocess.run(
                        [
                            sys.executable, '-m', 'xml2rfc.run',
                            '--skip-config-files', '--no-network', '--cache', str(root / 'cache'),
                            f'--{output_format}', '--out', str(output), str(source),
                        ],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(
                        'Warning: Country lookup failed for <country>The Netherlands</country>',
                        result.stderr,
                    )
                    if output_format == 'text':
                        address_lines = output.read_text(encoding='utf-8').splitlines()
                    else:
                        document = html.parse(str(output)).getroot()
                        address_lines = [node.text_content() for node in document.find_class('country-name')]
                    self.assertIn('The Netherlands', [line.strip() for line in address_lines])
