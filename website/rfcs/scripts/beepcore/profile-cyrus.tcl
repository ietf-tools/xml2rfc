#
# profile-cyrus.tcl - the Cyrus SASL family of profiles
#


package provide beepcore::profile::cyrus   1.0

package require beepcore::log
package require beepcore::sasl
package require beepcore::server
package require beepcore::util


#
# state variables:
#
#    logT: token for logging package
#    saslT: token for SASL package
#    cyrusT: server token
#    args: arglist for start/step
#    mechanism: mechanism in use
#
# top-level index variables:
#
#    cyrusP: loaded tclsasl
#    privacy: current level of privacy
#    cyrusT: server token
#    mechanisms: allowed mechanisms
#
# cyrus2profile: maps cyrusT to profile token
#


namespace eval beepcore::profile::cyrus {
    variable cyrus
    array set cyrus { uid 0 cyrusP 0 privacy none }

    variable cyrus2profile
    array set cyrus2profile {}

    namespace export info boot2 init fin exch \
                     log proxyP sasl_init
}


proc beepcore::profile::cyrus::info {logT} {
    if {[catch { package require sasl }]} {
        error "optional TclSASL package not installed, continuing..."
    }

    sasl::server_init \
        -callbacks [list [list log [list [namespace current]::log $logT]]]

    set p {}
    foreach m [sasl::mechanisms] {
        lappend p http://iana.org/beep/SASL/$m
    }
    if {[llength $p] == 0} {
        error "no mechanisms configured in Cyrus SASL package?!?"
    }

    return [list 0 $p \
                 [list boot2V [namespace current]::boot2 \
                       initV  [namespace current]::init  \
                       exchV  [namespace current]::exch  \
                       finV   [namespace current]::fin]]
}


proc beepcore::profile::cyrus::sasl_init {logT} {
    variable cyrus

    if {!$cyrus(cyrusP)} {
        if {[catch { package require sasl } result]} {
            return -code 7 [list code 451 diagnostic $result]
        }

        sasl::server_init \
            -callbacks [list [list log [list [namespace current]::log $logT]]]

        set cyrus(cyrusP) 1
    }
}

proc beepcore::profile::cyrus::boot2 {logT uri} {
    variable cyrus

    beepcore::sasl::tuneP

    sasl_init $logT

    array set tuning $::beepcore::server::tuning
    if {([string compare $cyrus(privacy) $tuning(privacy)]) \
            && ([::info exists cyrus(cyrusT)])} {
        catch { rename $cyrus(cyrusT) {} }
        unset cyrus(cyrusT)
    }

    if {![::info exists cyrus(cyrusT)]} {
        set cyrus(privacy) $tuning(privacy)

        set cyrus(cyrusT) [sasl::server_new \
                               -service   beep \
                               -callbacks [list [list proxy \
                                                      [list [namespace current]::proxyP $logT]]] \
                               -flags    [list success_data]]

        set max 0
        if {[set ssf $tuning(sbits)] == 0} {
            switch -- $cyrus(privacy) {
                strong {
                    set ssf 112
                }
    
                weak {
                    set ssf  56
                }
    
                none {
# for transform
                    if {![catch { package require Trf 2 }]} {
                        set max 256
                    }
                }
            }
        }
        if {[string compare $tuning(authname) ""]} {
            $cyrus(cyrusT) -operation setprop       \
                           -property  auth_external \
                           -value     $tuning(authname)
        }
        $cyrus(cyrusT) -operation setprop      \
                       -property  ssf_external \
                       -value     $ssf
        $cyrus(cyrusT) -operation setprop   \
                       -property  sec_props \
                       -value     [list min_ssf        0 \
                                        max_ssf     $max \
                                        max_bufsiz 65536]
        set cyrus(mechanisms) [$cyrus(cyrusT) -operation list]

        beepcore::log::entry $logT debug mechanisms $cyrus(mechanisms)
    }

    set x [string last / $uri]
    if {[lsearch -exact $cyrus(mechanisms) \
                 [set m [string range $uri [expr $x+1] end]]] < 0} {
        return -code 7 [list code 520 diagnostic "$m not available"]
    }
}


proc beepcore::profile::cyrus::log {logT data} {
    global errorCode errorInfo

    array set params $data

    set level [lindex [list debug4 error  info   info \
                            info   debug  debug2 debug3] $params(level)]
    if {![string compare $level ""]} {
        set level debug
    }
    if {![string compare $level error]} {
        set errorCode ""
        set errorInfo ""
    }

    beepcore::log::entry $logT $level cyrus $params(message)
}


