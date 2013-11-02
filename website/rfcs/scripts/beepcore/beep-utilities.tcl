#
# beep-utilities.tcl - miscellaneous routines
#


package provide beepcore::util  1.0

package require beepcore::log

package require expat 1.1
package require smtp


namespace eval ::beepcore::exml {
    variable exml

    array set exml { uid 0 }

    namespace export parser
}

proc ::beepcore::exml::parser {args} {
    variable exml

    # The Tclxml package provides the expat package but not the 'expat' command
    if {[catch {package require expat} ver]} {
        error "the \"expat\" package is unavailable"
    }
    if {[expr {$ver < 2.0}]} {
        return [eval [list expat [namespace current]::parser[incr exml(uid)]] \
                           $args]
    } else {
        return [eval [list xml::parser \
                           [namespace current]::parser[incr exml(uid)]] $args]
    }
}


namespace eval ::beepcore::util {
    variable parser [[namespace parent]::exml::parser]
    catch {
        $parser configure                               \
                -errorcommand [namespace current]::oops \
                -reportempty  no
    }
    variable state

    array set state [list languages [list i-default]]

    namespace export \
              exclfile tmpfile \
              timer_init timer_start timer_fin \
              xml_av xml_cdata xml_norm xml_pcdata xml_trace \
              xml_localize xml_error xml_error2 xml_blob \
              sa2xml xml2sa \
              getpass do_callback do_passback
}


proc ::beepcore::util::exclfile {fileN {stayP 0}} {
    global errorCode errorInfo

    for {set i 0} {$i < 10} {incr i} {
        if {![catch { open $fileN { RDWR CREAT EXCL } } xd]} {
            if {(![set code [catch { puts $xd [expr [pid]%65535]
                                     flush $xd } result]]) \
                    && (!$stayP)} {
                if {![set code [catch { close $xd } result]]} {
                    set xd ""
                }
            }

            if {$code} {
                set ecode $errorCode
                set einfo $errorInfo

                catch { close $xd }

                catch { file delete -- $fileN }

                return -code $code -errorinfo $einfo -errorcode $ecode $result
            }

            return $xd
        }
        set ecode $errorCode
        set einfo $errorInfo

        if {(([llength $ecode] != 3) \
                || ([string compare [lindex $ecode 0] POSIX]) \
                || ([string compare [lindex $ecode 1] EEXIST]))} {
            return -code 1 -errorinfo $einfo -errorcode $ecode $xd
        }

        after 1000
    }

    return -code 7 "unable to exclusively open $fileN"
}

proc ::beepcore::util::tmpfile {prefix {tmpD ""}} {
    global env
    global errorCode errorInfo

    if {(![string compare $tmpD ""]) && ([catch { set env(TMP) } tmpD])} {
        set tmpD /tmp
    }
    set file [file join $tmpD $prefix]

    append file [expr [pid]%65535]

    for {set i 0} {$i < 10} {incr i} {
        if {![set code [catch { open $file$i { WRONLY CREAT EXCL } } fd]]} {
            return [list file $file$i fd $fd]
        }
        set ecode $errorCode
        set einfo $errorInfo

        if {(([llength $ecode] != 3) \
                || ([string compare [lindex $ecode 0] POSIX]) \
                || ([string compare [lindex $ecode 1] EEXIST]))} {
            return -code $code -errorinfo $einfo -errorcode $ecode $fd
        }
    }

    error "unable to create temporary file"
}

proc ::beepcore::util::timer_init {} {
    global clicks clickZ

    catch { unset clicks }
    array set clicks {}
    set clickZ [clock clicks]
}

proc ::beepcore::util::timer_start {} {
    proc ::tclLog {message} {
        global clicks clickZ

        set x [expr [clock clicks]-$clickZ]
        lappend clicks($x) $message
    }
}

proc tclLog {message} {}

