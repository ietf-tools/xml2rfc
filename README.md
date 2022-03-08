<div align="center">
    
<img src="https://raw.githubusercontent.com/ietf-tools/common/main/assets/logos/xml2rfc.svg" alt="XML2RFC" height="125" />
    
[![Release](https://img.shields.io/github/release/ietf-tools/xml2rfc.svg?style=flat&maxAge=600)](https://github.com/ietf-tools/xml2rfc/releases)
[![License](https://img.shields.io/github/license/ietf-tools/xml2rfc)](https://github.com/ietf-tools/xml2rfc/blob/main/LICENSE)
[![PyPI - Version](https://img.shields.io/pypi/v/xml2rfc)](https://pypi.org/project/xml2rfc/)
[![PyPI - Status](https://img.shields.io/pypi/status/xml2rfc)](https://pypi.org/project/xml2rfc/)
[![PyPI - Format](https://img.shields.io/pypi/format/xml2rfc)](https://pypi.org/project/xml2rfc/)
    
##### Generate RFCs and IETF drafts from document source in XML according to the IETF xml2rfc v2 and v3 vocabularies
    
</div>

- [Changelog](https://github.com/ietf-tools/xml2rfc/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md)
- [Installation](#installation)
- [Usage](#usage)
- [Release Procedure](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md#release-procedure)

---

### Introduction

The [IETF] uses a specific format for the standards and other documents it publishes as [RFCs], and for the draft documents which are produced when developing documents for publications. There exists a number of different tools to facilitate the formatting of drafts and RFCs according to the existing rules, and this tool, **xml2rfc**, is one of them. It takes as input an xml file which contains the text and meta-information about author names etc., and transforms it into suitably formatted output. The input xml file should follow the grammars in [RFC7749] *(for v2 documents)* or [RFC7991] *(for v3 documents)*. Note that the grammar for v3 is still being refined, and changes will eventually be captured in the [bis draft for 7991]. Changes not yet captured can be seen in the xml2rfc source [v3.rng], or in the [documentation xml2rfc produces] with its `--doc` flag.

**xml2rfc** provides a variety of output formats. See the command line help for a full list of formats. It also provides conversion from v2 to v3, and can run the [preptool] on its input.

### Installation

Installation of the python package is done as usual with `pip install xml2rfc`, using appropriate switches and/or sudo.

#### Installation of support libraries for the PDF-formatter

In order to generate PDFs, **xml2rfc** uses the WeasyPrint module, which depends on external libaries that must be installed as native packages on your platform, separately from the **xml2rfc** install.

First, install the **Cairo**, **Pango**, and **GDK-PixBuf** library files on your system. See installation instructions on the [WeasyPrint Docs](https://weasyprint.readthedocs.io/en/stable/install.html).

> On some macOS systems with **System Integrity Protection** active, you may need to create a symlink from your home directory to the library installation directory (often `/opt/local/lib`):
> 
> ```sh
> ln -s /opt/local/lib ~/lib
> ```
> 
> in order for weasyprint to find the installed cairo and pango libraries. Whether this is needed or not depends on whether you used macports or homebrew to install cairo and pango, and the homebrew / macport version.

Next, install the `pycairo` and `weasyprint` python modules using pip. Depending on your system, you may need to use `sudo` or install in user-specific directories, using the `--user` switch.  On macOS in particular, you may also need to install a newer version of `setuptools` using `--user` before `weasyprint` can be installed.

> If you install with the `--user` switch, you may need to also set `PYTHONPATH`, e.g.:
> 
> ```sh
> PYTHONPATH=/Users/henrik/Library/Python/3.6/lib/python/site-packages
> ```
>
> for Python 3.6.

The basic pip commands (modify as needed according to the text above) are:

```sh
pip install 'pycairo>=1.18' 'weasyprint<=0.42.3'
```

With these installed and available to **xml2rfc**, the `--pdf` switch will be enabled.

For PDF output, you also need to install the Noto font set. [Download the full set](https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip) and install as appropriate for your platform.

### Usage

**xml2rfc** accepts a single XML document as input and outputs to one or more conversion formats.

#### Basic Usage

```sh
xml2rfc SOURCE [options] FORMATS...
```

Run `xml2rfc --help` for a full listing of command-line options.

[IETF]: https://www.ietf.org/
[RFCs]: https://www.rfc-editor.org/
[RFC7749]: https://tools.ietf.org/html/rfc7749
[RFC7991]: https://tools.ietf.org/html/rfc7991
[bis draft for 7991]: https://tools.ietf.org/html/draft-iab-rfc7991bis
[v3.rng]: https://trac.tools.ietf.org/tools/xml2rfc/trac/browser/trunk/cli/xml2rfc/data/v3.rng
[documentation xml2rfc produces]: https://xml2rfc.tools.ietf.org/xml2rfc-doc.html
[preptool]: https://tools.ietf.org/html/rfc7998
