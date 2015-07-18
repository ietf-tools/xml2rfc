#!/bin/sh
# the following restarts using tclsh \
DISPLAY= PATH=/usr/pkg/bin:/usr/local/bin:/usr/bin:/bin LD_LIBRARY_PATH=/usr/pkg/lib:/usr/local/lib:/usr/lib export DISPLAY PATH LD_LIBRARY_PATH; exec tclsh "$0" "$@"


#
# rfcindexer.tcl - process XML version of rfc-index
#



if {[catch { 


if {$argc != 2} {
    error "expecting argc=2 (homeD loggingF)\nnot expecting $argc ($argv)"
}


global debugP

if {![info exists debugP]} {
    set debugP 0
}

set homeD [lindex $argv 0]
if {[lsearch -exact $auto_path $homeD/scripts] < 0} {
    lappend auto_path $homeD/scripts
}

package require FTP   
package require http 2
package require beepcore::log   

global guiP
set guiP 0
source ../etc/xml2rfc.tcl
# package require xml

package require beepcore::util

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


namespace eval rfc {
    variable rfc
    array set rfc { uid 0 }

    variable parser [xml::parser]

    namespace export init fin
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

proc fetch_new_index {} {
    global logT

    catch { file delete -- [set newF data/rfc-indexer.new] }

    if {![FTP::New ftp.rfc-editor.org anonymous anonymous@[info hostname] \
                   -mode passive]} {
        return {}
    }

    FTP::What Type
    FTP::Type ascii

    FTP::What Get
    FTP::Where rfc-index.txt
    if {![FTP::Get in-notes/rfc-index.xml $newF]} {
        FTP::What Close
        FTP::Close

        return {}
    }

    set rfcT [rfc::init $logT]
    if {[catch { rfc::parse_new_index $rfcT $newF } result]} {
        beepcore::log::entry $logT error $result

        return 1
    }
    rfc::fin $rfcT

    if {[catch { file rename -force $newF data/rfc-index.xml } result]} {
        beepcore::log::entry $logT system $result
    }

    return 0
}

proc rfc::parse_new_index {token file} {
    global errorCode errorInfo
    global logT

    variable $token
    upvar 0 $token state

    array set emptyA {}

    variable parser
    $parser configure \
            -elementstartcommand    "rfc::new_element_start $token" \
            -elementendcommand      "rfc::new_element_end   $token" \
            -characterdatacommand   "rfc::new_cdata         $token" \
            -entityreferencecommand ""                              \
            -errorcommand           "rfc::oops              $token" \
            -entityvariable         emptyA                          \
            -final                  yes                             \
            -reportempty            no


    set fd [open $file { RDONLY }]
    set buffer ""
    while {![eof $fd]} {
        while {[gets $fd line] >= 0} {
            append buffer "\n" $line
            if {[set x [string first "</rfc-entry>" $buffer]] >= 0} {
                set data [string range $buffer 0 [expr $x+11]]
                set buffer [string range $buffer [expr $x+12] end]
                if {[set x [string first "<rfc-entry>" $data]] > 0} {
                    set data [string range $data $x end]
                }
    
                set state(stack) {}

                if {[set code [catch { $parser parse $data } result]]} {
                    set ecode $errorCode
                    set einfo $errorInfo
                    if {($code == 1) && ([llength $state(stack)] > 0)} {
                        set text "File:    $file\nContext: "
                        foreach frame $state(stack) {
                            append text "<[lindex $frame 0]>"
                        }
                        append result "\n\n$text"
                    }

                    return -code $code -errorinfo $einfo -errorcode $ecode
                           $result
                }    
            }
        }
    }
    close $fd

    catch { file delete -- [set newF data/rfc-items.new] }

    set fd [open $newF { WRONLY CREAT TRUNC }]
    catch { array set rfcinfo $state(rfcinfo) }
    foreach r [lsort -integer [array names rfcinfo]] {
        foreach {k v} $rfcinfo($r) {
            puts $fd [format "set rfcitems(%d,%s) {%s}" $r $k $v]
        }
    }
    close $fd

    if {[catch { file rename -force $newF data/rfc-items.tcl } result]} {
        beepcore::log::entry $logT system $result
    }

    catch { unset state(stack) }
    catch { unset state(rfcinfo) }

    return
}

proc rfc::new_element_start {token name {av {}}} {
    variable $token
    upvar 0 $token state

    lappend state(stack) [list $name $av ""]
    if {(![info exists rfcdata]) && (![string compare $name rfc-entry])} {
        set state(rfcdata) {}
    }
}

proc rfc::new_element_end {token name} {
    global logT

    variable $token
    upvar 0 $token state

    set frame [lindex $state(stack) end]
    set state(stack) [lreplace $state(stack) end end]

    array set rfcdata $state(rfcdata)
    set data [string trim [lindex $frame 2]]
    set parent [lindex [lindex $state(stack) end] 0]

    if {![string compare $name rfc-entry]} {
        if {![info exists rfcdata(doc-id)]} {
            beepcore::log::entry $logT user "no doc-id element"
        } else {
            set docid [string trimleft [string range $rfcdata(doc-id) 3 end] 0]
            if {![string is digit -strict $docid]} {
                    beepcore::log::entry $logT user \
                            "invalid doc-id element: $rfcdata(doc-id)"
            } else {
                lappend state(rfcinfo) $docid [array get rfcdata]
            }
        }

        unset state(rfcdata)
    } elseif {[info exists rfcdata]} {
        switch -- $name {
            title {
                switch -- $parent {
                    rfc-entry {
                        set rfcdata(doc-title) $data
                    }

                    default {
                        lappend rfcdata($parent) $data
                    }
                }
            }

            author
                -
            format {
                set x [llength [array names rfcdata ${name}*]]
                incr x
                array set fields {}
                switch -- $name {
                    author {
                        set ks [list name title organization org-abbrev]
                    }

                    format {
                        set ks [list file-format char-count page-count]
                    }
                }
                foreach k $ks {
                    catch {
                        set field($k) $rfcdata($k)
                        unset rfcdata($k)
                    }
                }
                set k $name$x
                set rfcdata($k) [array get field]
            }

            day {
                set rfcdata($name) [string trimleft $data 0]
            }

            kw {
                lappend rfcdata(keywords) $data
            }

            date
                -
            keywords
                -
            obsoletes
                -
            obsoleted-by
                -
            updates
                -
            updated-by
                -
            is-also
                -
            see-also {
            }

            doc-id {
                switch -- $parent {
                    rfc-entry {
                        set rfcdata($name) $data
                    }

                    default {
                        set prefix [string range $data 0 2]
                        set suffix [string trimleft \
                                           [string range $data 3 end] 0]
                        lappend rfcdata($parent) $prefix$suffix
                    }
                }
            }

            default {
                set rfcdata($name) $data
            }
        }

        set state(rfcdata) [array get rfcdata]
    }
}

proc rfc::new_cdata {token text} {
    variable $token
    upvar 0 $token state

    regsub -all "\r" $text "\n" text

    set frame [lindex $state(stack) end]
    set data [lindex $frame 2]
    append data $text

    set frame [lreplace $frame 2 2 $data]
    set state(stack) [lreplace $state(stack) end end $frame]
}


global logT

set logT [beepcore::log::init [lindex $argv 1] rfc]

beepcore::log::entry $logT info begin

adios [fetch_new_index] ""


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
