#
# profile-otp.tcl - the one-time password SASL profile
#


package provide beepcore::profile::otp   1.0

package require beepcore::log
package require beepcore::sasl
package require beepcore::util


#
# state variables:
#
#    logT: token for logging package
#    saslT: token for SASL package
#    rspP: expecting response
#    account: authname information
#    username: desired username
#    loseP: sent losing <challenge> (on purpose)
#    updateP: need to update SASL database
#


namespace eval beepcore::profile::otp {
    variable otp
    array set otp { uid 0 }

    namespace export info boot init fin exch \
                     makeseed
}


proc beepcore::profile::otp::info {logT} {
    return [list 0 \
                 [list http://iana.org/beep/SASL/OTP] \
                 [list bootV [namespace current]::boot \
                       initV [namespace current]::init \
                       exchV [namespace current]::exch \
                       finV  [namespace current]::fin]]
}


proc beepcore::profile::otp::boot {logT} {
    beepcore::sasl::tuneP

# for base64, hex, otp_md5, otp_sha1, otp_words
    if {[catch { package require Trf 2 } result]} {
        return -code 7 [list code 451 diagnostic $result]
    }
}


proc beepcore::profile::otp::init {logT serverD clientA upcallV uri} {
    global errorCode errorInfo

    beepcore::sasl::tuneP

    variable otp

    set token [namespace current]::[incr otp(uid)]

    variable $token
    upvar 0 $token state

    if {[set code [catch { beepcore::sasl::init $logT $clientA otp } saslT]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error sasl::init $saslT

        return -code $code -errorinfo $einfo -errorcode $ecode $saslT
    }

    array set state [list logT $logT saslT $saslT rspP 0 account "" \
                          username "" loseP 0 updateP 0]

    return $token
}


proc beepcore::profile::otp::fin {token status} {
    variable $token
    upvar 0 $token state

    if {[catch { beepcore::sasl::fin $state(saslT) } result]} {
        beepcore::log::entry $state(logT) error sasl::fin $result
    }

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}


proc beepcore::profile::otp::exch {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    beepcore::sasl::tuneP 1

    if {!$state(rspP)} {
        set state(account) ""
        set state(username) ""
        set state(loseP) 0
        set state(updateP) 0
    }
    switch -- [set code [catch { beepcore::sasl::parse $state(saslT) $data } \
                               result]] {
        0 {
            if {$state(rspP)} {
                return [exch2 $token $result]
            } else {
                return [exch1 $token $result]
            }
        }

        7 {
            set state(rspP) 0

            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::parse $result

            set state(rspP) 0

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::profile::otp::exch1 {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set parse $data

    if {[set x [string first "\0" $parse(blob)]] < 0} {
        return -code 7 [beepcore::util::xml_error 501 "missing NUL separator"]
    }
    set state(username) [string range $parse(blob) 0 [expr $x-1]]
    set authname [string range $parse(blob) [expr $x+1] end]
    if {![string compare $state(username) ""]} {
        set state(username) $authname
    }
    if {![string compare $authname ""]} {
        set authname $state(username)
    }

    switch -- [set code [catch { beepcore::sasl::lock $state(saslT) \
                                     $authname } result]] {
        0 {
        }

        7 {
            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::lock $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    switch -- [set code [catch { beepcore::sasl::fetch $state(saslT) \
                                     $authname } result]] {
        0 {
            array set info [set state(account) $result]
            array set otp $info(authentication)
        }

        7 {
            array set response $result
            if {$response(code) != 550} {
                release $token $authname
                return -code 7 [beepcore::util::xml_error $response(code) \
                                    $response(diagnostic)]
            }

            set state(loseP) 1
            array set otp [list sequence  1[expr [clock seconds]%1000] \
                                seed      [makeseed]                   \
                                algorithm md5                          \
                                key       0]
            set state(account) [list name $authname \
                                     authentication [array get otp]]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::fetch $result

            release $token $authname

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    if {$otp(sequence) <= 1} {
        release $token $authname

        return -code 7 [beepcore::util::xml_error 534 "sequence exhausted"]
    }

    set state(rspP) 1

    set data "otp-$otp(algorithm) [expr $otp(sequence)-1] $otp(seed) ext"
    beepcore::log::entry $state(logT) debug challenge $data

    return [beepcore::util::xml_blob $data]
}


proc beepcore::profile::otp::release {token authname} {
    variable $token
    upvar 0 $token state

    switch -- [catch { beepcore::sasl::release $state(saslT) $authname } \
                     result] {
        0 {
        }

        7 {
            array set response $result
            beepcore::log::entry $state(logT) notify beepcore::sasl::release \
                       "$response(code): $response(diagnostic)"
        }

        default {
            beepcore::log::entry $state(logT) notify beepcore::sasl::release \
                $result
        }
    }
}


proc beepcore::profile::otp::exch2 {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    set state(code) 500
    set state(diagnostic) ""

    set code [catch { exch2aux $token $data } result]
    set ecode $errorCode
    set einfo $errorInfo

    unset state(code) \
          state(diagnostic)

    array set info $state(account)
    set authname $info(name)
    if {$state(updateP)} {
        switch -- [catch { beepcore::sasl::store $state(saslT) $authname \
                               $state(account) } result2] {
            0 {
            }

            7 {
                array set response $result2
                beepcore::log::entry $state(logT) notify \
                    sasl::store "$response(code): $response(diagnostic)"
            }

            default {
                beepcore::log::entry $state(logT) notify \
                    sasl::store $result2
            }
        }
    }

    release $token $authname

    set state(rspP) 0

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


proc beepcore::profile::otp::exch2aux {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set parse $data

    if {![string compare $parse(status) abort]} {
        return "<blob status='complete' />"
    }

    set response [string trim [string tolower $parse(blob)]]
    beepcore::log::entry $state(logT) debug response $response

    if {[catch { split $response ":" } parts]} {
        set state(diagnostic) "extended response poorly formatted"
        return -code 7 [beepcore::util::xml_error $state(code) \
                            $state(diagnostic)]
    }

    array set info $state(account)
    array set otp $info(authentication)

    switch -- [lindex $parts 0]/[llength $parts] {
        hex/2
            -
        init-hex/4 {
            set key [parse_hex $token [lindex $parts 1]]
        }

        word/2
            -
        init-word/4 {
            set key [parse_words $token [lindex $parts 1]]
        }

        default {
            if {[set len [llength $parts]] != 1} {
                set s s
            } else {
                set s ""
            }
            if {$len == 0} {
                set state(diagnostic) "expecting a non-empty extended response"
            } else {
                set state(diagnostic) \
                    "not expecting \"[lindex $parts 0]\" with $len argument$s"
            }
        }
    }
    if {[string length $state(diagnostic)] > 0} {
        return -code 7 [beepcore::util::xml_error $state(code) \
                            $state(diagnostic)]
    }

    if {$state(loseP)} {
        beepcore::sasl::failure $state(saslT) $info(name) \
                      [list code 535 diagnostic "account unknown"]
        return -code 7 [beepcore::util::xml_error 535 "account unknown"]
    }

    if {[string compare [hex -mode decode -- $otp(key)] \
                        [otp_$otp(algorithm) -- $key]]} {
        beepcore::sasl::failure $state(saslT) $info(name) \
                      [list code 535 diagnostic "digest mismatch"]
        return -code 7 [beepcore::util::xml_error 535 "account unknown"]
    }

    set state(updateP) 1
    incr otp(sequence) -1
    set otp(key) [hex -mode encode -- $key]
    array set init ""
    switch -- [lindex $parts 0] {
        init-hex {
            array set init [parse_params $token $otp(seed) [lindex $parts 2]]
            set init(key) [hex -mode encode -- \
                               [parse_hex $token [lindex $parts 3]]]
        }

        init-word {
            array set init [parse_params $token $otp(seed) [lindex $parts 2]]
            set init(key) [hex -mode encode -- \
                               [parse_words $token [lindex $parts 3]]]
        }
    }
    if {[string length $state(diagnostic)] > 0} {
        return -code 7 [beepcore::util::xml_error $state(code) \
                            $state(diagnostic)]
    }
    array set otp [array get init]
    set info(authentication) [array get otp]
    set state(account) [array get info]


    switch -- [set code [catch { beepcore::sasl::proxyP $state(saslT) \
                                     $info(name) $state(username) } result]] {
        0 {
            beepcore::sasl::login $state(saslT) $state(username)

            return "<blob status='complete' />"
        }

        7 {
            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::proxyP $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::profile::otp::parse_hex {token text} {
    variable $token
    upvar 0 $token state

    set hex ""
    foreach c [split $text ""] {
        append hex [string trim $c]
    }
    if {[string length $hex] != 16} {
        set state(code) 501
        set state(diagnostic) "expecting 16 hexadecimal characters"
        return
    }

    if {[catch { hex -mode decode -- $hex } result]} {
        set state(code) 501
        set state(diagnostic) $result
        return
    }

    return $result
}


proc beepcore::profile::otp::parse_words {token text} {
    variable $token
    upvar 0 $token state

    set s ""
    if {[set x [llength [set words [split [string trim $text]]]]] != 6} {
        if {$x != 1} {
            set s s
        }
        set state(code) 501
        set state(diagnostic) "expecting 6, not $x, word$s"
        return
    }

    set text ""
    foreach word $words {
        append text $s $word
        set s " "
    }
    if {[catch { otp_words -mode decode -- $text } result]} {
        set state(code) 501
        set state(diagnostic) $result
        return
    }

    return $result
}


proc beepcore::profile::otp::parse_params {token oseed text} {
    variable $token
    upvar 0 $token state

    if {[llength [set terms [split $text]]] != 3} {
        set state(code) 501
        set state(diagnostic) "expecting 3 terms for new parameters"
        return
    }

    switch -- [set algorithm [lindex $terms 0]] {
        md5
            -
        sha1 {
        }

        default {
            set state(code) 504
            set state(diagnostic) \
                "only the MD5 and SHA1 algorithms are supported"
            return
        }
    }

    if {[scan [lindex $terms 1] "%d" sequence] !=1} {
        set state(code) 501
        set state(diagnostic) "sequence-number is poorly formed"
        return
    } 
    if {($sequence < 100) || ($sequence > 9999)} {
        set state(code) 501
        set state(diagnostic) "sequence-number not in 100..9999 range"
        return
    }

    if {([set len [string length [set seed [lindex $terms 2]]]] < 1) \
            || ($len > 16)} {
        set state(code) 501
        set state(diagnostic) "seed length not in 1..16 range"
        return
    }
    if {![regexp -- {^[A-Za-z0-9]+$} $seed]} {
        set state(code) 501
        set state(diagnostic) "seed is poorly formed"
        return
    }
    if {![string compare $seed $oseed]} {
        set state(code) 534
        set state(diagnostic) "seed not updated"
        return
    }

    return [list algorithm $algorithm sequence $sequence \
                 seed [string tolower $seed]]
}


proc beepcore::profile::otp::makeseed {} {
    set seed ""
    foreach c [split [string tolower [::info hostname]] ""] {
        if {[regexp -- {^[A-Za-z0-9]+$} $c]} {
            append seed $c
        }
    }
    append seed [expr [clock seconds]%100000]
    if {[set len [string length $seed]] > 16} {
        set seed [string range $seed [expr $len-16] end]
    }

    return $seed
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
