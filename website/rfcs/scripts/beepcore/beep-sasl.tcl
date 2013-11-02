#
# beep-sasl.tcl - SASL routines
#


package provide beepcore::sasl  1.0

package require beepcore::server
package require beepcore::log
package require beepcore::util

package require smtp


#
# namespace variables:
#
#    account: current user
#    accountA: serialized-array of users' information
#    privacyL: ordered list of privacy weights
#
# state variables:
#
#    logT: token for logging package
#    clientA: serialized array of client information
#    mechanism: corresponding SASL mechanism
#    mgmtP: management interface in use
#    locks: list of accounts locked
#    authname: if doing proxying
#
# present only during XML parsing
#
#    stack: list containing parse context
#    code: reply code
#    blob: blob element
#    status: abort/completion flag
#


namespace eval beepcore::sasl {
    variable sasl
    array set sasl { uid 0 id2name 0 specials { .default .unknown }}

    variable parser [[namespace parent]::exml::parser]
    catch {
        $parser configure                               \
                -errorcommand [namespace current]::oops \
                -reportempty  no
    }

    variable account .default

    variable accountA
    array set accountA {}

    set fd ""
    if {[catch {
        set fd [open [file join auth default] { RDONLY }]
        set line [string trim [read $fd]]
        if {[string first "<" $line] == 0} {
            set line [beepcore::util::xml2sa $line]
        }
        array set info $line
        close $fd 
    }]} {
        if {[string compare $fd ""]} {
            catch { close $fd }
        }
        set line [list name           $account \
                       authentication "" \
                       authorization  [list acl ""]]
    }
    set accountA($account) $line

    variable privacyL [list none weak strong]

    namespace export init fin \
                     fetch store lock release parse \
                     tuneP id2name unknownA \
                     proxyP login failure logout \
                     allowP \
                     users specialP delete disable
}

proc beepcore::sasl::init {logT clientA {mechanism ""} {mgmtP 0}} {
    variable sasl

    set token [namespace current]::[incr sasl(uid)]

    variable $token
    upvar 0 $token state

    array set state [list logT $logT clientA $clientA mechanism $mechanism \
                          mgmtP $mgmtP locks {} authname ""]

    return $token
}

proc beepcore::sasl::fin {token} {
    variable $token
    upvar 0 $token state

    foreach name $state(locks) {
        catch { file delete -- [authfile $token $name lock] }
    }
    set state(locks) {}

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}

proc beepcore::sasl::fetch {token name} {
    variable $token
    upvar 0 $token state

    variable accountA
    variable privacyL

    nameP $token $name
    if {![file exists [set file [authfile $token $name]]]} {
        if {($state(mgmtP)) && (![string compare $name .default])} {
            return $accountA(.default)
        }

        return -code 7 [list code 550 \
                             diagnostic "username unknown"]
    }

    if {[catch { open $file { RDONLY } } fd]} {
        beepcore::log::entry $state(logT) system $fd
        return -code 7 [list code 451 diagnostic $fd]
    }

    if {[catch {
        set line [string trim [read $fd]]
        if {[string first "<" $line] == 0} {
            set line [beepcore::util::xml2sa $line]
        }
        array set info $line
    }]} {
        catch { close $fd }
        return -code 7 [list code 451 \
                             diagnostic "authorization database corrupt"]
    }

    if {[catch { close $fd } result]} {
        beepcore::log::entry $state(logT) system $result
    }

    set accountA($name) $line

    switch -- [set mechanism $state(mechanism)] {
        external - "" {
        }

        default {
            array set auth $info(authentication)

            if {(![catch { set auth(disabled) } disabled]) \
                    && ([smtp::boolean $disabled])} {
                return -code 7 [list code 534 \
                                     diagnostic "username disabled"]
            }

            if {[string compare $auth(mechanism) $mechanism]} {
                return -code 7 [list code 535 \
                                     diagnostic "authentication mechanism mismatch"]
            }

            set priv $auth(privacy)
            array set tuning $::beepcore::server::tuning
            if {[lsearch -exact $privacyL $priv] \
                    > [lsearch -exact $privacyL $tuning(privacy)]} {
                return -code 7 [list code 538 \
                                     diagnostic "authentication mechanism requires encryption"]
            }
        }
    }

    return $line
}

