#
# beep-peer.tcl - BEEP peer-level routines
#


package provide beepcore::peer   2.0

package require beepcore::log
package require beepcore::util

package require mime
package require smtp


# backwards compatibility with 1.0
#
#     -answerCallback
#     -requestCallback
#     -responseCallback
#     -serialNumbers
#
#     serialNumber
#
#     ::request
#     ::response
#

#
# peerT state variables:
#
#     logT: token for logging package
#     inputT: input side of channel
#     outputT: input side of channel
#     options: from ::join
#       -localize
#       -profiles
#       -serverName
#       -initiator
#       -startCallback
#       -eventCallback
#       -updateSeq
#     features: feature tokens from peer's greeting
#     localize: desired languages from peer's greeting
#     profiles: URIs from peer's greeting
#     channelL: list of channelTs
#     channelN: last channel-number we started
#     channelX: last channelT that sent a frame
#     readable: semaphore for vwait
#       0/1: (not) readable
#        -1: timeout (transient)
#        -2: network error
#        -3: premature end-of-file
#        -4: peer error
#        -5: fileevent error
#     writable: according to fileevent
#     afterID: for timeout
#     rcv.stamp: timestamp of last activity
#     event: serialized array
#     incoming: a serialized array for incoming frame
#     buffer: incoming octets
#     slideL: list of channels that need to have their window updated
#     crtVs: array of create callback vectors (indexed by channelNumber)
#     fin1P: locally-initiated graceful release in progress
#     fin2P: remotely-initiated graceful release successful
#
# present only during XML parsing
#
#    stack: list containing parse context
#    code: reply code
#    top: kind of element being parsed
#    lang/data/ftrs/locs/uriL/dataL/number/serverName: attributes/elements
#

#
# channelT state variables:
#
#     logT: token for logging package
#     peerT: parent token
#     channelNumber: the channel number
#     options: from ::start/::accept
#       -messageCallback
#       -segmentCallback
#       -releaseCallback
#     profile: profile bound to channel
#     datum: data returned when channel started
#     snd.una / snd.nxt / snd.wnd / rcv.nxt / rcv.wnd: sequence space info
#     rcv.buf: maximum space to allocate
#     rcv.stamp: timestamp of last activity
#     sendQ: list of outgoing frames
#     recvQ: list of incoming frames
#     busyP: processing a message
#     rpyVs: array of reply callback vectors (indexed by msgNo)
#     msgN: last message-number we used
#     msgNos: a serialized array mapping
#       msgNo,local: local MSG, final segment not yet sent
#       msgNo,remote: remote MSG, final segment not yet rcvd
#       msgNo,reply: status associated with previous segment of remote reply
#


namespace eval beepcore::peer {
    variable peer
    array set peer [list uid   0 \
                         empty [list waitingFor   header \
                                     ansNo        ""]]

    variable parser [[namespace parent]::exml::parser]
    catch {
        $parser configure                               \
                -errorcommand [namespace current]::oops \
                -reportempty  no
    }

    namespace export join done \
                     start accept decline stop \
                     getprop setprop \
                     message reply \
                     sendseg \
                     wait \
                     str2xml errfmt errfmt2 errfmt3 errfmt4 errscan errscan2 \
                     request response \

    set bits 1
    set value 1
    while {$value > 0} {
        incr bits
        set value [expr $value<<1]
    }
    if {$bits != 32} {
        error "expecting a 32-bit architecture..."
    }
}


#
# peer binding
#


