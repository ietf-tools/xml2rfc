#
# profile-tunnel.tcl - the TUNNEL profile
#
#
# 1. optionally, create
#
#     tunnel/hop2a.tcl    # to define hop2a {saslT props}
#
# this is responsible for determining the authentication parameters to use
# for the next hop. this module defines a stub version of this routine,
# looking for an entry in the authorization database called "tunnel".
#
#
# 2. optionally, create
#
#     tunnel/e2hop.tcl    # to define e2hop {profile}
#     tunnel/p2hop.tcl    # to define p2hop {profile}
#
# these are responsible for mapping from an endpoint/profile attribute to the
# next hop (and associated authentication parameters). this module defines
# stub versions of these two routines, which error, obviously.
#
#
# 3. authorize users accordingly:
#
#       scope - tunnel:ipv4:$ipv4:$portno
#             - tunnel:fqdn:$fqdn:$portno
#             - tunnel:fqdn:$fqdn:$service
#             - tunnel:profile:$profile
#             - tunnel:endpoint:$endpoint
#
#     actions - tunnel
#
# e.g.,
#
#    <elem key="authorization">
#        <elem key="acl">
#            <elem key="tunnel:fqdn:*">
#                <elem key="scope">tunnel:fqdn:*</elem>
#                <elem key="privs">tunnel</elem>
#            </elem>
#            <elem key="tunnel:fqdn:*">
#                <elem key="scope">tunnel:fqdn:example.com</elem>
#                <elem key="privs">none</elem>
#            </elem>
#            <elem key="tunnel:fqdn:*">
#                <elem key="scope">tunnel:fqdn:*.example.com</elem>
#                <elem key="privs">none</elem>
#            </elem>
#        </elem>
#    </elem>
#
# allows tunnelling to any port/service at any domain name, except that no 
# access is allowed to example.com or any of its subdomains
#


package provide beepcore::profile::tunnel  1.0

package require beepcore::client
package require beepcore::log
package require beepcore::peer
package require beepcore::sasl
package require beepcore::util


#
# state variables (beep profile):
#
#    logT: token for logging package
#    saslT: token for SASL package
#
#
# state variables (tunnel link):
#
#    logT: token for logging package
#    {up,down}C: {up,down}stream channel
#    {up,down}B: {up,down}stream write buffer
#    {up,down}R: {up,down}stream readable event enabled
#    {up,down}W: {up,down}stream is writable
#    code: final result
#    diagnostic: associated diagnostic
#
#
# present only during XML parsing
#
#    stack: list containing parse context
#    code: reply code
#    data: <tunnel> content
#    mode: <tunnel> signature
#    fqdn/ip4/port/srv/profile/endpoint: <tunnel> attributes
#


namespace eval beepcore::profile::tunnel {
    variable tunnel
    array set tunnel { uid 0 }

    variable parser [::beepcore::exml::parser]
    catch {
        $parser configure                               \
                -errorcommand [namespace current]::oops \
                -reportempty  no
    }

    namespace export info boot init fin exch
}


