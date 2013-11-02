#
# profile-authmgmt.tcl - the AUTHMGMT profile
#
#
# Access control parameters:
#
#       scope - authmgmt:
#               authmgmt:$user 
#
#     actions - create, delete, disable, list, modify, template, test
#


package provide beepcore::profile::authmgmt  1.0

package require beepcore::log
package require beepcore::peer
package require beepcore::sasl
package require beepcore::util


#
# state variables (beep profile):
#
#    logT: token for logging package
#    saslT: token for SASL package
#    cyrusT: server token
#
#
# present only during XML parsing
#
#    stack: list containing parse context
#    code: reply code
#    top: the top-level element received
#    user/scope/action: top-level attributes
#    array: content
#


namespace eval beepcore::profile::authmgmt {
    variable authmgmt
    array set authmgmt { uid 0 }

    variable parser [::beepcore::exml::parser]
    catch {
        $parser configure                               \
                -errorcommand [namespace current]::oops \
                -reportempty  no
    }

    namespace export info boot init fin exch
}


proc beepcore::profile::authmgmt::info {logT} {
    return [list 0 \
                 [list http://beepcore.org/beep/AUTHMGMT] \
                 [list bootV [namespace current]::boot \
                       initV [namespace current]::init \
                       exchV [namespace current]::exch \
                       finV  [namespace current]::fin]]
}


proc beepcore::profile::authmgmt::boot {logT} {
}


proc beepcore::profile::authmgmt::init {logT serverD clientA upcallV uri} {
    global errorCode errorInfo

    variable authmgmt

    set token [namespace current]::[incr authmgmt(uid)]

    variable $token
    upvar 0 $token state

    if {[set code [catch { beepcore::sasl::init $logT $clientA "" 1 } \
                         saslT]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error sasl::init $saslT

        return -code $code -errorinfo $einfo -errorcode $ecode $saslT
    }

    if {[catch { package require beepcore::profile::cyrus
                 beepcore::profile::cyrus::sasl_init  }]} {
        set cyrusT ""
    } elseif {[set code [catch { sasl::server_new -service beep } cyrusT]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT error cyrus::server_new $result

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }

    array set state [list logT $logT saslT $saslT cyrusT $cyrusT]

    return $token
}


proc beepcore::profile::authmgmt::fin {token status} {
    variable $token
    upvar 0 $token state

    if {([string compare $state(cyrusT) ""]) \
            && ([catch { rename $state(cyrusT) {} } result])} {
        beepcore::log::entry $state(logT) error cyrus::fin $result
    }

    if {[catch { beepcore::sasl::fin $state(saslT) } result]} {
        beepcore::log::entry $state(logT) error sasl::fin $result
    }

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}


proc beepcore::profile::authmgmt::exch {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

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

            beepcore::log::entry $state(logT) error authmgmt::parse $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    if {![string compare \
                 [::info commands [namespace current]::exch_$parse(top)] ""]} {
        return -code 7 [beepcore::util::xml_error 500 \
                            "unknown operation: $parse(top)"]
    }

    switch -- [set code [catch { 
        eval [list [namespace current]::exch_$parse(top) $token $result]
    } result]] {
        0 {
             return $result
        }

        7 {
            return -code 7 [beepcore::util::xml_error2 $result]
        }

        default {
            set ecode $errorCode
            set einfo $errorInfo

            beepcore::log::entry $state(logT) error \
                authmgmt::exch_$parse(top) $result

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::profile::authmgmt::exch_list {token props} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set parse $props

    beepcore::sasl::allowP $state(logT) list authmgmt:$parse(user)

    if {[string compare $parse(user) ""]} {
        array set info [beepcore::sasl::fetch $state(saslT) $parse(user)]
        array set auth [list mechanism ""]
        array set auth $info(authentication)
        array set tuning $::beepcore::server::tuning
        switch -- $tuning(privacy)/$auth(mechanism) {
            none/login
                -
            none/plain {
                unset info(authentication)
            }
        }

        return [beepcore::util::sa2xml [array get info]]
    }

    set users {}
    foreach user [beepcore::sasl::users $state(saslT)] {
        lappend users $user {}
    }
    return [beepcore::util::sa2xml $users]
}


proc beepcore::profile::authmgmt::exch_modify {token props} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set parse $props

    if {[catch { array set info [beepcore::util::xml2sa $parse(array)] } \
               result]} {
        return -code 7 [list code 501 diagnostic "invalid array: $result"]
    }

    set elems [list name]
    switch -- $parse(action) {
        create {
            lappend elems authentication authorization

            set authenticationP 1
        }

        modify {
            lappend elems authorization

            set line2 [beepcore::sasl::fetch $state(saslT) $info(name)]
            foreach e [list authentication authorization] {
                if {[::info exists info($e)]} {
                    set ${e}P 1
                } else {
                    array set info2 $line2
                    set info($e) $info2($e) 
                    set ${e}P 0
                }
            }
        }

        default {
            beepcore::sasl::fetch $state(saslT) $info(name)
        }
    }
    foreach e $elems {
        if {![::info exists info($e)]} {
            return -code 7 [list code 501 \
                                 diagnostic "invalid array: no \"$e\" element"]
        }
    }

    beepcore::sasl::allowP $state(logT) $parse(action) authmgmt:$info(name)

    beepcore::sasl::lock $state(saslT) $info(name)

    set code [catch {
        switch -- $parse(action) {
            create
                -
            modify {
                if {([string compare $state(cyrusT) ""]) \
                        && (![beepcore::sasl::specialP $state(saslT) \
                                  $info(name)]) \
                        && ([string compare $info(name) anonymous]) \
                        && ($authenticationP)} {
                    array set auth $info(authentication)

                    if {[catch { set auth(newpass) } newpass]} {
                        return -code 7 [list code 501 \
                                             diagnostic "missing authentication.newpass"]
                    }
                    unset auth(newpass)
                    set args {}
                    if {![catch { set auth(oldpass) } oldpass]} {
                        lappend args -oldpass $oldpass
                        unset auth(oldpass)
                    }
                    if {![string compare $parse(action) create]} {
                        lappend args -flags create
                    }
                    eval [list $state(cyrusT) -operation setpass       \
                                              -user      $info(name)   \
                                              -realm     [::info host] \
                                              -newpass   $newpass] $args

                    set info(authentication) [array get auth]
                }
                beepcore::sasl::store $state(saslT) $info(name) \
                    [array get info] [string compare modify $parse(action)]
            }
    
            delete
                -
            disable {
                if {([string compare $state(cyrusT) ""]) \
                        && (![beepcore::sasl::specialP $state(saslT) \
                                  $info(name)])} {
                    $state(cyrusT) -operation setpass -user $info(name) \
                                   -realm [::info host] -flags disable
                }
                beepcore::sasl::$parse(action) $state(saslT) $info(name)
            }
        }
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    beepcore::sasl::release $state(saslT) $info(name)

    switch -- $code {
        0 {
            set result "<ok />"
        }

        2 {
            set code 7
        }
    }

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


proc beepcore::profile::authmgmt::exch_template {token props} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set parse $props

    beepcore::sasl::allowP $state(logT) template authmgmt:$parse(user)

    if {[string compare $parse(user) ""]} {
        array set info [beepcore::sasl::fetch $state(saslT) $parse(user)]
    } else {
        array set info [beepcore::sasl::unknownA $state(saslT)]
    }

    set info(name) %USER%

    if {[string compare $state(cyrusT) ""]} { 
        set auth(newpass) %PASS%
    }
    array set auth $info(authentication)

    set auth(mechanism) otp
    set auth(sequence)  %SEQUENCE%
    set auth(seed)      %SEED%
    set auth(key)       %KEY%
    set auth(algorithm) %ALGORITHM%
    set info(authentication) [array get auth]
    
    return [beepcore::util::sa2xml [array get info]]
}


proc beepcore::profile::authmgmt::exch_test {token props} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    array set parse $props

    beepcore::sasl::allowP $state(logT) test authmgmt:$parse(user)
    
    beepcore::sasl::fetch $state(saslT) $parse(user)
    beepcore::sasl::allowP $state(logT) $parse(action) $parse(scope) \
        $parse(user)

    return "<ok />"
}


#    role      MSG      RPY      ERR
#    ====      ===      ===      ===
#     I        list     array    error
#     I        modify   ok       error
#     I        template array    error
#     I        test     ok       error
#
#    
#    <!ELEMENT list     EMPTY>
#    <!ATTLIST list
#              user     CDATA    #IMPLIED>
#    
#    <!ELEMENT template EMPTY>
#    <!ATTLIST template
#              user     CDATA    #IMPLIED>
#    
#    <!ELEMENT modify   (array)>
#    <!ATTLIST modify
#              action   (create|delete|disable|modify)
#                                "modify">
#
#    <!ELEMENT test     EMPTY>
#    <!ATTLIST list
#              user     CDATA    #REQUIRED
#              scope    CDATA    #REQUIRED
#              action   CDATA    #REQUIRED>
#
#    
#    <!ELEMENT array    (elem)*>
#    
#    <!ELEMENT elem     ((elem*)|(#PCDATA))> 
#    <!ELEMENT key      CDATA    #REQUIRED>
#    

proc beepcore::profile::authmgmt::parse {token data} {
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable parser

    $parser configure                                                         \
            -elementstartcommand  "[namespace current]::element $token start" \
            -elementendcommand    "[namespace current]::element $token end"   \
            -characterdatacommand "[namespace current]::cdata   $token"       \
            -final                yes

    set state(stack)   {}
    set state(code)    500
    set state(top)     ""
    set state(user)    ""
    set state(array)   "" 
    set state(scope)   ""
    set state(action)  ""

    set code [catch {
        $parser reset
        $parser parse $data
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result [list top    $state(top)   \
                             user   $state(user)  \
                             array  $state(array) \
                             scope  $state(scope) \
                             action $state(action)]
        }

        7 {
        }

        default {
            append result [beepcore::util::xml_trace $state(logT) authmgmt \
                               $result $data $state(stack)]

            set code 7

            set result [list code       $state(code) \
                             diagnostic $result]
        }
    }

    unset state(stack) \
          state(code)  \
          state(top)   \
          state(user)  \
          state(array) \
          state(scope) \
          state(action)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


#
# XML parsing
#

proc beepcore::profile::authmgmt::element {token tag name {av {}}} {
    variable $token
    upvar 0 $token state

    set depth [llength $state(stack)]
    switch -- $tag {
        start {
            set oopsP 0 
            switch -glob -- $depth/$state(top) {
                0/ {
                    switch -- $name {
                        list
                            -
                        template {
                            array set attrs [list user ""]
                            array set attrs $av
                            set state(user) $attrs(user)
                        }

                        modify {
                            array set attrs [list action modify]
                            array set attrs $av
                            if {[lsearch [list create delete disable modify] \
                                         [set state(action) $attrs(action)]] \
                                    < 0} {
                                oops "invalid value $attrs(action) for $k attribute in <$name> element"
                            }
                        }

                        test {
                            array set attrs [list user "" scope "" action ""]
                            array set attrs $av
                            foreach k [list user scope action] {
                                if {![string compare $attrs($k) ""]} {
                                    oops "expecting $k attribute in <$name> element"
                                } else {
                                    set state($k) $attrs($k)
                                }
                            }
                        }

                        default {
                            set oopsP 1 
                        }
                    }
                    set state(top) $name
                }

                */modify {
                    append state(array) "<$name"
                    foreach {k v} $av {
                        append state(array) " $k=[beepcore::util::xml_av $v]"
                    }
                    append state(array) ">"                 
                }

                default {
                    set oopsP 1 
                }
            }
            if {$oopsP} {
                set state(code) 501
                oops "not expecting <$name> element"
            }

            lappend state(stack) [list $name $av]
        }

        end {
            switch -glob -- $depth/$state(top) {
                1/modify {
                }

                */modify {
                    append state(array) "</$name>"
                }
            }

            set state(stack) [lreplace $state(stack) end end]
        }
    }
}


proc beepcore::profile::authmgmt::cdata {token text} {
    variable $token
    upvar 0 $token state

    set frame [lindex $state(stack) 0]
    set name [lindex $frame 0]

    switch -glob -- $state(top)/$name {
        */modify {
            append state(array) $text
        }

        default {
            if {[string compare [string trim $text] ""]} {
                oops "$name element isn't allowed to have content"
            }
        }
    }
}


proc beepcore::profile::authmgmt::oops {args} {
    return -code error [join $args " "]
}
