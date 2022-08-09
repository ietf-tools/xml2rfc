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
- [Usage](#usage)
- [Contributing](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md)
- [Getting Started](#getting-started)
    - [Git Cloning Tips](#git-cloning-tips)
    - [Docker Dev Environment](#docker-dev-environment)
- [Release Procedure](https://github.com/ietf-tools/.github/blob/main/CONTRIBUTING.md#release-procedure)

---

### Introduction

The [IETF] uses a specific format for the standards and other documents it publishes as [RFCs], and for the draft documents which are produced when developing documents for publications. There exists a number of different tools to facilitate the formatting of drafts and RFCs according to the existing rules, and this tool, **xml2rfc**, is one of them. It takes as input an xml file that contains the text and meta-information about author names etc., and transforms it into suitably formatted output. The input xml file should follow the grammars in [RFC7749] *(for v2 documents)* or [RFC7991] *(for v3 documents)*. Note that the grammar for v3 is still being refined, and changes will eventually be captured in the [bis draft for 7991]. Changes not yet captured can be seen in the xml2rfc source [v3.rng], or in the [documentation xml2rfc produces] with its `--doc` flag.

**xml2rfc** provides a variety of output formats. See the command line help for a full list of formats. It also provides conversion from v2 to v3, and can run the [preptool] on its input.

### Installation

Installation of the python package is done as usual with `pip install xml2rfc`, using appropriate switches.

#### Installation of support libraries for the PDF-formatter

In order to generate PDFs, **xml2rfc** uses the [WeasyPrint] module, which depends on external libraries that must be installed as native packages on your platform, separately from the **xml2rfc** install.

1. First, install the **Pango**, and other required libraries on your system.  See installation instructions on the [WeasyPrint Docs].

2. Next, install WeasyPrint python modules using pip.

```sh
pip install 'weasyprint==55.0'
```
3. Finally, install the full **Noto Font** and **Roboto Mono** packages:
  * Download the full font file from:
    https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip
  * Follow the installation instructions at
    https://www.google.com/get/noto/help/install/
  * Go to https://fonts.google.com/specimen/Roboto+Mono, and download the
    font.  Follow the installation instructions above, as applied to this download.

With these installed and available to **xml2rfc**, the `--pdf` switch will be enabled.

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
[bis draft for 7991]: https://datatracker.ietf.org/doc/draft-iab-rfc7991bis/
[v3.rng]: xml2rfc/data/v3.rng
[documentation xml2rfc produces]: https://ietf-tools.github.io/xml2rfc/
[preptool]: https://www.rfc-editor.org/info/rfc7998
[WeasyPrint]: https://weasyprint.org/
[WeasyPrint Docs]: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
