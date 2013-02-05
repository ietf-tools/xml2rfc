GUI_PATH = ../../../gui
CLI_PATH = ../../../cli
SYNC = rsync -aW --exclude-from=../../shared/exclude.txt
BUILD_ROOT = build
DIST_ROOT = dist
TEMPLATE_ROOT = template
APP = $(BUILD_ROOT)/dist/xml2rfc.app
VERSION := $(shell cd "$(GUI_PATH)" && python -c "import xml2rfc_gui; print '.'.join(map(str, xml2rfc_gui.VERSION))")
OUTPUT := $(DIST_ROOT)/xml2rfc-gui-$(VERSION).dmg

APP_FILES = $(BUILD_ROOT)/xml2rfc \
			$(BUILD_ROOT)/xml2rfc_gui \
			$(BUILD_ROOT)/setup.py \
			$(BUILD_ROOT)/xml2rfc-gui.py \
			$(BUILD_ROOT)/cli_hook/xml2rfc-cli-boot.py \
			$(BUILD_ROOT)/cli_hook/xml2rfc-cli.sh

$(OUTPUT): $(APP)
	@# Create dmg
	@echo "Creating dmg..."
	gzcat dmg/template.dmg.gz > /tmp/tmp.dmg
	hdiutil resize -size 200m /tmp/tmp.dmg
	open /tmp/tmp.dmg
	@echo "Waiting for dmg to mount..."
	@while [ ! -d "/Volumes/xml2rfc" ]; do \
		sleep 1; \
		/bin/echo -n .; \
	done
	sleep 2
	cp -RP "$<" /Volumes/xml2rfc
	sync
	diskutil eject xml2rfc

	@# Compress dmg
	@echo "Finalizing dmg..."
	mkdir -p $(DIST_ROOT)
	rm -f $@
	hdiutil convert /tmp/tmp.dmg -format UDZO -imagekey zlib-level=9 -o "$@"


$(APP): $(APP_FILES)
	@echo "Building $(VERSION) for OSX..."

	@# Run py2app
	rm -rf $@
	cd $(BUILD_ROOT) && python setup.py py2app

	@# Install custom CLI scripts
	@echo "Installing CLI hook for OSX..."
	cp "$(CLI_PATH)/scripts/xml2rfc" "$(BUILD_ROOT)/dist/xml2rfc.app/Contents/Resources/xml2rfc-cli.py"
	cp $(BUILD_ROOT)/cli_hook/xml2rfc-cli-boot.py "$(BUILD_ROOT)/dist/xml2rfc.app/Contents/Resources/xml2rfc-cli-boot.py"
	cp $(BUILD_ROOT)/cli_hook/xml2rfc-cli.sh "$(BUILD_ROOT)/dist/xml2rfc.app/Contents/MacOS/xml2rfc-cli"


# Client xml2rfc code
$(BUILD_ROOT)/xml2rfc: $(shell find $(CLI_PATH)/xml2rfc -name *.py)
	mkdir -p $(BUILD_ROOT)
	$(SYNC) $(CLI_PATH)/xml2rfc/ $@
	touch $@


# GUI xml2rfc code
$(BUILD_ROOT)/xml2rfc_gui: $(shell find $(GUI_PATH)/xml2rfc_gui -name *.py)
	mkdir -p $(BUILD_ROOT)
	$(SYNC) $(GUI_PATH)/xml2rfc_gui/ $@
	$(SYNC) $(GUI_PATH)/assets $(BUILD_ROOT)
	touch $@


# Copy template file into build root
$(BUILD_ROOT)/%: $(TEMPLATE_ROOT)/%
	@mkdir -p `dirname $@`
	cp $< $@


clean:
	@echo "Cleaning for OSX..."
	rm -rf "$(BUILD_ROOT)"
	rm -rf "$(DIST_ROOT)"
