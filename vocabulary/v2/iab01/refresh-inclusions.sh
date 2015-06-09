#!/bin/sh
# refresh file inclusions

expand() {

  cat $1 | awk ' 

  function filecontents(filename) {
    while (getline < filename > 0) {
      fc[filename] = fc[filename] $0 "\n"
    }
    return fc[filename]
  }

  BEGIN {
    includefile = "";
    includeescapedfile = "";
  }
  
  # start include (verbatim mode)
  /<\?BEGININC .* \?>$/ {
    print
    keyword = "<?BEGININC " 
    extract = match($0, /<\?BEGININC .* \?>$/)
    includefile = substr($0, RSTART + length(keyword), RLENGTH - 3 - length(keyword))
    output = filecontents(includefile)
    printf("%s", output)
  }
  
  # start include (escape-for-XML mode)
  /<\?BEGINESCAPEDINC .* \?>$/ {
    print
    keyword = "<?BEGINESCAPEDINC " 
    extract = match($0, /<\?BEGINESCAPEDINC .* \?>$/)
    includeescapedfile = substr($0, RSTART + length(keyword), RLENGTH - 3 - length(keyword))
    output = filecontents(includeescapedfile)
    # escape ampersand, less-than, and greater-than if part of a CDATA end marker
    gsub(/&/, "\\&amp;", output)
    gsub(/</, "\\&lt;", output)
    gsub(/]]>/, "]]\\&gt;", output)
    printf("%s", output)
  }

  # end include (verbatim mode)
  /^<\?ENDINC .* \?>/ {
    if ($2 != includefile) {
      printf ("unexpected ENDINC, got %s but expected %s\n", $2, includefile) >> "/dev/stderr"
    }
    includefile = "";
  }
  
  # end include (escape-for-XML mode)
  /^<\?ENDESCAPEDINC .* \?>/ {
    if ($2 != includeescapedfile) {
      printf ("unexpected ENDESCAPEDINC, got %s but expected %s\n", $2, includeescapedfile) >> "/dev/stderr"
    }
    includeescapedfile = "";
  }

  #default
  {
    if (includefile == "" && includeescapedfile == "") {
      print
    }
  }
  
  END {
    if (includefile != "") {
      printf ("missing ENDINC for %s\n", includefile) >> "/dev/stderr"
    }
    if (includeescapedfile != "") {
      printf ("missing ENDESCAPEDINC for %s\n", includeescapedfile) >> "/dev/stderr"
    }
  }
  
  ' > $$
  
  # check for changes
  
  cmp -s $1 $$ || ( cp $$ $1 ; echo $1 updated )
  
  rm -f $$
}

[ $# -ne 0 ] || ( echo "refresh-inclusions.sh file..." >&2 ; exit 2 )

for i in $*
do
  expand $i
done
