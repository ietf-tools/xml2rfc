#!/bin/sh
# the following restarts using tclsh \
PATH=/usr/pkg/bin:/usr/local/bin:/usr/bin:/bin LD_LIBRARY_PATH=/usr/pkg/lib:/usr/local/lib:/usr/lib export PATH LD_LIBRARY_PATH; exec tclsh "$0" "$@"


#
# rfcmixer.tcl - mix RFCs
#
# (c) 1998-99 Invisible Worlds, Inc.
#

#
# create directories/files for use by the HTTP server
#
# retrieve rfc-index.txt from ftp.rfc-editor.org
#
#     store new .txt files in ../htdocs/public/rfc/txt/
#     create minimal .xml files in xml/minimal
#     make the fulltext indices
#
# for complete XML versions:
#
#     store new .xml files in ../htdocs/public/rfc/xml/
#     create .html files in ../htdocs/public/rfc/html/
#
# for all XML versions:
#
#     create biblio .xml files in ../htdocs/public/rfc/html/
#     store blocks versions under doc.rfc
#


if {[catch { 


if {$argc != 5} {
    error "expecting argc=5 (homeD bxxpD userN httpD loggingF)\nnot expecting $argc ($argv)"
}

global homeD bxxpD userN httpD

cd [set homeD [lindex $argv 0]]
set bxxpD [lindex $argv 1]
set userN [lindex $argv 2]
set httpD [lindex $argv 3]


global debugP

if {![info exists debugP]} {
    set debugP 0
}
if {($debugP < 2) && (![string compare $userN ""])} {
    error "must specify username for server at $bxxpD"
}


global auto_path

if {[lsearch -exact $auto_path $homeD/scripts] < 0} {
    lappend auto_path $homeD/scripts
}

package require csv
package require FTP   
package require http 2
package require beepcore::log   

global guiP
set guiP 0
set env(REQUEST_METHOD) ""
source ../etc/xml2rfc.tcl
# package require xml   

package require beepcore::util

if {[set blocksP [file exists scripts/mixer-subrs.tcl]]} {
    source scripts/mixer-subrs.tcl
} else {
proc make_readonly {logT file} {
    global tcl_platform

    if {[string compare $tcl_platform(platform) unix]} {
        return
    }

    if {[catch { file attributes $file -permissions \
                      [expr [file attributes $file -permissions]&0444] } \
               result]} {
        beepcore::log::entry $logT system $result
    }
}

namespace eval FTP {
    variable  ftp

    proc DisplayMsg {msg {state ""}} {
        global debugP
        global logT

        variable  ftp

        if {[info exists ftp(where)]} {
            append ftp(where) " "
        } else {
            set ftp(where) ""
        }
        if {![string compare $state error]} {
            beepcore::log::entry $logT error $ftp(what) $ftp(where)$msg
        } elseif {$debugP} {
            if {[string compare $state ""]} {
                set msg "$state $msg"
            }
            beepcore::log::entry $logT debug $ftp(what) $ftp(where)$msg
        }
    }

    proc What {what} {
        variable ftp

        set ftp(what) FTP::$what
    }

    proc Where {where} {
        variable ftp

        set ftp(where) FTP::$where
    }

    proc New {args} {
        global errorInfo
        variable ftp

        What Open
        Where [lindex $args 0]

        set errorInfo ""
        if {[catch { eval Open $args } result]} {
            catch { unset ftp }
            return 0
        }
        return $result
    }
}
}




# clean-up and exit

proc adios {status level args} {
    global debugP logT

    if {[string compare $level ""]} {
        eval beepcore::log::entry $logT $level $args
        puts stderr [join $args " "]
    }

    beepcore::log::entry $logT info end $status
    beepcore::log::fin $logT

    if {$debugP > 1} {
        puts stderr "exit $status"
        return
    }

    exit $status
}


# the rfc namespace for mixing

namespace eval rfc {
    variable rfc
    array set rfc { uid 0 }

    variable parser [xml::parser]

    variable context
    #              element       rewrite         beginF  endF
    set context { {rfc/0         ""              yes     yes}
                  {front/1       doc.front}
                  {title/2       doc.title}
                  {author/2      doc.author}
                  {organization/3}
                  {address/3}
                  {postal/4}
                  {street/5}
                  {city/5}
                  {region/5}
                  {code/5}
                  {country/5}
                  {phone/4}
                  {facsimile/4}
                  {email/4}
                  {uri/4}
                  {date/2        doc.date}
                  {area/2        doc.area}
                  {workgroup/2   doc.workgroup}
                  {keyword/2     doc.keyword}
                  {abstract/2    ""              yes     yes}
                  {note/2        ""              yes     yes}
                  {back/1        ""              yes     yes}
                  {seriesInfo/4  ""              yes     yes}
                }

    namespace export init fin args transform
}

proc rfc::init {logT} {
    variable rfc

    set token [namespace current]::[incr rfc(uid)]

    variable $token
    upvar 0 $token state

    array set state [list logT $logT]

    return $token
}

proc rfc::fin {token} {

    variable $token
    upvar 0 $token state

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}

proc rfc::args {} {
    global debugP userN

    set result ""
    if {$debugP > 1} {
        set result [concat $result -local true]
    }

    if {[string compare $userN ""]} {
        set result [concat $result -mechanism otp -username $userN \
                           -passback passback]
    }

    return $result
}

proc rfc::transform {token file serial} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set emptyA {}

    variable parser
    $parser configure \
            -elementstartcommand    "rfc::element_start $token" \
            -elementendcommand      "rfc::element_end   $token" \
            -characterdatacommand   "rfc::cdata         $token" \
            -entityreferencecommand ""                          \
            -errorcommand           "rfc::oops          $token" \
            -entityvariable         emptyA                      \
            -final                  yes                         \
            -reportempty            no

    set fd [open $file { RDONLY }]
    set data [beepcore::util::xml_norm [read $fd]]
    if {[catch { close $fd } result]} {
        beepcore::log::entry $logT system $result
    }

    set state(stack) ""
    set state(serial) $serial
    set state(relativeSize) [string length $data]
    set state(name) ""
    set state(body) ""
    set state(number) ""
    set state(obsoletes) ""
    set state(updates) ""
    set state(abstractP) 0
    set state(noteP) 0

    set code [catch { $parser parse $data } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result [list name $state(name) body $state(body)]
        }

        1 {
            if {[llength $state(stack)] > 0} {
                set text "File:    $file\nContext: "
                foreach frame $state(stack) {
                    append text "<[lindex $frame 0]>"
                }
                append result "\n\n$text"
            }
        }
    }

    unset state(stack) \
          state(serial) \
          state(relativeSize) \
          state(name) \
          state(body) \
          state(number) \
          state(obsoletes) \
          state(updates) \
          state(abstractP) \
          state(noteP) \

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc rfc::element_start {token name {av {}}} {
    variable $token
    upvar 0 $token state

    variable context

    set depth [llength $state(stack)]

    if {[set idx [lsearch -glob $context $name/$depth*]] >= 0} {
        set info [lindex $context $idx] 
        if {[string compare [lindex $info 0] $name/$depth]} {
            set idx -1
        }
    }

    if {$idx >= 0} {
        if {![string compare [lindex $info 2] yes]} {
            rfc::start_$name $token $av
        } else {
            if {![string compare [set elem [lindex $info 1]] ""]} {
                set elem $name
            }
            append state(body) "\n<$elem"
            foreach {n v} $av {
                append state(body) " $n=[beepcore::util::xml_av $v]"
            }
            append state(body) >
        }
    }

    lappend state(stack) [list $name $av $idx ""]
}

proc rfc::element_end {token name} {
    variable $token
    upvar 0 $token state

    variable context

    set frame [lindex $state(stack) end]
    set state(stack) [lreplace $state(stack) end end]

    if {[set idx [lindex $frame 2]] >= 0} {
        set info [lindex $context $idx]
        if {![string compare [lindex $info 3] yes]} {
            rfc::end_$name $token $frame
        } else {
            append state(body) [beepcore::util::xml_cdata [lindex $frame 3]]
            if {![string compare [set elem [lindex $info 1]] ""]} {
                set elem $name
            }
            append state(body) </$elem>
        }
    }
}

proc rfc::cdata {token text} {
    variable $token
    upvar 0 $token state

    if {[string length [string trim $text]] <= 0} {
        return
    }

    set frame [lindex $state(stack) end]
    if {[set idx [lindex $frame 2]] < 0} {
        return
    }

    regsub -all "\r" $text "\n" text

    set data [lindex $frame 3]
    append data $text

    set frame [lreplace $frame 3 3 $data]
    set state(stack) [lreplace $state(stack) end end $frame]
}

proc rfc::oops {token args} {
    variable $token
    upvar 0 $token state

    return -code error [join $args " "]
}

proc rfc::start_rfc {token av} {
    variable $token
    upvar 0 $token state

    array set rfc [list obsoletes "" updates "" category info seriesNo "" \
                        size 0]
    array set rfc $av
    if {[catch { set rfc(number) }]} {
        rfc::oops $token "missing number attribute in rfc element"
    }
    rfc::validate $token $rfc(number) "rfc element's number attribute"
    if {$rfc(size) == 0} {
        set rfc(size) $state(relativeSize)
    }

    set state(name) doc.rfc.$rfc(number)

    set state(body) "<rfc name=[beepcore::util::xml_av doc.rfc.$rfc(number)] serial=[beepcore::util::xml_av $state(serial)]>
<rfc.props relativeSize=[beepcore::util::xml_av $rfc(size)]"
    foreach n {number category} {
        if {![string compare [set v $rfc($n)] ""]} {
            continue
        }
        append state(body) " $n=[beepcore::util::xml_av $rfc($n)]"
    }
    append state(body) " />
<doc.props>"

    set state(number) $rfc(number)
    set state(obsoletes) $rfc(obsoletes)
    set state(updates) $rfc(updates)
    set state(abstractP) 0
    set state(noteP) 0
}

proc rfc::end_rfc {token frame} {
    global httpD

    variable $token
    upvar 0 $token state

    append state(body) "</doc.props>\n"

    set path public/rfc/html/rfc$state(number).html
    if {[file exists ../htdocs/$path]} {
        append state(body) \
               "<remote.props uri=[beepcore::util::xml_av http://$httpD/$path] />\n"
    }

    set path public/rfc/txt/rfc$state(number).txt
    if {[file exists ../htdocs/$path]} {
        append state(body) \
               "<remote.props uri=[beepcore::util::xml_av http://$httpD/$path] language=[beepcore::util::xml_av text] />\n"
    }

    append state(body) "</rfc>\n"
}

proc rfc::start_abstract {token av} {
    variable $token
    upvar 0 $token state

    set state(abstractP) 1
}

proc rfc::end_abstract {token frame} {
}

proc rfc::start_note {token av} {
    variable $token
    upvar 0 $token state

    set state(noteP) 1
}

proc rfc::end_note {token frame} {
}

proc rfc::start_back {token av} {
    variable $token
    upvar 0 $token state

    if {$state(abstractP) || $state(noteP)} {
        append state(body) "<doc.extras"
        foreach {k v} {abstract abstractP note noteP} {
            if {$state($v)} {
                set value true
            } else {
                set value false
            }
            append state(body) " $k=[beepcore::util::xml_av $value]"
        }
        append state(body) " />\n"
    }

    append state(body) "<doc.links>\n"
    foreach o [split $state(obsoletes) ,] {
        rfc::validate $token [set o [string trim $o]] \
                      "rfc element's obsolete attribute"
        append state(body) "<doc.obsoletes target=[beepcore::util::xml_av doc.rfc.$o] />\n"
    }
    foreach u [split $state(updates) ,] {
        rfc::validate $token [set u [string trim $u]] \
                      "rfc element's updates attribute"
        append state(body) "<doc.updates target=[beepcore::util::xml_av doc.rfc.$u] />\n"
    }
}

proc rfc::end_back {token frame} {
    variable $token
    upvar 0 $token state

    append state(body) "</doc.links>\n"
}

proc rfc::start_seriesInfo {token av} {
    variable $token
    upvar 0 $token state

# backwards compatibility...
    return

    array set series $av
    if {[catch { set series(name) }]} {
        rfc::oops $token "missing name attribute in series element"
    }
    if {[catch { set series(value) }]} {
        rfc::oops $token "missing number attribute in series element"
    }
}

proc rfc::end_seriesInfo {token frame} {
    variable $token
    upvar 0 $token state

# backwards compatibility...
    array set series [lindex $frame 1]
    if {([info exists series(name)]) && ([info exists series(number)])} {
        if {![string compare $series(name) RFC]} {
            rfc::validate $token [set r $series(value)] "RFC series value"
            append state(body) "<doc.references target=[beepcore::util::xml_av doc.rfc.$r] />\n"
        }
    } else {
        set data [string trim [lindex $frame 3]]
        if {[string match "RFC *" $data]} {
            rfc::validate $token [set r [string range $data 4 end]] \
                          "RFC seriesInfo"
            append state(body) "<doc.references target=[beepcore::util::xml_av doc.rfc.$r] />\n"
        }
    }
}

proc rfc::validate {token v s} {
    variable $token
    upvar 0 $token state

    if {![regexp -- {^[0-9]+$} $v]} {
        rfc::oops $token "$s should be numeric, not \"$v\""
    }
}


# indices stuff

proc be_do_get_rfc {} {
    global logT
    global rfcmtime

    catch { file delete -- [set newF data/rfc-index.new] }

    if {![FTP::New ftp.rfc-editor.org anonymous anonymous@[info hostname] \
                   -mode passive]} {
        return {}
    }

    FTP::What Type
    FTP::Type ascii

    FTP::What Get
    FTP::Where rfc-index.txt
    if {![FTP::Get in-notes/rfc-index.txt $newF]} {
        FTP::What Close
        FTP::Close

        return {}
    }

    array set rfc [parse_rfc_index $newF]

    if {[file exists data/rfc-index.xml]} {
        parse_rfc_index2 data/rfc-index.xml
    }

    set homeD [pwd]
    cd ../htdocs/public/rfc/txt
    set txtD [pwd]
    cd $homeD
    cd ../htdocs/public/rfc/bibxml
    set bibD [pwd]
    cd $homeD

    set copyP [file exists $txtD/rfc-index.txt]

    set createL ""
    set loseP 0
    foreach n [lsort -dictionary [array names rfc]] {
        if {($copyP) \
                && ([string first "(Format: PDF=" $rfc($n)] < 0) \
                && ([string first "(Not online)" $rfc($n)] < 0) \
                && (![file exists [set txt $txtD/rfc$n.txt]])} {
            FTP::What Get
            FTP::Where rfc$n.txt
            if {[FTP::Get in-notes/rfc$n.txt $txt]} {
                lappend createL $txt
                beepcore::log::entry $logT info created [file2uri $txt]
                make_readonly $logT $txt
            } else {
                set loseP 1
            }
        }

        if {![string compare [set body [parse_rfc_entry $n $rfc($n)]] ""]} {
            set loseP 1
            continue
        }

        if {([file exists xml/complete/rfc$n.xml]) \
                || ([file exists xml/partial/rfc$n.xml])} {
            continue
        }

        if {[file exists [set output xml/minimal/rfc$n.xml]]} {
            set data ""
            set fd ""
            if {[catch { set data [read [set fd [open $output { RDONLY }]]] } \
                       result]} {       
                beepcore::log::entry $logT system $result
            }
            if {([string compare $fd ""]) && ([catch { close $fd } result])} {
                beepcore::log::entry $logT system $result
            }
            if {![string compare $body $data]} {
                continue
            }
            catch { file delete -- $output }
            set action updated
        } else {
            set action created
        }

        if {[catch { set fd [open $output { WRONLY CREAT TRUNC }] } result]} {
            beepcore::log::entry $logT system $result
            continue
        }
        if {[set code [catch { puts -nonewline $fd $body ; flush $fd } result]]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info $action $output
        }
        if {[catch { close $fd } result]} {
            beepcore::log::entry $logT system $result
        }
    }

    if {([llength $createL] > 0) && $copyP} {
        catch { file delete -- $txtD/rfc-index.txt }

        if {[catch { file copy $newF $txtD/rfc-index.txt } result]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info created [file2uri $txtD/rfc-index.txt]
            make_readonly $logT $txtD/rfc-index.txt
        }
    }
    if {!$loseP} {
        if {[catch { file rename -force $newF data/rfc-index.txt } \
                   result]} {
            beepcore::log::entry $logT system $result
        }
    }

    FTP::What Close
    FTP::Close

    return $createL
}

proc parse_rfc_index {file} {
    global logT

    if {[catch { set fd [open $file { RDONLY }] } result]} {
        beepcore::log::entry $logT system $result
        return
    }

    set pos 0
    while {[gets $fd line] >= 0} {
        if {[string first "0001 Host Software." $line] == 0} {
            break
        }
        set pos [tell $fd]
    }
    if {[eof $fd]} {
        beepcore::log::entry $logT user "$file is malformed"
        catch { close $fd }
        return
    }
    seek $fd $pos start

    set state 0
    array set rfc ""
    while {[gets $fd line] >= 0} {
        set line [string trimright $line]
        switch -- $state {
            -1 {
                if {![string compare $line ""]} {
                    set state 0
                }
                continue
            }

            0 {
                if {![string compare $line ""]} {
                    continue
                }
                if {![regexp {^([0-9]+)([ ]+)(.*)} $line x number s rest]} {
                    beepcore::log::entry $logT user "[file tail $file] malformed"
                    break
                }
                set state 1
                set number [string trimleft $number 0]
                set rfc($number) [string trim $rest]
            }

            1 {
                if {![string compare $line ""]} {
                    set state 0
                } else {
                    append rfc($number) " " [string trim $line]
                }
            }
        }
    }

    if {[catch { close $fd } result]} {
        beepcore::log::entry $logT system $result     
    }

    foreach n [array names rfc] {
        if {[string first "Not Issued." $rfc($n)] == 0} {
            unset rfc($n)
        }
    }

    return [array get rfc]
}

proc parse_rfc_index2 {file} {
    global rfcabstracts

    array set rfcabstracts {}

    if {[catch { set fd [open $file { RDONLY }] } result]} {
        beepcore::log::entry $logT system $result
        return
    }

    set state 0
    while {[gets $fd line] >= 0} {
        if {[string first "</rfc-entry>" $line] >= 0} {
            set state 0
            continue
        }
        switch -- $state {
            0 {
                if {[string first "<rfc-entry>" $line] >= 0} {
                    set state 1
                }
            }

            1 {
                if {[set x [string first "<doc-id>RFC" $line]] >= 0} {
                    set state 2
                    set docid [string range $line [expr $x+11] end]
                    if {[set x [string first "<" $docid]] >= 1} {
                        set docid [string trimleft \
                                          [string range $docid 0 [expr $x-1]] \
                                          0]
                    } else {
                        set state 0
                    }
                }
            }

            2 {
                if {[set x [string first "<abstract>" $line]] >= 0} {
                    set state 0
                    set abstract [string range $line [expr $x+10] end]
                    if {[set x [string first "</abstract>" $abstract]] >= 1} {
                        set abstract [string range $abstract 0 [expr $x-1]]

                        set rfcabstracts($docid) [string trim $abstract]
                    }
                }       
            }
        }
    }

    if {[catch { close $fd } result]} {
        beepcore::log::entry $logT system $result     
    }
}

proc parse_rfc_entry {number entry} {
    global logT
    global rfcabstracts
    global rfcformats
    global rfcmtime

    if {![regexp {^(.*)\. \((.*)$} $entry x first last]} {
        beepcore::log::entry $logT user "rfc$number: initial parse failed"
        return ""
    }
    set last "($last"

    set first [string trimright $first]
    if {![string first "Conversations with S. Crocker (UCLA)" $first]} {
        set x [string first "." $first]
        set first [string replace $first $x $x "teve"]
    }
    if {![string first "Correction to BBN Report No. 1822 (NIC NO 7958)" \
                 $first]} {
        set x [string first "o." $first]
        set first [string replace $first $x [expr $x+1] "umber"]
    }
    if {![string first "An Agreement between the Internet Society and Sun Microsystems, Inc" \
                 $first]} {
        set x [string first "." $first]
        set first [string replace $first $x $x]
    }
    if {![string first "U.S. " $first]} {
        set first [string replace $first 0 3 "US"]
    }
    if {![string first "LDAPv2 Client vs. the Index Mesh" $first]} {
        set x [string first "." $first]
        set first [string replace $first $x $x]
    }
    if {![string first "An Agreement Between the Internet Society, the IETF, and Sun Microsystems, Inc. in the matter of NFS V.4 Protocols" \
                 $first]} {
        for {set y 0} {$y < 2} {incr y} {
            set x [string first "." $first]
            set first [string replace $first $x $x]
        }
    }
    if {![string first "RTP Payload Format for the 1998 Version of ITU-T Rec. H.263 Video (H.263+)" \
                 $first]} {
        for {set y 0} {$y < 3} {incr y} {
            set x [string first "." $first]
            set first [string replace $first $x $x]
        }
    }

    if {[set x [string first ". " $first]] < 0} {
        beepcore::log::entry $logT user \
                   "rfc$number: failed to split $first into title/authors+date"
        return ""
    }
    set title [string range $first 0 [expr $x-1]]

    if {[set x [string last ". " \
                       [set rest [string range $first [expr $x+1] end]]]] \
            < 0} {
        beepcore::log::entry $logT user \
                   "rfc$number: failed to split $rest into authors/date"
        return ""
    }
    set names [string trim [string range $rest 0 [expr $x-1]]]

    set date [string trim [string range $rest [expr $x+1] end]]
    set dotm 1
    if {[set x [string first "1 April " $date]] == 0} {
        set date April-01-[string trim [string range $date 8 end]]
    }
    if {[set x [string first " " $date]] > 0} {
        set day ""
        set month [string range $date 0 [expr $x-1]]
        set year [string range $date [expr $x+1] end]
    } elseif {[regexp {^(.*)-(.*)-(.*)$} $date x month day year]} {
        set dotm [string trimleft $day 0]
        set day " day=[beepcore::util::xml_av $dotm]"
    } elseif {[regexp {^(.*)-(.*)$} $date x month year]} {
        set day ""
    } else {
        beepcore::log::entry $logT user \
                   "rfc$number: failed to split $date into month/year"
        return ""
    }
    if {[set x [lsearch -exact [list Jan Feb Mar Apr May Jun \
                                     Jul Aug Sep Oct Nov Dec] $month]] >= 0} {
        set month [lindex [list January February March     \
                                April   May      June      \
                                July    August   September \
                                October November December] $x]
    }

    set raw $names
    foreach suffix [list ", et al." ", Ed." ", ed." ", Editors" ", Editor" \
                         ", Eds." " (Ed. of this version)" ", Chair" ", Jr." \
                         ", WG Chair" " (deceased)" \
                         " (Editor of this version)" ", 3rd" " 3rd" " II"] {
        while {[set x [string last $suffix $names]] > 0} {
            set tail  [string range $names [expr $x+[string length $suffix]] \
                              end]
            set names [string range $names 0 [expr $x-1]]$tail
        }
    }
    if {([set x [string last ", Ed" $names]] > 0) \
            && ([expr $x+4] == [string length $names])} {
        set names [string range $names 0 [expr $x-1]]
    }
    while {[set x [string first "St. " $names]] > 0} {
        set names [string replace $names [expr $x+3] [expr $x+3] "+"]
    }
    foreach k [list \
            "ACM SIGUCCS" \
            "EARN Staff" \
            "Federal Networking Council" \
            "Gateway Algorithms and Data Structures Task Force" \
            "Internet Architecture Board" \
            "Internet Assigned Numbers Authority" \
            "ISOC Board of Trustees" \
            "International Organization for Standardization" \
            "International Telegraph and Telephone Consultative Committee of the International Telecommunication Union" \
            "KOI8-U Working Group" \
            "National Bureau of Standards" \
            "National Research Council" \
            "North American Directory Forum" \
            "Sun Microsystems" \
            "Sun Microsystems, Inc." \
            "The Internet Society" \
            "The North American Directory Forum" \
            "Vietnamese Standardization Working Group" \
    ] {
        if {![string compare $names $k]} {
            set names [list $k]
            break
        }
    }
    foreach {k v} [list \
            "Internet Assigned Numbers Authority" "Internet Assigned Numbers Authority (IANA)" \
            "International Organization for Standardization" "International Organization for Standardization (ISO)" \
            "Internet Activities Board"      "Defense Advanced Research Projects Agency, Internet Activities Board" \
            "Internet Architecture Board"    "Internet Architecture Board, Internet Engineering Steering Group" \
            "National Science Foundation"    "National Science Foundation, Network Technical Advisory Group" \
            "NetBIOS Working Group"          "NetBIOS Working Group in the Defense Advanced Research Projects Agency, Internet Activities Board, End-to-End Services Task Force" \
            "RFC Editor"                     "RFC Editor, et al" \
            "SRI/Network Information Center" "Network Information Center. Stanford Research Institute" \
            "USC/Information Sciences Institute" "Information Sciences Institute University of Southern California" \
    ] {
        if {![string compare $names $v]} {
            set names [list $k]
            break
        }
    }

    if {[string compare $raw $names]} {
###     beepcore::log::entry $logT info oldnames $raw
###     beepcore::log::entry $logT info newnames $names
    }

    set authors ""
    if {([string first . $names] < 0) && ([string first & $names] < 0)} {
        lappend authors $names
    } else {
        regsub " & " $names ", " names
        foreach name [split $names ,] {
            if {![string compare [set name [string trim $name]] ""]} {
                continue
            }
            if {[set x [string last ". " $name]] > 0} {
                lappend authors [list [join [split [string range $name 0 $x] \
                                                   " "] ""] \
                                      [string range $name [expr $x+2] end]]
            } else {
                lappend authors [list $name]
            }
        }
    }
    set cooked {}
    foreach author $authors {
        if {![string compare $author "IAB, IESG"]} {
            lappend cooked IAB IESG
            continue
        }
        if {![string compare $author [list A. [list Lyman Chapin]]]} {
            set author [list "A.L." "Chapin" "A. Lyman Chapin"]
        }

        lappend cooked $author
    }
    set authors $cooked

    set obsoletes ""
    set updates ""
    set category ""
    set seriesNo ""
    set size 0
    set formats {}
    while {[string compare $last ""]} {
        if {[set x [string first ")" $last]] < 0} {
            beepcore::log::entry $logT user \
                       "rfc$number: failed to split $last into attributes"
            return
        }
        set attr [string range $last 1 [expr $x-1]]
        set last [string trim [string range $last [expr $x+1] end]]

        if {[set x [string first " " $attr]] < 0} {
            beepcore::log::entry $logT user \
                       "rfc$number: failed to split $attr into keyword/value"
            return
        }
        set key [string range $attr 0 [expr $x-1]]
        set value [string trim [string range $attr [expr $x+1] end]]
        switch -- $key {
            Also {
                foreach memo [string trim $value ,] {
                    switch -glob -- [set memo [string trim $memo]] {
                        BCP*
                            -
                        FYI*
                            -
                        STD* {
                            set seriesNo [string range $memo 3 end]
                            set seriesNo [string trim $seriesNo]
                            set seriesNo [string trimleft $seriesNo 0]
                        }
                    }
                    if {[string compare $seriesNo ""]} {
                        break
                    }
                }
            }

            Format: {
                foreach instance [split $value ","] {
                    set instance [string trim $instance]
                    if {[regexp {(.*)=([0-9]+)} $instance x type \
                                octets]} {
                        set format [list type $type octets $octets]
                        if {![string compare $type TXT]} {
                            set size $octets
                        }
                        lappend format target \
                                http://www.rfc-editor.org/rfc/rfc$number.[string tolower $type]
                        lappend formats $format
                    }
                }
            }

            Status: {
                switch -- $value {
                    "BEST CURRENT PRACTICE" {
                        set category bcp
                    }

#                    "DRAFT STANDARD"
#                        -
                    "PROPOSED STANDARD"
                        -
                    "INTERNET STANDARD"
                        -
                    "STANDARDS TRACK" {
                        set category std
                    }

                    "EXPERIMENTAL" {
                        set category exp
                    }

                    "HISTORIC" {
                        set category historic
                    }

                    "INFORMATIONAL" {
                        set category info
                    }
                }
            }

            Obsoletes
                -
            Updates {
                if {[string compare $key Obsoletes]} {
                    set v updates
                } else {
                    set v obsoletes
                }
                set s ""
                set skipP 0
                foreach memo [split $value ,] {
                    if {$skipP} {
                        set skipP 0
                        continue
                    }
                    if {![string first RFC [set memo [string trim $memo]]]} {
                        set m [string range $memo 3 end]
                    } elseif {![string first NIC $memo]} {
                        set skipP 1
                        continue
                    } elseif {![regexp {^([0-9]+)$} $memo x m]} {
                        continue
                    }
                    append $v $s [string trimleft $m 0]
                    set s ", "
                }
            }
        }
    }

    set stamp [clock format [clock seconds] -format "on %D at %T"]
    set body "<?xml version=[beepcore::util::xml_av 1.0] encoding=[beepcore::util::xml_av UTF-8]?>
<!DOCTYPE rfc SYSTEM [beepcore::util::xml_av rfc2629.dtd]>

<!--
    XML synopsis of RFC based on rfc-index.txt

    Canonical version of this document is at:
        http://www.rfc-editor.org/rfc/rfc$number.txt

    Implementors should verify all content with the canonical version.
    Failure to do so may result in protocol failures.
  -->

<rfc number=[beepcore::util::xml_av $number]"
    foreach k {obsoletes updates category seriesNo size} {
        if {[string compare [set v [set $k]] ""]} {
            append body " $k=[beepcore::util::xml_av $v]"
        }
    }
    append body ">
<front>\n\n<title>[beepcore::util::xml_cdata $title]</title>
"
    foreach author $authors {
        if {![string compare $author Mitra]} {
            set author [list "" $author $author]
        }
        if {[llength $author] != 1} {
            set initials [join [split [lindex $author 0] " "] ""]
            regsub -all "\[ \]+" \
                   [join [split [join [split [lindex $author 1] "+"] " "] "."] ". "] \
                   " " surname
            if {[llength $author] == 2} {
                set fullname "$initials $surname"
            } else {
                set fullname [lindex $author 2]
            }
            append body "\n<author initials=[beepcore::util::xml_av $initials] surname=[beepcore::util::xml_av $surname] fullname=[beepcore::util::xml_av $fullname]>
    <organization />
</author>
"
        } else {
            append body "<author>
    <organization>[beepcore::util::xml_cdata [lindex $author 0]]</organization>
</author>
"
        }
    }
    append body "
<date month=[beepcore::util::xml_av $month]$day year=[beepcore::util::xml_av $year] />"

    if {![catch { set rfcabstracts($number) } description]} {
        regsub -all -- {<p>} [string trim $description] {<t>} description
        regsub -all -- {</p>} $description {</t>} description
        if {[string range $description 0 2] == "<t>"} {
            set description [string range $description 3 end]
        }
        if {[string range $description end-3 end] == "</t>"} {
            set description [string range $description 0 end-4]
        }

        append body "
<abstract><t>[beepcore::util::xml_cdata $description]</t></abstract>"
    } else {
        set description ""
    }

    append body "
</front>

<middle><section title="
    append body [beepcore::util::xml_av "not available"]
    append body "/></middle>
</rfc>
"
    set rfcformats($number) $formats

    return $body
}


proc be_do_get_id {} {
    global logT

    catch { file delete -- [set newF data/1id-abstracts.new] }

#    if {![FTP::New ftp.ietf.org anonymous anonymous@[info hostname] \
#                   -mode passive]} {
#        return
#    }
#
#    FTP::What Type
#    FTP::Type ascii
#
#    FTP::What Get
#    FTP::Where 1id-abstracts.txt
#    if {![FTP::Get internet-drafts/1id-abstracts.txt $newF]} {
#        FTP::What Close
#        FTP::Close
#
#        return
#    }
#
#    FTP::What Close
#    FTP::Close

    set fd ""
    set code [catch {
        set httpT [http::geturl http://www.ietf.org/id/1id-abstracts.txt]
        set fd [open $newF { WRONLY CREAT TRUNC }]
        puts -nonewline $fd [set body [http::data $httpT]]
        close $fd
    } result]
    catch { http::cleanup $httpT }
    if {$code} {
        catch { file delete -- $newF }
        catch { close $fd }
        return
    }



    array set id [parse_id_index $newF]

    set homeD [pwd]
    cd ../htdocs/public/rfc/bibxml3
    set bibD [pwd]
    cd $homeD

    set hitP 0
    set then [expr [clock seconds]-(182*24*60*60)]

    if {[catch { exec find $bibD -name "reference.*.xml" -mtime +182 -print } \
               files]} {
        beepcore::log::entry $logT user "find: $result"
        set files {}
    }
### don't delete info on I-Ds that should have expired...
    set files {}
    foreach file $files {
        if {[catch { file delete -- $file } result]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info deleted $file
            set hitP 1
        }
    }

    set loseP 0
    foreach docName [lsort -dictionary [array names id]] {
        set itemN [llength [set items [split $docName -]]]
        set anchor [join [lrange $items 1 [expr $itemN-2]] -]
        if {![string compare $anchor ""]} {
            beepcore::log::entry $logT user "invalid I-D entry: $id($docName)"
            set loseP 1
            continue
        }
        set anchor I-D.$anchor

        array set info [parse_id_entry $docName $anchor $id($docName)]
        if {![string compare $info(body) ""]} {
            set loseP 1
            continue
        }

        if {$info(mtime) <= $then} {
### don't delete info on I-Ds that should have expired...
#           beepcore::log::entry $logT info expired $docName
#           continue
        }

# create both a generic and an version-specific file...
    foreach file [list $bibD/reference.$anchor.xml \
                       $bibD/reference.I-D.$docName.xml] {
        if {[file exists $file]} {
            set data ""
            set fd ""
            if {[catch { set data [read [set fd [open $file { RDONLY }]]] } \
                       result]} {       
                beepcore::log::entry $logT system $result
            }
            if {([string compare $fd ""]) && ([catch { close $fd } result])} {
                beepcore::log::entry $logT system $result
            }
            if {![string compare $info(body) $data]} {
                continue
            }
            catch { file delete -- $file }
            set action updated
        } else {
            set action created
        }

        if {[catch { set fd [open $file { WRONLY CREAT TRUNC }] } result]} {
            beepcore::log::entry $logT system $result
            continue
        }

        if {[catch { puts -nonewline $fd $info(body) ; flush $fd } result]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info $action $file
        }

        if {[catch { close $fd } result]} {
            beepcore::log::entry $logT system $result
        }

        make_readonly $logT $file
        if {[catch { file mtime $file $info(mtime) } result]} {
            beepcore::log::entry $logT system $result
        }
    }

        set item $bibD/rdf/item.$anchor.rdf

        catch { file delete -- $item }

        if {[catch { set fd [open $item { WRONLY CREAT TRUNC }] } result]} {
            beepcore::log::entry $logT system $result
            continue
        }

        if {[catch { puts -nonewline $fd $info(item) ; flush $fd } result]} {
            beepcore::log::entry $logT system $result
        }

        if {[catch { close $fd } result]} {
            beepcore::log::entry $logT system $result
        }

        make_readonly $logT $item
        if {0 && ([catch { file mtime $item $info(mtime) } result])} {
            beepcore::log::entry $logT system $result
        }

        set hitP 1
    }
    if {$hitP} {
        if {([file exists $bibD/browse.html]) \
                && ([catch { file mtime $bibD/browse.html $then } result])} {
            beepcore::log::entry $logT system $result
        }
    }
    if {!$loseP} {
        if {[catch { file rename -force $newF data/1id-abstracts.txt } \
                   result]} {
            beepcore::log::entry $logT system $result
        }
    }
}

proc parse_id_index {file} {
    global logT
    global idexts
    global idabstract

    if {[catch { set fd [open $file { RDONLY }] } result]} {
        beepcore::log::entry $logT system $result
        return
    }

    set pos 0
    while {[gets $fd line] >= 0} {
        if {[string first "----" $line] == 0} {
            set pos [tell $fd]
            break
        }
    }
    if {[eof $fd]} {
        beepcore::log::entry $logT user "$file is malformed"
        catch { close $fd }
        return
    }
    seek $fd $pos start

    set state 0
    array set id {}
    set entry ""
    set abstract ""
    while {[gets $fd line] >= 0} {
        switch -- $state {
            0 {
                if {[string first "  \"" $line]} {
                    continue
                }
                set state 1
                set entry [string range $line 2 end]
            }

            1 {
                if {![string compare "" $line]} {
                    set state 2
                } else {
                    append entry " " [string trim $line]
                }
            }

            2 {
                if {![string compare "" $line]} {
                    if {([set x [string last ".txt" $entry]] <= 0) \
                            || ([set y [string last ">" $entry]] < $x)} {
                        beepcore::log::entry $logT user "[file tail $file] malformed(1)"
                        beepcore::log::entry $logT user "entry: $entry"
                        set state 0
                        set entry ""
                        set abstract ""
                        continue
                    }
                    set exts [string range $entry [expr $x+1] [expr $y-1]]
                    set entry [string replace $entry $x $y]
                    if {[set x [string first "\", " $entry]] <= 0} {
                        beepcore::log::entry $logT user "[file tail $file] malformed(2)"
                        beepcore::log::entry $logT user "entry: $entry"
                        set state 0
                        set entry ""
                        set abstract ""
                        continue
                    }
                    set items [split [string range $entry [expr $x+3] end] ","]
                    set docName [string trim \
                                        [string range [lindex $items end] \
                                                2 end]]
                    if {[string first "<" $docName] == 0} {
                        set docName [string range $docName 1 end]
                    }
                    set id($docName) $entry
                    set idexts($docName) [join [split $exts ","] ""]
                    set idabstract($docName) [string trim $abstract]

                    set state 0
                    set entry ""
                    set abstract ""
                } else {
                    append abstract " " [string trim $line]
                }
            }
        }
    }

    if {[catch { close $fd } result]} {
        beepcore::log::entry $logT system $result     
    }

    return [array get id]
}

proc parse_id_entry {docName anchor entry} {
    global logT
    global idexts
    global idabstract

    set x [string first "\", " $entry]
    set title [string trim [string range $entry 1 [expr $x-1]]]
    set entry [string range $entry [expr $x+3] end]

    set items [lreplace [split $entry ","] end end]

    set mtime [clock scan [lindex $items end] -base [clock seconds]]
    set day [string trimleft [clock format $mtime -format %e]]
    set month [clock format $mtime -format %B]
    set year [clock format $mtime -format %Y]
    set items [lreplace $items end end]

    set body "<?xml version=[beepcore::util::xml_av 1.0] encoding=[beepcore::util::xml_av UTF-8]?>

<reference anchor=[beepcore::util::xml_av $anchor]>
<front>
<title>[beepcore::util::xml_cdata $title]</title>
"
    set tsuffix ""
    set s ""
    foreach author $items {
        if {![string compare [set author [cleanauth $author]] ""]} {
            continue
        }
        set x [string last " " $author]
        set initials [string range $author 0 0]
        set surname [string trimleft [string range $author [expr $x+1] end]]

        append body "\n<author initials=[beepcore::util::xml_av $initials] surname=[beepcore::util::xml_av $surname] fullname=[beepcore::util::xml_av $author]>
    <organization />
</author>
"

        append tsuffix $s $author
        set s ", "
    }
    append body "
<date month=[beepcore::util::xml_av $month] day=[beepcore::util::xml_av $day] year=[beepcore::util::xml_av $year] />
"

    if {[string compare $idabstract($docName) ""]} {
        append body "
<abstract><t>[beepcore::util::xml_cdata $idabstract($docName)]</t></abstract>
"
    }

    append body "
</front>

<seriesInfo name=[beepcore::util::xml_av Internet-Draft] value=[beepcore::util::xml_av $docName] />
"

    set url ""
    foreach ext [split $idexts($docName) "."] {
        set url http://www.ietf.org/internet-drafts/$docName.$ext
        append body \
               "<format type=[beepcore::util::xml_av [string toupper $ext]]
        target=[beepcore::util::xml_av $url] />
"
    }

    append body "</reference>
"

    if {[string compare $tsuffix ""]} {
        set title "\"$title\", $tsuffix"
    }
    set item "
<item rdf:about=[beepcore::util::xml_av $url]>
    <title>[beepcore::util::xml_cdata $title]</title>
    <link>[beepcore::util::xml_cdata $url]</link>
    <description>[beepcore::util::xml_cdata $idabstract($docName)]</description>
    <dc:date>[beepcore::util::xml_cdata [clock format $mtime -format %Y-%m-%dT%T-00:00 -gmt true]]</dc:date>
</item>
"

    return [list body $body mtime $mtime item $item]
}

proc be_do_get_w3c {} {
    global logT

    catch { file delete -- [set newF data/tr.new] }

    set fd ""
    set code [catch {
        set httpT [http::geturl http://www.w3.org/2002/01/tr-automation/tr.rdf]
        set fd [open $newF { WRONLY CREAT TRUNC }]
        puts -nonewline $fd [set body [http::data $httpT]]
        close $fd
    } result]
    catch { http::cleanup $httpT }
    if {$code} {
        catch { file delete -- $newF }
        catch { close $fd }
        return
    }

    set rfcT [rfc::init $logT]
    if {[catch { array set w3c [rfc::parse_w3c_index $rfcT $newF $body] } \
               result]} {
        beepcore::log::entry $logT error $result

        return
    }
    rfc::fin $rfcT

    set homeD [pwd]
    cd ../htdocs/public/rfc/bibxml4
    set bibD [pwd]
    cd $homeD

    set hitP 0
    set then [expr [clock seconds]-(182*24*60*60)]

    set loseP 0
    foreach docName [lsort -dictionary [array names w3c]] {
        set anchor W3C.$docName

        array set info $w3c($docName)
        if {![string compare $info(type)$info(dc:title)$info(dc:date) ""]} {
            set loseP 1
            continue
        }

        set file $bibD/reference.$anchor.xml
        set item $bibD/rdf/item.$anchor.rdf

        set body "<?xml version=[beepcore::util::xml_av 1.0] encoding=[beepcore::util::xml_av UTF-8]?>

<reference anchor=[beepcore::util::xml_av $anchor]
           target=[beepcore::util::xml_av $info(rdf:about)]>
<front>
<title>[beepcore::util::xml_cdata [lindex $info(dc:title) 0]]</title>
"
        set tsuffix ""
        set s ""
        foreach author $info(contact:fullName) {
            if {![string compare [set author [cleanauth $author]] ""]} {
                continue
            }
            set x [string last " " $author]
            set initials [string range $author 0 0]
            set surname [string trimleft [string range $author [expr $x+1] end]]

        append body "\n<author initials=[beepcore::util::xml_av $initials.] surname=[beepcore::util::xml_av $surname] fullname=[beepcore::util::xml_av $author]>
    <organization />
</author>
"

            append tsuffix $s $author
            set s ", "
        }
        set mtime [clock scan [lindex $info(dc:date) 0] \
                         -base [clock seconds]]
        set day [string trimleft [clock format $mtime -format %e]]
        set month [clock format $mtime -format %B]
        set year [clock format $mtime -format %Y]
        set type "World Wide Web Consortium "
        switch -- $info(type) {
            REC { append type "Recommendation" }
            default { append type $info(type) }
        }
        set v $info(rdf:about)
        if {[set x [string last "/" $v]] >= 0} {
            set v [string range $v [expr $x+1] end]
        }
        append body "
<date month=[beepcore::util::xml_av $month] day=[beepcore::util::xml_av $day] year=[beepcore::util::xml_av $year] />
</front>

<seriesInfo name=[beepcore::util::xml_av $type] value=[beepcore::util::xml_av $v] />
<format type=[beepcore::util::xml_av HTML] target=[beepcore::util::xml_av $info(rdf:about)] />
</reference>
"

        if {[file exists $file]} {
            set data ""
            set fd ""
            if {[catch { set data [read [set fd [open $file { RDONLY }]]] } \
                       result]} {       
                beepcore::log::entry $logT system $result
            }
            if {([string compare $fd ""]) && ([catch { close $fd } result])} {
                beepcore::log::entry $logT system $result
            }
            if {![string compare $body $data]} {
                continue
            }
# continue
            catch { file delete -- $file }
            set action updated
        } else {
            set action created
        }

        if {[catch { set fd [open $file { WRONLY CREAT TRUNC }] } result]} {
            beepcore::log::entry $logT system $result
            continue
        }

        if {[catch { puts -nonewline $fd $body ; flush $fd } result]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info $action $file
        }

        if {[catch { close $fd } result]} {
            beepcore::log::entry $logT system $result
        }

        make_readonly $logT $file
        if {[catch { file mtime $file $mtime } result]} {
            beepcore::log::entry $logT system $result
        }

        set title [lindex $info(dc:title) 0]
        if {[string compare $tsuffix ""]} {
            set title "\"$title\", $tsuffix"
        }
        set body "
<item rdf:about=[beepcore::util::xml_av $info(rdf:about)]>
    <title>[beepcore::util::xml_cdata $title]</title>
    <link>[beepcore::util::xml_cdata $info(rdf:about)]</link>
    <dc:date>[beepcore::util::xml_cdata [clock format $mtime -format %Y-%m-%dT%T-00:00 -gmt true]]</dc:date>
</item>
"

        catch { file delete -- $item }

        if {[catch { set fd [open $item { WRONLY CREAT TRUNC }] } result]} {
            beepcore::log::entry $logT system $result
            continue
        }

        if {[catch { puts -nonewline $fd $body ; flush $fd } result]} {
            beepcore::log::entry $logT system $result
        }

        if {[catch { close $fd } result]} {
            beepcore::log::entry $logT system $result
        }

        make_readonly $logT $item
        if {0 && ([catch { file mtime $item $mtime } result])} {
            beepcore::log::entry $logT system $result
        }

        set hitP 1
    }
    if {$hitP} {
        if {([file exists $bibD/browse.html]) \
                && ([catch { file mtime $bibD/browse.html $then } result])} {
            beepcore::log::entry $logT system $result
        }
    }
    if {!$loseP} {
        if {[catch { file rename -force $newF data/tr.rdf } result]} {
            beepcore::log::entry $logT system $result
        }
    }
}

proc rfc::parse_w3c_index {token file data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set emptyA {}

    variable parser
    $parser configure \
            -elementstartcommand    "rfc::w3c_element_start $token" \
            -elementendcommand      "rfc::w3c_element_end   $token" \
            -characterdatacommand   "rfc::w3c_cdata         $token" \
            -entityreferencecommand ""                              \
            -errorcommand           "rfc::oops              $token" \
            -entityvariable         emptyA                          \
            -final                  yes                             \
            -reportempty            no


    set data [beepcore::util::xml_norm $data]

    set state(stack) ""
    set state(docs) {}

    set code [catch { $parser parse $data } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result $state(docs)
        }

        1 {
            if {[llength $state(stack)] > 0} {
                set text "File:    $file\nContext: "
                foreach frame $state(stack) {
                    append text "<[lindex $frame 0]>"
                }
                append result "\n\n$text"
            }
        }
    }

    unset state(stack) \
          state(docs)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc rfc::w3c_element_start {token name {av {}}} {
    variable $token
    upvar 0 $token state

    set depth [llength $state(stack)]

    switch -- $depth/$name {
        1/CR -
        1/NOTE -
        1/PR -
        1/REC -
        1/WD -
        1/FirstEdition -
        1/LastCall {
            set onoff -1
        }

        2/dc:date -
        2/dc:title - 
        3/contact:fullName {
            set onoff 1
        }

        default {
            if {$depth == 1} {
            }
            set onoff 0
        }
    }

    lappend state(stack) [list $name $av $onoff ""]
}

proc rfc::w3c_element_end {token name} {
    variable $token
    upvar 0 $token state

    set frame [lindex $state(stack) end]
    set state(stack) [lreplace $state(stack) end end]

    switch -- [set depth [llength $state(stack)]] {
        1 {
            if {[lindex $frame 2] < 0} {
                array set av [lindex $frame 1]
                set av(type) $name
                if {[set x [string last "/" $av(rdf:about)]] \
                            == [expr [string length $av(rdf:about)]-1]} {
                    set av(rdf:about) [string range $av(rdf:about) 0 end-1]
                }
                if {([set x [string last "/" $av(rdf:about)]] > 0) \
                        && ([string last "-" $av(rdf:about)] > $x)} {
                    lappend state(docs) \
                               [string range $av(rdf:about) [expr $x+1] end] \
                               [array get av]
                }
            }
        }

        2 - 3 {
            if {[lindex $frame 2] > 0} {
                set parent [lindex $state(stack) 1]
                array set av [lindex $parent 1]
                lappend av($name) [lindex $frame 3]
                set parent [lreplace $parent 1 1 [array get av]]
                set state(stack) [lreplace $state(stack) 1 1 $parent]
            }
        }

        default {
        }
    }
}

proc rfc::w3c_cdata {token text} {
    variable $token
    upvar 0 $token state

    if {[string length [string trim $text]] <= 0} {
        return
    }

    set frame [lindex $state(stack) end]
    if {[lindex $frame 2] <= 0} {
        return
    }

    regsub -all "\r" $text "\n" text

    set data [lindex $frame 3]
    append data $text

    set frame [lreplace $frame 3 3 $data]
    set state(stack) [lreplace $state(stack) end end $frame]
}


proc be_do_get_3gpp {} {
    global logT

    catch { file delete -- [set newF data/3gpp.new] }

    set fd ""
    set code [catch {
        set httpT [http::geturl \
                         http://www.3gpp.org/ftp/Specs/html-info/2003-04-10_webexp11a_status-report_special_select.txt]
        set fd [open $newF { WRONLY CREAT TRUNC }]
        puts -nonewline $fd [set body [http::data $httpT]]
        close $fd
    } result]
    catch { http::cleanup $httpT }
    if {$code} {
        catch { file delete -- $newF }
        catch { close $fd }
        return
    }

    array set docs [parse_3gpp_index $newF]

    set homeD [pwd]
    cd ../htdocs/public/rfc/bibxml5
    set bibD [pwd]
    cd $homeD

    set hitP 0
    set then [expr [clock seconds]-(182*24*60*60)]

    set loseP 0
    foreach docName [lsort -dictionary [array names docs]] {
        # set anchor 3GPP.$docName
        foreach anchor [list 3GPP.$docName SDO-3GPP.$docName] {

            array set info [parse_3gpp_entry $anchor $docs($docName)]
            if {![string compare $info(body) ""]} {
		set loseP 1
		continue
	    }

            set file $bibD/reference.$anchor.xml
            set item $bibD/rdf/item.$anchor.rdf

            if {[file exists $file]} {
                set data ""
                set fd ""
                if {[catch { set data [read [set fd [open $file { RDONLY }]]] } \
                       result]} {       
                    beepcore::log::entry $logT system $result
                }
                if {([string compare $fd ""]) && ([catch { close $fd } result])} {
                    beepcore::log::entry $logT system $result
                }
                if {![string compare $info(body) $data]} {
                    continue
                }
                catch { file delete -- $file }
                set action updated
            } else {
                set action created
            }

            if {[catch { set fd [open $file { WRONLY CREAT TRUNC }] } result]} {
                beepcore::log::entry $logT system $result
                continue
            }

            if {[catch { puts -nonewline $fd $info(body) ; flush $fd } result]} {
                beepcore::log::entry $logT system $result
            } else {
                beepcore::log::entry $logT info $action $file
            }

            if {[catch { close $fd } result]} {
                beepcore::log::entry $logT system $result
            }

            make_readonly $logT $file
            if {[catch { file mtime $file $info(mtime) } result]} {
                beepcore::log::entry $logT system $result
            }

            catch { file delete -- $item }

            if {[catch { set fd [open $item { WRONLY CREAT TRUNC }] } result]} {
                beepcore::log::entry $logT system $result
                continue
            }

            if {[catch { puts -nonewline $fd $info(item) ; flush $fd } result]} {
                beepcore::log::entry $logT system $result
            }

            if {[catch { close $fd } result]} {
                beepcore::log::entry $logT system $result
            }

            make_readonly $logT $item
            if {0 && ([catch { file mtime $item $info(mtime) } result])} {
                beepcore::log::entry $logT system $result
            }

            set hitP 1
        }
    }
    if {$hitP} {
        if {([file exists $bibD/browse.html]) \
                && ([catch { file mtime $bibD/browse.html $then } result])} {
            beepcore::log::entry $logT system $result
        }
    }
    if {!$loseP} {
        if {[catch { file rename -force $newF data/3gpp.csv } result]} {
            beepcore::log::entry $logT system $result
        }
    }
}

proc parse_3gpp_index {file} {
    global logT
    global idexts

    if {[catch { set fd [open $file { RDONLY }] } result]} {
        beepcore::log::entry $logT system $result
        return
    }

    array set docs {}
    set firstP 1
    while {[gets $fd line] >= 0} {
        set fields [::csv::split $line "~"]
        if {$firstP} {
            if {[set statrepspec \
                     [lsearch -exact [set headers $fields] statrepspec]] < 0} {
                beepcore::log::entry $logT error \
                                     "no statrepspec column in header"
                return
            }
            set statrepavailable [lsearch -exact $headers statrepavailable]
            set firstP 0
        } else {
            if {![string compare [lindex $fields $statrepavailable] "\""]} {
                continue
            }
            set docName [lindex $fields $statrepspec]
            set entry {}
            foreach k $headers v $fields {
                lappend entry $k $v
            }
            set docs($docName) $entry
        }
    }

    if {[catch { close $fd } result]} {
        beepcore::log::entry $logT system $result     
    }

    return [array get docs]
}

proc parse_3gpp_entry {anchor entry} {
    global logT

    array set kv $entry

    set title $kv(statreptitle)
    if {[scan [set date $kv(statrepavailable)] %d/%d/%d d m y] == 3} {
        set date $m/$d/$y
    }
    if {[catch { set mtime [clock scan $date] } result]} {
        beepcore::log::entry $logT user \
                             "unable to scan '$kv(statrepavailable)'"
        set mtime [clock seconds]
    }
    set year [clock format $mtime -format "%Y"]
    set month [clock format $mtime -format "%B"]
    set day [clock format $mtime -format "%d"]
    set sName "3GPP $kv(statreptype)"
    set sValue "$kv(statrepspec) $kv(statrepvers)"
    set target http://www.3gpp.org/ftp/Specs/html-info/$kv(statrepwebpage)

    set body "<?xml version=[beepcore::util::xml_av 1.0] encoding=[beepcore::util::xml_av UTF-8]?>

<reference anchor=[beepcore::util::xml_av $anchor]>
<front>
<title>[beepcore::util::xml_cdata $title]</title>
<author><organization>3GPP</organization></author>
<date day=[beepcore::util::xml_av $day] month=[beepcore::util::xml_av $month] year=[beepcore::util::xml_av $year] />
</front>

<seriesInfo name=[beepcore::util::xml_av $sName] value=[beepcore::util::xml_av $sValue] />
<format type=[beepcore::util::xml_av HTML] target=[beepcore::util::xml_av $target] />
</reference>
"
    set item "
<item rdf:about=[beepcore::util::xml_av $target]>
    <title>[beepcore::util::xml_cdata $title]</title>
    <link>[beepcore::util::xml_cdata $target]</link>
    <description />
    <dc:date>[beepcore::util::xml_cdata [clock format $mtime -format %Y-%m-%dT%T-00:00 -gmt true]]</dc:date>
</item>
"

    return [list body $body mtime $mtime item $item]
}


proc cleanauth {author} {
    set len [string length [set author [string trim $author]]]
    if {![string compare $author "Intellectual Property"]} {
        return ""
    }
    if {[set x [string last " Jr." $author]] == [expr $len-4]} {
        set author [string trimright [string range $author 0 $x]]
    }
    return $author
}

proc file2uri {file} {
    global httpD

    if {([set x [string first [set s htdocs/] $file]] < 0) \
            && ([set x [string first [set s web/] $file]] < 0)} {
        return $file
    }
    return http://$httpD[string range $file [expr $x+[string length $s]-1] end]
}


proc sortmtimes {a b} {
    global mtimes

    set diff [expr $mtimes($b)-$mtimes($a)]
    if {$diff != 0} {
        return $diff
    }
    return [string compare [file tail [file rootname b]] \
                           [file tail [file rootname a]]]

}

proc make_rdf_index {dir series source} {
    global logT
    global mtimes

    set index $dir/index.rdf
    if {[file exists $index]} {
        set then [expr [clock seconds]-(3*24*60*60)]
    } else {
        set then 0
    }

    array set mtimes {}
    set files {}
    set high 0
    foreach file [glob -nocomplain $dir/rdf/item.*.rdf] {
        if {[catch { file mtime $file } mtime]} {
            beepcore::log::entry $logT system $mtime
            continue
        }

        if {$mtime >= $then} {
            lappend files $file
            set mtimes($file) $mtime
            if {$mtime > $high} {
                set high $mtime
            }
        }
    }
    if {[llength $files] <= 0} {
        return
    }
    set files [lsort -command sortmtimes $files]

    set url [file2uri $index]
    set title "Recent $series"
    set description "Automatically generated from $source"
    set body "<?xml version=[beepcore::util::xml_av 1.0] encoding=[beepcore::util::xml_av UTF-8]?>

<rdf:RDF 
  xmlns=[beepcore::util::xml_av http://purl.org/rss/1.0/]
  xmlns:rdf=[beepcore::util::xml_av http://www.w3.org/1999/02/22-rdf-syntax-ns#]
  xmlns:dc=[beepcore::util::xml_av http://purl.org/dc/elements/1.1/]>

    <channel rdf:about=[beepcore::util::xml_av $url]>
        <title>[beepcore::util::xml_cdata $title]</title>
        <link>[beepcore::util::xml_cdata $url]</link>
        <description>[beepcore::util::xml_cdata $description]</description>
        <dc:language>en-us</dc:language>
        <dc:date>[beepcore::util::xml_cdata [clock format $mtime -format %Y-%m-%dT%T-00:00 -gmt true]]</dc:date>

        <items><rdf:Seq>"

    foreach file $files {
        set data ""
        set fd ""
        if {[catch { set data [read [set fd [open $file { RDONLY }]]] } \
                   result]} {       
            beepcore::log::entry $logT system $result
        }
        if {([string compare $fd ""]) && ([catch { close $fd } result])} {
            beepcore::log::entry $logT system $result
        }

        set url2 ""
        if {[set x [string first "rdf:about=" $data]] >= 0} {
            incr x 10
            set d [string range $data [expr $x+1] end]
            if {[set x [string first [string range $data $x $x] $d]] >= 0} {
                set url2 [string range $d 0 [expr $x-1]]
            }
        }

        append body "
            <rdf:li resource=[beepcore::util::xml_av $url2] />"       
        append body2 $data
    }

    append body "
        </rdf:Seq></items>
    </channel>
" $body2 "

</rdf:RDF>
"

    if {[file exists $index]} {
        set data ""
        set fd ""
        if {[catch { set data [read [set fd [open $index { RDONLY }]]] } \
                   result]} {       
            beepcore::log::entry $logT system $result
        }
        if {([string compare $fd ""]) && ([catch { close $fd } result])} {
            beepcore::log::entry $logT system $result
        }
        if {![string compare $body $data]} {
            return
        }
        catch { file delete -- $index }
    }

    if {[catch { set fd [open $index { WRONLY CREAT TRUNC }] } result]} {
        beepcore::log::entry $logT system $result
        return
    }

    if {[catch { puts -nonewline $fd $body ; flush $fd } result]} {
        beepcore::log::entry $logT system $result
    }

    if {[catch { close $fd } result]} {
        beepcore::log::entry $logT system $result
    }

    make_readonly $logT $index
    if {[catch { file mtime $index $high } result]} {
        beepcore::log::entry $logT system $result
    }
}


# and... we're off!

global logT

set logT [beepcore::log::init [lindex $argv 4] rfc]


beepcore::log::entry $logT info begin $httpD


set destD ../htdocs/public/rfc


# create directories/files for use by the HTTP server

foreach dir [list bibxml bibxml2 bibxml3 bibxml4 bibxml5 \
                  bibxml/rdf bibxml3/rdf bibxml4/rdf bibxml5/rdf \
                  html txt xml] {
    if {![file isdirectory $destD/$dir]} {
        if {[catch { file mkdir $destD/$dir } result]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info created $destD/$dir
        }
    }
}

set dtime [file mtime ../etc/rfc2629.dtd]
foreach dir [list $destD/bibxml $destD/bibxml2 $destD/bibxml3 $destD/bibxml4 \
                  $destD/bibxml5 $destD/xml] {
    if {([catch { file mtime $dir/rfc2629.dtd } ntime]) \
            || ($dtime > $ntime)} {
        catch { file delete -- $dir/rfc2629.dtd }
        if {[catch { file copy ../etc/rfc2629.dtd \
                          $dir/rfc2629.dtd } result]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info created $dir/rfc2629.dtd
            make_readonly $logT $dir/rfc2629.dtd
        }
    }
}


# retrieve rfc-index.txt from ftp.rfc-editor.org
#     store new .txt files in ../htdocs/public/rfc/txt/
#     create minimal .xml files in xml/minimal/
#     make the fulltext indices

foreach dir [list data xml/index xml/minimal xml/partial xml/complete] {
    if {![file isdirectory $dir]} {
        if {[catch { file mkdir $dir } result]} {
            beepcore::log::entry $logT system $result
        } else {
            beepcore::log::entry $logT info created $dir
        }
    }
}

set createL [be_do_get_rfc]

set homeD [pwd]
cd ../htdocs/public/rfc/txt
set txtD [pwd]
cd $homeD

if {$blocksP} {
    manage_full_index $logT doc.rfc $txtD txt 0 $createL
}



# for complete XML versions:
#     store new .xml files in ../htdocs/public/rfc/xml/
#     create .html files in ../htdocs/public/rfc/html/

global env guiP tcl_platform

switch -- $tcl_platform(platform) {
    windows {
        set c ";"
    }

    default {
        set c ":"
    }
}
append env(XML_LIBRARY) "$c$destD/xml$c$destD/bibxml"
set guiP 0

set files [lsort -dictionary [glob -nocomplain xml/complete/rfc*.xml]]

foreach file $files {
    set mtime($file) [file mtime $file]

    set tail [file tail $file]
    if {(![catch { file mtime $destD/xml/$tail } ntime]) \
            && ($mtime($file) <= $ntime)} {
        continue
    }

    catch { file delete -- $destD/xml/$tail }

    if {[catch { xml2rfc $file $destD/xml/$tail "" 0} result]} {
        beepcore::log::entry $logT user $file $result
    } else {
        beepcore::log::entry $logT info created $destD/xml/$tail
        make_readonly $logT $destD/xml/$tail
    }
}

foreach file $files {
    set base [file tail [file rootname $file]]
    if {(![catch { file mtime $destD/html/$base.html } ntime]) \
            && ($mtime($file) <= $ntime)} {
        continue
    }

    catch { file delete -- $destD/html/$base.html }

    if {[catch { xml2rfc $file $destD/html/$base.html "" 0} result]} {
        beepcore::log::entry $logT user $file $result
    } else {
        beepcore::log::entry $logT info created [file2uri $destD/html/$base.html]
        make_readonly $logT $destD/html/$base.html
    }
}


# for all XML versions:
#
#     create biblio .xml files in ../htdocs/public/rfc/bibxml/
#     store blocks versions under doc.rfc

set files [glob -nocomplain $destD/xml/rfc*.xml]
foreach file [glob -nocomplain xml/partial/rfc*.xml] {
    if {[lsearch -exact $files $destD/xml/[file tail $file]] < 0} {
        lappend files $file
    }
}
foreach file [glob -nocomplain xml/minimal/rfc*.xml] {
    if {([lsearch -exact $files $destD/xml/[file tail $file]] < 0) \
            && ([lsearch -exact $files \
                         xml/partial/[file tail $file]] < 0)} {
        lappend files $file
    }
}

proc sortfile {a b} {
    set a [string trimleft [string range [file tail [file rootname $a]] \
                                   3 end] 0]
    set b [string trimleft [string range [file tail [file rootname $b]] \
                                   3 end] 0]
    return [expr $a-$b]
}
set files [lsort -command sortfile $files]

set refP 0
foreach file $files {
    set mtime($file) [file mtime $file]

    set n [string range [file tail [file rootname $file]] 3 end]
    set tail reference.RFC.[format %04d $n].xml
    if {(![catch { file mtime $destD/bibxml/$tail } ntime]) \
            && ($mtime($file) <= $ntime)} {
        continue
    }

    set tmp $destD/bibxml/$tail.tmp
    set item $destD/bibxml/rdf/item.RFC.[format %04d $n].rdf
    catch { file delete -- $tmp }

    if {[catch { set rfcformats($n) } formats]} {
        set formats {}
    }
    set htmlP 0
    set xmlP 0
    foreach format $formats {
        catch { unset fv }
        array set fv $format
        switch -- $fv(type) {
            HTML { set htmlP 1 }
            XML { set xmlP 1 }
        }
    }
    foreach type [list html xml] {
        if {(![set ${type}P]) \
                && ([file exists [set t $destD/$type/rfc$n.$type]])} {
            lappend formats [list type [string toupper $type] \
                                  octets [file size $t] \
                                  target [file2uri $t]]
        }
    }

    if {[catch { xml2ref $file $tmp $formats $item } result]} {
        beepcore::log::entry $logT user $file $result
    } elseif {[catch { file rename -force $tmp $destD/bibxml/$tail } result]} {
        beepcore::log::entry $logT user $file $result
        catch { file delete -- $tmp }
    } else {
        beepcore::log::entry $logT info created $destD/bibxml/$tail
        make_readonly $logT $destD/bibxml/$tail
        set refP 1
    }
}

cd $homeD
cd ../htdocs/public/rfc/
set rfcD [pwd]
cd $homeD

make_rdf_index $rfcD/bibxml RFCs rfc-index.txt

be_do_get_id
make_rdf_index $rfcD/bibxml3 Internet-drafts 1id-abstracts

be_do_get_w3c
make_rdf_index $rfcD/bibxml4 "W3C publications" tr.rdf

be_do_get_3gpp
make_rdf_index $rfcD/bibxml5 "3GPP publications" ""

set now [clock seconds]
set later [expr $now+(24*60*60)]

set args [list -title    "The (unofficial) RFC Index" -subtitle "rfc-index"]
foreach bib [list bibxml bibxml2 bibxml3 bibxml4 bibxml5] {
    if {[lsearch -exact [list bibxml2] $bib] >= 0} {
        set indexP 1
    } else {
        set indexP 0
    }
    if {[file exists [set file $destD/$bib/browse.html]]} {
        set i2P 0
        set a2P 0
    
        set ftime [file mtime $file]
        foreach file [glob -nocomplain -- $destD/$bib/reference.*.xml] {
            if {(![catch { file mtime $file } ntime]) && ($ftime < $ntime)} {
                if {$ntime <= $now} {
                    set i2P $indexP
                    set a2P 1
                    break
                }
                if {$ntime > ($now+24*60*60)} {
                    beepcore::log::entry $logT info "$file is futuristic"
                }
            }
        }
    } elseif {$indexP} {
        set a2P 1
    } else {
        set i2P 0
        set a2P $refP
    
        if {[file exists [set file $destD/$bib/index.xml]]} {
            set ftime [file mtime $file]
            foreach file [glob -nocomplain -- $destD/$bib/reference.*.xml] {
                if {(![catch { file mtime $file } ntime]) \
                        && ($ftime < $ntime)} {
                    if {$ntime <= $now} {
                        set i2P 1
                        break
                    }
                    if {$ntime > ($now+24*60*60)} {
                        beepcore::log::entry $logT info "$file is futuristic"
                    }
                }
            }
            foreach sfx [list zip tgz] {
                if {(![file exists $destD/$bib.$sfx]) \
                        || ((![catch { file mtime $destD/$bib.$sfx } ntime])
                                && ($ftime > $ntime))} {
                    set a2P 1
                }
            }
        }
    }
    
    cd  $rfcD/$bib
    if {$i2P} {
        lappend args -output [set tmp $homeD/data/index.xml]
        if {[catch { eval exec $homeD/../etc/mkindex.tcl $args } result]} {
            beepcore::log::entry $logT user mkindex $result
        } elseif {[catch { file rename -force $tmp index.xml } result]} {
            beepcore::log::entry $logT user index.xml $result
            catch { file delete -- $tmp }
        } else {
            beepcore::log::entry $logT info created \
                [file2uri $rfcD/$bib/index.xml]
            make_readonly $logT $rfcD/$bib/index.xml
        }

        if {!$indexP} {
        } elseif {[catch { exec tclsh $homeD/../etc/xml2rfc.tcl xml2html \
                                 index.xml [set tmp $homeD/data/browse.html] \
                         } result]} {
            beepcore::log::entry $logT user xml2rfc $result
        } elseif {[catch { file rename -force $tmp browse.html } result]} {
            beepcore::log::entry $logT user browse.html $result
            catch { file delete -- $tmp }
        } else {
            beepcore::log::entry $logT info created \
                [file2uri $rfcD/$bib/browse.html]
            make_readonly $logT $rfcD/$bib/browse.html
        }
    }
    if {$a2P} {
        catch { file delete -- ../$bib.tmp }
        if {[catch { exec zip -r ../$bib.tmp . } result]} {
            beepcore::log::entry $logT user $result
        } elseif {[catch { file rename -force ../$bib.tmp ../$bib.zip } \
                         result]} {
            beepcore::log::entry $logT user $result
        } else {
            beepcore::log::entry $logT info created [file2uri $rfcD/$bib.zip]
            make_readonly $logT $rfcD/$bib.zip
        }
        catch { file delete -- ../$bib.tmp }
        if {[catch { exec tar cf - --exclude rdf . | gzip > ../$bib.tmp } result]} {
            beepcore::log::entry $logT user $result
        } elseif {[catch { file rename -force ../$bib.tmp ../$bib.tgz } \
                         result]} {
            beepcore::log::entry $logT user $result
        } else {
            beepcore::log::entry $logT info created [file2uri $rfcD/$bib.tgz]
            make_readonly $logT $rfcD/$bib.tgz
        }
        catch { file delete -- ../$bib.tmp }
    }
    set args {}
    cd $homeD
}

if {[set status $blocksP]} {
    set rfcT [rfc::init $logT]

    set status [make_and_store_blocks $logT $bxxpD doc.rfc \
                                      data/timestamp \
                                      $files [list rfc::transform $rfcT] \
                                      rfc::args]

    rfc::fin $rfcT
}


adios $status ""


} result]} {
    catch {
        global errorCode errorInfo
        global logT

        beepcore::log::entry $logT fatal $errorCode $errorInfo $result
    }

    puts stderr $result

    catch {
        global debugP

        if {$debugP > 1} {
            return
        }
    }

    exit 1
}
