# Local variables
TARGET := $(shell bash platform.sh)
WIN_PATH = platforms/win
OSX_PATH = platforms/osx
DEB_PATH = platforms/debian
RPM_PATH = platforms/fedora
GUI_PATH = ../gui
DIST = dist

all: prepare run

prepare:
	mkdir -p "$(DIST)"

# Run platform specific make file and copy the output to dist
run:
#ifeq "$(TARGET)" "Darwin"
#	cd "$(OSX_PATH)" && $(MAKE)
#	cp $(OSX_PATH)/$(DIST)/* $(DIST)
#else
ifeq "$(TARGET)" "debian"
	cd "$(DEB_PATH)" && $(MAKE)
	cp $(DEB_PATH)/$(DIST)/* $(DIST)
else
ifeq "$(TARGET)" "fedora"
	cd "$(RPM_PATH)" && $(MAKE)
	cp $(RPM_PATH)/$(DIST)/* $(DIST)
#endif
endif
endif
	@echo "All done.  Output in $(DIST)/"

clean:
	@echo "Cleaning all platforms..."
	rm -rf "$(DIST)"
	# cd "$(OSX_PATH)" && $(MAKE) clean
	cd "$(DEB_PATH)" && $(MAKE) clean
	cd "$(RPM_PATH)" && $(MAKE) clean