proc beepcore::sasl::store {token name line {createP 0}} {
    variable sasl

    variable $token
    upvar 0 $token state

    nameP $token $name
    set file [authfile $token $name]

    if {[lsearch -exact $sasl(specials) $name] >= 0} {
        array set info $line
        set info(authentication) ""
        set line [array get info]
    }

    set createP [smtp::boolean $createP]
    if {($createP) && ([file exists $file])} {
        return -code 7 [list code 554 \
                             diagnostic "authorization entry already exists"]
    } 
    if {[lsearch -exact $state(locks) $name] < 0} {
        return -code 7 [list code 450 \
                             diagnostic "username not locked"]
    }

    set fd ""
    if {[catch { 
        set fd [open [set tmp [authfile $token $name tmp]] \
                     { WRONLY CREAT TRUNC }]
        puts $fd [beepcore::util::sa2xml $line]
        flush $fd
    } result]} {
        beepcore::log::entry $state(logT) system $result
        if {[string compare $fd ""]} {
            catch { close $fd }
        }
        return -code 7 [list code 451 diagnostic $result]
    }
    if {[catch { close $fd } result]} {
        beepcore::log::entry $state(logT) system $result
    }

    if {[catch { file rename -force -- $tmp $file } result]} {
        beepcore::log::entry $state(logT) system $result
        return -code 7 [list code 451 diagnostic $result]
    }

    set accountA($name) $line
}

proc beepcore::sasl::lock {token name} {
    variable $token
    upvar 0 $token state

    nameP $token $name

    if {[catch { beepcore::util::exclfile [authfile $token $name lock] } \
               result]} {
        return -code 7 [list code 450 \
                             diagnostic "authorization entry being updated"]
    }

    lappend state(locks) $name
}

proc beepcore::sasl::release {token name} {
    variable $token
    upvar 0 $token state

    if {[set x [lsearch -exact $state(locks) $name]] < 0} {
        return -code 7 [list code 553 \
                             diagnostic "username not locked"]
    }

    if {[catch { file delete -- [authfile $token $name lock] } result]} {
        beepcore::log::entry $state(logT) system $result
        return -code 7 [list code 451 diagnostic $result]
    }

    set state(locks) [lreplace $state(locks) $x $x]
}

proc beepcore::sasl::nameP {token name} {
    variable sasl

    variable $token
    upvar 0 $token state

    if {($state(mgmtP)) && ([lsearch -exact $sasl(specials) $name] >= 0)} {
        return
    }

    if {[catch { split $name . } nameL]} {
        return -code 7 [list code 554 diagnostic "invalid username: $name"]
    }
    
    if {![regexp -- {^[A-Za-z]+$} [lindex $nameL 0]]} {
        return -code 7 [list code 554 diagnostic "invalid username: $name"]
    }

    foreach node [lrange $nameL 1 end] {
        if {![regexp -- {^[A-Za-z0-9_]+$} $node]} {
            return -code 7 [list code 554 diagnostic "invalid username: $name"]
        }
    }
}

proc beepcore::sasl::authfile {token name {suffix sasl}} {
    variable sasl

    variable $token
    upvar 0 $token state

    if {($state(mgmtP)) \
            && (![string compare $suffix sasl]) \
            && ([lsearch -exact $sasl(specials) $name] >= 0)} {
        set name [string range $name 1 end]
        set suffix ""
    } else {
        set suffix .$suffix
    }

    return [file join auth $name$suffix]
}

