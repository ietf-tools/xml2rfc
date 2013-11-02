#
# beep-server.tcl - BEEP server loop
#


package provide beepcore::server  1.1

package require beepcore::log
package require beepcore::peer
package require beepcore::util

package require mime


#
# namespace variables:
#
#    tuning: tuning properties
#       privacy: none, weak, strong
#       sbits:   0..256
#       sasl:    props: mechanism
#       tls:     props: subject issuer notBefore notAfter serial cipher ?sbits?
#
# state variables:
#
#    logT: token for logging package
#    serverD: domain name offering this service
#    clientA: serialized array of client information
#    inputC: channel for reading
#    outputC: channel for writing
#    plaintextL: vector of supported profiles for plaintext operation
#    encryptedL: vector of supported profiles for encrypted operation
#    peerT: token for peer package
#    firstP: waiting for first successful start
#    restartP: waiting to restart
#    callback: for transport security profiles
#    methods: serialized array mapping channel to profile's method
#    event: the terminal event
#    hackNo: hack to support answers in ::upcall
#


namespace eval beepcore::server {
    variable beep
    array set beep { uid 0 }

    variable tuning [list privacy none sbits 0 authname "" realname "" \
                          sasl "" tls ""]

    namespace export init loop getmethod
}

proc beepcore::server::init {logT serverD clientA inputC outputC plaintextL 
                           encryptedL} {
    variable beep

    set token [namespace current]::[incr beep(uid)]

    variable $token
    upvar 0 $token state

    tclLog "start beep::init"

    if {![string compare $outputC ""]} {
        set outputC $inputC
    }
    if {[llength $plaintextL] == 0} {
        error "no bootable profiles!"
    }

    if {[file exists etc/serverD]} {
        source etc/serverD
    }

    array set state [list logT $logT serverD $serverD clientA $clientA \
                          inputC $inputC outputC $outputC \
                          plaintextL $plaintextL encryptedL $encryptedL \
                          peerT "" firstP 1 restartP 0 callback "" \
                          methods {} event ""]

    tclLog "end beep::init"

    return $token
}


# return code usage:
#
#     0: send RSP
#     7: send ERR
#     8: send RSP, eval callback, do tuning reset
#     9: send NUL
#    10: send ERR, eval callback, do tuning reset
#
# if callback does "-code 7", exit instead of doing a tuning reset

