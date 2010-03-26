#!/bin/sh
# the next line restarts using wish \
exec wish "$0" "$0" "$@"


# TODO:
#       seriesInfo: RFC, I-D
#       iref


package require xml 1.8


global dparser
if {![info exists dparser]} {
    set dparser ""
}


proc xml2sgml {input {output ""}} {
    global errorCode errorInfo
    global dparser errorP passno stdout

    if {![string compare [file extension $input] ""]} {
        append input .xml
    }

    set stdin [open $input { RDONLY }]
    set inputD [file dirname [set ifile $input]]

    if {![string compare $output ""]} {
        set output [file rootname $input].sgml
    }
    if {![string compare $input $output]} {
        error "input and output files must be different"
    }

    if {[file exists [set file [file join $inputD .xml2rfc.rc]]]} {
        source $file
    }

    set data [prexml [read $stdin] $inputD $input]

    catch { close $stdin }

    set code [catch {
        if {![string compare $dparser ""]} {
            global emptyA

            set dparser [xml::parser]
            array set emptyA {}

            $dparser configure \
                        -elementstartcommand          { xml_begin           } \
                        -elementendcommand            { xml_end             } \
                        -characterdatacommand         { xml_pcdata          } \
                        -entityreferencecommand       ""                      \
                        -errorcommand                 { unexpected error    } \
                        -warningcommand               { unexpected warning  } \
                        -entityvariable               emptyA                  \
                        -final                        yes                     \
                        -reportempty                  no
        }

        set passmax 2
        set stdout ""
        for {set passno 1} {$passno <= $passmax} {incr passno} {
            xml_pass start $output
            $dparser parse $data
            xml_pass end
            if {$errorP} {
                break
            }
        }
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    catch { close $stdout }

    if {$code == 1} {
        set result [around2fl $result]

        catch {
            global stack

            if {[llength $stack] > 0} {
                set text "Context: "
                foreach frame $stack {
                    append text "\n    <[lindex $frame 0]"
                    foreach {k v} [lindex $frame 2] {
                        regsub -all {"} $v {&quot;} v
                        append text " $k=\"$v\""
                    }
                    append text ">"
                }
                append result "\n\n$text"
            }
        }
    }

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc prexml {stream inputD {inputF ""}} {
    global env tcl_platform

    if {[catch { set path $env(XML_LIBRARY) }]} {
        set path [list $inputD]
    }
    switch -- $tcl_platform(platform) {
        windows {
            set c ";"
        }

        default {
            set c ":"
        }
    }
    set path [split $path $c]

    if {[string first "%include." $stream] < 0} {
        set newP 1
    } else {
        set newP 0
    }
    set stream [prexmlaux $newP $stream $inputD $inputF $path]

# because <![CDATA[ ... ]]> isn't supported in TclXML...
    set data ""
    set litN [string length [set litS "<!\[CDATA\["]]
    set litO [string length [set litT "\]\]>"]]
    while {[set x [string first $litS $stream]] >= 0} {
        append data [string range $stream 0 [expr $x-1]]
        set stream [string range $stream [expr $x+$litN] end]
        if {[set x [string first $litT $stream]] < 0} {
            error "missing close to CDATA"
        }
        set y [string range $stream 0 [expr $x-1]]
        regsub -all {&} $y {\&amp;} y
        regsub -all {<} $y {\&lt;}  y
        append data $y
        set stream [string range $stream [expr $x+$litO] end]
    }
    append data $stream

    return $data
}

proc prexmlaux {newP stream inputD inputF path} {
    global fldata

# an MTR hack...

# the old way:
#
# whenever "%include.whatever;" is encountered, act as if the DTD contains
#
#       <!ENTITY % include.whatever SYSTEM "whatever.xml">
#
# this yields a nested (and cheap-and-easy) include facility.
#

# the new way:
#
# <?rfc include='whatever' ?>
#
# note that this occurs *before* the xml parsing occurs, so they aren't hidden
# inside a <![CDATA[ ... ]]> block.
#

    if {$newP} {
        set litS "<?rfc include="
        set litT "?>"
    } else {
        set litS "%include."
        set litT ";"
    }
    set litN [string length $litS]
    set litO [string length $litT]

    set data ""
    set fldata [list [list $inputF [set lineno 1] [numlines $stream]]]
    while {[set x [string first $litS $stream]] >= 0} {
        incr lineno [numlines [set initial \
                                   [string range $stream 0 [expr $x-1]]]]
        append data $initial
        set stream [string range $stream [expr $x+$litN] end]
        if {[set x [string first $litT $stream]] < 0} {
            error "missing close to %include.*"
        }
        set y [string range $stream 0 [expr $x-1]]
        if {$newP} {
            set y [string trim $y]
            if {[set quoteP [string first "'" $y]]} {
                regsub -- {^"([^"]*)"$} $y {\1} y
            } else {
                regsub -- {^'([^']*)'$} $y {\1} y
            }
        }
        if {![regexp -nocase -- {^[a-z0-9.-]+$} $y]} {
            error "invalid include $y"
        }
        set include ""
        foreach dir $path {
            if {(![file exists [set file [file join $dir $y]]]) \
                    && (![file exists [set file [file join $dir $y.xml]]])} {
                continue
            }
            set fd [open $file { RDONLY }]
            set include [read $fd]
            catch { close $fd }
            break
        }
        if {![string compare $include ""]} {
            error "unable to find external file $y.xml"
        }

        set len [numlines $include]
        set flnew {}
        foreach fldatum $fldata {
            set end [lindex $fldatum 2]
            if {$end >= $lineno} {
                set fldatum [lreplace $fldatum 2 2 [expr $end+$len]]
            }
            lappend flnew $fldatum
        }
        set fldata $flnew
        lappend fldata [list $file $lineno $len]

        set stream $include[string range $stream [expr $x+$litO] end]
    }
    append data $stream

    return $data
}

proc numlines {text} {
    set n [llength [split $text "\n"]]
    if {![string compare [string range $text end end] "\n"]} {
        incr n -1
    }

    return $n
}

proc around2fl {result} {
    global fldata

    if {[regexp -nocase -- { around line ([1-9][0-9]*)} $result x lineno] \
            != 1} {
        return $result
    }

    set file ""
    set offset 0
    set max 0
    foreach fldatum $fldata {
        if {[set start [lindex $fldatum 1]] > $lineno} {
            break
        }
        if {[set new [expr $start+[set len [lindex $fldatum 2]]]] < $max} {
            continue
        }

        if {$lineno <= $new} {
            set file [lindex $fldatum 0]
            set offset [expr $lineno-$start]
        } else {
            incr offset -$len
            set max $new
        }
    }

    set tail " around line $offset"
    if {[string compare $file [lindex [lindex $fldata 0] 0]]} {
        append tail " in $file"
    }
    regsub " around line $lineno" $result $tail result

    return $result
}

proc xml_pass {tag {output ""}} {
    global counter depth elem elemN errorP passno stack stdout

    switch -- $tag {
        start {
            catch { unset depth }
            array set depth [list bookinfo 0 list 0 note 0 section 0]
            set elemN 0
            set stack {}
            switch --  $passno {
                1 {
                    catch {unset counter }
                    catch {unset elem }
                    set errorP 0
                }

                2 {
                    set stdout [open $output { WRONLY CREAT TRUNC }]
                }
            }
        }

        end {
        }
    }

}

proc xml_begin {name {av {}}} {
    global counter depth elem elemN errorP passno stack stdout

    incr elemN

# because TclXML... quotes attribute values containing "]"
    set kv ""
    foreach {k v} $av {
        lappend kv $k
        regsub -all {\\\[} $v {[} v
        lappend kv $v
    }
    set av $kv

    if {$elemN > 1} {
        set parent [lindex [lindex $stack end] 1]
        array set pv $elem($parent)
        lappend pv(.CHILDREN) $elemN
        set elem($parent) [array get pv]
    }

    lappend stack [list $name [set elemX $elemN] $av]

    if {$passno == 1} {
        array set attrs $av
        array set attrs [list .NAME $name .CHILDREN {}]
        if {[lsearch -exact [list title organization \
                                  street city region code country \
                                  phone facsimile email uri \
                                  area workgroup keyword \
                                  xref eref seriesInfo] $name] >= 0} {
            set attrs(.PCDATA) ""
        }
        switch -- $name {
            list {
		if {![info exists attrs(style)]} {
		    set style empty
    
                    foreach frame [lrange $stack 0 end-1] {
                        if {[string compare [lindex $frame 0] list]} {
                            continue
                        }
                        set elemY [lindex $frame 1]
                        array set pv $elem($elemY)
        
			set style $pv(style)
                    }

		    set attrs(style) $style
                }

		if {![string first "format " $attrs(style)]} {
		    set format [string trimleft \
				       [string range $attrs(style) 7 end]]
		    set attrs(style) hanging
		    if {([string compare [set attrs(format) $format] ""]) \
			    && (![info exists counter($format)])} {
			set counter($format) 0
		    }
		} else {
		    set attrs(format) ""
		}
            }

            t {
                if {![info exists attrs(hangText)]} {
		    set style ""
		    set format ""
    
                    foreach frame [lrange $stack 0 end-1] {
                        if {[string compare [lindex $frame 0] list]} {
                            continue
                        }
                        set elemY [lindex $frame 1]
                        array set pv $elem($elemY)

			set style $pv(style)
			set format $pv(format)
                    }
		
		    if {[string compare $format ""]} {
			set attrs(hangText) \
			    [format $format [incr counter($format)]]
		    }
		}
	    }
	}

        set elem($elemN) [array get attrs]

        return
    }

    if {([lsearch -exact [list front area workgroup keyword \
                               abstract note section \
                               t list figure preamble postamble \
                               xref eref iref vspace back] $name] >= 0) \
            && ([lsearch0 $stack references] >= 0)} {
        return  
    }

    array set attrs $elem($elemX)

    switch -- $name {
        rfc {
            puts $stdout \
                 "<!DOCTYPE book PUBLIC \"-//OASIS//DTD DocBook V3.1//EN\">"
            puts $stdout "<book>"
        }

        front {
            incr depth(bookinfo)
            puts $stdout "<bookinfo>"

            if {[lsearch0 $stack reference] >= 0} {
                set hitP 0
                foreach child [find_element seriesInfo $attrs(.CHILDREN)] {
                    array set sv $elem($child)
                    switch -- $sv(name) {
                        isbn - issn {
                            set hitP 1
                        }
                    }
                    unset sv
                }
                if {!$hitP} {
                    set attrs(.ORGNAME) ""
                    set elem($elemX) [array get attrs]
                }
            }
        }

        title {
            if {[lsearch0 $stack reference] >= 0} {
                set reference [lindex [lindex $stack end-2] 1]
                array set rv $elem($reference)
                foreach child [find_element seriesInfo $rv(.CHILDREN)] {
                    array set sv $elem($child)
                    switch -- $sv(name) {
                        RFC {
                            set attrs(.PCDATA) \
                                "RFC $sv(value): $attrs(.PCDATA)"
                            break
                        }
                    }
                    unset sv
                }
            }

            puts -nonewline $stdout "<title>"
            pcdata_sgml $attrs(.PCDATA)
            puts $stdout "</title>"
        }

        author {
            if {[lsearch0 $stack reference] >= 0} {
                set reference [lindex [lindex $stack end-2] 1]
                array set rv $elem($reference)
            }
            set authorP 0
            set firstP 0

            if {[info exists attrs(fullname)]} {
                if {([info exists attrs(surname)]) \
                        && ([string compare $attrs(fullname) \
                                    "$attrs(initials) $attrs(surname)"]) \
                        && ([set x [string last $attrs(surname) \
                                           $attrs(fullname)]] > 0)} {
                    set name [string range $attrs(fullname) 0 [expr $x-1]]

                    if {[info exists attrs(initials)]} {
                        set i {}
                        foreach n [lrange [split $attrs(initials) .] 1 end-1] {
                            set i [linsert $i 0 $n]
                        }
                        foreach n $i {
                            if {[set x [string last "$n. " $name]] > 0} {
                                set name [string range $name 0 [expr $x-1]]
                            } else {
                                break
                            }
                        }
                    }

                    if {([info exists attrs(initials)]) \
                            && ([string compare $attrs(initials) \
                                        [set name \
                                             [string trimright $name]]])} {
                        if {!$authorP} {
                            incr authorP
                            puts $stdout "<author>"
                        }

                        incr firstP
                        puts -nonewline $stdout "<firstname>"
                        pcdata_sgml $name
                        puts $stdout "</firstname>"
                    }
                }
            }

            if {(!$firstP) && ([info exists attrs(initials)])} {
                if {!$authorP} {
                    incr authorP
                    puts $stdout "<author>"
                }
                puts -nonewline $stdout "<othername role=\"initials\">"
                pcdata_sgml $attrs(initials)
                puts $stdout "</othername>"
            }

            if {[info exists attrs(surname)]} {
                if {!$authorP} {
                    incr authorP
                    puts $stdout "<author>"
                }
                puts -nonewline $stdout "<surname>"
                pcdata_sgml $attrs(surname)
                puts $stdout "</surname>"
            }

            foreach child [find_element organization $attrs(.CHILDREN)] {
                array set ov $elem($child)
                if {[set x [string last . $ov(.PCDATA)]] \
                        == [expr [string length $ov(.PCDATA)]-1]} {
                    set ov(.PCDATA) [string range $ov(.PCDATA) 0 [expr $x-1]]
                }
                if {[lsearch0 $stack reference] >= 0} {
                    if {![info exists rv(.ORGNAME)]} {
                        set rv(.ORGNAME) $ov(.PCDATA)
                        set elem($reference) [array get rv]
                    }
                    break
                }

                if {!$authorP} {
                    incr authorP
                    puts $stdout "<author>"
                }
                puts $stdout "<affiliation>"

                puts -nonewline $stdout "<orgname>"
                pcdata_sgml $ov(.PCDATA)
                puts $stdout "</orgname>"

                if {[info exists ov(abbrev)]} {
                    puts -nonewline $stdout "<shortaffil>"
                    pcdata_sgml $ov(abbrev)
                    puts $stdout "</shortaffil>"
                }

                puts $stdout "</affiliation>"
                break
            }

# street, city, region, code country
# phone, facsimile, email, uri

            if {$authorP} {
                puts $stdout "</author>"
            }
        }

        date {
            if {[lsearch0 $stack reference] >= 0} {
                set tag releaseinfo
            } else {
                set tag pubdate
            }
            if {[info exists attrs(year)]} {
                puts -nonewline $stdout "<$tag>"
                if {[info exists attrs(month)]} {
                    puts -nonewline $stdout "$attrs(month) "
                }
                puts $stdout "$attrs(year)</$tag>"
            }

            if {$depth(bookinfo) > 0} {
                incr depth(bookinfo) -1
                puts $stdout "</bookinfo>"
            }
        }

        area - workgroup - keyword {
        }

        abstract {
            puts $stdout "<preface>"
            puts $stdout "<title>Abstract</title>"
        }

        note {
            if {![string compare [string tolower $attrs(title)] dedication]} {
                puts $stdout "<dedication>"
                return
            }

            if {$depth(note) > 0} {
                puts $stdout "<sect$depth(note)>"
            } else {
                puts $stdout "<preface>"
            }
            puts -nonewline $stdout "<title>"
            pcdata_sgml $attrs(title)
            puts $stdout "</title>"

            incr depth(note)
        }

        middle {
        }

        section {
            if {$depth(section) > 0} {
                puts -nonewline $stdout "<sect$depth(section)"
            } elseif {[lsearch0 $stack back] >= 0} {
                puts $stdout "<appendix"
            } else {
                puts -nonewline $stdout "<chapter"
            }
            if {[info exists attrs(anchor)]} {
                av_sgml id $attrs(anchor)
                av_sgml xreflabel $attrs(title)
            }
            puts $stdout ">"
            puts -nonewline $stdout "<title>"
            pcdata_sgml $attrs(title)
            puts $stdout "</title>"

            incr depth(section)
        }

        t {
            if {[info exists attrs(hangText)]} {
                puts -nonewline $stdout "<varlistentry><term>"
                pcdata_sgml $attrs(hangText)
                puts $stdout "</term>"
            }
            if {[lsearch0 $stack list] >= 0} {
                puts $stdout "<listitem>"
            }
            puts $stdout "<para>"
        }

        list {
            switch -- $attrs(style) {
                numbers {
                    puts $stdout "<orderedlist numeration=\"arabic\">"
                }

                symbols {
                    puts $stdout "<itemizedlist>"
                }

                hanging {
                    puts $stdout "<variablelist>"
                }

                default {
                    error "list style empty"
                }
            }

            incr depth(list)
        }

        figure {
# handled in artwork...
        }

        preamble {
            puts $stdout "<para>"
        }

        artwork {
            set figure [lindex [lindex $stack end-1] 1]
            array set fv $elem($figure)

            if {[info exists fv(title)]} {
                if {[info exists attrs(type)]} {
                    puts -nonewline $stdout "<example"
                } else {
                    puts -nonewline $stdout "<figure"
                }
                if {[info exists fv(anchor)]} {
                    av_sgml id $fv(anchor)
                    av_sgml xreflabel $fv(title)
                }
                puts $stdout ">"                
                puts -nonewline $stdout "<title>"
                pcdata_sgml $fv(title)
                puts $stdout "</title>"
            }

            if {[info exists attrs(type)]} {
                puts $stdout "<$attrs(type)>"
            } else {
                puts $stdout "<screen>"
            }
        }

        postamble {
            puts $stdout "<para>"
        }

        xref {
            if {[string compare $attrs(.PCDATA) ""]} {
                pcdata_sgml "$attrs(.PCDATA) "
            }
            puts -nonewline $stdout " <xref "
            av_sgml linkend $attrs(target)
            puts -nonewline $stdout ">"                
        }

        eref {
            if {[string compare $attrs(.PCDATA) ""]} {
                pcdata_sgml $attrs(.PCDATA)
                puts -nonewline $stdout " (<systemitem"
                av_sgml role $attrs(target)
                puts -nonewline $stdout "></systemitem>"
            } else {
                error "eref contains no pcdata"
            }
        }

        iref {
        }

        vspace {
        }

        back {
        }

        references {
            puts $stdout "<bibliography>"
            if {[info exists attrs(title)]} {
                puts -nonewline $stdout "<title>"
                pcdata_sgml $attrs(title)
                puts $stdout "</title>"
            } else {
                puts $stdout "<title>References</title>"
            }
        }

        reference {
            puts -nonewline $stdout "<biblioentry"
            if {[info exists attrs(anchor)]} {
                av_sgml id $attrs(anchor)
                av_sgml xreflabel $attrs(anchor)
            }
            puts $stdout ">"
        }

        seriesInfo {
            set reference [lindex [lindex $stack end-1] 1]
            array set rv $elem($reference)

            switch -- [set tag [string tolower $attrs(name)]] {
                isbn - issn {
                    puts $stdout "<$tag>$attrs(value)</$tag>"
                    if {[info exists rv(.ORGNAME)]} {
                        puts -nonewline $stdout "<publisher><publishername>"
                        pcdata_sgml $rv(.ORGNAME)
                        puts $stdout "</publishername></publisher>"
                    }
                }

                rfc {
                }

                internet-draft {
                }
            }
        }
    }
}

proc xml_end {name} {
    global counter depth elem elemN errorP passno stack stdout

    set frame [lindex $stack end]
    set stack [lreplace $stack end end]

    if {$passno == 1} {
        return
    }

    if {([lsearch -exact [list front abstract note section \
                               t list figure preamble postamble \
                               xref eref iref vspace back] $name] >= 0) \
            && ([lsearch0 $stack references] >= 0)} {
        return  
    }

    set elemX [lindex $frame 1]
    array set attrs $elem($elemX)

    switch -- $name {
        rfc {
            puts $stdout "</book>"
        }

        front {
            if {$depth(bookinfo) > 0} {
                incr depth(bookinfo) -1
                puts $stdout "</bookinfo>"
            }
        }

        title {
        }

        author {
        }

        date {
        }

        area - workgroup - keyword {
        }

        abstract {
            puts $stdout "</preface>"
        }

        note {
            if {![string compare [string tolower $attrs(title)] dedication]} {
                puts $stdout "</dedication>"
                return
            }

            incr depth(note) -1

            if {$depth(note) > 0} {
                puts $stdout "</sect$depth(note)>"
            } else {
                puts $stdout "</preface>"
            }
        }

        middle {
        }

        section {
            incr depth(section) -1

            if {$depth(section) > 0} {
                puts $stdout "</sect$depth(section)>"
            } elseif {[lsearch0 $stack back] >= 0} {
                puts $stdout "</appendix>"
            } else {
                puts $stdout "</chapter>"
            }
        }

        t {
            puts $stdout ""
            puts $stdout "</para>"
            if {[lsearch0 $stack list] >= 0} {
                puts $stdout "</listitem>"
            }
            if {[info exists attrs(hangText)]} {
                puts $stdout "</varlistentry>"
            }
        }

        list {
            incr depth(list) -1

            switch -- $attrs(style) {
                numbers {
                    puts $stdout "</orderedlist>"
                }

                symbols {
                    puts $stdout "</itemizedlist>"
                }

                hanging {
                    puts $stdout "</variablelist>"
                }

                default {
                }
            }
        }

        figure {
# handled in artwork...
        }

        preamble {
            puts $stdout ""
            puts $stdout "</para>"
        }

        artwork {
            set figure [lindex [lindex $stack end] 1]
            array set fv $elem($figure)

            if {[info exists attrs(type)]} {
                puts $stdout "</$attrs(type)>"
            } else {
                puts $stdout "</screen>"
            }
            if {[info exists fv(title)]} {
                if {[info exists attrs(type)]} {
                    puts -nonewline $stdout "</example>"
                } else {
                    puts -nonewline $stdout "</figure>"
                }
            }
        }

        postamble {
            puts $stdout ""
            puts $stdout "</para>"
        }

        xref {
        }

        eref {
        }

        iref {
        }

        vspace {
        }

        back {
        }

        references {
            puts $stdout "</bibliography>"
        }

        reference {
            puts $stdout "</biblioentry>"
        }

        seriesInfo {
        }
    }
}

proc xml_pcdata {text} {
    global counter depth elem elemN errorP passno stack stdout

    if {[string length [set chars [string trim $text]]] <= 0} {
        return
    }

    regsub -all "\r" $text "\n" text

    set frame [lindex $stack end]

    if {$passno == 1} {
        set elemX [lindex $frame 1]
        array set attrs $elem($elemX)
        if {[info exists attrs(.PCDATA)]} {
            append attrs(.PCDATA) $chars
            set elem($elemX) [array get attrs]
        }

        return
    }

    if {[lsearch0 $stack references] >= 0} {
        return
    }

    switch -- [lindex $frame 0] {
        artwork {
            set pre 1
        }

        t
            -
        preamble
            -
        postamble {
            set pre 0
        }

        default {
            return
        }
    }

    pcdata_sgml $text $pre
}

proc av_sgml {k v} {
    global counter depth elem elemN errorP passno stack stdout

    regsub -all {"} $v {\&quot;} v

    puts -nonewline $stdout " $k=\"$v\""
}

proc pcdata_sgml {text {pre 0}} {
    global counter depth elem elemN errorP passno stack stdout

    if {$pre} {
        puts $stdout $text
        return
    }

    foreach {ei begin end} [list *   <emphasis>        </emphasis> \
                                 '   <literal>         </literal>  \
                                 {"} <computeroutput>  </computeroutput>] {
        set body ""
        while {[set x [string first "|$ei" $text]] >= 0} {
            if {$x > 0} {
                append body [string range $text 0 [expr $x-1]]
            }
            append body "$begin"
            set text [string range $text [expr $x+2] end]
            if {[set x [string first "|" $text]] < 0} {
                error "missing close for |$ei"
            }
            if {$x > 0} {
                append body [string range $text 0 [expr $x-1]]
            }
            append body "$end"
            set text [string range $text [expr $x+1] end]
        }
        append body $text
        set text $body
    }

    regsub -all -nocase {&apos;} $text {'} text
    regsub -all -nocase {&quot;} $text {"} text
    regsub -all -nocase {&#151;} $text {\&mdash;} text

    puts -nonewline $stdout $text
}

proc lsearch0 {list exact} {
    set x 0
    foreach elem $list {
        if {![string compare [lindex $elem 0] $exact]} {
            return $x
        }
        incr x
    }

    return -1
}

proc find_element {name children} {
    global counter depth elemN elem passno stack xref

    set result ""
    foreach child $children {
        array set attrs $elem($child)

        if {![string compare $attrs(.NAME) $name]} {
            lappend result $child
        }
    }

    return $result
}

proc unexpected {args} {
    global errorP

    set text [join [lrange $args 1 end] " "]

    set errorP 1
    return -code error $text
}


#
# tclsh/wish linkage
#


global guiP
if {[info exists guiP]} {
    return
}
set guiP 0
if {![info exists tk_version]} {
    if {$tcl_interactive} {
        set guiP -1
        puts stdout ""
        puts stdout "invoke as \"xml2sgml input-file output-file\""
    }
} elseif {[llength $argv] > 0} {
    switch -- [llength $argv] {
        2 {
            set file [lindex $argv 1]
            if {![string compare $tcl_platform(platform) windows]} {
                set f ""
                foreach c [split $file ""] {
                    switch -- $c {
                        "\\" { append f "\\\\" }

                        "\a" { append f "\\a" }

                        "\b" { append f "\\b" }

                        "\f" { append f "\\f" }

                        "\n" { append f "\\n" }

                        "\r" { append f "\\r" }

                        "\v" { append f "\\v" }

                        default {
                            append f $c
                        }
                    }
                }
                set file $f
            }

            eval [file tail [file rootname [lindex $argv 0]]] $file
        }

        3 {
            xml2sgml [lindex $argv 1] [lindex $argv 2]
        }
    }

    exit 0
} else {
    set guiP 1

    proc convert {w} {
        if {![string compare [set input [.input.ent get]] ""]} {
            tk_dialog .error "xml2sgml: oops!" "no input filename specified" \
                      error 0 OK
            return
        }
        set output [.output.ent get]

        if {[catch { xml2sgml $input $output } result]} {
            tk_dialog .error "xml2sgml: oops!" $result error 0 OK
        }
    }

    proc fileDialog {w ent operation} {
        set input {
            {"XML files"                .xml                    }
            {"All files"                *                       }
        }
        set output {
            {"SGML files"               .sgml                   }
        }
        if {![string compare $operation "input"]} {
            set file [tk_getOpenFile -filetypes $input -parent $w]
        } else {
            if {[catch { set input [.input.ent get] }]} {
                set input Untitled
            } else {
                set input [file rootname $input]
            }
            set file [tk_getSaveFile -filetypes $output -parent $w \
                            -initialfile $input -defaultextension .txt]
        }
        if [string compare $file ""] {
            $ent delete 0 end
            $ent insert 0 $file
            $ent xview end
        }
    }

    eval destroy [winfo child .]

    wm title . xml2sgml
    wm iconname . xml2sgml
    wm geometry . +300+300

    label .msg -font "Helvetica 14" -wraplength 4i -justify left \
          -text "Convert XML (rfc2629) to SGML (docbook)"
    pack .msg -side top

    frame .buttons
    pack .buttons -side bottom -fill x -pady 2m
    pack \
        [button .buttons.code -text Convert -command "convert ."] \
        [button .buttons.dismiss -text Quit -command "destroy ."] \
        -side left -expand 1
    
    foreach i {input output} {
        set f [frame .$i]
        label $f.lab -text "Select $i file: " -anchor e -width 20
        entry $f.ent -width 20
        button $f.but -text "Browse ..." -command "fileDialog . $f.ent $i"
        pack $f.lab -side left
        pack $f.ent -side left -expand yes -fill x
        pack $f.but -side left
        pack $f -fill x -padx 1c -pady 3
    }
}