proc beepcore::sasl::parse {token data} {
    global errorCode errorLine

# for base64
    package require Trf 2

    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable parser

    $parser configure                                                         \
            -elementstartcommand  "[namespace current]::element $token start" \
            -elementendcommand    "[namespace current]::element $token end"   \
            -characterdatacommand "[namespace current]::cdata   $token"       \
            -final                yes

    set state(stack)  ""
    set state(code)   500
    set state(blob)   ""
    set state(status) ""

    set code [catch {
        $parser reset
        $parser parse $data
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result [list blob          $state(blob) \
                             status        $state(status)]
        }

        default {
            append result [beepcore::util::xml_trace $state(logT) sasl \
                               $result $data $state(stack)]

            set code 7

            set result [list code       $state(code) \
                             diagnostic $result]
        }
    }

    unset state(stack) \
          state(code)  \
          state(blob)  \
          state(status)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc beepcore::sasl::proxyP {token authname username} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable accountA

    array set tuning $::beepcore::server::tuning
    if {(![string compare $authname $username]) \
            || (![string compare $username ""]) \
            || (![string compare $tuning(realname) $username])} {
        return
    }

    beepcore::log::entry $state(logT) debug proxyP $authname $username

    if {![info exists accountA($username)]} {
        switch -- [set code [catch { fetch $token $username } result]] {
            0 {
            }

            7 {
                if {![info exists accountA($username)]} {
                    return -code 7 $result
                }
            }

            default {
                set ecode $errorCode
                set einfo $errorInfo

                beepcore::log::entry $state(logT) error sasl::fetch $result

                return -code $code -errorinfo $einfo -errorcode $ecode $result
            }
        }
    }

    array set info $accountA($username)
    array set auth $info(authorization)
    if {([catch { set auth(proxy) } proxy]) \
            || ([lsearch -exact $proxy $authname] < 0)} {
        return -code 7 [list code 539 diagnostic "proxy not authorized"]
    }

    set state(authname) $authname
}

proc beepcore::sasl::login {token name {options {}}} {
    variable $token
    upvar 0 $token state

    variable account

    array set info $state(clientA)
    array set info $options
    if {([string compare $state(authname) ""]) \
            && ([string compare $state(authname) $name])} {
        set info(authname) $state(authname)
    }
    array set tuning $::beepcore::server::tuning
    if {[string compare $tuning(realname) ""]} {
        set info(realname) $tuning(realname)
    }

    set account [set info(name) $name]
    beepcore::log::entry $state(logT) stats sasl::login [array get info]

    if {[string compare $state(mechanism) ""]} {
        array set tuning $::beepcore::server::tuning
        set tuning(sasl) [list mechanism [string toupper $state(mechanism)]]
        set ::beepcore::server::tuning [array get tuning]
    }
}

proc beepcore::sasl::failure {token name options} {
    variable $token
    upvar 0 $token state

    array set info $state(clientA)
    array set info $options
    set info(name) $name
    beepcore::log::entry $state(logT) stats sasl::failure [array get info]
}

proc beepcore::sasl::logout {} {
    variable account

    set account .default
}

proc beepcore::sasl::allowP {logT action scope {name ""}} {
    variable account
    variable accountA

    if {![string compare $name ""]} {
        set name $account
    }

    array set info $accountA($name)
    array set auth $info(authorization)
    array set acl $auth(acl)

    array set allow [list scope $scope privs ""]
    foreach base [lsort -dictionary -decreasing [array names acl]] {
        if {(![string compare $base ""]) \
                || (![string compare $base $scope]) \
                || ([string match $base $scope])} {
            array set allow $acl($base)
            break
        }
    }

    if {([string compare $allow(privs) all]) \
            && ([lsearch -exact $allow(privs) $action] < 0)} {
        beepcore::log::entry $logT stats sasl::allowP \
                   [list name $name action $action scope $scope]
        return -code 7 [list code 537 \
                             diagnostic "action \"$action\" not authorized for scope \"$scope\""]
    }
}

proc beepcore::sasl::tuneP {{errorP 0} {privP 0}} {
    variable account

    if {$privP} {
        array set tuning $::beepcore::server::tuning
        if {(![string compare $tuning(privacy) none]) \
                && ($tuning(sbits) == 0)} {
            return
        }
        set diagnostic "already tuned for privacy"
    } elseif {![string compare $account .default]} {
        return
    } else {
        set diagnostic "already tuned for authentication"
    }

    if {$errorP} {
        set result [beepcore::util::xml_error 520 $diagnostic]
    } else {
        set result [list code 520 diagnostic $diagnostic]
    }

    return -code 7 $result
}