proc beepcore::server::loop {token} {
    global debugP
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable tuning
    beepcore::log::entry $state(logT) info tuning $tuning

    array set tuningA $tuning
    if {[string compare $tuningA(privacy) none]} {
        set profiles $state(encryptedL)
    } else {
        set profiles $state(plaintextL)
    }
    set allowed {}
    set possible {}
    foreach profile $profiles {
        catch { unset vector }
        array set vector [lindex $profile 1]
        if {[info exists vector(boot2V)]} {
            switch -- [catch  { eval $vector(boot2V) \
                                     [list $state(logT) \
                                           [lindex $profile 0]] } result] {
                0 {
                    lappend allowed $profile
                }
            
                7 {
                    array set response $result
                    if {$response(code) != 520} {
                        beepcore::log::entry $state(logT) user \
                            "$response(code): $response(diagnostic)"
                    } else {
                        beepcore::log::entry $state(logT) debug \
                            [lindex $vector(boot2V) 0] $result
                    }
                }

                default {
                    beepcore::log::entry $state(logT) error \
                        [lindex $vector(boot2V) 0] $result
                }
            }
        } else {
            switch -- [catch  { eval $vector(bootV) \
                                     [list $state(logT)] } result] {
                0 {
                    lappend possible $profile
                }
            
                7 {
                    array set response $result
                    if {$response(code) != 520} {
                        beepcore::log::entry $state(logT) user \
                            "$response(code): $response(diagnostic)"
                    } else {
                        beepcore::log::entry $state(logT) debug \
                            [lindex $vector(bootV) 0] $result
                    }
                }

                default {
                    beepcore::log::entry $state(logT) error \
                        [lindex $vector(bootV) 0] $result
                }
            }
        }
    }
    set profiles $allowed
    foreach profile $possible {
        if {[lsearch -glob $profiles "[lindex $profile 0] *"] < 0} {
            lappend profiles $profile
        }
    }

    set uris {}
    foreach profile $profiles {
        lappend uris [lindex $profile 0]
    }
    set uris [lsort -dictionary $uris]

    tclLog "start beep::loop"

    if {[set code [catch {
        set state(peerT) [beepcore::peer::join $state(logT) \
                              [list $state(inputC) $state(outputC)] \
                              -profiles      $uris \
                              -initiator     false \
                              -eventCallback [list [namespace current]::eventCallback \
                                                   $token] \
                              -startCallback [list [namespace current]::startCallback \
                                                   $token $profiles]]
    } result]]} {
        set ecode $errorCode
        set einfo $errorInfo

        if {($code != 8) && ($code != 10)} {
            foreach name [array names state] {
                unset state($name)
            }
            unset $token

            tclLog "end beep::loop"

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    if {($code != 8) && ($code != 10)} {
        beepcore::peer::wait $state(peerT) -timeout [expr 10*60*1000] \
            -msgNos new
    }

    if {([set eventP [string compare $state(event) ""]]) \
            || (!$state(restartP))} {
        if {$eventP} {
            array set response $state(event)

            if {$response(code) <= 299} {
                set code 0
            } else {
                set code 7
            }
        } else {
            if {[catch { beepcore::peer::done $state(peerT) -release \
                             abortive } result]} {
                beepcore::log::entry $state(logT) error peer::done $result
            }

            set code 7
            set response(diagnostic) timeout
        }

        foreach name [array names state] {
            unset state($name)
        }
        unset $token

        tclLog "end beep::loop"

        return -code $code $response(diagnostic)
    }

    # the $state(callback) does the negotiation after the peer loop exits
    if {[set code [catch { eval $state(callback) \
                                [list $state(logT) $state(inputC)] } \
                         result]]} {
        if {$code == 7} {
            array set response $result

            if {$response(code) <= 299} {
                set code 0
            } else {
                set code 7
            }

            foreach name [array names state] {
                unset state($name)
            }
            unset $token

            tclLog "end beep::loop"


            return -code $code $response(diagnostic)
        }

        beepcore::log::entry $state(logT) error [lindex $state(callback) 0] \
            $result
    }

    # tuning is now finished, in case you're wondering why we recurse here...
    set state(firstP) 1
    set state(restartP) 0
    set state(callback) ""
    set state(methods) {}

    tclLog "end beep::loop"

    return [loop $token]
}


proc beepcore::server::eventCallback {token peerT args} {
    variable $token
    upvar 0 $token state

    array set argv [set state(event) $args]

    if {[catch { beepcore::peer::done $peerT -release terminal } result]} {
        beepcore::log::entry $state(logT) error peer::done $result
    }
}


proc beepcore::server::startCallback {token profiles peerT args} {
    variable $token
    upvar 0 $token state

    array set argv $args

    if {$state(firstP)} {
        catch { beepcore::util::xml_localize [beepcore::peer::getprop $peerT \
                    localize] }
    }

    set hitP 0

    for {set x 0} {$x < [llength $argv(profiles)]} {incr x} {
        set profile [lindex $argv(profiles) $x]
        for {set y 0} {$y < [llength $profiles]} {incr y} {
            set entry [lindex $profiles $y]
            if {![string compare $profile [lindex $entry 0]]} {
                set hitP 1
                array set vector [lindex $entry 1]
                break
            }
        }
        if {$hitP} break
    }

    if {!$hitP} {
        return -code 7 [list code       550                      \
                             diagnostic "no acceptable profiles" \
                             language   en-US]
    }

    if {($state(firstP)) && ([string compare $argv(serverName) ""])} {
        if {[lsearch -exact $state(serverD) $argv(serverName)] < 0} {
            return -code 7 [list code       501 \
                                 diagnostic "serverName attribute is unacceptable" \
                                 language   en-US]
        }
        set state(serverD) $argv(serverName)
    }
    set state(firstP) 0

    if {[set exch2P [info exists vector(exch2V)]]} {
        set exchV "$vector(exch2V) $peerT"
    } else {
        set exchV $vector(exchV)
    }

    switch -- [set code [catch { eval $vector(initV) \
                      [list $state(logT) $state(serverD) $state(clientA) \
                           [list [namespace current]::upcall $token $exch2P \
                                  [set channelNumber $argv(channelNumber)]] \
                            $profile] } profileT]] {
        0 {
        }

        7 {
            return -code 7 $profileT
        }

        default {
            beepcore::log::entry $state(logT) error \
                [lindex $vector(initV) 0] $profileT

            return -code 7 [list code 550 diagnostic $profileT language en-US]
        }
    }

    catch {
        array set methods $state(methods)
        set methods($channelNumber) $vector(methodV)
        lappend methods($channelNumber) $profileT
        set state(methods) [array get methods]
    }

    if {[set len [string length \
                         [set data [string trim [lindex $argv(data) $x]]]]] \
            > 0} {
        set state(callback) ""

        if {$exch2P} {
            set data [mime::initialize -canonical application/octet-stream \
                          -string $data]
        }

        tclLog "eval [set downcall [lindex $exchV 0]]"
        switch -- [set code [catch { eval $exchV [list $profileT $data] } \
                                   data]] {
            0 -  7 {
            }

            8 - 10 {
                beepcore::peer::wait $peerT -drain true

                set state(callback) [lindex $data 1]
                set data [lindex $data 0]
            }

            default {
                beepcore::log::entry $state(logT) error $downcall $data

                set data [beepcore::peer::errfmt2 $state(peerT) 550 $data \
                              en-US]
            }
        }
        tclLog "end $downcall"

        if {$exch2P} {
            set data [mime::getbody [set mimeT $data]]
            mime::finalize $mimeT
        }
    } else {
        set len no
    }

    beepcore::peer::accept $peerT $argv(channelNumber) $profile \
        -datum $data \
        -messageCallback [list [namespace current]::messageCallback $token \
                                   $profileT $exchV $exch2P] \
        -releaseCallback [list [namespace current]::releaseCallback $token \
                                   $profileT $vector(finV)]

    beepcore::log::entry $state(logT) info start $profile ($len payload)

    if {[string compare $state(callback) ""]} {
        beepcore::peer::wait $peerT -drain true
        beepcore::peer::done $peerT -release terminal

        set state(restartP) 1
        array set $peerT [list restartP 1]
        return -code $code
    }
}


proc beepcore::server::messageCallback {token profileT exchV exch2P channelT 
                                      args} {
    variable beep

    variable $token
    upvar 0 $token state

    array set argv $args

    if {$exch2P} {
        set data $argv(mimeT)
    } else {
        if {[string compare [set content [mime::getproperty $argv(mimeT) \
                                                content]] \
                            application/beep+xml]} {
            mime::finalize $argv(mimeT)

            set mimeT [beepcore::peer::errfmt $state(peerT) 500 \
                          "expecting application/beep+xml in request, not $content" \
                          en-US]

            beepcore::peer::reply $channelT $argv(serialNumber) $mimeT \
                -status negative

            mime::finalize $mimeT

            return
        }

        set data [mime::getbody $argv(mimeT)]

        mime::finalize $argv(mimeT)
    }

    set state(callback) ""
    set state(hackNo) $argv(serialNumber)
    set status negative
    tclLog "eval [set downcall [lindex $exchV 0]]"
    switch -- [set code [catch { eval $exchV [list $profileT $data] } data]] {
        0 {
            set status positive
        }

        7 {
        }

        8 - 10 {
            if {$code == 8} {
                set status positive
            } else {
                set status negative
            }
            set state(callback) [lindex $data 1]
            set data [lindex $data 0]
            beepcore::peer::wait $state(peerT) -drain true
        }

        9 {
            set status nul
        }

        default {
            beepcore::log::entry $state(logT) error $downcall $data

            set data [beepcore::peer::errfmt2 $state(peerT) 550 $data en-US]
        }
    }
    tclLog "end $downcall"

    if {$exch2P} {
        set mimeT $data
    } else {
        set mimeT [beepcore::peer::str2xml $data]
    }

    beepcore::peer::reply $channelT $argv(serialNumber) $mimeT \
        -status $status

    mime::finalize $mimeT

    if {[string compare $state(callback) ""]} {
        beepcore::peer::wait $state(peerT) -drain true
        beepcore::peer::done $state(peerT) -release terminal

        set state(restartP) 1
    }
}


proc beepcore::server::releaseCallback {token profileT finV channelT source
                                      mode} {
    variable $token
    upvar 0 $token state

    if {![string compare $finV ""]} {
        return
    }

    switch -- $mode {
        commit {
            set status +
        }

        abort {
            set status -
        }

        default {
            return
        }
    }

    if {[catch { eval $finV [list $profileT $status] } result]} {
        beepcore::log::entry $state(logT) error [lindex $finV 0] $result
        if {![string compare $mode commit]} {
            return -code 7 [list code 550 diagnostic $result language en-US]
        }
    }
}


proc beepcore::server::upcall {token exch2P channelNumber data rspV args} {
    variable $token
    upvar 0 $token state

    if {$exch2P} {
        set mimeT $data
    } else {
        set mimeT [beepcore::peer::str2xml $data]
    }

    array set argv [list -mode request]
    array set argv $args

    switch -- $argv(-mode) {
        request {
            beepcore::peer::message [beepcore::peer::getprop $state(peerT) \
                                         $channelNumber] $mimeT \
                -replyCallback [list [namespace current]::replyCallback \
                                          $token $rspV $exch2P]
        }

        answer {
            beepcore::peer::reply [beepcore::peer::getprop $state(peerT) \
                                       $channelNumber] \
                $state(hackNo) $mimeT -status answer -ansNo $argv(-ansNo)
        }

        default {
            error "unknown argument to -mode: $argv(-mode)"
        }
    }

    if {!$exch2P} {
        mime::finalize $mimeT
    }
}


proc beepcore::server::replyCallback {token rspV exch2P channelT args} {
    variable beep

    variable $token
    upvar 0 $token state

    array set argv $args

    switch -- $exch2P/$argv(status) {
        0/positive {
            set status +
        }

        0/negative {
            set status -
        }

        default {
            set status $argv(status)
        }
    }

    if {$exch2P} {
        set data $argv(mimeT)
    } else {
        if {[string compare [set content [mime::getproperty $argv(mimeT) \
                                              content]] \
                            application/beep+xml]} {
            set data [beepcore::peer::errfmt2 $state(peerT) 500 \
                          "expecting application/beep+xml in response, not $content" \
                          en-US]
        } else {
            set data [mime::getbody $argv(mimeT)]
        }

        mime::finalize $argv(mimeT)
    }

    if {[catch { eval $rspV [list $status $data] } result]} {
        beepcore::log::entry $state(logT) error [lindex $rspV 0] $result
    }
}


proc beepcore::server::getmethod {token channelNumber} {
    variable $token
    upvar 0 $token state

    if {[catch { beepcore::peer::getprop $state(peerT) $channelNumber }]} {
        error "no such channel $channelNumber"
    }

    array set methods $state(methods)
    if {![info exists methods($channelNumber)]} {
        error "no method registered for channel $channelNumber"
    }

    return $methods($channelNumber)
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
