GUI_PATH = ../../../gui
CLI_PATH = ../../../cli
SYNC = rsync -aW --exclude-from=../../shared/exclude.txt
BUILDROOT = build
DISTROOT = dist
VERSION := $(shell cd "$(GUI_PATH)" && python -c "import xml2rfc_gui; print '.'.join(map(str, xml2rfc_gui.VERSION))")

all: clean prepare run

prepare:
	@echo "Preparing build directory for Fedora..."

	@# Create workspace
	mkdir -p "$(BUILDROOT)"
	mkdir -p "$(DISTROOT)"

	@# Copy core+GUI
	$(SYNC) "$(GUI_PATH)/xml2rfc_gui" "$(BUILDROOT)"
	$(SYNC) "$(CLI_PATH)/xml2rfc" "$(BUILDROOT)"

	@# Copy setup script and run script
	cp scripts/setup.py "$(BUILDROOT)"
	cp scripts/setup.cfg "$(BUILDROOT)"
	cp ../../shared/xml2rfc-gui.py "$(BUILDROOT)/xml2rfc-gui"


run:
	@echo "Building $(VERSION) for Fedora..."
	cd $(BUILDROOT) && python setup.py bdist_rpm
	cp $(BUILDROOT)/dist/* $(DISTROOT)

clean:
	@echo "Cleaning for Fedora..."
	rm -rf "$(BUILDROOT)"
	rm -rf "$(DISTROOT)"
