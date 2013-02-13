PLATFORM=`uname -s`

if [ "$PLATFORM" = "Linux" ]; then
    if [ -f "/etc/debian_version" ]; then
        PLATFORM="debian"
    fi
    if [ -f "/etc/fedora-release" ]; then
	PLATFORM="fedora"
    fi
fi

echo $PLATFORM