proc beepcore::profile::tunnel::info {logT} {
    return [list 0 \
                 [list http://xml.resource.org/profiles/TUNNEL] \
                 [list bootV [namespace current]::boot \
                       initV [namespace current]::init \
                       exchV [namespace current]::exch \
                       finV  [namespace current]::fin]]
}


proc beepcore::profile::tunnel::boot {logT} {
    beepcore::sasl::tuneP 0 1
}


proc beepcore::profile::tunnel::init {logT serverD clientA upcallV uri} {
    beepcore::sasl::tuneP 0 1

    variable tunnel

    set token [namespace current]::[incr tunnel(uid)]

    variable $token
    upvar 0 $token state

    if {[set code [catch { beepcore::sasl::init $logT $clientA "" 1 } \
                         saslT]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error sasl::init $saslT

        return -code $code -errorinfo $einfo -errorcode $ecode $saslT
    }

    array set state [list logT $logT saslT $saslT]

    foreach name [list hop2a e2hop p2hop] {
        set file [file join tunnel $name.tcl]
        if {([file exists $file]) && ([catch { source $file } result])} {
            beepcore::log::entry $logT info "$file: $result"
        }
    }

    return $token
}


proc beepcore::profile::tunnel::fin {token status} {
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


proc beepcore::profile::tunnel::exch {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    beepcore::sasl::tuneP 1 1

    switch -- [set code [catch { parse $token $data } result]] {
        0 {
            array set parse $result
        }

        7 {
            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error tune::parse $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    array set mapping [list port "" authparams ""]
    switch -- $parse(mode) {
        .inner {
            return -code 8 [list "<ok />" [namespace current]::noop]
        }

        .fqdn.port.outer
            -
        .fqdn.port.inner
            -
        .ip4.port.outer
            -
        .ip4.port.inner {
            if {[string length $parse(fqdn)] > 0} {
                set scope fqdn
            } else {
                set scope ipv4
            }

            if {[catch { beepcore::sasl::allowP $state(logT) tunnel \
                             tunnel:$scope:$parse(fqdn)$parse(ip4):$parse(port) } \
                       result]} {
                return -code 7 [beepcore::util::xml_error2 $result]
            }

            if {[string compare $parse(data) ""]} {
                set mapping(authparams) [hop2a $state(saslT) [array get parse]]
            }

            set code [catch {
                socket $parse(fqdn)$parse(ip4) $parse(port)
            } result]
        }

        .fqdn.srv.inner
            -
        .fqdn.srv.outer
            -
        .fqdn.port.srv.inner
            -
        .fqdn.port.srv.outer {
            if {[catch { package require srvrr }]} {
                return -code 7 [beepcore::util::xml_error 504 "no SRV support"]
            }
            if {([catch { llength [set parts [split $parse(srv) .]] } len]) \
                    || ($len != 2)} {            
                return -code 7 [beepcore::util::xml_error 500 \
                                "srv attribute poorly formed"]
            }
            if {[string compare [string trimleft [lindex $parts 1] _] tcp]} {
                return -code 7 [beepcore::util::xml_error 504 \
                                "transport protocol unsupported in srv attribute"]
            }
            set service [string trimleft [lindex $parts 0] _]

            if {[catch { beepcore::sasl::allowP $state(logT) tunnel \
                             tunnel:fqdn:$parse(fqdn):$service } result]} {
                return -code 7 [beepcore::util::xml_error2 $result]
            }

            if {[string compare $parse(data) ""]} {
                set mapping(authparams) [hop2a $state(saslT) [array get parse]]
            }

            set code [catch {
                eval [list srvrr::socket -service $service $parse(fqdn)] \
                                         $parse(port)
            } result]
        }

        .profile.inner
            -
        .endpoint.inner {
            if {[string length $parse(profile)] > 0} {
                set scope profile
                set prochop p2hop
            } else {
                set scope endpoint
                set prochop e2hop
            }

            if {[catch { beepcore::sasl::allowP $state(logT) tunnel \
                             tunnel:$scope:$parse($scope) } result]} {
                return -code 7 [beepcore::util::xml_error2 $result]
            }

            array set mapping [$prochop $parse($scope)]
            set parse(data) $mapping(data)
            if {[info exists mapping(service)]} {
                if {[catch { package require srvrr }]} {
                    return -code 7 [beepcore::util::xml_error 504 \
                                        "no SRV support"]
                }
                
                set code [catch {
                    eval [list srvrr::socket -service $mapping(service) \
                                   $mapping(system)] $mapping(port)
                } result]
            } else {
                set code [catch {
                    socket $mapping(system) $mapping(port)
                } result]
            }
        }
    }

    switch -- $code {
        0 {
            set socketC $result

            if {![string compare $parse(data) ""]} {
                return -code 8 [list "<ok />" \
                                     [list [namespace current]::shuffle \
                                               $socketC]]
            }
        }

        7 {
            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            beepcore::log::entry $state(logT) system $result

            return -code 7 [beepcore::util::xml_error 550 $result]
        }
    }

    if {[catch { beepcore::peer::join $state(logT) $socketC } peerT]} {
        if {[catch { close $socketC } result]} {
            beepcore::log::entry $state(logT) system $result    
        }

        return -code 7 [beepcore::util::xml_error 450 $peerT]
    }

    if {[lsearch -exact [beepcore::peer::getprop $peerT -names] profiles] \
            < 0} {
        beepcore::peer::wait $peerT -msgNos [list 0]
    }

    set uri http://xml.resource.org/profiles/TUNNEL

    set code [catch {
        if {[lsearch -exact [beepcore::peer::getprop $peerT profiles] $uri] \
                < 0} {
            return -code 7 [list code 550 diagnostic "no tunnel downstream"]
        }

        if {[string compare $mapping(authparams) ""]} {
            array set auth $mapping(authparams)
            if {![::info exists auth(-username)]} {
                set auth(-username) $auth(-authname)
                set mapping(authparams) [array get auth]
            }
            eval [list beepcore::client::init $state(logT) ""] \
                       $mapping(authparams) -privacy none -signed false \
                       -peerT $peerT -socketC $socketC
        }

        beepcore::peer::setprop $peerT updateSeq 0
        beepcore::peer::start $peerT [list $uri] -data [list $parse(data)]
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set channelT $result

            if {[string first <error \
                        [set result [beepcore::peer::getprop $channelT \
                                        datum]]] >= 0} {
                set code 7
            }
        }

        2 {
            set code 7
        }

        7 {
        }

        default {
            beepcore::log::entry $state(logT) error peer::start $result
        }
    }

    if {$code} {
        if {[catch { beepcore::peer::done $peerT -release abortive } \
                   result2]} {
            beepcore::log::entry $state(logT) error peer::done $result2
        }
        if {[catch { close $socketC } result2]} {
            beepcore::log::entry $state(logT) system $result2
        }

        if {$code == 7} {
            set result [beepcore::util::xml_error2 $result]
        }

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }

    if {[catch { beepcore::peer::done $peerT -release terminal } result]} {
        beepcore::log::entry $state(logT) error peer::done $result      
    }

    return -code 8 [list "<ok />" \
                         [list [namespace current]::shuffle $socketC]]
}


proc beepcore::profile::tunnel::parse {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable parser

    $parser configure                                                         \
            -elementstartcommand  "[namespace current]::element $token start" \
            -elementendcommand    "[namespace current]::element $token end"   \
            -characterdatacommand "[namespace current]::cdata   $token"       \
            -final                yes

    set state(stack)    {}
    set state(code)     500
    set state(data)     ""
    set state(mode)     ""
    set state(fqdn)     ""
    set state(ip4)      ""
    set state(port)     ""
    set state(srv)      ""
    set state(profile)  ""
    set state(endpoint) ""

    set code [catch {
        $parser reset
        $parser parse $data
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result [list data     $state(data)     \
                             mode     $state(mode)     \
                             fqdn     $state(fqdn)     \
                             ip4      $state(ip4)      \
                             port     $state(port)     \
                             srv      $state(srv)      \
                             profile  $state(profile)  \
                             endpoint $state(endpoint)]
        }

        7 {
        }

        default {
            append result [beepcore::util::xml_trace $state(logT) tunnel \
                               $result $data $state(stack)]

            set code 7

            set result [list code       $state(code) \
                             diagnostic $result]
        }
    }

    unset state(stack)    \
          state(code)     \
          state(data)     \
          state(mode)     \
          state(fqdn)     \
          state(ip4)      \
          state(port)     \
          state(srv)      \
          state(profile)  \
          state(endpoint)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


proc beepcore::profile::tunnel::noop {logT inputC} {
    beepcore::sasl::logout
}


proc beepcore::profile::tunnel::shuffle {downC logT upC} {
    variable tunnel

    set token [namespace current]::[incr tunnel(uid)]

    variable $token
    upvar 0 $token state

    array set state [list logT  $logT  code 320 diagnostic "" \
                          downC $downC downB "" downR 1 downW 0 \
                          upC   $upC   upB   "" upR   1 upW   0]

    if {[catch {
        fconfigure $upC -blocking off -buffersize 65536 \
                          -encoding binary -translation binary
        fileevent $upC readable \
                  [list [namespace current]::readable $token up down]
        fileevent $upC writable \
                  [list [namespace current]::writable $token down up]

        fconfigure $downC -blocking off -buffersize 65536 \
                          -encoding binary -translation binary
        fileevent $downC readable \
                  [list [namespace current]::readable $token down up]
        fileevent $downC writable \
                  [list [namespace current]::writable $token up down]

        beepcore::log::entry $state(logT) info "now a tunnel"
        while {$state(code) == 320} {
            vwait $token
        }
    } result]} {
        beepcore::log::entry $state(logT) error "shuffle loses"
        set state(code) 550
        set state(diagnostic) $result

    }

    foreach stream [list up down] {
        if {[catch { close [set ${stream}C] } result]} {
            beepcore::log::entry $state(logT) info \
                "error closing ${stream}steam"
        }
    }

    return -code 7 [list code $state(code) diagnostic $state(diagnostic)]
}

proc beepcore::profile::tunnel::readable {token src dst} {
    variable $token
    upvar 0 $token state

    if {[eof $state(${src}C)]} {
        beepcore::log::entry $state(logT) debug2 eof on ${src}stream 

        set state(code) 200
    } elseif {[catch {
        set len [string length [set buffer [read $state(${src}C)]]]
        append state(${dst}B) $buffer   

        beepcore::log::entry $state(logT) debug2 read $len octets on \
                ${src}stream
    } result]} {
        beepcore::log::entry $state(logT) system $result

        set state(code) 521
        set state(diagnostic) "error reading on ${src}stream"
    } elseif {$len == 0} {
# about to get an eof...
    } elseif {$state(${dst}W)} {
        writable $token $src $dst
    } elseif {[set len [string length $state(${dst}B)]] < 1048576} {
        beepcore::log::entry $state(logT) debug2 $len octets buffered for \
            ${dst}stream
    } elseif {[catch { fileevent $state(${src}C) readable "" } result]} {
        beepcore::log::entry $state(logT) system $result

        set state(code) 521
        set state(diagnostic) "error on fileevent for ${src}stream"
    } else {
        set state(${src}R) 0

        beepcore::log::entry $state(logT) debug2 disabling reads on ${src}stream
    }

    if {$state(code) != 320} {
        catch { fileevent $state(${src}C) readable {} }
        catch { fileevent $state(${src}C) writable {} }
        catch { fileevent $state(${dst}C) readable {} }
        catch { fileevent $state(${dst}C) writable {} }
    }
}


proc beepcore::profile::tunnel::writable {token src dst} {
    variable $token
    upvar 0 $token state

    if {[set len [string length $state(${dst}B)]] == 0} {
        set state(${dst}W) 1

        beepcore::log::entry $state(logT) debug2 ${dst}stream writable

        if {[catch { fileevent $state(${dst}C) writable {} } result]} {
            beepcore::log::entry $state(logT) system $result

            set state(code) 521
            set state(diagnostic) "error on fileevent for ${dst}stream"
        }
    } elseif {[catch {
        puts -nonewline $state(${dst}C) $state(${dst}B)
        flush $state(${dst}C)

        beepcore::log::entry $state(logT) debug2 wrote $len octets on \
                ${dst}stream
    } result]} {
        beepcore::log::entry $state(logT) system $result

        set state(code) 521
        set state(diagnostic) "error writing on ${dst}stream"
    } elseif {(!$state(${src}R)) \
                && ([catch {
        fileevent $state(${src}C) readable \
                  [list [namespace current]::readable $token $src $dst] 
        beepcore::log::entry $state(logT) debug2 enabling reads on ${src}stream
    } result])} {
        beepcore::log::entry $state(logT) system $result

        set state(code) 521
        set state(diagnostic) "error on fileevent for ${src}stream"
    } elseif {[catch { fileevent $state(${dst}C) writable \
                           [list [namespace current]::writable $token \
                                     $src $dst] } \
                     result]} {
        beepcore::log::entry $state(logT) system $result

        set state(code) 521
        set state(diagnostic) "error on fileevent for ${dst}stream"
    } else {
        set state(${dst}B) ""
        set state(${src}R) 1
        set state(${dst}W) 0
    }

    if {$state(code) != 320} {
        catch { fileevent $state(${src}C) readable {} }
        catch { fileevent $state(${src}C) writable {} }
        catch { fileevent $state(${dst}C) readable {} }
        catch { fileevent $state(${dst}C) writable {} }
    }
}

#
# XML parsing
#

proc beepcore::profile::tunnel::element {token tag name {av {}}} {
    variable $token
    upvar 0 $token state

    set depth [llength $state(stack)]
    switch -- $tag {
        start {
            if {[string compare $name tunnel]} {
                oops "not expecting <$name> element"
            }

            if {$depth == 0} {
                array set attrs $av
                foreach k [list fqdn ip4 port srv profile endpoint] {
                    if {[::info exists attrs($k)]} {
                        if {[string length [set state($k) $attrs($k)]] > 0} {
                            append state(mode) .$k
                        }
                    }
                }
            } else {
                append state(data) "<$name"
                foreach {k v} $av {
                    append state(data) " $k=[beepcore::util::xml_av $v]"
                }
                append state(data) ">"
            }

            lappend state(stack) [list $name $av]
        }

        end {
            if {$depth == 1} {
                if {[string length $state(data)] > 0} {
                    append state(mode) .outer
                } else {
                    append state(mode) .inner
                }

                switch $state(mode) {
                    .fqdn.port.outer
                        -
                    .fqdn.port.inner
                        -
                    .ip4.port.outer
                        -
                    .ip4.port.inner
                        -
                    .fqdn.srv.outer
                        -
                    .fqdn.srv.inner
                        -
                    .fqdn.port.srv.outer
                        -
                    .fqdn.port.srv.inner
                        -
                    .profile.inner
                        -
                    .endpoint.inner
                        -
                    .inner {
                    }

                    default {
                        oops "invalid attribute combination in tunnel element"
                    }
                }
            } else {
                append state(data) "</$name>"
            }

            set state(stack) [lreplace $state(stack) end end]
        }
    }
}


proc beepcore::profile::tunnel::cdata {token text} {
    variable $token
    upvar 0 $token state

    if {[string compare [string trim $text] ""]} {
        oops "tunnel element isn't allowed to have content"
    }
}


proc beepcore::profile::tunnel::oops {args} {
    return -code error [join $args " "]
}


# when ...::init runs, it tries to source files that will re-define
# these routines. note that when the files are sourced, they are already 
# inside the "desired" namespace...
#

#
# map the next hop to an auth entry (and, optionally, -username, a proxy name)
#

proc beepcore::profile::tunnel::hop2a {saslT props} {
    switch -- [set code [catch { beepcore::sasl::fetch $saslT tunnel } \
                               result]] {
        0 {
            array set info $result
            array set auth [list mechanism any]
            array set auth $info(authentication)

            return [list -mechanism  $auth(mechanism)  \
                         -authname   tunnel            \
                         -passphrase $auth(passphrase)]
        }

        7 {
            array set response $result
            if {$response(code) != 550} {
                return -code 7 $result
            }
            return ""
        }

        default {
            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


#
# map a profile/endpoint attribute to the next hop
#
#
# a successful return is:
#
#     return [list system "example.com" port "10288" service "idxp"
#                  data "<tunnel> ... </tunnel>"
#                  authparams [list -mechanism "any"    -authname   "wilma" 
#                                   -username  "fred  " -passphrase "secret"]]
#
# where the "system" parameter can be either an ipv4 address or a domain name
#

proc beepcore::profile::tunnel::p2hop {profile} {
    return -code 7 [beepcore::util::xml_error 551 "unknown profile"]
}


proc beepcore::profile::tunnel::e2hop {endpoint} {
    return -code 7 [beepcore::util::xml_error 551 "unknown endpoint"]
}