proc ::beepcore::util::timer_fin {logT} {
    global clicks clickZ

    set click0 $clickZ
    set firstP 1
    foreach click [lsort -integer [array names clicks]] {
        if {$firstP} {
            set elapsed [format %10s ""]
            set firstP 0
        } else {
            set elapsed [expr $click-$click0]
            if {[set x [string length $elapsed]] > 6} {
                set elapsed [format %3s.%s \
                                    [string range $elapsed 0 [expr $x-7]] \
                                    [string range $elapsed [expr $x-6] end]]
            } else {
                set elapsed [format %10s $elapsed]
            }
        }

        if {[set x [string length $click]] > 6} {
            set stamp [format %3s.%s \
                              [string range $click 0 [expr $x-7]] \
                              [string range $click [expr $x-6] end]]
        } else {
            set stamp [format %10s $click]
        }
        foreach message $clicks($click) {
            beepcore::log::entry $logT timing $stamp $elapsed $message
        }

        set click0 $click
    }
}

proc ::beepcore::util::xml_av {text {allP 1}} {
# &amp; must always be first...
    if {$allP} {
        set entities { {\&amp;}  {&} 
                       {\&lt;}   {<}
                       {\&apos;} {'}
                       {\&quot;} {"}
                       {]]\&gt;} {]]>}
                     }
    } else {
        set entities { {\&apos;} {'}
                       {]]\&gt;} {]]>}
                     }
    }

    foreach {entity chars} $entities {
        regsub -all $chars $text $entity text
    }

    return '$text'
}

proc ::beepcore::util::xml_cdata {text} {
# &amp; must always be first...
    set entities { {\&amp;}  {&} 
                   "'"       ""
                   {\&lt;}   {<}
                   {]]\&gt;} {]]>}
                 }

    foreach {entity chars} $entities {
        regsub -all $chars $text $entity text
    }

    return $text
}

proc ::beepcore::util::xml_trace {logT prefix info data {stack {}}} {
    beepcore::log::annotate $logT $data
    beepcore::log::entry $logT notify ${prefix}::parse $info

    set text ""
    catch {
        if {[llength $stack] > 0} {
            set text "\n\nContext:"
            foreach frame $stack {
                append text " <[lindex $frame 0]>"
            }
        }
    }

    return $text
}

# because <![CDATA[ ... ]]> isn't supported in TclXML...

proc ::beepcore::util::xml_norm {text} {
    set data ""
    set litN [string length [set litS "<!\[CDATA\["]]
    set litO [string length [set litT "\]\]>"]]
    while {[set x [string first $litS $text]] >= 0} {
        append data [string range $text 0 [expr $x-1]]
        set text [string range $text [expr $x+$litN] end]
        if {[set x [string first $litT $text]] < 0} {
            error "missing close to CDATA"
        }
        set y [string range $text 0 [expr $x-1]]
        regsub -all {&} $y {\&amp;} y
        regsub -all {<} $y {\&lt;}  y
        append data $y
        set text [string range $text [expr $x+$litO] end]
    }
    append data $text

    return $data
}

