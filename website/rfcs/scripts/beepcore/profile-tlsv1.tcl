#
# profile-tlsv1.tcl - the TLS profile
#


package provide beepcore::profile::tlsv1 1.0

package require beepcore::log
package require beepcore::sasl
package require beepcore::server
package require beepcore::util


#
# state variables:
#
#    logT: token for logging package
#    version: minimally-acceptable TLS version
#
# present only during XML parsing
#
#    stack: list containing parse context
#    code: reply code
#    version: TLS version number
#


namespace eval beepcore::profile::tlsv1 {
    variable tlsv1
    array set tlsv1 { uid 0 }

    variable parser [::beepcore::exml::parser]
    catch {
        $parser configure                               \
                -errorcommand [namespace current]::oops \
                -reportempty  no
    }

    namespace export info boot init fin exch
}


proc beepcore::profile::tlsv1::info {logT} {
    return [list 1 \
                 [list http://iana.org/beep/TLS] \
                 [list bootV [namespace current]::boot \
                       initV [namespace current]::init \
                       exchV [namespace current]::exch \
                       finV  [namespace current]::fin]]
}


proc beepcore::profile::tlsv1::boot {logT} {
    global debugP

    beepcore::sasl::tuneP 0 1
    beepcore::sasl::tuneP

    if {[catch { package require tls } result]} {
        return -code 7 [list code 451 diagnostic $result]
    }

    set tls::debug $debugP
    set tls::logcmd [list beepcore::log::entry $logT debug tls]
}


proc beepcore::profile::tlsv1::init {logT serverD clientA upcallV uri} {
    beepcore::sasl::tuneP 0 1
    beepcore::sasl::tuneP

    variable tlsv1

    set token [namespace current]::[incr tlsv1(uid)]

    variable $token
    upvar 0 $token state

    array set state [list logT $logT]

    return $token
}


proc beepcore::profile::tlsv1::fin {token status} {
    variable $token
    upvar 0 $token state

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}


proc beepcore::profile::tlsv1::exch {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    beepcore::sasl::tuneP 1 1
    beepcore::sasl::tuneP 1

    switch -- [set code [catch { parse $token $data } result]] {
        0 {
            return -code 8 [list "<proceed />" \
                                 [list [namespace current]::import $token]]
        }

        7 {
            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error tlsv1::parse $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::profile::tlsv1::parse {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable parser

    $parser configure                                                         \
            -elementstartcommand  "[namespace current]::element $token start" \
            -elementendcommand    "[namespace current]::element $token end"   \
            -characterdatacommand "[namespace current]::cdata   $token"       \
            -final                yes

    set state(stack)   ""
    set state(code)    500
    set state(version) 1

    set code [catch {
        $parser reset
        $parser parse $data
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result ""
        }

        7 {
        }

        default {
            append result [beepcore::util::xml_trace $state(logT) tlsv1 \
                               $result $data $state(stack)]

            set code 7

            set result [list code       $state(code) \
                             diagnostic $result]
        }
    }

    unset state(stack) \
          state(code)  \
          state(version)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


proc beepcore::profile::tlsv1::tls_handshake {token inputC} {
    variable $token
    upvar 0 $token state

    if {![::info exists state(tls_fail_count)]} {
       set state(tls_fail_count) 0
    }
    if {[eof $inputC]} {
        # close $inputC ; # don't close it. Let other stuff
        set state(tls_handshake_done) 0
        unset state(tls_fail_count)
        fileevent $inputC readable {}
        fileevent $inputC writable {}
        return
    }
    set x [catch {tls::handshake $inputC} result]
    if {$x == 0 && $result == 1} {
        set state(tls_handshake_done) 1
        unset state(tls_fail_count)
    } else {
        incr state(tls_fail_count)
        if {15 < $state(tls_fail_count)} {
            unset state(tls_fail_count)
            set state(tls_handshake_done) 0
        }
    }
}


proc beepcore::profile::tlsv1::callback {logT args} {
    catch { beepcore::log::entry $logT debug tlsv1::callback $args }

    if {![string compare [lindex $args 0] verify]} {
        if {![string compare [lindex $args 5] "self signed certificate"]} {
            return 1
        }
        return [lindex $args 4]
    }
}


proc beepcore::profile::tlsv1::import {token logT inputC} {
    variable $token
    upvar 0 $token state

    beepcore::sasl::logout

    set readable [fileevent $inputC readable]
    set writable [fileevent $inputC writable]

    tls::import $inputC \
        -ssl2    false  -ssl3    false -tls1   true         \
        -request true   -require false -server true         \
        -command [list [namespace current]::callback $logT] \
        -certfile [file join certs server.pem]              \
        -keyfile  [file join certs privkey.pem]

    fconfigure $inputC -encoding binary -translation binary
    fileevent $inputC readable \
              [list [namespace current]::tls_handshake $token $inputC]
    fileevent $inputC writable {}

    catch { tls::handshake $inputC }
    while {![::info exists state(tls_handshake_done)]} {
        vwait $token
    }

    set readable [fileevent $inputC readable]
    set writable [fileevent $inputC writable]
    if {!$state(tls_handshake_done)} {
        set ::beepcore::server::tuning \
            [list privacy none sbits 0 authname "" realname "" sasl "" tls ""]
      return
    }
    unset state(tls_handshake_done)

    fileevent $inputC readable $readable
    fileevent $inputC writable $writable

    array set props [set status [tls::status $inputC]]

    if {[::info exists props(sbits)]} {
        set sbits $props(sbits)
        unset props(sbits)

        if {$sbits >= 112} {
            set privacy strong
        } elseif {$sbits >= 40} {
            set privacy weak
        } else {
            set privacy none
        }
    } else {
        set sbits 0

        if {(![::info exists props(cipher)]) \
                || (![string compare $props(cipher) ""])} {
            set privacy none
        } else {
            set privacy weak
            if {[string first EXP- $props(cipher)] != 0} {
                foreach x {DES-CBC3 RC4 IDEA} {
                    if {[string first $x $props(cipher)] >= 0} {
                        set privacy strong
                        break
                    }
                }
            }
        }
    }

    set cipher $props(cipher)
    unset props(cipher)
    array set local {}
    if {![catch { array set local [tls::status -local $state(socketC)] }]} {
        unset local(sbits)
        unset local(cipher)
    }

    if {[catch { beepcore::sasl::id2name $logT \
                     [set realname $props(subject)] } authname]} {
        set authname ""
        set realname ""
    }

    set ::beepcore::server::tuning \
        [list privacy  $privacy  \
              sbits    $sbits    \
              authname $authname \
              realname $realname \
              sasl     ""        \
              tls      [list cipher $cipher           \
                             remote [array get props] \
                             local  [array get local]]]
}


#
# XML parsing
#

proc beepcore::profile::tlsv1::element {token tag name {av {}}} {
    variable $token
    upvar 0 $token state

    switch -- $tag {
        start {
            if {([llength $state(stack)] > 0) \
                    || ([string compare $name ready])} {
                set state(code) 501
                oops "not expecting <$name> element"
            }
            array set attrs [list version 1]
            array set attrs $av
            if {[string compare $attrs(version) 1]} {
                set state(code) 501
                oops "version attribute poorly formed in <$name> element"
            }
            set state(version) $attrs(version)

            lappend state(stack) [list $name $av "" ""]
        }

        end {
            set state(stack) [lreplace $state(stack) end end]
        }
    }
}


proc beepcore::profile::tlsv1::cdata {token text} {
    variable $token
    upvar 0 $token state

    if {![string compare [string trim $text] ""]} {
        return
    }

    oops "unexpected character data"
}


proc beepcore::profile::tlsv1::oops {args} {
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
