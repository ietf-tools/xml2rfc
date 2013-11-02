#
# profile-null.tcl - the NULL family of profiles
#


package provide beepcore::profile::null  1.0

package require beepcore::log
package require beepcore::util


#
# state variables:
#
#    logT: token for logging package
#    echoP: true if we're echoing
#    upcallV: callback for answers
#
# present only during XML parsing
#
#    stack: list containing parse context
#    code: reply code
#    data: <data> element
#    count: count attribute
#


namespace eval beepcore::profile::null {
    variable null
    array set null { uid 0 }

    variable parser [::beepcore::exml::parser]
    catch {
        $parser configure                               \
                -errorcommand [namespace current]::oops \
                -reportempty  no
    }

    namespace export info boot init fin exch
}


proc beepcore::profile::null::info {logT} {
    return [list 0 \
                 [list http://xml.resource.org/profiles/NULL/ECHO \
                       http://xml.resource.org/profiles/NULL/SINK] \
                 [list bootV [namespace current]::boot \
                       initV [namespace current]::init \
                       exchV [namespace current]::exch \
                       finV  [namespace current]::fin]]
}


proc beepcore::profile::null::boot {logT} {
}


proc beepcore::profile::null::init {logT serverD clientA upcallV uri} {
    variable null

    set token [namespace current]::[incr null(uid)]

    variable $token
    upvar 0 $token state

    if {[string first echo [string tolower $uri]] >= 0} {
        set echoP 1
    } else {
        set echoP 0
    }

    array set state [list logT $logT echoP $echoP upcallV $upcallV]

    return $token
}


proc beepcore::profile::null::fin {token status} {
    variable $token
    upvar 0 $token state

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}



proc beepcore::profile::null::exch {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    if {!$state(echoP)} {
        return "<null />"
    } elseif {[string first "<data" [string trimleft $data]]} {
        return $data
    }

    switch -- [set code [catch { parse $token $data } result]] {
        0 {
            array set parse $result

            if {$parse(count) == 1} {
                return $parse(data)
            }

            for {set i 1} {$i <= $parse(count)} {incr i} {
                if {[set code [catch { eval $state(upcallV) \
                                            [list $parse(data) "" \
                                                  -mode answer -ansNo $i] 
                                     } result]]} {
                    if {$code == 7} {
                        beepcore::log::entry $state(logT) user $result
                    } else {
                        beepcore::log::entry $state(logT) error \
                           [lindex $state(upcallV) 0] $result
                    }

                    break
                }
            }

            return -code 9 ""
        }

        7 {
            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::parse $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::profile::null::parse {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable parser

    $parser configure                                                         \
            -elementstartcommand  "[namespace current]::element $token start" \
            -elementendcommand    "[namespace current]::element $token end"   \
            -characterdatacommand "[namespace current]::cdata   $token"       \
            -final                yes

    set state(stack) {}
    set state(code)  500
    set state(data)  ""
    set state(count) 1

    set code [catch {
        $parser reset
        $parser parse $data
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result [list data  $state(data) \
                             count $state(count)]
        }

        7 {
        }

        default {
            append result [beepcore::util::xml_trace $state(logT) echo \
                               $result $data $state(stack)]

            set code 7

            set result [list code       $state(code) \
                             diagnostic $result]
        }
    }

    unset state(stack) \
          state(data)  \
          state(code)  \
          state(count)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


#
# XML parsing
#

proc beepcore::profile::null::element {token tag name {av {}}} {
    variable $token
    upvar 0 $token state

    set depth [llength $state(stack)]
    switch -- $tag {
        start {
            if {$depth == 0} {
                if {[string compare $name data]} {
                    oops "not expecting <$name> element"
                }

                array set attrs [list count 1]
                array set attrs $av

                set state(count) $attrs(count)
            }

            append state(data) "<$name"
            foreach {k v} $av {
                append state(data) " $k=[beepcore::util::xml_av $v]"
            }
            append state(data) ">"

            lappend state(stack) [list $name $av]
        }

        end {
            append state(data) "</$name>"

            set state(stack) [lreplace $state(stack) end end]
        }
    }
}


proc beepcore::profile::null::cdata {token text} {
    variable $token
    upvar 0 $token state

    append state(data) [beepcore::util::xml_cdata $text]
}


proc beepcore::profile::null::oops {args} {
    return -code error [join $args " "]
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