proc ::beepcore::util::xml_pcdata {text {flattenP 1}} {
    set flattenP [smtp::boolean $flattenP]

# &amp; must always be last...
    if {$flattenP} {
        set entities { "\r"             "\n"
                       "\n[ \t\n]*"     "\n"
                       "[ \t]*\n[ \t]*" { }
                       {&lt;}           {<} 
                       {&apos;}         {'} 
                       {&quot;}         {"}
                       {&gt;}           {>}
                       {&amp;}          {\&}
                     } 
    } else {
        set entities { {&lt;}           {<} 
                       {&apos;}         {'} 
                       {&quot;}         {"}
                       {&gt;}           {>}
                       {&amp;}          {\&}
                     }
    }

    foreach {entity chars} $entities {
        regsub -all -nocase $entity $text $chars text
    }

    return $text
}

# not documented...

proc ::beepcore::util::xml_localize {languages} {
    variable state

    set state(languages) [string tolower $languages]
}

proc ::beepcore::util::xml_error {code {diagnostic ""} {language en-US}} {
    variable state

    set string "<error code=[xml_av $code]"

    if {[string compare $diagnostic ""]} {
        if {[string compare [lindex $state(languages) 0] \
                    [string tolower $language]]} {
            append string " xml:lang=[xml_av $language]"
        }

        append string ">[xml_cdata $diagnostic]</error>"
    } else {
        append string " />"
    }

    return $string
}

proc ::beepcore::util::xml_error2 {replyA} {
    array set reply [list code 500 diagnostic "" language en-US]
    array set reply $replyA

    return [xml_error $reply(code) $reply(diagnostic) $reply(language)]
}

#
# gets around the line-centric nature of base64
#

proc ::beepcore::util::xml_blob {text {status continue}} {
# for base64
    package require Trf 2

    set result "<blob"
    if {[string compare $status continue]} {
        append result " status=[xml_av $status]"
    }
    if {![string compare $text ""]} {
        return "$result />"
    }
    append result ">"

    foreach line [split [string trim [base64 -mode encode $text]] " \r\n"] {
        append result [string trim $line]
    }
    return "$result</blob>"
}


#
# xml to/from serialized array
#

proc ::beepcore::util::sa2xml {data} {
    if {[string length $data] == 0} {
        return "<array />"
    }

    array set info $data
    foreach k [list name authentication authorization] {
        if {[info exists info($k)]} {
            append result "\n[sa2xml_aux $k $info($k) 0]\n"
            unset info($k)
        }
    }
    set data [array get info]

    set s "\n"
    foreach {k v} $data {
        append result "$s[sa2xml_aux $k $v 0]\n"
        set s ""
    }
    return "<array>$result</array>"
}

proc ::beepcore::util::sa2xml_aux {k v level} {
    incr level 4
    set s [format "%*.*s" $level $level ""]

    if {[string length $v] == 0} {
        return "$s<elem key=[xml_av $k] />"
    }

    if {([catch { llength $v } len]) || ($len % 2)} {
        return "$s<elem key=[xml_av $k]>[xml_cdata $v]</elem>"
    } 

    foreach {p q} $v {
        append result "[sa2xml_aux $p $q $level]\n"
    }
    return "$s<elem key=[xml_av $k]>\n$result$s</elem>"
}


proc ::beepcore::util::xml2sa {data} {
    global errorCode errorInfo

    variable parser

    variable state

    $parser configure                                                  \
            -elementstartcommand  "[namespace current]::element start" \
            -elementendcommand    "[namespace current]::element end"   \
            -characterdatacommand "[namespace current]::cdata"         \
            -final                yes

    set code [catch {
        set state(stack) {}
        $parser reset
        $parser parse [xml_norm $data]
        lindex [lindex [lindex $state(stack) 0] 0] 1
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    unset state(stack)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc ::beepcore::util::element {tag name {av {}}} {
    variable state

    switch -- $tag {
        start {
            if {[llength $state(stack)] == 0} {
                if {[string compare $name array]} {
                    oops "expecting <array> element, not <$name>"
                }
                array set attrs [list key ""]
            } elseif {[string compare $name elem]} {
                oops "expecting <elem> element, not <$name>"
            }
            array set attrs $av
            lappend state(stack) [list $attrs(key) {} ""]
        }

        end {
            set frame [lindex $state(stack) end]
            set name [lindex $frame 0]
            set children [lindex $frame 1]
            set text [lindex $frame 2]
            if {([llength $children] > 0) \
                    && ([string length [string trim $text]] > 0)} {
                oops "not expecting both elements and text in <$name>"
            }

            set state(stack) [lreplace $state(stack) end end]
            set frame [lindex $state(stack) end]
            set value [lindex $frame 1]

            if {[llength $children] > 0} {
                lappend value $name $children
            } else {
                lappend value $name $text
            }
            set frame [lreplace $frame 1 1 $value]
            set state(stack) [lreplace $state(stack) end end $frame]
        }
    }
}

proc ::beepcore::util::cdata {text} {
    variable state

    set frame [lindex $state(stack) end]
    set state(stack) [lreplace $state(stack) end end \
                               [lreplace $frame 2 2 [lindex $frame 2]$text]]
}

proc ::beepcore::util::oops {args} {
    return -code error [join $args " "]
}


# these three aren't documented...

proc ::beepcore::util::getpass {name} {
    for {set i 0} {$i < 2} {incr i} {
        puts -nonewline stderr "Enter passphrase for $name: "
        if {[gets stdin pass1] <= 0} {
            return -code 7 [list code 500 diagnostic "no input"]
        }

        puts -nonewline stderr "Again passphrase for $name: "
        if {[gets stdin pass2] <= 0} {
            return -code 7 [list code 500 diagnostic "no input"]
        }

        if {[string compare $pass1 $pass2]} {
            puts stderr "Sorry, no match"
            continue
        }

        if {([set len [string length $pass1]] < 10) || ($len > 63)} {
            puts stderr "passphrase must have 10..63 characters"
            continue
        }

        puts stderr ""
        return $pass1
    }

    return -code 7 [list code 550 diagnostic "loser..."]
}


proc ::beepcore::util::do_callback {opts clientT data} {
    array set options $opts
    array set params $data

    switch -- [set key $params(id)] {
        authname {
            if {![info exists options(-$key)]} {
                set key username
            }
        }

        user {
            set key username
            if {![info exists options(-$key)]} {
                catch {
                    array set tuning [beepcore::client::tuningA $clientT]
                    array set props $tuning(tls)
                    array set cert $props(local)
                    set options(-username) $cert(subject)
                }
            }
        }

        pass {
            set key passphrase
        }
    }    

    if {[info exists options(-$key)]} {
        return $options(-$key)
    }

    puts -nonewline stderr "enter $key: "
    flush stderr
    if {[gets stdin input] <= 0} {
        return ""
    }
    return $input
}


proc ::beepcore::util::do_passback {serverD name algorithm seqno seed} {
    puts -nonewline stderr \
         "enter secret password for $name@$serverD\n$seqno $seed: "
    flush stderr
    if {[gets stdin passphrase] <= 0} {
        return ""
    }

    set key $seed$passphrase
    set n [expr $seqno+1]
    while {[incr n -1] >= 0} {
        set key [otp_$algorithm -- $key]
    }

    set result hex:[hex -mode encode -- $key]

    if {($seqno <= 10) \
            && (![catch { package require beepcore::profile::otp }])} {
        puts -nonewline stderr \
             "OTP sequence nearing expiration, re-generate(yes/no)?"
        flush stderr
        set regenP 0
        if {[gets stdin yesno] > 0} {
            catch { set regenP [smtp::boolean $yesno] }
        }

        if {$regenP} {
            set seqno 9999
            set seed [beepcore::profile::otp::makeseed]

            set key $seed$passphrase
            set n [expr $seqno+1]
            while {[incr n -1] >= 0} {
                set key [otp_$algorithm -- $key]
            }

            set result init-$result
            append result ":$algorithm $seqno $seed:"
            append result [hex -mode encode $key]
        }
    }

    return $result
}


return


# Blocks Public License
# Copyright (c) 2000, Invisible Worlds, Inc. 
# All rights reserved. 
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met: 
# 
# * Redistributions of source code must retain the above copyright notice, 
#   this list of conditions and the following disclaimer. 
# 
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution. 
# 
# * Neither the name, trademarks, or tradenames of Invisible Worlds, Inc., nor 
#   the names, trademarks, or tradenames of its contributors may be used to 
#   endorse or promote products derived from this software without specific 
#   prior written permission. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL INVISIBLE WORLDS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