proc beepcore::profile::cyrus::proxyP {logT data} {
    global errorCode errorInfo

    variable cyrus2profile

    array set params $data
    set mappingT $params(token)

    variable [set token $cyrus2profile($mappingT)]
    upvar 0 $token state

    if {![string compare $params(user) $params(target)]} {
        return 0
    }

    switch -- [set code [catch { beepcore::sasl::proxyP $state(saslT) \
                                     $params(user) $params(target) } result]] {
        0 {
            return 0
        }

        7 {
            array set response $result
            beepcore::sasl::failure $state(saslT) $params(target) \
                [list authname   $params(user)   \
                      code       $response(code) \
                      diagnostic $response(diagnostic)]

            return -14
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::proxyP $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::profile::cyrus::init {logT serverD clientA upcallV uri} {
    global errorCode errorInfo

    beepcore::sasl::tuneP

    variable cyrus
    variable cyrus2profile

    set token [namespace current]::[incr cyrus(uid)]

    variable $token
    upvar 0 $token state

    if {[set code [catch { beepcore::sasl::init $logT $clientA } saslT]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error sasl::init $saslT

        return -code $code -errorinfo $einfo -errorcode $ecode $saslT
    }

    set mechanism [string range $uri [expr [string last / $uri]+1] end]
    set args [list -operation start -mechanism $mechanism]

    array set state [list logT $logT saslT $saslT \
                          cyrusT [set mappingT $cyrus(cyrusT)] \
                          args $args mechanism $mechanism]
    unset cyrus(cyrusT)

    set cyrus2profile($mappingT) $token

    return $token
}


proc beepcore::profile::cyrus::fin {token status} {
    variable cyrus2profile

    variable $token
    upvar 0 $token state

    if {[::info exists state(cyrusT)]} {
        catch { unset cyrus2profile($mappingT) }
        if {[catch { rename [set mappingT $state(cyrusT)] {} } result]} {
            beepcore::log::entry $state(logT) error cyrus::fin $result
        }
    }

    if {[catch { beepcore::sasl::fin $state(saslT) } result]} {
        beepcore::log::entry $state(logT) error sasl::fin $result
    }

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}


proc beepcore::profile::cyrus::exch {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    beepcore::sasl::tuneP 1

    switch -- [set code [catch { beepcore::sasl::parse $state(saslT) $data } \
                               result]] {
        0 {
        }

        7 {
            set start(args) [list -operation start \
                                  -mechanism $state(mechanism)]

            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error sasl::parse $result

            set start(args) [list -operation start \
                                  -mechanism $state(mechanism)]

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    array set parse $result

    if {![string compare $parse(status) abort]} {
        return "<blob status='complete' />"
    }

    set code [catch {
        eval [list $state(cyrusT) -input $parse(blob)] $state(args)
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set user [$state(cyrusT) -operation getprop -property username]
            set mech [$state(cyrusT) -operation getprop -property mechname]
            set ssf  [$state(cyrusT) -operation getprop -property ssf]

            array set tuning $::beepcore::server::tuning
            if {![string compare $user $tuning(realname)]} {
                set user $tuning(authname)
            }

            if {[catch { beepcore::sasl::fetch $state(saslT) $user }]} {
                beepcore::sasl::unknownA $state(saslT) $user
            }

            if {$ssf > 0} {
                set code 8
                if {$ssf >= 112} {
                    set privacy strong
                } elseif {$ssf >= 40} {
                    set privacy weak
                } else {
                    set privacy none
                }
                set ::beepcore::server::tuning \
                    [list privacy $privacy sbits $ssf authname "" realname "" \
                          tls "" sasl [list mechanism $mech]]
            } else {
                set tuning(sasl) [list mechanism $mech]
                set ::beepcore::server::tuning [array get tuning]
            }

            beepcore::sasl::login $state(saslT) $user

            set blob "<blob status='complete'"
        }

        4 {
            set blob "<blob"
        }

        default {
            set start(args) [list -operation start \
                                  -mechanism $state(mechanism)]

            if {[string compare [lindex $errorCode 0] SASL]} {
                beepcore::log::entry $state(logT) error cyrus_operation $result

                return -code $code -errorinfo $einfo -errorcode $ecode $result
            }

            array set errstr [list diagnostic "" language ""]
            array set errstr [sasl::errstring -code \
                                              [set scode \
                                                   [lindex $errorCode 2]]]
            set diagnostic $errstr(diagnostic)
            switch -- $scode {
                 -1 -  -4 -  -5 -  -6 { set code 550 }

                 -2 -  -3             { set code 450 }

                 -7 - -12             { set code 500 }

                 -8                   { set code 430 }

                 -9 - -13 - -15 - -16 - 
                -17 - -18 - -19 - -20 -
                -23 - -24 - -26       { 
                                        set code 535 
                                        set errstr(diagnostic) \
                                            "account unknown"
                                      }

                -14                   {
                                        set code 539 
                                        set errstr(diagnostic) \
                                            "proxy not authorized"
                                      }

                default {
                    set code 550
                    beepcore::log::entry $state(logT) info \
                        "unknown cyrus result: $errorCode"
                }
            }

            if {[catch { $state(cyrusT) -operation getprop \
                             -property username } user]} {
                set user ""
            }
            set ssf  [$state(cyrusT) -operation getprop -property ssf]

            beepcore::sasl::failure $state(saslT) "" \
                [list code $code diagnostic $diagnostic]

            if {$ssf == 0} {
                return -code 7 [beepcore::util::xml_error $code \
                                   $errstr(diagnostic) $errstr(language)]
            }
            return -code 10 [list [beepcore::util::xml_error $code \
                                       $errstr(diagnostic) $errstr(language)] \
                                  [list [namespace current]::import ""]]
        }
    }
    set state(args) [list -operation step]

    if {[string length $result] > 0} {
        append blob ">[sasl::encode64 $result]</blob>"
    } else {
        append blob " />"
    }

    if {$code != 8} {
        return $blob
    }

    set cyrusT $state(cyrusT)
    unset state(cyrusT)
    return -code 8 [list $blob [list [namespace current]::import $cyrusT]]
}


proc beepcore::profile::cyrus::import {cyrusT logT inputC} {
    if {[string compare $cyrusT ""]} {
        fileevent $inputC readable {}
        fileevent $inputC writable {}
        flush $inputC
        ::transform -attach $inputC \
                    -command [list [namespace current]::transform \
                                       $cyrusT $logT]
    }
}


proc beepcore::profile::cyrus::transform {cyrusT logT command buffer} {
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

        delete/read
            -
        delete/write {
            catch { rename $cyrusT {} }
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
