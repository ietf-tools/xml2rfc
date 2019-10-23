#!/bin/bash

echo "Gathering info ..."

if [ ! "$USER" ]; then
    echo "Environment variable USER is not set -- will set USER='user'."
    USER="user"
fi
if [ ! "$UID" ]; then
    echo "Environment variable UID is not set -- will set UID='1000'."
    UID="1000"
fi
if [ ! "$GID" ]; then
    echo "Environment variable GID is not set -- will set GID='1000'."
    GID="1000"
fi
if [ ! "$TAG" ]; then
    echo "Environment variable TAG is not set -- will set TAG='xml2rfc'."
    TAG="xml2rfc"
fi
echo "User $USER ($UID:$GID)"

if ! id -u "$USER" &> /dev/null; then
    echo "Creating user '$USER' ..."
    useradd -s /bin/bash --groups staff,sudo,tty --uid $UID --gid $GID $USER
    echo "$USER:$USER" | chpasswd
fi

if [ "$HOSTNAME" ]; then
    hostname "$HOSTNAME"
else
    echo "Environment variable HOSTNAME is not set -- cannot set hostname"
fi

#VIRTDIR="/opt/home/$USER/$TAG"
VIRTDIR="/home/$USER/$CWD/env"
echo "Checking that there's a virtual environment for $TAG ..."
if [ ! -f $VIRTDIR/bin/activate ]; then
    echo "Setting up python virtualenv at $VIRTDIR ..."
    mkdir -P $VIRTDIR
    virtualenv --system-site-packages $VIRTDIR
    echo -e "
# This is from $VIRTDIR/bin/activate, to activate the
# virtual python environment on docker container entry:
" >> /etc/bash.bashrc
    cat $VIRTDIR/bin/activate >> /etc/bash.bashrc
    cat /usr/local/share/xml2rfc/setprompt >> /etc/bash.bashrc 
else
    echo "Using virtual environment at $VIRTDIR"
fi

echo "Activating the virtual python environment ..."
. $VIRTDIR/bin/activate

chmod -R g+w   /usr/local/lib/		# so we can patch libs if needed

chmod g+rw /dev/pts/0                   # to make /usr/bin/pinentry work

echo "Checking for local font directory"
LOCAL_FONTS="/home/$USER/.fonts/opentype/noto/"
[ -d $LOCAL_FONTS ] || echo "
 *** Missing font directory: $LOCAL_FONTS ***
"

FONT_COUNT=1605
echo "Checking for local fonts"
local_fonts="$(ls $LOCAL_FONTS | grep '\.[to]tf' | wc -l)"
[ $local_fonts = $FONT_COUNT ] || echo "
 *** Missing local fonts: Expected $FONT_COUNT, found $local_fonts ***
"

# Check that local fonts are linked to fontconfig dir
found_fonts="$(ls /usr/share/fonts/truetype/noto/ | grep '\.[to]tf' | wc -l)"
[ $found_fonts = $local_fonts ] || {
  echo "Linking in Noto fonts"
  ln -sf $LOCAL_FONTS/*.[to]tf /usr/share/fonts/truetype/noto/
}

cd "/home/$USER/$CWD" || cd "/home/$USER/"

echo "Done!"

su $USER
