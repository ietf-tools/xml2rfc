#
# beep-client.tcl - BEEP client API
#


package provide beepcore::client 1.1

package require beepcore::log
package require beepcore::peer
package require beepcore::util

package require mime
package require smtp


#
# state variables:
#
#    logT: token for logging package
#    serverD: domain name of offered service
#    options: options to beepcore::client::init
#    magicP: preserve socketC/peerT
#    socketC: channel for reading
#    peerT: token for peer package
#    reqno: last reqno used
#    eofP: responded to request to release connection
#    errP: saw error on connection
#    notifyA: array of notification vectors
#    debugZ: initial debug setting
#    fastP: doing fast start
#    tlsT: token for TLS channel
#    saslT: token for SASL channel
#    cyrusT: token for Tcl SASL package (optional)
#    tls_handshake_done: Filled in when TLS handshake is done
#    tls_fail_count: Counts failures, since SSL is screwy
#    tuning: tuning properties
#       privacy: none, weak, strong
#       sbits:    0..256
#       authname: ""
#       realname: ""
#       sasl:     { mechanism }
#       tls:      { subject issuer notBefore notAfter serial cipher ?sbits? }
#


namespace eval beepcore::client {
    variable client
    array set client { uid 0 }

    namespace export init fin \
                     profiles tuningA create destroy exch errscan peerT
}

