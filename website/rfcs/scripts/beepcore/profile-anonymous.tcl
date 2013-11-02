#
# profile-anonymous.tcl - the anonymous SASL profile
#


package provide beepcore::profile::anonymous  1.0

package require beepcore::log
package require beepcore::sasl
package require beepcore::util


#
# state variables:
#
#    logT: token for logging package
#    saslT: token for SASL package
#


namespace eval beepcore::profile::anonymous {
    variable anonymous
    array set anonymous { uid 0 }

    namespace export info boot init fin exch
}


proc beepcore::profile::anonymous::info {logT} {
    return [list 0 \
                 [list http://iana.org/beep/SASL/ANONYMOUS] \
                 [list bootV [namespace current]::boot \
                       initV [namespace current]::init \
                       exchV [namespace current]::exch \
                       finV  [namespace current]::fin]]
}


proc beepcore::profile::anonymous::boot {logT} {
    global errorCode errorInfo

    beepcore::sasl::tuneP

    if {[set code [catch { beepcore::sasl::init $logT "" anonymous } saslT]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error sasl::init $saslT

        return -code $code -errorinfo $einfo -errorcode $ecode $saslT
    }

    set code [catch { beepcore::sasl::fetch $saslT anonymous } result]
    set ecode $errorCode
    set einfo $errorInfo

    if {($code != 0) && ($code != 7)} {
        beepcore::log::entry $logT error sasl::fetch $result
        set code 7
        set result [list code 451 diagnostic $result]
    }

    if {[catch { beepcore::sasl::fin $saslT } result2]} {
        beepcore::log::entry $state(logT) error sasl::fin $result2
    }

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


proc beepcore::profile::anonymous::init {logT serverD clientA upcallV uri} {
    global errorCode errorInfo

    beepcore::sasl::tuneP

    variable anonymous

    set token [namespace current]::[incr anonymous(uid)]

    variable $token
    upvar 0 $token state

    if {[set code [catch { beepcore::sasl::init $logT $clientA anonymous } \
                         saslT]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error sasl::init $saslT

        return -code $code -errorinfo $einfo -errorcode $ecode $saslT
    }

    array set state [list logT $logT saslT $saslT]

    return $token
}


proc beepcore::profile::anonymous::fin {token status} {
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



proc beepcore::profile::anonymous::exch {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    beepcore::sasl::tuneP 1

    switch -- [set code [catch { beepcore::sasl::parse $state(saslT) $data } \
                               result]] {
        0 {
            return [exch1 $token $result]
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


proc beepcore::profile::anonymous::exch1 {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set parse $data
    set trace $parse(blob)

    switch -- [set code [catch { beepcore::sasl::fetch $state(saslT) \
                                     anonymous } result]] {
        0 {
        }

        7 {
            array set response $result
            if {$response(code) == 550} {
                set response(diagnostic) "anonymous login not allowed"
            }
            return -code 7 [beepcore::util::xml_error $response(code) \
                                $response(diagnostic)]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::fetch $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    if {[string length $trace] > 255} {
        return -code 7 [beepcore::util::xml_error 551 \
                            "poorly formed trace information"]
    }
        
    beepcore::sasl::login $state(saslT) anonymous [list trace $trace]

    return "<blob status='complete' />"
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
