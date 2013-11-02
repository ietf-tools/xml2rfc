#
# profile-syslog-raw.tcl - a stub implementation (just for testing clients)
#


package provide beepcore::profile::syslog-raw  1.0

package require beepcore::log
package require beepcore::util


#
# state variables:
#
#    logT: token for logging package
#    upcallV: callback for sending the MSG
#


namespace eval beepcore::profile::syslog-raw {
    variable syslog
    array set syslog { uid 0 }

    namespace export info boot init fin exch2
}


proc beepcore::profile::syslog-raw::info {logT} {
    return [list 0 \
                 [list http://iana.org/beep/syslog/RAW] \
                 [list bootV  [namespace current]::boot  \
                       initV  [namespace current]::init  \
                       exch2V [namespace current]::exch2 \
                       finV   [namespace current]::fin]]
}


proc beepcore::profile::syslog-raw::boot {logT} {
}


proc beepcore::profile::syslog-raw::init {logT serverD clientA upcallV uri} {
    variable syslog

    set token [namespace current]::[incr syslog(uid)]

    variable $token
    upvar 0 $token state

    array set state [list logT $logT upcallV $upcallV]

# after idle sometimes triggers before peer::accept !
    after 1000 [list [namespace current]::start $token]

    return $token
}


proc beepcore::profile::syslog-raw::fin {token status} {
    variable $token
    upvar 0 $token state

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}



proc beepcore::profile::syslog-raw::exch2 {peerT token mimeT} {
    variable $token
    upvar 0 $token state

    mime::finalize $mimeT

    return -code 7 [beepcore::peer::errfmt $peerT 500 "not expecting MSG"]
}


proc beepcore::profile::syslog-raw::start {token} {
    variable $token
    upvar 0 $token state

    set mimeT [mime::initialize \
                   -canonical application/octet-stream \
                   -string "Central Services. This has not been a recording."]

    switch -- [catch { eval $state(upcallV) \
                           [list $mimeT [list [namespace current]::reply \
                                                  $token]] } result] {
        0 {
        }

        7 {
            variable [set beepT [lindex $state(upcallV) 1]]
            upvar 0 $beepT server

            array set reply [beepcore::peer::errscan $server(peerT) \
                                 $result -finalize true]
            beepcore::log::entry $state(logT) info syslog-raw::start \
                $reply(code) $reply(diagnostic) $reply(language)
        }

        default {
            beepcore::log::entry $state(logT) error \
                [lindex $state(upcallV) 0] $result
        }
    }

    mime::finalize $mimeT
}


proc beepcore::profile::syslog-raw::reply {token status mimeT} {
    variable $token
    upvar 0 $token state

    beepcore::log::entry $state(logT) debug syslog-raw::reply $status
    if {![string compare $status answer]} {
        beepcore::log::entry $state(logT) debug syslog-raw::reply \
            [mime::getbody $mimeT]
    }

    mime::finalize $mimeT
}