proc beepcore::client::init {logT serverD args} {
    global errorCode errorInfo

    array set options $args
    if {![info exists options(-tunnel)]} {
        return [eval init_aux [list $logT $serverD] $args]
    }
    unset options

    array set hopopts {}
    array set peeropts {}
    foreach {k v} $args {
        switch -glob -- $k {
            -tunnel {
                set tunnel $v
            }

            -tunnel.* {
                set k [string range $k 8 end]
                set hopopts(-$k) $v
            }

            default {
                set peeropts($k) $v
            }
        }
    }

    foreach p [list debug port service] {
        if {[catch { set hopopts(-$p) }]} {
            catch { set hopopts(-$p) $peeropts(-$p) }
        }
    }
    set hopopts(-signed) false
    set hopopts(-privacy) none
    if {![info exists hopopts(-servername)]} {
        set hopopts(-servername) ""
    }

    variable [set token [eval init_aux [list $logT $serverD] \
                                  [array get hopopts]]]
    upvar 0 $token state

    set profile http://xml.resource.org/profiles/TUNNEL
    if {[lsearch -exact [beepcore::peer::getprop $state(peerT) profiles] \
                 $profile] < 0} {
        if {[catch { fin $token } result]} {
            beepcore::log::entry $logT error client::fin $result
        }

        return -code 7 [list code 550 \
                             diagnostic "TUNNEL profile not available"]
    }

    set code [catch {
        set ewhat peer::setprop
        beepcore::peer::setprop $state(peerT) updateSeq 0

        set ewhat peer::start
        set tunnelT [beepcore::peer::start $state(peerT) [list $profile] \
                         -data [list $tunnel]]

        set ewhat peer::getprop
        set data [beepcore::peer::getprop $tunnelT datum]
        if {[string first <error $data] >= 0} {
            return -code 7 [beepcore::peer::errscan2 $state(peerT) $data]
        }

        set ewhat peer::join
        catch { beepcore::peer::done $state(peerT) -release terminal }
        set state(peerT) [beepcore::peer::join $logT $state(socketC) \
                              -serverName $hopopts(-servername)]
        set peeropts(-socketC) $state(socketC)
        set peeropts(-peerT) $state(peerT)
        set peeropts(-magicP) false

        set ewhat client::init_aux
        eval init_aux [list $logT ""] [array get peeropts]
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    if {$code} {
        if {$code == 2} {
            set code 7
        }
        if {$code != 7} {
            beepcore::log::entry $logT error $ewhat $result
        }
    } else {
        set state(magicP) 1
    }

    if {[catch { fin $token } result2]} {
        beepcore::log::entry $logT error client::fin $result2
    }

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc beepcore::client::init_aux {logT serverD args} {
    global debugP
    global errorCode errorInfo

    variable client

    set token [namespace current]::[incr client(uid)]

    variable $token
    upvar 0 $token state

    array set options [list -debug      false    -magicP true  \
                            -mechanism  none     -signed false \
                            -privacy    optional               \
                            -port 10288          -service ""   \
                            -servername ""]
    array set options $args
    set debugZ $debugP
    if {(!$debugP) \
            && ([set options(-debug) [smtp::boolean $options(-debug)]])} {
        set debugP 1
    }
    if {[set options(-signed) [smtp::boolean $options(-signed)]]} {
        if {([string compare $options(-privacy) none]) \
                && ([string compare $options(-privacy) optional])} {
            set options(-signed) 0
        } elseif {[catch { package require sasl }]} {
            set options(-signed) 0
            set options(-privacy) weak
        } elseif {![string compare $options(-mechanism) none]} {
            set options(-mechanism) any
        }
    }
    if {(![string compare $options(-service) ""]) \
            || ([catch { package require srvrr }])} {
        set args {}
    } else {
        srvrr::toggle 1
        set args [list -service $options(-service)]
    }

    if {![catch { set options(-peerT) } peerT]} {
        set code 0
        set socketC $options(-socketC)
        set magicP [smtp::boolean $options(-magicP)]
    } elseif {[set code [catch {
        set socketC [eval socket $args [list $serverD $options(-port)]]
    } result]]} {
        set ecode $errorCode
        set einfo $errorInfo
        set ewhat socket
    } elseif {[set code [catch {
        set peerT [beepcore::peer::join $logT $socketC \
                       -serverName $options(-servername)]
    } result]]} {
        set ecode $errorCode
        set einfo $errorInfo
        set ewhat peer::join

        if {[catch { close $socketC } result2]} {
            beepcore::log::entry $logT system $result2
        }
    } else {
        set magicP 0
    }

    if {$code} {
        beepcore::log::entry $logT error $ewhat $result

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }

    array set state [list logT $logT serverD $serverD magicP $magicP \
                          options [array get options] socketC $socketC \
                          peerT $peerT reqno 0 eofP 0 \
                          errP 0 notifyA "" debugZ $debugZ fastP 0 \
                          tlsT "" saslT "" cyrusT "" \
                          tuning [list privacy none sbits 0 authname "" \
                                       realname "" sasl "" tls ""]]

    if {[set code [catch {
        beep_start $token
        tls_start $token
        sasl_start $token
    } result]]} {
        set ecode $errorCode
        set einfo $errorInfo

        switch -- $code {
            7 {
                beepcore::log::entry $state(logT) user $result
            }

            default {
                beepcore::log::entry $state(logT) error client::start $result
            }
        }

        if {[catch { fin $token } result2]} {
            beepcore::log::entry $state(logT) error client::fin $result2
        }

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }

    beepcore::log::entry $state(logT) info tuning $state(tuning)

    if {$state(magicP)} {
        fin $token
    } else {
        return $token
    }
}

proc beepcore::client::fin {token} {
    global debugP

    variable $token
    upvar 0 $token state

    set debugZ $state(debugZ)

    array set options $state(options)

    if {!$state(magicP)} {
        set closeP 0
        if {(!$state(eofP)) \
                && (!$state(errP)) \
                && (!$state(fastP))} {
            if {[catch { beepcore::peer::done $state(peerT) } result]} {
                beepcore::log::entry $state(logT) error peer::done $result
            } else {
                set closeP 1
            }
        }
        if {(!$closeP) \
                && ([catch { beepcore::peer::done $state(peerT) \
                                 -release terminal } result])} {
            beepcore::log::entry $state(logT) error peer::done $result
        }
    
        if {[catch { close $state(socketC) } result]} {
            beepcore::log::entry $state(logT) system $result
        }
    }

    if {([string compare $state(cyrusT) ""]) \
            && ([catch { rename $state(cyrusT) {} } result])} {
        beepcore::log::entry $state(logT) system $result
    }

    set debugP $debugZ

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}


#
# direct beep access
#

proc beepcore::client::profiles {token} {
    variable $token
    upvar 0 $token state

    if {[lsearch -exact [beepcore::peer::getprop $state(peerT) -names] \
                 profiles] < 0} {
        beepcore::peer::wait $state(peerT) -msgNos [list 0]
    }

    return [beepcore::peer::getprop $state(peerT) profiles]
}

proc beepcore::client::tuningA {token} {
    variable $token
    upvar 0 $token state

    return $state(tuning)
}

proc beepcore::client::create {token profile {data ""}} {
    variable $token
    upvar 0 $token state

    if {[llength $profile] < 2} {
	set data [list $data]
    }

    return [beepcore::peer::start $state(peerT) $profile -data $data]
}

proc beepcore::client::destroy {token {channelT ""}} {
    variable $token
    upvar 0 $token state

    if {[catch { beepcore::peer::stop $channelT } result]} {
        beepcore::log::entry $state(logT) error peer::stop $result

        catch { beepcore::peer::setprop $channelT rcv.buf 0 }
    }
}

proc beepcore::client::exch {token channelT mimeT} {
    variable $token
    upvar 0 $token state

    return [beepcore::peer::message $channelT $mimeT]
}

proc beepcore::client::errscan {token mimeT} {
    variable $token
    upvar 0 $token state

    return [beepcore::peer::errscan $state(peerT) $mimeT]
}

proc beepcore::client::peerT {token} {
    variable $token
    upvar 0 $token state

    return $state(peerT)
}


# beep initialization

proc beepcore::client::beep_start {token} {
    variable $token
    upvar 0 $token state

    array set options $state(options)

    if {(![string compare $options(-privacy) none]) \
            && (![string compare $options(-mechanism) none])} {
        set state(fastP) 1
    }

    if {!$state(fastP)} {
        beep_startaux $token
    }
}

proc beepcore::client::beep_startaux {token} {
    variable $token
    upvar 0 $token state

    if {[lsearch -exact [beepcore::peer::getprop $state(peerT) -names] \
                 profiles] < 0} {
        beepcore::peer::wait $state(peerT) -msgNos [list 0]
    }
    if {![catch { beepcore::peer::getprop $state(peerT) event } event]} {
        return -code 7 $event
    }

    beepcore::util::xml_localize [set localize [beepcore::peer::getprop \
                                                    $state(peerT) localize]]

    beepcore::log::entry $state(logT) debug beep_start \
               [beepcore::peer::getprop $state(peerT) features] $localize 
    foreach profile [beepcore::peer::getprop $state(peerT) profiles] {
        beepcore::log::entry $state(logT) debug beep_start $profile
    }
}

# This handles tls::handle events

proc beepcore::client::tls_handshake {token} {
    global debugP

    variable $token
    upvar 0 $token state

    if {![::info exists state(tls_fail_count)]} {set state(tls_fail_count) 0}
    if {[eof $state(socketC)]} {
        set state(tls_handshake_done) "EOF during TLS handshake"
        fileevent $state(socketC) readable {}
        fileevent $state(socketC) writable {}
        return
    }
    flush $state(socketC)
    set thrown [catch {tls::handshake $state(socketC)} shook]
    if {!$thrown && $shook} {
        # We are done!
        set state(tls_handshake_done) ""
        unset state(tls_fail_count)
    } else {
        incr state(tls_fail_count)
        if {15 < $state(tls_fail_count)} {
            set state(tls_handshake_done) $shook
            unset state(tls_fail_count)
        }
    }
}

proc beepcore::client::tls_callback {logT args} { 
    beepcore::log::entry $logT debug client::tls_callback $args

    if {![string compare [lindex $args 0] verify]} {
        if {![string compare [lindex $args 5] "self signed certificate"]} {
            return 1
        }
        return [lindex $args 4]
    }
}

# tls initialization

proc beepcore::client::tls_start {token} {
    global debugP

    variable $token
    upvar 0 $token state

    array set options $state(options)

    switch -- $options(-privacy) {
        none 
            -
        optional {
            return
        }

        weak
            -
        strong {
            if {[catch { package require tls } result]} {
                return -code 7 [list code 451 diagnostic $result]
            }

            set profile http://iana.org/beep/TLS
            if {[lsearch -exact [beepcore::peer::getprop $state(peerT) \
                                     profiles] \
                         $profile] < 0} {
                return -code 7 [list code 550 \
                                     diagnostic "TLS profile not available"]
            }

            set tls::debug $debugP
            set tls::logcmd [list beepcore::log::entry $state(logT) debug tls]

            beepcore::peer::setprop $state(peerT) updateSeq 0
            set state(tlsT) \
                [beepcore::peer::start $state(peerT) [list $profile] \
                     -data [list "<ready />"]]

            set data [beepcore::peer::getprop $state(tlsT) datum]
            if {[string first <error $data] >= 0} {
                return -code 7 [beepcore::peer::errscan2 $state(peerT) $data]
            }

            set args {}
            if {[info exists options(-certfile)]} {
                lappend args -certfile $options(-certfile)
                if {[info exists options(-keyfile)]} {
                    lappend args -keyfile $options(-certfile)
                }
            }

            eval [list tls::import $state(socketC)                          \
                           -ssl2    false -ssl3    false -tls1   true       \
                           -request true  -require false -server false      \
                           -command [list [namespace current]::tls_callback \
                                              $state(logT)]] $args

            fconfigure $state(socketC) -encoding binary -translation binary
            fileevent $state(socketC) readable \
                [list [namespace current]::tls_handshake $token]
            fileevent $state(socketC) writable {}

            tls_handshake $token
            while {![::info exists state(tls_handshake_done)]} {
                vwait $token
            }

            if {[string length [set status [tls::status $state(socketC)]]] \
                    == 0} {
                error "handshake failed: $state(tls_handshake_done)"
            }

            array set props $status

            if {[::info exists props(sbits)]} {
                set sbits $props(sbits)
                unset props(sbits)

                if {$sbits >= 112} {
                    set privacy strong
                } elseif {$sbits >= 40} {
                    if {![string compare $options(-privacy) strong]} {
                        error "strong privacy negotiation failed"
                    }
                    set privacy weak
                } else {
                    error "privacy negotiation failed"
                }
            } else {
                set sbits 0

                if {(![::info exists props(cipher)]) \
                        || (![string compare $props(cipher) ""])} {
                    error "privacy negotatiation failed"
                }
                set privacy weak
                if {[string first EXP- $props(cipher)] != 0} {
                    foreach x {DES-CBC3 RC4 IDEA} {
                        if {[string first $x $props(cipher)] >= 0} {
                            set privacy strong
                            break
                        }
                    }
                }
                if {(![string compare $options(-privacy) strong]) \
                        && ([string compare $privacy strong])} {
                    error "strong privacy negotatiation failed"
                }
            }

            set cipher $props(cipher)
            unset props(cipher)
            array set local {}
            if {![catch { array set local [tls::status -local \
                                              $state(socketC)] }]} {
                unset local(sbits)
                unset local(cipher)
            }

            set state(tuning) \
                [list privacy  $privacy \
                      sbits    $sbits   \
                      authname ""       \
                      realname ""       \
                      sasl     ""       \
                      tls      [list cipher $cipher           \
                                     remote [array get props] \
                                     local  [array get local]]]

            catch { beepcore::peer::done $state(peerT) -release terminal }
            set state(peerT) [beepcore::peer::join $state(logT) \
                                  $state(socketC) \
                                  -serverName $options(-servername)]

            return [beep_startaux $token]
        }

        default {
            return -code 7 [list code 550 \
                                 diagnostic "unknown privacy level: $options(-privacy)"]
        }
    }
}


# sasl initialization

proc beepcore::client::sasl_start {token} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set options $state(options)

    if {$options(-signed)} {
        return -code 7 [list code 550 \
                             diagnostic "message integrity unavailable"]
    }

    switch -- $options(-mechanism) {
        none {
            return
        }

        anonymous {
# for base64
            if {[catch { package require Trf 2 } result]} {
                return -code 7 [list code 451 diagnostic $result]
            }

            set profile http://iana.org/beep/SASL/ANONYMOUS
            if {[lsearch -exact [beepcore::peer::getprop $state(peerT) \
                                     profiles] \
                         $profile] < 0} {
                return -code 7 [list code 550 \
                                     diagnostic "ANONYMOUS profile not available"]
            }

            if {[catch { set trace $options(-trace) }]} {
                if {([catch { set trace $options(-authname) }]) \
                        && ([catch { set trace $options(-username) }])} {
                    return -code 7 [list code 500 \
                                         diagnostic "missing -trace option"]
                }

                set options(-trace) $trace
                set state(options) [array get options]
            }

            set state(saslT) \
                [beepcore::peer::start $state(peerT) [list $profile] \
                     -data [list [beepcore::util::xml_blob $trace]]]
            set data [beepcore::peer::getprop $state(saslT) datum]
            if {[string first <error $data] >= 0} {
                return -code 7 [beepcore::peer::errscan2 $state(peerT) $data]
            }
            destroy $token $state(saslT)

            return
        }

        external {
# for base64
            if {[catch { package require Trf 2 } result]} {
                return -code 7 [list code 451 diagnostic $result]
            }

            set profile http://iana.org/beep/SASL/EXTERNAL
            if {[lsearch -exact [beepcore::peer::getprop $state(peerT) \
                                     profiles] \
                         $profile] < 0} {
                return -code 7 [list code 550 \
                                     diagnostic "EXTERNAL profile not available"]
            }

            if {[catch { set options(-username) } external]} {
                set external ""
            }

            set state(saslT) \
                [beepcore::peer::start $state(peerT) [list $profile] \
                     -data [list [beepcore::util::xml_blob $external]]]
            set data [beepcore::peer::getprop $state(saslT) datum]
            if {[string first <error $data] >= 0} {
                return -code 7 [beepcore::peer::errscan2 $state(peerT) $data]
            }
            destroy $token $state(saslT)

            return
        }

        otp {
# for base64, otp_md5, otp_sha1, hex
            if {[catch { package require Trf 2 } result]} {
                return -code 7 [list code 451 diagnostic $result]
            }

            set profile http://iana.org/beep/SASL/OTP
            if {[lsearch -exact [beepcore::peer::getprop $state(peerT) \
                                     profiles] \
                         $profile] < 0} {
                return -code 7 [list code 550 \
                                     diagnostic "OTP profile not available"]
            }

            if {[catch { set options(-username) } user]} {
                return -code 7 [list code 500 \
                                     diagnostic "missing -username option"]
            }
            if {[catch { set options(-authname) } auth]} {
                set auth $user
            }
            append pair "$user\0$auth"

            set passphrase ""
            if {![catch { set options(-passphrase) } passphrase]} {
            } elseif {![catch { set options(-passback) } upcallV]} {
            } else {
                return -code 7 [list code 500 \
                                     diagnostic "missing -pass* options"]
            }

            set state(saslT) \
                [beepcore::peer::start $state(peerT) [list $profile] \
                     -data [list [beepcore::util::xml_blob $pair]]]
            set data [beepcore::peer::getprop $state(saslT) datum]
            if {[string first <error $data] >= 0} {
                return -code 7 [beepcore::peer::errscan2 $state(peerT) $data]
            }

            if {([string first <blob $data] < 0) \
                    || ([set x0 [string first > $data]] < 0) \
                    || ([set x1 [string last < $data]] < 0)
                    || ($x0 > $x1)} {
                return -code 7 [list code 500 \
                                     diagnostic "syntax error while starting OTP"]
            }
            set data [string trim \
                             [string range $data [expr $x0+1] [expr $x1-1]]]
            if {[catch { base64 -mode decode $data } data]} {
                return -code 7 [list code 500 \
                                     diagnostic "invalid blob encoding: $data"]
            }
            set data [string trim $data]

            if {([llength [set items [split $data]]] != 4) \
                    || ([scan [lindex $items 1] %d seqno] != 1) \
                    || ([string first ext [lindex $items 3]] < 0)} {
                return -code 7 [list code 500 \
                                     diagnostic "invalid OTP terms: $data"]
            }
            switch -- [set algorithm [lindex $items 0]] {
                otp-md5
                    -
                otp-sha1 {
                    set algorithm [string range $algorithm 4 end]
                }

                default {
                    catch { beepcore::peer::message $state(saslT) \
                                  [beepcore::peer::str2xml \
                                       "<blob status='abort' />"] }
                    return -code 7 [list code 504 \
                                         diagnostic "unsupported OTP algorithm: $algorithm"]
                }
            }
            set seed [lindex $items 2]
            if {[string compare $passphrase ""]} {
                if {[catch { package require beepcore::profile::otp } \
                           result]} {
                    catch { beepcore::peer::message $state(saslT) \
                                  [beepcore::peer::str2xml \
                                       "<blob status='abort' />"] }
                    return -code 7 [list code 451 diagnostic $result]
                }

                set key $seed$passphrase
                set n [expr $seqno+1]
                while {[incr n -1] >= 0} {
                    set key [otp_$algorithm -- $key]
                }
                set result hex:[hex -mode encode -- $key]

                if {$seqno <= 10} {
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
            } else {
                set result [eval $upcallV [list $state(serverD) \
                                                $name $algorithm $seqno $seed]]
            }

            if {[string compare $result ""]} {
                set data [beepcore::util::xml_blob $result]
            } else {
                set data "<blob status='abort' />"
            }

            set code [catch { beepcore::peer::message $state(saslT) \
                                  [set mimeT [beepcore::peer::str2xml \
                                                  $data]] } result]
            set ecode $errorCode
            set einfo $errorInfo

            mime::finalize $mimeT

            set mimeT $result

            switch -- $code {
                0 {
                    set doneP [string first complete [mime::getbody $mimeT]]

                    mime::finalize $mimeT

                    if {$doneP} {
                        destroy $token $state(saslT)
                        return
                    }

                    return -code 7 \
                           [list       code 500 \
                                 diagnostic "syntax error while completing SASL"]
                }

                7 {
                    return -code 7 [beepcore::peer::errscan $state(peerT) \
                                        $mimeT]
                }

                default {
                    return -code $code -errorinfo $einfo -errorcode $ecode \
                           $result
                }
            }
        }

        default {
            return -code 7 [list code 550 \
                                 diagnostic "unknown mechanism: $options(-mechanism)"]
        }
    }
}


#
# request/response handling
#

proc beepcore::client::request {token data {channelT ""}} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    if {$state(fastP)} {
        set state(fastP) 0

        beep_startaux $token
    }

    set mimeT [beepcore::peer::str2xml $data]

    set code [catch { beepcore::peer::message $channelT $mimeT } result]
    set ecode $errorCode
    set einfo $errorInfo

    mime::finalize $mimeT

    switch -- $code {
        0 {
            return [list status positive mimeT $result]
        }

        7 {
            return [list status negative mimeT $result]
        }

        default {
            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


# backwards-compatibility

package provide beepcore::mixer 1.1

foreach p \
        [list init fin profiles create destroy exch errscan] {
    namespace eval beepcore::mixer "namespace export $p"

    proc beepcore::mixer::$p args "eval beepcore::client::$p \$args"
}

namespace eval beepcore::mixer {
    namespace export wait connectedP 
}

proc beepcore::mixer::wait {token args} {
    variable $token
    upvar 0 $token state

    eval [list beepcore::peer::wait $state(peerT)] $args
}

proc beepcore::mixer::connectedP {token} {
    variable $token
    upvar 0 $token state

    if {![info exists state(logT)]} {
        return 0
    }

    if {![string compare $state(peerT) ""]} {
        return 1
    }

    switch -- [set code [catch { beepcore::peer::wait $state(peerT) \
                                     -timeout 0 } result]] {
        0 {
            return 1
        }

        7 {
            array set response $result
            beepcore::log::entry $state(logT) info $response(code) \
                $response(diagnostic)
        }

        default {
            beepcore::log::entry $state(logT) error peer::wait $result
        }
    }

    return 0
}

if {[catch { package require sasl }]} {
    return
}

proc beepcore::client::sasl_log {logT data} {
    array set params $data

    set level [lindex [list debug4 notify info   info \
                            info   debug  debug2 debug3] $params(level)]
    if {![string compare $level ""]} {
        set level debug
    }

    beepcore::log::entry $logT $level cyrus $params(message)
}

proc beepcore::client::sasl_interact {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set options $state(options)

    array set params $data

    catch { set value $params(default) }
    switch -- $params(id) {
        authname {
            if {[info exists options(-authname)]} {
                set value $options(-authname)
            } else {
                set value $options(-username)
            }
        }

        user {
            set value $options(-username)
        }

        pass {
            if {[info exists options(-passphrase)]} {
                set value $options(-passphrase)
            }
        }
    }

    return $value
}

proc beepcore::client::sasl_start {token} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set options $state(options)

    if {![string compare $options(-mechanism) none]} {
        return
    }

    array set tuning $state(tuning)

    if {![catch { set options(-callbacks) } callbacks]} {
        set interact ""
        set cblist $callbacks
        set callbacks {}
        foreach cb $cblist {
            if {[llength $cb] <= 1} {
                lappend callbacks $cb
            } else {
                set command [lindex $cb 1]
                lappend command $token
                lappend callbacks [lreplace $cb 1 1 $command]
            }
        }
    } elseif {![string compare [string tolower $options(-mechanism)] \
                       external]} {
        if {[catch { set options(-username) }]} {
            if {[catch { 
                array set props $tuning(tls)
                array set cert $props(local)
                set options(-username) $cert(subject)
                set state(options) [array get options]
            }]} {
                return -code 7 [list code 500 \
                                     diagnostic "missing -username option"]
            }
        }

        set callbacks [list authname user pass]
        set interact [list -interact \
                           [list [namespace current]::sasl_interact $token]]
    } else {
        if {[catch { set options(-username) }]} {
            if {[catch { set options(-trace) }]} {
                return -code 7 [list code 500 \
                                     diagnostic "missing -username option"]
            }

            set options(-username) $options(-trace)
            set state(options) [array get options]
        }

        if {([catch { set options(-passphrase) }]) \
                && ([catch { set options(-trace) }])} {
            if {[catch { set options(-passback) }]} {
                 return -code 7 [list code 500 \
                                      diagnostic "missing -passphrase option"]
            }
            return -code 7 [list code 500 \
                                 diagnostic "use -callbacks, not -passback"]
        }

        set callbacks [list authname user pass]
        set interact [list -interact \
                           [list [namespace current]::sasl_interact $token]]
    }

    sasl::client_init \
        -callbacks  [list [list log [list [namespace current]::sasl_log \
                                          $state(logT)]]]

    if {![string compare [set fqdn $state(serverD)] localhost]} {
        set fqdn [info host]
    }
    set state(cyrusT) [sasl::client_new -service    beep       \
                                        -serverFQDN $fqdn      \
                                        -callbacks  $callbacks \
                                        -flags      [list success_data]]
    
    set min   0
    set max   0
    if {[set ssf $tuning(sbits)] == 0} {
        switch -- $tuning(privacy) {
            strong {
                set ssf 112
            }
    
            weak {
                set ssf  40
            }
    
            none {
# for transform
                if {([string compare $options(-privacy) none]) \
                        && (![catch { package require Trf 2 }])} {
                    if {$options(-signed)} {
                        set min   1
                        set max   1
                    } else {
                        set max 256
                    }
                }
            }
        }
    }
    if {[set bufsiz [fconfigure $state(socketC) -buffersize]] < 4096} {
        set bufsiz 65536
    }
    catch {
        array set props $tuning(tls)
        array set cert $props(local)
        $state(cyrusT) -operation setprop       \
                       -property  auth_external \
                       -value     $cert(subject)
    }
    $state(cyrusT) -operation setprop      \
                   -property  ssf_external \
                   -value     $ssf
    $state(cyrusT) -operation setprop   \
                   -property  sec_props \
                   -value     [list min_ssf    $min \
                                    max_ssf    $max \
                                    max_bufsiz $bufsiz]

    set prefix http://iana.org/beep/SASL/
    if {[string compare [set mechanism $options(-mechanism)] any]} {
        set mechanisms [list [string toupper $mechanism]]
    } else {
        set plen [string length $prefix]
        set mechanisms {}
        foreach profile [beepcore::peer::getprop $state(peerT) profiles] {
            if {[string first $prefix $profile] == 0} {
                lappend mechanisms [string range $profile $plen end]
            }
        }
    }

    set code [catch {
        eval [list $state(cyrusT) -operation  start \
                                  -mechanisms $mechanisms] $interact
    } result]

    switch -- $code {
        0 - 4 {
            array set data $result

            if {$max > 0} {
                beepcore::peer::setprop $state(peerT) updateSeq 0
            }
            set state(saslT) [beepcore::peer::start $state(peerT) \
                                  [list $prefix$data(mechanism)] \
                                  -data [list [beepcore::util::xml_blob \
                                                   $data(output)]]]

            set xode [catch {
                sasl_parseblob $token \
                    [beepcore::peer::getprop $state(saslT) datum]
            } result]
            set ecode $errorCode
            set einfo $errorInfo

            switch -- $xode {
                0 {
                    array set parse $result
                }

                7 {
                    if {[$state(cyrusT) -operation getprop -property ssf] \
                            > 0} {
                        catch { beepcore::peer::done $state(peerT) \
                                    -release terminal }
                        set state(peerT) [beepcore::peer::join $state(logT) \
                                              $state(socketC) \
                                              -serverName \
                                              $options(-servername)]
                        beep_startaux $token
                    }

                    return -code 7 $result
                }

                default {
                    return -code $xode -errorinfo $einfo -errorcode $ecode \
                           $result
                }
            }
        }

        default {
            return -code 7 [list code 550 diagnostic $result]
        }
    }

    while {$code == 4} {
        set code [catch {
            eval [list $state(cyrusT) -operation step \
                                      -input     $parse(blob)] $interact
        } output]

        switch -- $code {
            0 {
                if {![string compare $output ""]} {
                    break
                }
            }

            4 {
                if {$max > 0} {
                    beepcore::peer::setprop $state(peerT) updateSeq 1
                }
            }

            default {
                return -code 7 [list code 550 diagnostic $output]
            }
        }

        if {[string compare $parse(status) continue]} {
            return -code 7 \
                   [list code 520 \
                         diagnostic "server says complete, client says continue"]
        }

        if {$max > 0} {
            beepcore::peer::setprop $state(peerT) updateSeq 0
        }

        set xode [catch {
            beepcore::peer::message $state(saslT) \
                [set mimeT [beepcore::peer::str2xml \
                                [beepcore::util::xml_blob $output]]]
        } result]
        set ecode $errorCode
        set einfo $errorInfo

        mime::finalize $mimeT
        set mimeT $result 

        switch -- $xode {
            0 {
                array set parse [sasl_parseblob $token [mime::getbody $mimeT]]
                mime::finalize $mimeT
            }

            7 {
                if {[$state(cyrusT) -operation getprop -property ssf] > 0} {
                    catch { beepcore::peer::done $state(peerT) \
                                -release terminal }
                    set state(peerT) [beepcore::peer::join $state(logT) \
                                          $state(socketC) \
                                          -serverName $options(-servername)]
                    beep_startaux $token
                }

                return -code 7 [beepcore::peer::errscan $state(peerT) $mimeT]
            }

            default {
                return -code $xode -errorinfo $einfo -errorcode $ecode $result
            }
        }
    }

    if {[string compare $parse(status) complete]} {
        return -code 7 \
               [list code 520 \
                     diagnostic "server says continue, client says complete"]
    }

    if {[set ssf [$state(cyrusT) -operation getprop -property ssf]] \
            <= 0} {
        set tuning(sasl) [list mechanism $data(mechanism)]
        set state(tuning) [array get tuning]

        if {$max > 0} {
            beepcore::peer::setprop $state(peerT) updateSeq 1
        }
        destroy $token $state(saslT)
        return
    }

    if {$ssf >= 112} {
        set privacy strong
    } elseif {$ssf >= 40} {
        set privacy weak
    } else {
        set privacy none
    }
    set state(tuning) \
        [list privacy $privacy sbits $ssf authname "" realname "" tls "" \
              sasl [list mechanism $data(mechanism)]]

    fileevent $state(socketC) readable {}
    fileevent $state(socketC) writable {}
    flush $state(socketC)
    transform -attach $state(socketC) \
              -command [list [namespace current]::sasl_transform \
                                 $state(cyrusT) $state(logT)]

    catch { beepcore::peer::done $state(peerT) -release terminal }
    set state(peerT) [beepcore::peer::join $state(logT) \
                          $state(socketC) -serverName $options(-servername)]

    return [beep_startaux $token]
}


proc beepcore::client::sasl_transform {cyrusT logT command buffer} {
    global errorCode errorInfo

    switch -- $command {
        write {
            set script [list $cyrusT -operation encode -output $buffer]
        }

        read {
            set script [list $cyrusT -operation decode -input  $buffer]
        }

        query/maxRead {
            return -1
        }

        query/ratio {
            return [list 0 0]
        }

        
        default {
            beepcore::log::entry $logT debug transform $command
            return
        }
    }

    if {[set code [catch { eval $script } result]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error cyrus::$command $result

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }

    beepcore::log::entry $logT debug transform $command \
        in=[string length $buffer] out=[string length $result]

    return $result
}


proc beepcore::client::sasl_parseblob {token input} {
    variable $token
    upvar 0 $token state

    if {[string first <error $input] >= 0} {
        return -code 7 [beepcore::peer::errscan2 $state(peerT) $input]
    }

    set x2 0
    if {([string first <blob $input] < 0) \
            || ([set x0 [string first > $input]] < 0) \
            || ([set x1 [string last < $input]] < 0) \
            || (($x0 > $x1) \
                    && ([set x2 [string first "/>" $input]] \
                            != [expr $x0-1]))} {
        return -code 7 [list code 500 \
                             diagnostic "syntax error while parsing blob"]
    }

    if {[string first complete [string range $input 0 $x0]] > 0} {
        set status complete
    } else {
        set status continue
    }

    if {$x2 > 0} {
        set blob ""
    } elseif {[catch { sasl::decode64 [string trim \
                                              [string range $input \
                                                      [expr $x0+1] \
                                                      [expr $x1-1]]] } blob]} {
        return -code 7 [list code 500 \
                             diagnostic "invalid blob encoding: $input"]
    }

    return [list blob $blob status $status]
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