proc beepcore::peer::join {logT socketT args} {
    global errorCode errorInfo

    variable peer

    set peerT [namespace current]::[incr peer(uid)]

    variable $peerT
    upvar 0 $peerT state

    array set argv [list -localize      {i-default} \
                         -profiles      {}          \
                         -serverName    ""          \
                         -initiator     true        \
                         -startCallback {}          \
                         -eventCallback {}          \
                         -updateSeq     1]
    array set argv $args

    if {[set argv(-initiator) [smtp::boolean $argv(-initiator)]]} {
        set channelN -1
    } else {
        set channelN 0
    }

    if {[llength $socketT] == 1} {
        lappend socketT $socketT
    }

    array set state [list logT      $logT               \
                          inputT    [lindex $socketT 0] \
                          outputT   [lindex $socketT 1] \
                          options   [array get argv]    \
                          features  {}                  \
                          localize  {}                  \
                          profiles  {}                  \
                          channelL  {}                  \
                          channelN  $channelN           \
                          channelX  ""                  \
                          readable  0                   \
                          writable  0                   \
                          afterID   ""                  \
                          rcv.stamp ""                  \
                          event     {}                  \
                          incoming  $peer(empty)        \
                          buffer    ""                  \
                          slideL    {}                  \
                          crtVs     ""                  \
                          fin1P     0                   \
                          fin2P     0]

    set greeting "<greeting"
    if {[string compare $argv(-localize) i-default]} {
        append greeting " localize=[beepcore::util::xml_av $argv(-localize)]"
    }
    if {[llength $argv(-profiles)] > 0} {
        append greeting ">\n"
        foreach uri $argv(-profiles) {
            append greeting \
                "    <profile uri=[beepcore::util::xml_av $uri] />\n"
        }
        append greeting "</greeting>"
    } else {
        append greeting " />"
    }

    if {[set code [catch {
        fconfigure $state(inputT) -blocking off -buffersize 65536 \
                   -translation binary
        if {[string compare $state(inputT) $state(outputT)]} {
            fconfigure $state(outputT) -blocking off -buffersize 65536 \
                       -translation binary
        }
        fileevent $state(inputT)  readable \
                  [list [namespace current]::readable $peerT]
        fileevent $state(outputT) writable \
                  [list [namespace current]::writable $peerT]

        variable [set channelT \
                      [up $peerT 0 \
                           -messageCallback [namespace current]::channel0_message \
                           -releaseCallback [namespace current]::channel0_release]]
        upvar 0 $channelT child

        array set callbacks $child(rpyVs)
        set callbacks(0) [list rpyV [namespace current]::channel0_greeting]
        set child(rpyVs) [array get callbacks]

        reply $channelT 0 [set mimeT [str2xml $greeting]]

        mime::finalize $mimeT
    } result]]} {
        set ecode $errorCode
        set einfo $errorInfo

        beepcore::log::entry $logT system $result

        catch { done $peerT -release terminal }

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }

    set code [catch { wait $peerT -timeout 0 } result]
    set ecode $errorCode
    set einfo $errorInfo

    if {[info exists state(restartP)] && $state(restartP)} {
        return -code 8 $peerT
    }

    if {![info exists state(logT)]} {
        error "peer token destroyed"
    }

    switch -- $code {
        0 {
            return $peerT
        }

        default {
            if {$code != 7} {
                beepcore::log::entry $state(logT) error peer::wait $result
            } else {
                set code 1

                array set reply $result
                set result $reply(diagnostic)
            }

            catch { done $peerT -release terminal }

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::peer::done {peerT args} {
    global errorCode errorInfo

    variable $peerT
    upvar 0 $peerT state

    tokenP $peerT peer

    array set argv [list -release       orderly \
                         -code          200     \
                         -diagnostic    ""      \
                         -language      ""      \
                         -finalCallback {}]
    array set argv $args

    set asyncP [string compare $argv(-finalCallback) ""]
    switch -- $argv(-release) {
        orderly {
            if {!$state(fin2P)} {
            } elseif {$asyncP} {
                return -code 7 $state(event)
            } else {
                set argv(-release) terminal
            }
        }

        abortive
            -
        terminal {
            if {$asyncP} {
                error "use of -finalCallback requires -release orderly"
            }
        }

        default {
            error "unknown argument to -release: $argv(-release)"
        }
    }

    if {![string compare $argv(-release) orderly]} {
        switch -- [set code [catch { twopass $peerT internal } result]] {
            0 {
            }

            8 {
                return
            }

            7
                -
            default {
                set ecode $errorCode
                set einfo $errorInfo

                if {$code != 7} {
                    beepcore::log::entry $state(logT) error peer::twopass \
                        $result
                }

                return -code $code -errorinfo $einfo -errorcode $ecode \
                       $result
            }
        }

        set mimeT [str2xml [xmlfmt $peerT close $argv(-code) \
                                   $argv(-diagnostic) $argv(-language)]]

        incr state(fin1P)

        if {$asyncP} {
            set code [catch {
                message [child $peerT 0] $mimeT \
                    -replyCallback [list [namespace current]::channel0_closing \
                                             $argv(-finalCallback) ""]
            } result]
        } else {
            set code [catch { message [child $peerT 0] $mimeT } result]
        }
        set ecode $errorCode
        set einfo $errorInfo

        mime::finalize $mimeT

        if {($code) || (!$asyncP)} {
            incr state(fin1P) -1
        }

        switch -- $code {
            0 {
                if {$asyncP} {
                    return $result
                }

                mime::finalize $result
            }

            7 {
                return -code 7 [errscan $peerT $result -finalize true]
            }

            default {
                return -code $code -errorinfo $einfo -errorcode $ecode \
                       $result
            }
        }
    } else {
        if {!$state(fin2P)} {
            foreach channelT $state(channelL) {
                variable $channelT
                upvar 0 $channelT child

                array set options $child(options)
                if {[string compare $options(-releaseCallback) ""]} {
                    if {[catch { eval $options(-releaseCallback) \
                                      [list $channelT internal abort] } \
                                result]} {
                        log $peerT user $result
                    }
                }

                unset options

                if {![info exists state(logT)]} {
                    return
                }
            }
        }

        if {![string compare $argv(-release) abortive]} {
            if {$argv(-code) < 400} {
                set argv(-code) 550
            }
            set mimeT [str2xml [xmlfmt $peerT close $argv(-code) \
                                       $argv(-diagnostic) $argv(-language)]]

            if {[catch { message [child $peerT 0] $mimeT \
                             -replyCallback [list [namespace current]::channel0_closing \
                                                      "" ""] } result]} {
                log $peerT error peer::message $result
            }

            mime::finalize $mimeT
        }
    }

    if {![info exists state(logT)]} {
        return
    }

    foreach channelT $state(channelL) {
        if {[catch { down $channelT } result]} {
            beepcore::log::entry $state(logT) error peer::down $result
        }
    }

    catch { fileevent $state(inputT)  readable "" }
    catch { fileevent $state(outputT) writable "" }
    if {[string compare $state(afterID) ""]} {
        catch { after cancel $state(afterID) }
        set state(afterID) ""
    }

    foreach name [array names state] {
        unset state($name)
    }
    unset $peerT

}


# eval'd when a message is received on channel zero

proc beepcore::peer::channel0_message {channelZ args} {
    variable $channelZ
    upvar 0 $channelZ state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set argv $args

    set code [catch { parse $peerT $argv(mimeT) loop } result]

    mime::finalize $argv(mimeT)

    switch -- $code {
        0 {
            array set reply $result
        }

        default {
            beepcore::log::entry $state(logT) error peer::parse $result

            set result [list code       550     \
                             diagnostic $result \
                             language   en-US]

            set mimeT [errfmt3 $peerT $result]

            if {[catch { reply $channelZ $argv(msgNo) $mimeT \
                               -status negative } result]} {
                log $peerT error peer::reply $result
            }

            mime::finalize $mimeT

            return
        }
    }

    switch -- $reply(top) {
        start {
            array set options $parent(options)
            if {![string compare $options(-startCallback) ""]} {
                set mimeT [errfmt $peerT 550 "not creating channels" en-US]

                if {[catch { reply $channelZ $argv(msgNo) $mimeT \
                                   -status negative } result]} {
                    log $peerT error peer::reply $result
                }

                mime::finalize $mimeT

                return
            }

            set channelNumber $reply(number)

            array set callbacks $parent(crtVs)
            if {[info exists callbacks($channelNumber)]} {
                set diagnostic "already creating channel"
            } elseif {![catch { child $peerT $channelNumber }]} {
                set diagnostic "channel already in use"
            } else {
                set diagnostic ""
            }

            if {[string compare $diagnostic ""]} {
                set mimeT [errfmt $peerT 550 $diagnostic en-US]

                if {[catch { reply $channelZ $argv(msgNo) $mimeT \
                                   -status negative } result]} {
                    log $peerT error peer::reply $result
                }

                mime::finalize $mimeT

                return
            }

            set reply(channelT) [up $peerT $channelNumber]
            set reply(msgNo) $argv(msgNo)
            set callbacks($channelNumber) [array get reply]
            set parent(crtVs) [array get callbacks]

            unset reply(msgNo)    \
                  reply(channelT) \
                  reply(number)

            if {[set code [catch { eval $options(-startCallback) \
                                        [list $peerT \
                                              channelNumber $channelNumber] \
                                        [array get reply] } result]]} {
                if {$code != 7} {
                    log $peerT user $result
                }
            }
            if {($code == 0) || (![info exists parent(logT)])} {
                return
            }

            unset callbacks \
                  reply

            array set callbacks $parent(crtVs)
            if {[catch { array set reply $callbacks($channelNumber) }]} {
                return
            }
            unset callbacks($channelNumber)
            set parent(crtVs) [array get callbacks]

            if {[catch { down $reply(channelT) } result2]} {
                beepcore::log::entry $state(logT) error peer::down $result2
            }

            if {$code != 7} {
                set result [list code       550     \
                                 diagnostic $result \
                                 language   en-US]
            }

            set mimeT [errfmt3 $peerT $result]

            if {[catch { reply [child $peerT 0] $reply(msgNo) $mimeT \
                               -status negative } result]} {
                log $peerT error peer::reply $result
            }

            mime::finalize $mimeT
        }

        close {
            switch -- [set code [catch {
                if {$reply(number) != 0} {
                    set channelT [child $peerT $reply(number)]
                }
                twopass $peerT external $reply(number)
            } result]] {
                0 {
                    if {$reply(number) == 0} {
                        set parent(fin2P) 1
                    }

                    set mimeT [str2xml "<ok />"]

                    if {[catch { reply $channelZ $argv(msgNo) $mimeT } \
                               result]} {
                        log $peerT error peer::reply $result
                    }

                    if {$reply(number) == 0} {
                        report $peerT external 200 \
                               "session released by remote peer"
                    } elseif {[catch { down $channelT } result]} {
                        beepcore::log::entry $state(logT) error peer::down \
                            $result
                    }
                }

                8 {
                    return
                }

                7
                    -
                default {
                    if {$code != 7} {
                        beepcore::log::entry $state(logT) error peer::twopass \
                            $result

                        set result [list code       550     \
                                         diagnostic $result \
                                         language   en-US]
                    }

                    set mimeT [errfmt3 $peerT $result]

                    if {[catch { reply $channelZ $argv(msgNo) $mimeT \
                                       -status negative } result]} {
                        log $peerT error peer::reply $result
                    }
                }
            }

            mime::finalize $mimeT

            return
        }
    }
}


proc beepcore::peer::twopass {peerT source {channelNumber 0}} {
    variable $peerT
    upvar 0 $peerT state

    set code 0
    array set reply {}

    set channelY {}
    set final commit

    foreach channelT $state(channelL) {
        variable $channelT
        upvar 0 $channelT child

        if {$channelNumber > 0} {
            if {$channelNumber != $child(channelNumber)} {
                continue
            }

            set hits [llength [concat $child(sendQ) $child(recvQ)]]

            array set msgNos $child(msgNos)
            foreach {k v} [array get msgNos] {
                if {([string first ,local $k] > 0) \
                        || ([string first ,remote $k] > 0)} {
                    incr hits
                    break
                }
            }

            if {$hits > 0} {
                set code 7
                array set reply [list code       550                    \
                                      diagnostic "messages outstanding" \
                                      language   en-US]
                set final rollback

                break
            }
        }

        array set options $child(options)
        if {[string compare $options(-releaseCallback) ""]} {
            switch -- [set code [catch { eval $options(-releaseCallback) \
                                              [list $channelT $source \
                                                    query] } result]] {
                0 {
                    lappend channelY $channelT
                }

                7 {
                    array set reply [list code       550 \
                                          diagnostic ""  \
                                          language   en-US]
                    catch { array set reply $result }

                    set final rollback

                    unset options
                    break
                }

                default {
                    log $peerT user $result
                }
            }

            if {![info exists state(logT)]} {
                return -code 8 ""
            }
        }

        unset options
    }

    if {![info exists state(logT)]} {
        return -code 8 ""
    }

    foreach channelT $channelY {
        upvar 0 $channelT child

        array set options $child(options)
        if {[catch { eval $options(-releaseCallback) \
                          [list $channelT $source $final] } result]} {
            log $peerT user $result
        }

        if {![info exists state(logT)]} {
            return -code 8 ""
        }

        unset options
    }

    return -code $code [array get reply]
}


# eval'd when either peer wants to release the session

proc beepcore::peer::channel0_release {channelZ source mode} {
    variable $channelZ
    upvar 0 $channelZ state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    if {([string compare $mode query]) || ($parent(fin1P))} {
        return
    }

    if {[string compare $parent(crtVs) ""]} {
        return -code 7 [list code       550                     \
                             diagnostic "callbacks outstanding" \
                             language   en-US]
    }

    if {![string compare $source internal]} {
        set hits 0
    } else {
        set hits -1
    }

    foreach channelT $parent(channelL) {
        variable $channelT
        upvar 0 $channelT child

        incr hits [llength [concat $child(sendQ) $child(recvQ)]]

        array set msgNos $child(msgNos)
        foreach {k v} [array get msgNos] {
            if {([string first ,local $k] > 0) \
                    || ([string first ,remote $k] > 0)} {
                incr hits
            }
        }

        unset msgNos

        if {$hits > 0} {
            return -code 7 [list code       550                    \
                                 diagnostic "messages outstanding" \
                                 language   en-US]
        }
    }
}


# eval'd when the initial greeting (a reply) is received

proc beepcore::peer::channel0_greeting {channelZ args} {
    variable $channelZ
    upvar 0 $channelZ state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set argv $args

    switch -- $argv(status) {
        positive {
            set code [catch { parse $peerT $argv(mimeT) greeting } result]

            mime::finalize $argv(mimeT)

            if {$code} {
                beepcore::log::entry $state(logT) error peer::parse $result

                report $peerT internal 550 $result

                return
            }

            array set reply $result

            set parent(features) $reply(features)
            set parent(localize) $reply(localize)
            set parent(profiles) [linsert $reply(profiles) 0 ""]
        }

        negative {
            array set reply [errscan $peerT $argv(mimeT) -finalize true]

            report $peerT external $reply(code) $reply(diagnostic) \
                   $reply(language)
        }

        default {
            mime::finalize $argv(mimeT)

            report $peerT internal 520 "not expecting $argv(status) reply"
        }
    }
}


# eval'd in reply to our message to release the session/close a channel

proc beepcore::peer::channel0_closing {callbackV channelT channelZ args} {
    variable $channelZ
    upvar 0 $channelZ state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set argv $args

    if {![set childP [string compare $channelT ""]]} {
        incr parent(fin1P) -1
    }

    switch -- $argv(status) {
        positive {
            array set reply [errscan $peerT $argv(mimeT) -finalize true \
                                     -tag ok]

            if {[string compare $callbackV ""]} {
                if {[catch { eval $callbackV \
                                  [list $peerT status $argv(status)] } \
                           result]} {
                    log $peerT user $result
                }
            }

            if {!$childP} {
                report $peerT internal 200 "orderly release successful"
            } elseif {[catch { down $channelT } result]} {
                beepcore::log::entry $state(logT) error peer::down $result
            }
        }

        negative {
            array set reply [errscan $peerT $argv(mimeT) -finalize true]

            if {[string compare $callbackV ""]} {
                if {[catch { eval $callbackV \
                                  [list $peerT status $argv(status)] \
                                  [array get reply] } result]} {
                    log $peerT user $result
                }
            }
        }

        default {
            mime::finalize $argv(mimeT)

            report $peerT internal 520 "not expecting $argv(status) reply"
        }
    }
}


#
# channel binding
#


proc beepcore::peer::start {peerT profiles args} {
    global errorCode errorInfo

    variable $peerT
    upvar 0 $peerT state

    tokenP $peerT peer

    set dataL {}
    for {set x [llength $profiles]} {$x > 0} {incr x -1} {
        lappend dataL ""
    }
    if {$state(channelN) < 1} {
        array set options $state(options)
        set serverName $options(-serverName)
    } else {
        set serverName ""
    }
    array set argv [list -data            $dataL      \
                         -serverName      $serverName \
                         -createCallback  {}          \
                         -messageCallback {}          \
                         -segmentCallback {}          \
                         -releaseCallback {}]
    array set argv $args
    if {![string compare $argv(-createCallback) ""]} {
        catch { set argv(-createCallback) $argv(-answerCallback) }
    }
    if {![string compare $argv(-messageCallback) ""]} {
        catch { set argv(-messageCallback) $argv(-requestCallback) }
    }

    if {[set x [llength $profiles]] != [llength $argv(-data)]} {
        error "profiles/-data length mismatch"
    }
    if {$x < 1} {
        error "at least one profile must be specified"
    }
    if {([string compare $argv(-messageCallback) ""]) \
            && ([string compare $argv(-segmentCallback) ""])} {
        error "both -messageCallback and -segmentCallback specified"
    }

    if {[set channelNumber [incr state(channelN) 2]] > 2147483647} {
        error "out of channels"
    }
    set start "<start number=[beepcore::util::xml_av $channelNumber]"
    if {[string compare $argv(-serverName) ""]} {
        append start " serverName=[beepcore::util::xml_av $argv(-serverName)]"
    }
    append start ">\n"
    foreach uri $profiles datum $argv(-data) {
        append start "    <profile uri=[beepcore::util::xml_av $uri]"
        if {[string compare $datum ""]} {
            append start ">" [beepcore::util::xml_cdata $datum] "</profile>\n"
        } else {
            append start " />\n"
        }
    }
    append start "</start>"

    variable [set channelT \
                  [up $peerT $channelNumber \
                       -messageCallback $argv(-messageCallback) \
                       -segmentCallback $argv(-segmentCallback) \
                       -releaseCallback $argv(-releaseCallback)]]
    upvar 0 $channelT child

    set mimeT [str2xml $start]

    if {[set asyncP [string compare $argv(-createCallback) ""]]} {
        set code [catch { message [child $peerT 0] $mimeT \
                              -replyCallback \
                                  [list [namespace current]::channel0_create \
                                        $channelT $argv(-createCallback)]
        } result]
    } else {
        set code [catch { message [child $peerT 0] $mimeT } result]
    }
    set ecode $errorCode
    set einfo $errorInfo

    mime::finalize $mimeT

    if {($code) && ([catch { down $channelT } result2])} {
        beepcore::log::entry $state(logT) error peer::down $result2
    }

    switch -- $code {
        0 {
            if {$asyncP} {
                return $result
            }

            set mimeT $result
        }

        7 {
            return -code 7 [errscan $peerT $result -finalize true]
        }

        default {
            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    set code [catch { parse $peerT $mimeT profile } result]
    set ecode $errorCode
    set einfo $errorInfo

    mime::finalize $mimeT

    if {$code} {
        beepcore::log::entry $state(logT) error peer::parse $result

        if {[catch { down $channelT } result2]} {
            beepcore::log::entry $state(logT) error peer::down $result2
        }

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }

    array set reply $result
    set child(profile) $reply(uri)
    set child(datum) $reply(data)

    return $channelT
}


proc beepcore::peer::accept {peerT channelNumber profile args} {
    variable $peerT
    upvar 0 $peerT state

    tokenP $peerT peer

    array set argv [list -datum           "" \
                         -messageCallback {} \
                         -segmentCallback {} \
                         -releaseCallback {}]
    array set argv $args
    if {![string compare $argv(-messageCallback) ""]} {
        catch { set argv(-messageCallback) $argv(-requestCallback) }
    }

    if {([string compare $argv(-messageCallback) ""]) \
            && ([string compare $argv(-segmentCallback) ""])} {
        error "both -messageCallback and -segmentCallback specified"
    }

    array set callbacks $state(crtVs)
    if {[catch { array set reply $callbacks($channelNumber) }]} {
        error "channelNumber doesn't refer to a channel pending creation"
    }
    if {[lsearch $reply(profiles) $profile] < 0} {
        error "URI wasn't offered"
    }
    unset callbacks($channelNumber)
    set state(crtVs) [array get callbacks]

    variable [set channelT $reply(channelT)]
    upvar 0 $channelT child

    set profile \
        "<profile uri=[beepcore::util::xml_av [set child(profile) $profile]]"
    if {[string compare $argv(-datum) ""]} {
        append profile ">" [beepcore::util::xml_cdata $argv(-datum)] \
               "</profile>"
    } else {
        append profile " />"
    }

    unset argv(-datum)
    set child(options) [array get argv]

    set mimeT [str2xml $profile]

    if {[catch { reply [child $peerT 0] $reply(msgNo) $mimeT } result]} {
        log $peerT error peer::reply $result
    }

    mime::finalize $mimeT

    return $channelT
}


proc beepcore::peer::decline {peerT channelNumber code {diagnostic ""} 
                              {language ""}} {
    variable $peerT
    upvar 0 $peerT state

    tokenP $peerT peer

    array set callbacks $state(crtVs)
    if {[catch { array set reply $callbacks($channelNumber) }]} {
        error "channelNumber doesn't refer to a channel pending creation"
    }
    unset callbacks($channelNumber)
    set state(crtVs) [array get callbacks]

    if {[catch { down $reply(channelT) } result]} {
        beepcore::log::entry $state(logT) error peer::down $result
    }

    set mimeT [errfmt $peerT $code $diagnostic $language]

    if {[catch { reply [child $peerT 0] $reply(msgNo) $mimeT \
                       -status negative } result]} {
        log $peerT error peer::reply $result
    }

    mime::finalize $mimeT
}


# eval'd when the reply to a <start> is received on channel zero

proc beepcore::peer::channel0_create {channelT callbackV channelZ args} {
    variable $channelT
    upvar 0 $channelT state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set argv $args

    switch -- $argv(status) {
        positive {
            set code [catch { parse $peerT $argv(mimeT) profile } result]

            mime::finalize $argv(mimeT)

            switch -- $code {
                0 {
                    array set reply $result

                    set params \
                        [list status   positive                         \
                              channelT $channelT                        \
                              profile  [set state(profile) $reply(uri)] \
                              datum    [set state(datum)   \
                                            [beepcore::util::xml_pcdata \
                                                 $reply(data)]]]
                }

                default {
                    beepcore::log::entry $state(logT) error peer::parse $result

                    if {[catch { down $channelT } result2]} {
                        beepcore::log::entry $state(logT) error peer::down \
                            $result2
                    }

                    set params [list status     negative \
                                     code       550      \
                                     diagnostic $result  \
                                     language   en-US]
                }
            }

            if {[catch { eval $callbackV [list $peerT] $params } result]} {
                log $peerT user $result
            }
        }

        negative {
            if {[catch { down $channelT } result]} {
                beepcore::log::entry $state(logT) error peer::down $result
            }

            array set reply [errscan $peerT $argv(mimeT) -finalize true]

            if {[catch { eval $callbackV \
                              [list $peerT status $argv(status)] \
                              [array get reply] } result]} {
                log $peerT user $result
            }
        }

        default {
            mime::finalize $argv(mimeT)

            report $peerT internal 520 "not expecting $argv(status) reply"
        }
    }
}


proc beepcore::peer::stop {channelT args} {
    global errorCode errorInfo

    variable $channelT
    upvar 0 $channelT state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set argv [list -code          200 \
                         -diagnostic    ""  \
                         -language      ""  \
                         -finalCallback {}]
    array set argv $args

    set asyncP [string compare $argv(-finalCallback) ""]

    switch -- [set code [catch { twopass $peerT internal \
                                         $state(channelNumber) } result]] {
        0 {
        }

        8 {
            return
        }

        7
            -
        default {
            set ecode $errorCode
            set einfo $errorInfo

            if {$code != 7} {
                beepcore::log::entry $state(logT) error peer::twopass $result
            }

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }

    set mimeT [str2xml \
                   [xmlfmt $peerT close $argv(-code) \
                        $argv(-diagnostic) $argv(-language) \
                        " number=[beepcore::util::xml_av $state(channelNumber)]"]]

    if {$asyncP} {
        set code [catch { message [child $peerT 0] $mimeT \
                              -replyCallback \
                                  [list [namespace current]::channel0_closing \
                                        $argv(-finalCallback) $channelT]
        } result]
    } else {
        set code [catch { message [child $peerT 0] $mimeT } result]
    }
    set ecode $errorCode
    set einfo $errorInfo

    mime::finalize $mimeT

    switch -- $code {
        0 {
            if {$asyncP} {
                return $result
            }

            mime::finalize $result
        }

        7 {
            return -code 7 [errscan $peerT $result -finalize true]
        }

        default {
            return -code $code -errorinfo $einfo -errorcode $ecode \
                   $result
        }
    }

    if {![info exists state(logT)]} {
        return
    }

    if {[catch { down $channelT } result]} {
        beepcore::log::entry $state(logT) error peer::down $result
    }
}


proc beepcore::peer::up {peerT channelNumber args} {
    variable peer

    variable $peerT
    upvar 0 $peerT parent

    variable [set channelT ${peerT}_$channelNumber]
    upvar 0 $channelT state

    array set argv [list -messageCallback {} \
                         -segmentCallback {} \
                         -releaseCallback {}]
    array set argv $args
    if {![string compare $argv(-messageCallback) ""]} {
        catch { set argv(-messageCallback) $argv(-requestCallback) }
    }

    if {$channelNumber == 0} {
        set msgNos(0,local)  0
        set msgNos(0,remote) 0
    }

    array set state [list logT          $parent(logT)       \
                          peerT         $peerT              \
                          channelNumber $channelNumber      \
                          options       [array get argv]    \
                          profile       ""                  \
                          datum         ""                  \
                          snd.una       0                   \
                          snd.nxt       0                   \
                          snd.wnd       4096                \
                          rcv.nxt       0                   \
                          rcv.wnd       65407               \
                          rcv.buf       100                 \
                          rcv.stamp     ""                  \
                          sendQ         {}                  \
                          recvQ         {}                  \
                          busyP         0                   \
                          rpyVs         {}                  \
                          msgN          0                   \
                          msgNos        [array get msgNos]]

    if {$channelNumber == 0} {
        set state(rcv.wnd) 4096
    }

    lappend parent(channelL) $channelT

    [namespace current]::upaux $peerT

    return $channelT
}

proc beepcore::peer::upaux {peerT} {
    variable $peerT
    upvar 0 $peerT state

    set total 0
    foreach channelT $state(channelL) {
        variable $channelT
        upvar 0 $channelT child

        if {$child(channelNumber) != 0} {
            incr total $child(rcv.buf)
        }
    }

    foreach channelT $state(channelL) {
        variable $channelT
        upvar 0 $channelT child

        if {$child(channelNumber) != 0} {
            if {$child(rcv.buf) == 0} {
                set child(rcv.wnd) 0
            } else {
                set child(rcv.wnd) [expr ($child(rcv.buf)*65407)/$total]
            }
            log $peerT debug $channelT rcv.wnd $child(rcv.wnd)
        }
    }
}

proc beepcore::peer::down {channelT} {
    variable $channelT
    upvar 0 $channelT state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set callbacks $state(rpyVs)
    foreach msgNo [array names callbacks] {
        array set reply $callbacks($msgNo)

        if {[info exists reply(mimeT)]} {
            mime::finalize $reply(mimeT)
        }

        unset reply
    }

    if {[set x [lsearch $parent(channelL) $channelT]] >= 0} {
        set parent(channelL) [lreplace $parent(channelL) $x $x]
    }
    if {![string compare $parent(channelX) $channelT]} {
        set parent(channelX) ""
    }

    foreach name [array names state] {
        unset state($name)
    }
    unset $channelT
}


#
# property management
#


proc beepcore::peer::getprop {token {property ""}} {
    variable $token
    upvar 0 $token state

    set peerP [tokenP $token either]

    array set options $state(options)

    switch -- $property/$peerP {
        /1 {
            array set properties \
                  [list channels      {}                       \
                        startCallback $options(-startCallback) \
                        eventCallback $options(-eventCallback) \
                        updateSeq     $options(-updateSeq)]
            foreach channelT $state(channelL) {
                variable $channelT
                upvar 0 $channelT child

                if {[string compare $child(profile) ""]} {
                    lappend properties(channels) $channelT
                }
            }
            if {[string compare $state(profiles) ""]} {
                set properties(features) $state(features)
                set properties(localize) $state(localize)
                set properties(profiles) [lrange $state(profiles) 1 end]
            }
            foreach prop [list rcv.stamp event] {
                if {[string compare $state($prop) ""]} {
                    set properties($prop) $state($prop)
                }
            }

            return [array get properties]
        }

        -names/1 {
            set names [list channels startCallback eventCallback updateSeq]
            if {[string compare $state(profiles) ""]} {
                lappend names features localize profiles
            }
            foreach prop [list rcv.stamp event] {
                if {[string compare $state($prop) ""]} {
                    lappend names $prop
                }
            }

            return $names
        }

        channels/1 {
            set channels {}
            foreach channelT $state(channelL) {
                variable $channelT
                upvar 0 $channelT child

                if {[string compare $child(profile) ""]} {
                    lappend channels $channelT
                }
            }

            return $channels
        }

        updateSeq/1
            -
        startCallback/1
            -
        eventCallback/1 {
            return $options(-$property)
        }

        features/1
            -
        localize/1 {
            if {[string compare $state(profiles) ""]} {
                return $state($property)
            }
        }

        profiles/1 {
            if {[string compare $state(profiles) ""]} {
                return [lrange $state(profiles) 1 end]
            }
        }

        rcv.stamp/1
            -
        event/1 {
            if {[string compare $state($property) ""]} {
                return $state($property)
            }
        }

        /0 {
            array set properties \
                  [list peer            $state(peerT)   \
                        profile         $state(profile) \
                        datum           $state(datum)   \
                        snd.wnd         $state(snd.wnd) \
                        rcv.wnd         $state(rcv.wnd) \
                        rcv.buf         $state(rcv.buf) \
                        releaseCallback $options(-releaseCallback)]
            if {[string compare $state(rcv.stamp) ""]} {
                set properties(rcv.stamp) $state(rcv.stamp)
            }
            if {![string compare $options(-segmentCallback) ""]} {
                set properties(messageCallback) $options(-messageCallback)
            } else {
                set properties(segmentCallback) $options(-segmentCallback)
            }

            variable [set peerT $state(peerT)]
            upvar 0 $peerT parent

            array set msgNos $state(msgNos)

            set properties(messages) {}
            foreach {k v} [array get msgNos] {
                if {([set x [string first ,local $k]] > 0) \
                        && ($state(channelNumber) == $v)} {
                    lappend properties(messages)  \
                            [string range $k 0 [expr $x-1]]
                }
            }

            return [array get properties]
        }

        -names/0 {
            set names [list peer     \
                            profile  \
                            datum    \
                            messages \
                            snd.wnd  \
                            rcv.wnd  \
                            rcv.buf  \
                            releaseCallback]
            if {[string compare $state(rcv.stamp) ""]} {
                lappend names rcv.stamp
            }
            if {![string compare $options(-segmentCallback) ""]} {
                lappend names messageCallback
            } else {
                lappend names segmentCallback
            }

            return $names
        }

        peer/0 {
            return $state(peerT)
        }

        profile/0
            -
        datum/0
            -
        snd.wnd/0
            -
        rcv.wnd/0
            -
        rcv.buf/0 {
            return $state($property)
        }

        requests/0
            -
        messages/0 {
            array set msgNos $state(msgNos)

            set result {}
            foreach {k v} [array get msgNos] {
                if {[set x [string first ,local $k]] > 0} {
                    lappend result [string range $k 0 [expr $x-1]]
                }
            }

            return $result
        }

        rcv.stamp/0 {
            if {[string compare $state(rcv.stamp) ""]} {
                return $state(rcv.stamp)
            }
        }

        messageCallback/0 {
            if {![string compare $options(-segmentCallback) ""]} {
                return $options(-messageCallback)
            }
        }

        segmentCallback/0 {
            if {[string compare $options(-segmentCallback) ""]} {
                return $options(-segmentCallback)
            }
        }

        releaseCallback/0 {
            return $options(-$property)
        }
    }

    if {($peerP) && (![catch { child $token $property } channelT])} {
        variable $channelT
        upvar 0 $channelT child

        if {[string compare $child(profile) ""]} {
            return $channelT
        }
    }

    error "unknown property $property"
}


proc beepcore::peer::setprop {token property value} {
    variable $token
    upvar 0 $token state

    set peerP [tokenP $token either]

    array set options $state(options)

    switch -- $property/$peerP {
        updateSeq/1
            -
        startCallback/1
            -
        eventCallback/1
            -
        releaseCallback/0 {
            set old $options(-$property)
            set options(-$property) $value
            set state(options) [array get options]
            switch -glob -- $property/$old$value {
                updateSeq/00 {
                }

                updateSeq/* {
                    push $token
                }

                default {
                }
            }

            return $old
        }

        rcv.buf/0 {
            if {[catch { incr value 0 }]} {
                error "$value not an integer"
            }
            set old $state(rcv.buf)
            set state(rcv.buf) $value

            upaux $state(peerT)

            return $old
        }

        messageCallback/0 {
            if {![string compare $options(-segmentCallback) ""]} {
                set old $options(-messageCallback)
                set options(-messageCallback) $value
                set state(options) [array get options]

                return $old
            }
        }

        segmentCallback/0 {
            if {[string compare [set old $options(-segmentCallback)] ""]} {
                if {![string compare $value ""]} {
                    error "must specify a value for -segmentCallback"
                }
                set options(-segmentCallback) $value
                set state(options) [array get options]

                return $old
            }
        }
    }

    error "unknown property $property"
}


#
# messages
#


proc beepcore::peer::request {args} {
    eval message $args
}

proc beepcore::peer::response {args} {
    eval reply $args
}

proc beepcore::peer::message {channelT mimeT args} {
    global errorCode errorInfo

    variable $channelT
    upvar 0 $channelT state

    tokenP $channelT channel

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set options $state(options)

    if {[string compare $options(-segmentCallback) ""]} {
        error "channel is configured for per-segment callbacks..."
    }

    array set msgNos $state(msgNos)
    while {1} {
        if {[set msgNo [incr state(msgN)]] <= 0} {
            set msgNo [set state(msgN) 1]
        }
        if {![info exists msgNos($msgNo,local)]} {
            break
        }
    }

    array set argv [list -replyCallback {}]
    array set argv $args
    if {![string compare $argv(-replyCallback) ""]} {
        catch { set argv(-replyCallback) $argv(-responseCallback) }
    }

    set payload "Content-Type: [mime::getproperty $mimeT content]"
    foreach {k v} [mime::getproperty $mimeT params] {
        append payload ";\r\n    $k=\"$v\""
    }
    append payload "\r\n"
    foreach {key values} [mime::getheader $mimeT] {
        if {![string compare $key Content-ID]} {
            continue
        }
        foreach value $values {
            append payload "$key: $value\r\n"
        }
    }
    if {![string compare $payload \
                 "Content-Type: application/octet-stream\r\n"]} {
        set payload ""
    }
    append payload "\r\n" [mime::getbody $mimeT]

    if {![set asyncP [string compare [set rpyV $argv(-replyCallback)] ""]]} {
        set rpyV [list [namespace current]::channelX_reply]
    }

    array set callbacks $state(rpyVs)
    set callbacks($msgNo) [list rpyV $rpyV]
    set state(rpyVs) [array get callbacks]

    sendseg $channelT $msgNo $payload \
        -type         message  \
        -continuation complete \
        -internal     true

    if {![info exists state(logT)]} {
        error "peer token destroyed"
    }

    if {$asyncP} {
        return $msgNo
    }

    set code [catch { wait $peerT -msgNos [list $msgNo] } result]
    set ecode $errorCode
    set einfo $errorInfo

    if {![info exists state(logT)]} {
        error "peer token destroyed"
    }

    array set callbacks $state(rpyVs)
    array set reply $callbacks($msgNo)
    unset callbacks($msgNo)
    set state(rpyVs) [array get callbacks]

    switch -- $code {
        0 {
            switch -- $reply(status) {
                positive { set code 0 }

                negative { set code 7 }

                default {
                    mime::finalize $reply(mimeT)

                    report $peerT internal 520 \
                           "not expecting $reply(status) reply"

                    error "not expecting $reply(status) reply"
                }
            }

            return -code $code $reply(mimeT)
        }

        default {
            if {$code != 7} {
                beepcore::log::entry $state(logT) error peer::wait $result
            } else {
                set code 1

                array set reply $result
                set result $reply(diagnostic)
            }

            if {[info exists reply(mimeT)]} {
                mime::finalize $reply(mimeT)
            }

            return -code $code -errorinfo $einfo -errorcode $ecode $result
        }
    }
}


proc beepcore::peer::reply {channelT msgNo mimeT args} {
    variable $channelT
    upvar 0 $channelT state

    tokenP $channelT channel

    array set options $state(options)

    if {[string compare $options(-segmentCallback) ""]} {
        error "channel is configured for per-segment callbacks..."
    }

    array set argv [list -status positive]
    array set argv $args

    if {[string compare $argv(-status) answer]} {
        set ansNo 0
    } elseif {[catch { set argv(-ansNo) } ansNo]} {
        error "missing -ansNo argument"
    }

    switch -- $argv(-status) {
        positive
            -
        negative
            -
        answer {
            set payload "Content-Type: [mime::getproperty $mimeT content]"
            foreach {k v} [mime::getproperty $mimeT params] {
                append payload ";\r\n    $k=\"$v\""
            }
            append payload "\r\n"
            foreach {key values} [mime::getheader $mimeT] {
                if {![string compare $key Content-ID]} {
                    continue
                }
                foreach value $values {
                    append payload "$key: $value\r\n"
                }
            }
            if {![string compare $payload \
                         "Content-Type: application/octet-stream\r\n"]} {
                set payload ""
            }
            append payload "\r\n" [mime::getbody $mimeT]
        }

        nul {
            if {([string compare $mimeT ""]) && ([mime::getsize $mimeT])} {
                error "mimeT should be empty for -status: $argv(-status)"
            }
            set payload ""
        }

        default {
            error "unknown argument to -status: $argv(-status)"
        }
    }

    set state(busyP) 0

    sendseg $channelT $msgNo $payload \
        -type         $argv(-status) \
        -continuation complete       \
        -ansNo        $ansNo         \
        -internal     true
}


# eval'd when a reply to a synchronous message is received

proc beepcore::peer::channelX_reply {channelT args} {
    variable $channelT
    upvar 0 $channelT state

    array set argv $args
    set msgNo $argv(msgNo)

    array set callbacks $state(rpyVs)
    lappend callbacks($msgNo) status $argv(status) mimeT $argv(mimeT)
    set state(rpyVs) [array get callbacks]
}


#
# segments
#


proc beepcore::peer::sendseg {channelT msgNo payload args} {
    variable $channelT
    upvar 0 $channelT state

    tokenP $channelT channel

    array set argv [list -type         message  \
                         -continuation complete \
                         -ansNo        ""       \
                         -internal     false]
    array set argv $args

    array set options $state(options)

    if {(![smtp::boolean $argv(-internal)]) \
            && (![string compare $options(-segmentCallback) ""])} {
        error "channel is not configured for per-segment callbacks..."
    }

    set tail ""
    switch -- $argv(-type) {
        message {
            set head MSG
        }

        positive {
            set head RPY
        }

        negative {
            set head ERR
        }

        answer {
            if {![string compare $argv(-ansNo) ""]} {
                error "must specify a value for -ansNo"
            }

            set head ANS
            set tail " $argv(-ansNo)"
        }

        nul {
            if {[string length $payload] > 0} {
                error "payload should be empty for -type: $argv(-type)"
            }
            if {[string compare $argv(-continuation) complete]} {
                error \
                "continuation should be complete for -type: $argv(-type)"
            }

            set head NUL
        }

        default {
            error "unknown argument to -type: $argv(-type)"
        }
    }
    if {[set more [lsearch {complete intermediate} $argv(-continuation)]] \
             < 0} {
        error "unknown argument to -continuation: $argv(-continuation)"
    }

    array set msgNos $state(msgNos)
    if {![string compare $argv(-type) message]} {
        if {(![catch { set msgNos($msgNo,local) } result]) && (!$result)} {
            error "message $msgNo already sent, but not yet replied"
        }
        set msgNos($msgNo,local) $more
        set state(msgNos) [array get msgNos]
    }  else {
        if {![info exists msgNos($msgNo,remote)]} {
            error "message $msgNo never received, or already replied"
        }
        if {(!$more) && ([string compare $argv(-type) answer])} {
            unset msgNos($msgNo,remote)
            set state(msgNos) [array get msgNos]
        }
    }
    append head " " $state(channelNumber)

    lappend state(sendQ) [list head    $head  \
                               msgNo   $msgNo \
                               more    $more  \
                               tail    $tail  \
                               payload $payload]

    push $state(peerT)
}


proc beepcore::peer::push {peerT} {
    variable $peerT
    upvar 0 $peerT state

    if {[catch { fileevent $state(inputT) readable "" } result]} {
        log $peerT system $result

        set state(readable) -5
        report $peerT internal 420 $result

        return
    }

    while {1} {
        if {$state(writable)} {
            if {(![send $peerT]) \
                    || (![info exists state(logT)]) \
                    || ($state(readable) < 0)} {
                break
            }

            set state(writable) 0
            if {[catch { fileevent $state(outputT) writable \
                                   [list [namespace current]::writable \
                                         $peerT] } result]} {
                log $peerT system $result

                set state(readable) -5
                report $peerT internal 420 $result
                break
            }
        }

        update

        if {![info exists state(logT)]} {
            return
        }

        if {(!$state(writable)) || ($state(readable) < 0)} {
            break
        }
    }

    if {![info exists state(logT)]} {
        return
    }

    if {[catch { fileevent $state(inputT) readable \
                           [list [namespace current]::readable $peerT] } \
               result]} {
        log $peerT system $result

        set state(readable) -5
        report $peerT internal 420 $result

        return
    }
}


#
# waiting
#


proc beepcore::peer::wait {token args} {
    if {[tokenP $token either]} {
        variable [set peerT $token]
    } else {
        variable [set channelT $token]
        upvar 0 $token child

        set peerT $child(parent)
    }
    upvar 0 $peerT state

    array set argv [list -drain   false \
                         -msgNos  {}    \
                         -timeout -1]
    array set argv $args
    if {![string compare $argv(-msgNos) ""]} {
        catch { set argv(-msgNos) $argv(-serialNumbers) }
    }

    set drainP [smtp::boolean $argv(-drain)]
    set newP 0
    while {[set x [lsearch $argv(-msgNos) new]] >= 0} {
        set newP 1
        set argv(-msgNos) [lreplace $argv(-msgNos) $x $x]
    }
    if {[set timeout $argv(-timeout)] < 0} {
        set foreverP 1
    } else {
        set foreverP 0
        set timeDone [expr $timeout+[clock clicks -milliseconds]]
    }

    while {([llength [set msgNos [waitaux $token $argv(-msgNos)]]] > 0) \
                || (($drainP) && ([send $peerT 1])) \
                || ($newP)} {
        if {$state(readable) < 0} {
            return -code 7 $state(event)
        } elseif {($state(readable)) || ($timeout == 0)} {
            update

            if {![info exists state(logT)]} {
                return 0
            }
        } else {
            if {!$foreverP} {
                set state(afterID) \
                    [after $timeout [list [namespace current]::timeout $peerT]]
            }

            tclLog "begin vwait"
            vwait $peerT
            tclLog "end vwait"

            if {![info exists state(logT)]} {
                return 0
            }

            if {[string compare $state(afterID) ""]} {
                catch { after cancel $state(afterID) }
                set state(afterID) ""
            }
        }

        set didP 0
        switch -- $state(readable) {
            -1 {
                beepcore::log::entry $state(logT) debug2 "<<< timeout"

                set state(readable) 0
                break
            }

            0 {
            }

            1 {
                if {[set code [catch { pull $peerT } result]]} {
                    log $peerT user $result
                }

                if {![info exists state(logT)]} {
                    return 0
                }

                if {$code} {
                    set state(readable) -4
                    return -code 7 [report $peerT internal 550 $result]
                }

                set didP 1
                if {$newP} {
                    set timeout $argv(-timeout)
                    set timeDone \
                        [expr $timeout+[clock clicks -milliseconds]]
                    continue
                }
            }

            default {
                return -code 7 $state(event)
            }
        }

        if {!$foreverP} {
            set timeout [expr $timeDone-[clock clicks -milliseconds]]
            if {$timeout <= 0} {
                if {$didP} {
                    set timeout 0
                } else {
                    set msgNos [waitaux $token $argv(-msgNos)]
                    break
                }
            }
        }
    }

    return [llength $msgNos]
}


proc beepcore::peer::waitaux {token msgL} {
    variable $token
    upvar 0 $token state

    if {![tokenP $token either]} {
        return [waitaux2 $token $msgL]
    }

    set result {}

    foreach channelT $state(channelL) {
        set result [concat $result [waitaux2 $channelT $msgL]]
    }

    return $result
}


proc beepcore::peer::waitaux2 {channelT msgL} {
    variable $channelT
    upvar 0 $channelT state

    set result {}

    array set msgNos $state(msgNos)
    if {[llength $msgL] > 0} {
        foreach msgNo $msgL {
            if {[info exists msgNos($msgNo,local)]} {
                lappend result $msgNo
            }
        }
    } else {
        foreach {k v} [array get msgNos] {
            if {[set x [string first ,local $k]] > 0} {
                lappend result [string range $k 0 [expr $x-1]]
            }
        }
    }

    return $result
}


proc beepcore::peer::readable {peerT} {
    variable $peerT
    upvar 0 $peerT state

    set state(rcv.stamp) [clock clicks -milliseconds]
    array set options $state(options)

    if {[eof $state(inputT)]} {
        set state(readable) -3
        report $peerT internal 521 "premature end-of-file"
    } elseif {[catch { 
        if {$options(-updateSeq)} {
            append state(buffer) [::read $state(inputT)]
        } else {
            while {1} {
                if {[set c [::read $state(inputT) 1]] == {}} {
                    break
                }
                append state(buffer) $c
                if {([string first "END\n" $state(buffer)] >= 0) \
                        || ([string first "END\r\n" $state(buffer)] >= 0)} {
                    break
                }
            }
        }
     } result]} {
        set state(readable) -2
        log $peerT system $result
        report $peerT internal 422 "network error"
    } else {
        set state(readable) 1
    }

    if {([info exists state(logT)]) && ($state(readable) != 1)} {
        if {[catch { fileevent $state(inputT)  readable "" } result]} {
            beepcore::log::entry $state(logT) system $result
        }
        if {[catch { fileevent $state(outputT) writable "" } result]} {
            beepcore::log::entry $state(logT) system $result
        }
    }
}


proc beepcore::peer::writable {peerT} {
    variable $peerT
    upvar 0 $peerT state

    if {![send $peerT]} {
        if {[catch { fileevent $state(outputT) writable "" } result]} {
            beepcore::log::entry $state(logT) system $result

            set state(readable) -5
            report $peerT internal 420 $result
        } else {
            set state(writable) 1
        }
    }
}


proc beepcore::peer::timeout {peerT} {
    variable $peerT
    upvar 0 $peerT state

    catch {
        set state(readable) -1
        set state(afterID) ""
    }
}


proc beepcore::peer::pull {peerT} {
    variable $peerT
    upvar 0 $peerT state

    array set options $state(options)
    while {[recv $peerT]} {
        if {![info exists state(logT)]} {
            return
        }

        foreach channelT $state(channelL) {
            upvar 0 $channelT child

            if {[info exists child(peerT)]} {
                pullaux $channelT
            }

            if {![info exists state(logT)]} {
                return
            }
        }
        if {!$options(-updateSeq)} {
            return
        }
    }

    if {![info exists state(logT)]} {
        return
    }

    if {$state(readable) == 1} {
        set state(readable) 0
    }
}


proc beepcore::peer::pullaux {channelT} {
    variable $channelT
    upvar 0 $channelT state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    array set options $state(options)

    if {[string compare $options(-segmentCallback) ""]} {
# it's up to the caller to enforce the "one message at a time" rule...

        foreach result $state(recvQ) {
            set state(recvQ) [lreplace $state(recvQ) 0 0]

            array set frame $result
            lappend result serialNumber $frame(msgNo)

            if {[catch { eval $options(-segmentCallback) \
                              [list $channelT] $result } result]} {
                log $peerT user $result
            }

            if {![info exists parent(logT)]} {
                return
            }
        }

        return
    }

    while {[llength $state(recvQ)] > 0} {
        array set frame [lindex $state(recvQ) 0]
        set state(recvQ) [lreplace $state(recvQ) 0 0]
        if {[string compare $frame(continuation) complete]} {
            set frames {}

            foreach result $state(recvQ) {
                if {![string compare $frame(continuation) complete]} {
                    lappend frames $result
                    continue
                }

                array set next $result
                if {(![string compare $frame(type) $next(type)]) \
                        && (![string compare $frame(msgNo) $next(msgNo)]) \
                        && (![string compare $frame(ansNo) $next(ansNo)])} {
                    append frame(payload) $next(payload)
                    set frame(continuation) $next(continuation)
                } else {
                    lappend frames $result
                }
            }

            set state(recvQ) $frames
            if {[string compare $frame(continuation) complete]} {
                set state(recvQ) [linsert $state(recvQ) 0 [array get frame]]
                return
            }
        }

        if {[string compare $frame(type) message]} {
            set msgNo $frame(msgNo)

            array set callbacks $state(rpyVs)
            array set reply $callbacks($msgNo)
            if {[string compare $frame(type) answer]} {
                unset callbacks($msgNo)
                set state(rpyVs) [array get callbacks]
            }

            set mimeT [payload2mime $frame(payload)]

            if {[catch { eval $reply(rpyV) \
                              [list $channelT \
                                     msgNo        $frame(msgNo) \
                                     serialNumber $frame(msgNo) \
                                     ansNo        $frame(ansNo) \
                                     status       $frame(type)  \
                                     mimeT        $mimeT] } result]} {
                log $peerT user $result
            }
        } elseif {![string compare $options(-messageCallback) ""]} {
            set mimeT [errfmt $state(peerT) 550 "not accepting messages" en-US]

            if {[catch { reply $channelT $frame(msgNo) $mimeT \
                               -status negative } result]} {
                log $peerT error peer::reply $result
            }

            mime::finalize $mimeT
        } else {
            if {$state(busyP)} {
                log $peerT debug "busy processing message"
                set state(recvQ) [linsert $state(recvQ) 0 [array get frame]]
                return
            }
            set mimeT [payload2mime $frame(payload)]

            set state(busyP) 1
            if {[catch { eval $options(-messageCallback) \
                              [list $channelT \
                                    msgNo        $frame(msgNo) \
                                    serialNumber $frame(msgNo) \
                                    mimeT        $mimeT] } result]} {
                log $peerT user $result
            }
        }

        if {![info exists parent(logT)]} {
            return
        }
    }
}


#
# miscellany
#


proc beepcore::peer::str2xml {string} {
    return [mime::initialize -canonical application/beep+xml -string $string]
}


proc beepcore::peer::errfmt {peerT code {diagnostic ""} {language ""}} {
    return [str2xml [errfmt2 $peerT $code $diagnostic $language]]
}


proc beepcore::peer::errfmt2 {peerT code {diagnostic ""} {language ""}} {
    return [xmlfmt $peerT error $code $diagnostic $language]
}


proc beepcore::peer::errfmt3 {peerT replyA} {
    array set reply [list code 500 diagnostic "" language en-US]
    array set reply $replyA

    return [errfmt $peerT $reply(code) $reply(diagnostic) $reply(language)]
}


proc beepcore::peer::errfmt4 {peerT replyA} {
    array set reply [list code 500 diagnostic "" language en-US]
    array set reply $replyA

    return [errfmt2 $peerT $reply(code) $reply(diagnostic) $reply(language)]
}


proc beepcore::peer::xmlfmt {peerT tag code {diagnostic ""} {language ""}
                             {hack ""}} {
    variable $peerT
    upvar 0 $peerT state

    tokenP $peerT peer

    if {![string compare $language ""]} {
        array set options $state(options)
        set language [lindex $options(-localize) 0]
    }

    set xmlmsg "<$tag code=[beepcore::util::xml_av $code]$hack"

    if {[string compare $diagnostic ""]} {
        if {[string compare [string tolower [lindex $state(localize) 0]] \
                    [string tolower $language]]} {
            append xmlmsg " xml:lang=[beepcore::util::xml_av $language]"
        }

        append xmlmsg ">[beepcore::util::xml_cdata $diagnostic]</$tag>"
    } else {
        append xmlmsg " />"
    }

    return $xmlmsg
}


proc beepcore::peer::errscan {peerT mimeT args} {
    variable $peerT
    upvar 0 $peerT state

    tokenP $peerT peer

    array set argv [list -finalize true \
                         -tag      error]
    array set argv $args

    switch -- [catch { parse $peerT $mimeT $argv(-tag) } result] {
        0 {
        }

        default {
            beepcore::log::entry $state(logT) error peer::parse $result

            set result [list code       500     \
                             diagnostic $result \
                             language   en-US]
        }
    }

    if {[smtp::boolean $argv(-finalize)]} {
        mime::finalize $mimeT
    }

    return $result
}


proc beepcore::peer::errscan2 {peerT string} {
    return [errscan $peerT [str2xml $string] -finalize true]
}


#
# framing
#


proc beepcore::peer::send {peerT {testP 0}} {
    variable $peerT
    upvar 0 $peerT state

    if {[sendaux1 $peerT $testP]} {
        return 1
    }

    if {[set x [lsearch $state(channelL) $state(channelX)]] >=  0} {
        set children [concat [lrange $state(channelL) [expr $x+1] end] \
                             [lrange $state(channelL) 0           $x]]
    } else {
        set children $state(channelL)
    }

    set didP 0
    foreach channelX $children {
        if {[set didP [sendaux2 $channelX $testP]]} {
            break
        }
    }

    if {($didP) && ([info exists state(logT)])} {
        set state(channelX) $channelX
    }

    return $didP
}


proc beepcore::peer::sendaux1 {peerT testP} {
    global debugP

    variable $peerT
    upvar 0 $peerT state

    array set options $state(options)
    if {![string compare [set channelT [lindex $state(slideL) 0]] ""]} {
        return 0
    } elseif {!$options(-updateSeq)} {
        return 0
    } elseif {$testP} {
        return 1
    }

    set state(slideL) [lreplace $state(slideL) 0 0]

    variable $channelT
    upvar 0 $channelT child

    if {[catch {
        puts -nonewline $state(outputT) \
             "SEQ $child(channelNumber) $child(rcv.nxt) $child(rcv.wnd)\r\n"
        if {$debugP > 1} {
            beepcore::log::entry $state(logT) debug \
               ">>> SEQ $child(channelNumber) $child(rcv.nxt) $child(rcv.wnd)"
        }
        flush $state(outputT)
    } result]} {
        set state(readable) -2
        report $peerT internal 422 "network error"
    }
    return 1
}

proc beepcore::peer::sendaux2 {channelT testP} {
    global debugP

    variable $channelT
    upvar 0 $channelT state

    variable [set peerT $state(peerT)]
    upvar 0 $peerT parent

    if {[llength $state(sendQ)] <= 0} {
        return 0
    } elseif {$testP} {
        return 1
    }
    array set frame [lindex $state(sendQ) 0]

    set size [string length $frame(payload)]
    set x $state(snd.una)
    incr x $state(snd.wnd)
    if {[set next $state(snd.nxt)] > $x} {
        incr next -4294967295
    }
    incr x -$next
    if {$debugP > 1} {
        beepcore::log::entry $state(logT) debug SND $state(channelNumber) \
           una=$state(snd.una) wnd=$state(snd.wnd) \
           nxt=$state(snd.nxt) avail=$x want=$size
    }

    if {$x == 0} {
        return 0
    }

    if {$size <= $x} {
        set x $size
        set cont .
    } else {
        set cont *
    }
    if {$frame(more)} {
        set cont *
    }

    set header \
        "$frame(head) $frame(msgNo) $cont $state(snd.nxt) $x$frame(tail)"

    if {[catch {
        set block "$header\r\n"
        if {$debugP > 1} {
            beepcore::log::entry $state(logT) debug ">>> $header"
        }

        append block [string range $frame(payload) 0 [expr $x-1]]
        if {$debugP > 2} {
            foreach line [split [string range $frame(payload) 0 \
                                        [expr $x-1]] "\n"] {
                beepcore::log::entry $state(logT) debug \
                    ">>> [string trimright $line]"
            }
        } elseif {$debugP > 1} {
            beepcore::log::entry $state(logT) debug ">>> write $x octets"
        }

        append block "END\r\n"
        if {$debugP > 1} {
            beepcore::log::entry $state(logT) debug ">>> END"
        }

        puts -nonewline $parent(outputT) $block
        flush $parent(outputT)
    } result]} {
        set parent(readable) -2
        report $peerT internal 422 "network error"
    } else {
        incr state(snd.nxt) $x

        if {[incr size -$x] > 0} {
            set frame(payload) [string range $frame(payload) $x end]

            set state(sendQ) [lreplace $state(sendQ) 0 0 [array get frame]]
        } else {
            set state(sendQ) [lreplace $state(sendQ) 0 0]
        }
    }

    return 1
}


proc beepcore::peer::recv {peerT} {
    global debugP

    variable peer

    variable $peerT
    upvar 0 $peerT state

    array set frame $state(incoming)

    while {1} {
        switch -- $frame(waitingFor) {
            header
                -
            trailer {
                if {[set x [string first "\n" $state(buffer)]] < 0} {
                    set state(incoming) [array get frame]
                    return 0
                }

                set line [string trimright \
                                 [string range $state(buffer) 0 [expr $x-1]]]
                set state(buffer) [string range $state(buffer) [expr $x+1] \
                                          end]

                if {$debugP > 1} {
                    beepcore::log::entry $state(logT) debug "<<< $line"
                }
            }

            payload {
                if {[set x [string length $state(buffer)]] == 0} {
                    set state(incoming) [array get frame]
                    return 0
                }

                if {$frame(size) < $x} {
                    set x $frame(size)
                }

                if {$debugP > 2} {
                    foreach line [split [string range $state(buffer) 0 \
                                                [expr $x-1]] "\n"] {
                        beepcore::log::entry $state(logT) debug \
                           "<<< [string trimright $line]"
                    }
                } elseif {$debugP > 1} {
                    beepcore::log::entry $state(logT) debug \
                        "<<< read $x octets"
                }

                append frame(payload) [string range $state(buffer) 0 \
                                              [expr $x-1]]
                set state(buffer) [string range $state(buffer) $x end]
            }
        }

        switch -- $frame(waitingFor) {
            header {
                if {[scan [set line [string trimright $line]] "%s" keyword] \
                        != 1} {
                    set keyword ""
                }
                switch -- $keyword {
                    SEQ {
                        if {([scan $line "SEQ %d %d %d" channelNumber ackno \
                                   window] != 3) \
                                || ($channelNumber < 0) \
                                || ($ackno < 0) \
                                || ($window < 0) \
                                || ($window > 2147483647)} {
                            error "unacceptable parameters: $line"
                        }

                        variable [set channelT [child $peerT $channelNumber]]
                        upvar 0 $channelT child

                        set child(snd.una) $ackno
                        set child(snd.wnd) $window
                        if {$debugP > 1} {
                            beepcore::log::entry $state(logT) debug SND \
                                $channelNumber \
                                una=$ackno wnd=$window nxt=$child(snd.nxt)
                        }

                        set state(incoming) $peer(empty)

                        push $peerT
                        if {![info exists state(logT)]} {
                            return 1
                        }

                        return [recv $peerT]
                    }

                    MSG {
                        if {([scan $line "MSG %d %d %s %d %d" \
                                   frame(channelNumber) frame(msgNo) more \
                                   seqno frame(size)] != 5) \
                                || ($frame(channelNumber) < 0) \
                                || ($frame(channelNumber) > 2147483647) \
                                || ([set msgNo $frame(msgNo)] < 0) \
                                || ($seqno < 0) \
                                || ($frame(size) < 0) \
                                || ($frame(size) > 2147483647)} {
                            error "unacceptable parameters: $line"
                        }
                        set frame(type) message

                        variable [set channelT [child $peerT \
                                                      $frame(channelNumber)]]
                        upvar 0 $channelT child

                        array set msgNos $child(msgNos)
                        if {(![catch { set msgNos($msgNo,remote) } result]) \
                                && (!$result)} {
                            error \
                            "message $msgNo already received, but not yet replied"
                        }
                        set msgNos($msgNo,remote) [string compare $more .]
                        set child(msgNos) [array get msgNos]
                    }

                    RPY
                        -
                    ERR {
                        if {([scan $line "%s %d %d %s %d %d" \
                                   reply frame(channelNumber) frame(msgNo) \
                                   more seqno frame(size)] != 6) \
                                || ($frame(channelNumber) < 0) \
                                || ($frame(channelNumber) > 2147483647) \
                                || ([set msgNo $frame(msgNo)] < 0) \
                                || ($seqno < 0) \
                                || ($frame(size) < 0) \
                                || ($frame(size) > 2147483647)} {
                            error "unacceptable parameters: $line"
                        }
                        if {![string compare $reply RPY]} {
                            set frame(type) positive
                        } else {
                            set frame(type) negative
                        }

                        variable [set channelT [child $peerT \
                                                      $frame(channelNumber)]]
                        upvar 0 $channelT child

                        array set msgNos $child(msgNos)
                        if {![info exists msgNos($msgNo,local)]} {
                            error "MSG $msgNo never sent"
                        }
                        if {([set earlierP \
                                  [info exists msgNos($msgNo,reply)]]) \
                                && ([string compare $msgNos($msgNo,reply) \
                                            $reply])} {
                            error "reply mismatch: $line"
                        }
                        if {[string compare $more .]} {
                            set msgNos($msgNo,reply) $reply
                        } elseif {$earlierP} {
                            unset msgNos($msgNo,reply)
                        }
                        set child(msgNos) [array get msgNos]
                    }

                    ANS {
                        if {([scan $line "ANS %d %d %s %d %d %d" \
                                   frame(channelNumber) frame(msgNo) \
                                   more seqno frame(size) frame(ansNo)] != 6) \
                                || ($frame(channelNumber) < 0) \
                                || ($frame(channelNumber) > 2147483647) \
                                || ([set msgNo $frame(msgNo)] < 0) \
                                || ($seqno < 0) \
                                || ($frame(size) < 0) \
                                || ($frame(size) > 2147483647) \
                                || ($frame(ansNo) < 0) \
                                || ($frame(ansNo) > 2147483647)} {
                            error "unacceptable parameters: $line"
                        }
                        set frame(type) answer

                        variable [set channelT [child $peerT \
                                                      $frame(channelNumber)]]
                        upvar 0 $channelT child

                        array set msgNos $child(msgNos)
                        if {![info exists msgNos($msgNo,local)]} {
                            error "MSG $msgNo never sent"
                        }
                        if {([set earlierP \
                                  [info exists msgNos($msgNo,reply)]]) \
                                && ([string compare $msgNos($msgNo,reply) \
                                            answer])} {
                            error "reply mismatch: $line"
                        }
                        set msgNos($msgNo,reply) answer
                        set child(msgNos) [array get msgNos]
                    }

                    NUL {
                        if {([scan $line "NUL %d %d %s %d %d" \
                                   frame(channelNumber) frame(msgNo) more \
                                   seqno frame(size)] != 5) \
                                || ($frame(channelNumber) < 0) \
                                || ($frame(channelNumber) > 2147483647) \
                                || ([set msgNo $frame(msgNo)] < 0) \
                                || ([string compare $more .]) \
                                || ($seqno < 0) \
                                || ($frame(size) != 0)} {
                            error "unacceptable parameters: $line"
                        }
                        set frame(type) nul

                        variable [set channelT [child $peerT \
                                                      $frame(channelNumber)]]
                        upvar 0 $channelT child

                        array set msgNos $child(msgNos)
                        if {![info exists msgNos($msgNo,local)]} {
                            error "MSG $msgNo never sent"
                        }
                        if {[info exists msgNos($msgNo,reply)]} {
                            if {[string compare $msgNos($msgNo,reply) \
                                        answer]} {
                                error "reply mismatch: $line"
                            }
                            unset msgNos($msgNo,reply)
                        }
                        set child(msgNos) [array get msgNos]
                    }

                    default {
                        error "unacceptable keyword: $line"
                    }
                }
                unset msgNos

                switch -- $more {
                    . { set frame(continuation) complete }

                    * { set frame(continuation) intermediate }

                    default {
                        error "unknown continuation indicator: $line"
                    }
                }

                if {[string compare $child(rcv.nxt) $seqno]} {
                    error "expecting seqno=$child(rcv.nxt), got $seqno"
                }
                incr child(rcv.nxt) $frame(size)
                if {$debugP > 1} {
                    beepcore::log::entry $state(logT) debug RCV \
                        $frame(channelNumber) \
                        nxt=$child(rcv.nxt) win=$child(rcv.wnd)
                }

                unset channelT

                if {$frame(size) > 0} {
                    set frame(waitingFor) payload
                } else {
                    append frame(payload) ""
                    set frame(waitingFor) trailer
                }
            }

            payload {
                if {[incr frame(size) -$x] == 0} {
                    set frame(waitingFor) trailer
                }
            }

            trailer {
                if {[string compare $line END]} {
                    error "expecting trailer, not $line"
                }

                variable [set channelT [child $peerT $frame(channelNumber)]]
                upvar 0 $channelT child

                unset frame(waitingFor)    \
                      frame(channelNumber) \
                      frame(size)
                lappend child(recvQ) [array get frame]
                set child(rcv.stamp) [clock clicks -milliseconds]

                if {[lsearch $state(slideL) $channelT] < 0} {
                    lappend state(slideL) $channelT
                    push $peerT

                    if {![info exists state(logT)]} {
                        return 1
                    }
                }

                if {![string compare $frame(continuation) complete]} {
                    switch -- $frame(type) {
                        positive
                            -
                        negative
                            -
                        nul {
                            set msgNo $frame(msgNo)
                            array set msgNos $child(msgNos)
                            unset msgNos($msgNo,local)
                            set child(msgNos) [array get msgNos]
                        }
                    }
                }

                set state(incoming) $peer(empty)
                return 1
            }
        }
    }
}


#
# parsing
#


# 0: [array get reply]
# *: $result

proc beepcore::peer::parse {peerT mimeT top} {
    global errorCode errorInfo

    variable $peerT
    upvar 0 $peerT state

    variable parser

    $parser configure                                                         \
            -elementstartcommand  "[namespace current]::element $peerT start" \
            -elementendcommand    "[namespace current]::element $peerT end"   \
            -characterdatacommand "[namespace current]::cdata   $peerT"       \
            -final                yes

    set state(stack)      {}
    set state(top)        $top
    set state(code)       500
    set state(lang)       {}
    set state(data)       ""
    set state(ftrs)       {}
    set state(locs)       {}
    set state(uriL)       {}
    set state(dataL)      {}
    set state(number)     0
    set state(serverName) ""

    if {[string compare [set content [mime::getproperty $mimeT content]] \
                application/beep+xml]} {
        error "expecting application/beep+xml, not $content"
    }

    set code [catch {
        $parser reset
        $parser parse [set data [beepcore::util::xml_norm \
                                     [mime::getbody $mimeT]]]
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            switch -- $state(top) {
                error {
                    set result [list code       $state(code) \
                                     language   $state(lang) \
                                     diagnostic $state(data)]
                }

                greeting {
                    set result [list features $state(ftrs) \
                                     localize $state(locs) \
                                     profiles $state(uriL)]
                }

                profile {
                    set result [list uri  [lindex $state(uriL) 0] \
                                     data [beepcore::util::xml_pcdata \
                                               $state(data)]]
                }

                start {
                    set result [list top        $state(top)                 \
                                     number     $state(number)              \
                                     profiles   $state(uriL)                \
                                     data       [beepcore::util::xml_pcdata \
                                                     $state(dataL)]         \
                                     serverName $state(serverName)]
                }

                close {
                    set result [list top        $state(top)    \
                                     number     $state(number) \
                                     code       $state(code)   \
                                     language   $state(lang)   \
                                     diagnostic $state(data)]
                }

                ok {
                    set result {}
                }
            }
        }

        default {
            append result [beepcore::util::xml_trace $state(logT) peer \
                               $result $data $state(stack)]
        }
    }

    unset state(stack)  \
          state(top)    \
          state(code)   \
          state(lang)   \
          state(data)   \
          state(ftrs)   \
          state(locs)   \
          state(uriL)   \
          state(dataL)  \
          state(number) \
          state(serverName)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}


proc beepcore::peer::element {token tag name {av {}}} {
    variable $token
    upvar 0 $token state

    switch -- $tag {
        start {
            switch -glob -- [llength $state(stack)]/$state(top) {
                0/loop {
                    switch -- $name {
                        start
                            -
                        close {
                            set state(top) $name
                            begin_$name $token $av
                        }

                        default {
                            set state(code) 501
                            oops "not expecting <$name> element"
                        }
                    }
                }

                0/* {
                    if {[string compare $state(top) $name]} {
                        set state(code) 501
                        oops "not expecting <$name> element"
                    }

                    begin_$name $token $av
                }

                1/greeting
                    -
                1/start {
                    if {[string compare $name profile]} {
                        set state(code) 501
                        oops "not expecting <$name> element"
                    }

                    begin_$name $token $av
                }

                default {
                    set state(code) 501
                    oops "not expecting <$name> element"
                }
            }

            lappend state(stack) $name
        }

        end {
            set state(stack) [lreplace $state(stack) end end]

            switch -glob -- [llength $state(stack)]/$state(top) {
                0/* {
                }

                1/greeting {
                }

                1/start {
                    lappend state(dataL) $state(data)
                    set state(data) ""
                }
            }
        }
    }
}


proc beepcore::peer::begin_error {token av} {
    variable $token
    upvar 0 $token state

    array set options $state(options)

    array set attrs [list xml:lang [lindex $options(-localize) 0]]
    array set attrs $av

    if {[catch { set attrs(code) } state(code)]} {
        oops "code attribute missing in <error> element"
    }
    if {[catch { incr state(code) 0 }]} {
        oops "code attribute poorly formed in <error> element"
    }
    if {($state(code) < 100) || ($state(code) > 599)} {
        oops "code attribute in <error> element must be three-digit reply code"
    }

    set state(lang) $attrs(xml:lang)
}


proc beepcore::peer::begin_greeting {token av} {
    variable $token
    upvar 0 $token state

    array set attrs [list features {} localize {i-default}]
    array set attrs $av

    if {[catch { split [set state(ftrs) $attrs(features)] }]} {
        oops "features attribute poorly formed in <greeting> element"
    }
    if {[catch { split [set state(locs) $attrs(localize)] }]} {
        oops "localize attribute poorly formed in <greeting> element"
    }
}


proc beepcore::peer::begin_profile {token av} {
    variable $token
    upvar 0 $token state

    array set attrs $av
    if {[catch { lappend state(uriL) $attrs(uri) }]} {
        oops "uri attribute missing in <profile> element"
    }

    set state(data) ""
}


proc beepcore::peer::begin_start {token av} {
    variable $token
    upvar 0 $token state

    array set attrs [list serverName ""]
    array set attrs $av

    set state(serverName) $attrs(serverName)
    if {[catch { set attrs(number) } state(number)]} {
        oops "number attribute missing in <start> element"
    }
    if {[catch { incr state(number) 0 }]} {
        oops "number attribute poorly formed in <start> element"
    }
    array set options $state(options)
    if {($state(number) <= 0) || ($state(number) > 2147483647)} {
        oops "number attribute must be 1..2147483647 in <start> element"
    }
    if {($state(number) % 2) != (!$options(-initiator))} {
        if {$options(-initiator)} {
            set parity even
        } else {
            set parity odd
        }
        oops "number attribute must be $parity in <start> element"
    }
}


proc beepcore::peer::begin_close {token av} {
    variable $token
    upvar 0 $token state

    array set options $state(options)

    array set attrs [list number   0 \
                          xml:lang [lindex $options(-localize) 0]]
    array set attrs $av

    if {[catch { expr $attrs(number)+0 } state(number)]} {
        oops "number attribute poorly formed in <close> element"
    }
    if {($state(number) < 0) || ($state(number) > 2147483647)} {
        oops "number attribute must be 0..2147483647 in <close> element"
    }
    if {[catch { set attrs(code) } state(code)]} {
        oops "code attribute missing in <close> element"
    }
    if {[catch { incr state(code) 0 }]} {
        oops "code attribute poorly formed in <close> element"
    }
    if {($state(code) < 100) || ($state(code) > 599)} {
        oops "code attribute in <close> element must be three-digit reply code"
    }

    set state(lang) $attrs(xml:lang)
}


proc beepcore::peer::begin_ok {token av} {}

proc beepcore::peer::cdata {token text} {
    variable $token
    upvar 0 $token state

    switch -- $state(top) {
        greeting { set len 0 }
        error    { set len 1 }
        profile  { set len 1 }
        start    { set len 2 }
        close    { set len 1 }
        ok       { set len 0 }
    }
    if {[llength $state(stack)] != $len} {
        if {![string compare [string trim $text] ""]} {
            return
        }
        set state(code) 501
        oops "unexpected character data"
    }

    if {[string compare $state(top) error]} {
        set text [beepcore::util::xml_cdata $text]
    }
    append state(data) $text
}


proc beepcore::peer::oops {args} {
    return -code error [::join $args " "]
}


#
# miscellany
#


proc beepcore::peer::tokenP {token what} {
    variable $token
    upvar 0 $token state

    switch -glob -- \
    $what/[set x [info exists state(inputT)]]/[info exists state(peerT)] {
        peer/1/0
            -
        channel/0/1 {
        }

        peer/*/*
            -
        channel/*/* {
            error "not a $what"
        }

        either/1/0
            -
        either/0/1 {
            return $x
        }

        default {
            error "neither a peer nor a channel"
        }
    }
}


proc beepcore::peer::child {peerT channelNumber} {
    variable $peerT
    upvar 0 $peerT parent

    variable [set channelT ${peerT}_$channelNumber]
    upvar 0 $channelT state

    if {([info exists state(channelNumber)]) \
            && ($state(channelNumber) == $channelNumber)} {
        return $channelT
    }

    error "channel $channelNumber doesn't exist"
}


proc beepcore::peer::payload2mime {payload} {
    switch -- [string range $payload 0 0] {
        "\r" - "\n" {
            set prefix \
                "Content-Type: application/octet-stream\r\nContent-Transfer-Encoding: binary\r\n"
        }

        default {
            set prefix ""
        }
    }

    if {[catch { mime::initialize -string "$prefix$payload" } mimeT]} {
        set mimeT [mime::initialize -canonical application/octet-stream \
                       -string "$prefix$payload"]
    }

    return $mimeT
}


proc beepcore::peer::report {peerT source code {diagnostic ""} 
                             {language en-US}} {
    variable $peerT
    upvar 0 $peerT state

    if {![info exists state(logT)]} {
        return
    }

    beepcore::log::entry $state(logT) info report $source $code $diagnostic \
        $language

    if {![string compare $state(event) ""]} {
        set state(event) [list source     $source     \
                               code       $code       \
                               diagnostic $diagnostic \
                               language   $language]

        array set options $state(options)
        if {[string compare $options(-eventCallback) ""]} {
            if {[catch { eval $options(-eventCallback)  [list $peerT] \
                              $state(event) } result]} {
                log $peerT user $result
            }
        }
    }

    return [list code $code diagnostic $diagnostic language $language]
}


proc beepcore::peer::log {peerT level args} {
    variable $peerT
    upvar 0 $peerT state

    if {[info exists state(logT)]} {
        eval [list beepcore::log::entry $state(logT) $level] $args
    }
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