proc beepcore::sasl::id2name {logT id} {
    variable sasl

    if {$sasl(id2name)} {
        return $id
    }

    set sasl(id2name) 1

# NB: this file is being sourced inside the "desired" namespace...

    if {[file exists [set file [file join auth external.tcl]]]} {
        if {[catch { source $file } result]} {
            beepcore::log::entry $logT info "$file: $result"
        } else {
            set id [id2name $logT $id]
        }
    }

    set sasl(id2name) 0

    return $id
}


proc beepcore::sasl::unknownA {token {name .unknown}} {
    variable $token
    upvar 0 $token state

    variable accountA

    if {![catch { set accountA(.unknown) } line]} {
        return $line
    }

    set fd ""
    if {[catch {
        set fd [open [file join auth unknown] { RDONLY }]
        set line [string trim [read $fd]]
        if {[string first "<" $line] == 0} {
            set line [beepcore::util::xml2sa $line]
        }
        array set info $line
        close $fd 
    }]} {
        if {[string compare $fd ""]} {
            catch { close $fd }
        }
        array set info $accountA(.default)
        set info(name) .unknown
    }
    set accountA(.unknown) [array get info]

    if {[string compare $name .unknown]} {
        beepcore::log::entry $state(logT) info \
            "user $name authenticated but not authorized, using template"
        set info(name) $name
        set accountA($name) [array get info]
    }

    return $accountA($name)
}


proc beepcore::sasl::users {token} {
    variable sasl

    variable $token
    upvar 0 $token state

    set users {}
    foreach user $sasl(specials) {
        if {[file exists [authfile $token $user]]} {
            lappend users $user
        }
    }
    if {[lsearch -exact $users .default] < 0} {
        lappend users .default
    }

    foreach file [glob -nocomplain [authfile $token *]] {
        lappend users [file tail [file rootname $file]]
    }

    return [lsort -dictionary $users]
}

proc beepcore::sasl::specialP {token name} {
    variable sasl

    variable $token
    upvar 0 $token state

    if {[lsearch -exact $sasl(specials) $name] >= 0} {
        return 1
    }

    return 0
}

proc beepcore::sasl::delete {token name} {
    variable $token
    upvar 0 $token state

    variable accountA

    if {![string compare $name .default]} {
        return -code 7 [list code 551 \
                             diagnostic "special entry may not be removed"]
    }

    if {[catch { file rename -force -- [set src [authfile $token $name]] \
                      [authfile $token $name .del] } result]} {
        beepcore::log::entry $state(logT) system $result

        if {[catch { file delete -- $src } result]} {
            beepcore::log::entry $state(logT) system $result
            return -code 7 [list code 451 diagnostic $result]
        }
    }

    catch { unset accountA($name) }
}

proc beepcore::sasl::disable {token name} {
    variable sasl

    variable $token
    upvar 0 $token state

    if {[lsearch -exact $sasl(specials) $name] >= 0} {
        return -code 7 [list code 551 \
                             diagnostic "special entry may not be disabled"]
    }

    array set info [fetch $token $name]
    array set auth $info(authentication)
    set auth(disabled) true
    set info(authentication) [array get auth]

    store $token $name [array get info] 
}


#
# XML parsing
#

proc beepcore::sasl::element {token tag name {av {}}} {
    variable $token
    upvar 0 $token state

    switch -- $tag {
        start {
            switch -- $name/[llength $state(stack)] {
                blob/0 {
                    array set attrs [list status "continue"]
                    array set attrs $av
                    if {[lsearch -exact [list abort complete continue] \
                                 $attrs(status)] < 0} {
                        set state(code) 501
                        oops "status attribute poorly formed in <blob> element"
                    }
                    set state(status) $attrs(status)
                }

                default {
                    oops "not expecting <$name> element"
                }
            }

            lappend state(stack) [list $name $av "" ""]
        }

        end {
            set state(stack) [lreplace $state(stack) end end]

            if {(![string compare $name blob]) \
                    && ([catch { base64 -mode decode $state(blob) } \
                               state(blob)])} {
                oops "invalid blob encoding: $state(blob)"
            }
        }
    }
}

proc beepcore::sasl::cdata {token text} {
    variable $token
    upvar 0 $token state

    append state(blob) [string trim $text]
}

proc beepcore::sasl::oops {args} {
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
