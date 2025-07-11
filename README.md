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
- [Installation](#installation)
- [Updating xml2rfc](#updating-xml2rfc)
- [Usage](#usage)
- [Contributing](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md)
- [Getting Started](#getting-started)
    - [Git Cloning Tips](#git-cloning-tips)
    - [Docker Dev Environment](#docker-dev-environment)
- [Release Procedure](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md#release-procedure)

---

### Introduction

The [IETF] uses a specific format for the standards and other documents it publishes as [RFCs], and for the draft documents which are produced when developing documents for publications. There exists a number of different tools to facilitate the formatting of drafts and RFCs according to the existing rules, and this tool, **xml2rfc**, is one of them. It takes as input an xml file that contains the text and meta-information about author names etc., and transforms it into suitably formatted output. The input xml file should follow the grammars in [RFC7749] *(for v2 documents)* or [RFC7991] *(for v3 documents)*.

[RFCXML vocabulary reference] is available at [authors.ietf.org].

**xml2rfc** provides a variety of output formats. See the command line help for a full list of formats. It also provides conversion from v2 to v3, and can run the [preptool] on its input.

### Installation

`xml2rfc` is available as Python package. You can install it with following command:
```sh
pip install xml2rfc
```

If you're using [pipx](https://pipx.pypa.io/stable/), you can install `xml2rfc` with the following command:
```sh
pipx install xml2rfc
```

`xml2rfc` also provides `pdf` extra package to install required packages required for PDF file generation.
See [next section](#installation-of-support-libraries-for-the-pdf-formatter) about additional requirements for PDF generation.

To install `xml2rfc` with PDF generation support run:
```sh
pip install "xml2rfc[pdf]"
```

To install `pdf` extra with `pipx` run:
```sh
pipx install "xml2rfc[pdf]"
```

#### Installation of support libraries for the PDF-formatter

In order to generate PDFs, **xml2rfc** uses the [WeasyPrint] module, which depends on external libraries that must be installed as native packages on your platform, separately from the **xml2rfc** install.

1. First, install the **Pango**, and other required libraries on your system.  See installation instructions on the [WeasyPrint Docs].

2. Next, install WeasyPrint python modules using pip.

```sh
pip install "xml2rfc[pdf]"
```
3. Finally, install the required fonts:
  * Download latest fonts from [xml2rfc-fonts](https://github.com/ietf-tools/xml2rfc-fonts/releases/latest).
  * In the **Assets** section, download either the `tar.gz` or the `zip` archive.
  * Extract the contents of the downloaded `xml2rfc-fonts` archive.
  * Install the fonts found in the `noto` and `roboto_mono` directories to your operating system.

With these installed and available to **xml2rfc**, the `--pdf` switch will be enabled.

### Updating xml2rfc

To update `xml2rfc`, run the following command:
```sh
pip install --upgrade xml2rfc
```

If you are using `pipx`, you can update it with:
```sh
pipx upgrade xml2rfc
```

### Usage

**xml2rfc** accepts a single XML document as input and outputs to one or more conversion formats.

#### Basic Usage

```sh
xml2rfc SOURCE [options] FORMATS...
```

Run `xml2rfc --help` for a full listing of command-line options.

### Getting Started

This project is following the standard **Git Feature Workflow** development model. Learn about all the various steps of the development workflow, from creating a fork to submitting a pull request, in the [Contributing](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md) guide.

> Make sure to read the [Styleguides](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md#styleguides) section to ensure a cohesive code format across the project.

You can submit bug reports, enhancements and new feature requests in the [discussions](https://github.com/ietf-tools/xml2rfc/discussions) area. Accepted tickets will be converted to issues.

#### Git Cloning Tips

As outlined in the [Contributing](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md) guide, you will first want to create a fork of the xml2rfc project in your personal GitHub account before cloning it.

For example *(replace `USERNAME` with your GitHub username)*:

```sh
git clone https://github.com/USERNAME/xml2rfc.git
```
#### Docker Dev Environment

Run `./run.sh` command to build and start a docker development environment.
The initial build may take time because it downloads all required fonts as well.


```sh
./run.sh
```

[IETF]: https://www.ietf.org/
[RFCs]: https://www.rfc-editor.org/
[RFC7749]: https://www.rfc-editor.org/info/rfc7749
[RFC7991]: https://www.rfc-editor.org/info/rfc7991
[RFCXML vocabulary reference]: https://authors.ietf.org/en/rfcxml-vocabulary
[authors.ietf.org]: https://authors.ietf.org/
[preptool]: https://www.rfc-editor.org/info/rfc7998
[WeasyPrint]: https://weasyprint.org/
[WeasyPrint Docs]: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
