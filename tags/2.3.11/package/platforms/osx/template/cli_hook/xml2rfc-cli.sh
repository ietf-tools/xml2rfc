#!/usr/bin/env bash

# Get path of script
ORIGINAL_CWD=`pwd`;
SCRIPT_PATH="${BASH_SOURCE[0]}";
if ([ -h "${SCRIPT_PATH}" ]) then
  while([ -h "${SCRIPT_PATH}" ]) do SCRIPT_PATH=`readlink "${SCRIPT_PATH}"`; done
fi
pushd . > /dev/null
cd `dirname ${SCRIPT_PATH}` > /dev/null
SCRIPT_PATH=`pwd`;
popd  > /dev/null

# Make sure we dont mess with the cwd
cd "${ORIGINAL_CWD}"

# Launch xml2rfc with custom interpreter
export PYTHONHOME="${SCRIPT_PATH}/../Resources"
"${SCRIPT_PATH}/python" "${SCRIPT_PATH}/../Resources/xml2rfc-cli-boot.py" $@
