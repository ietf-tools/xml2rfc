#
# beep-logging.tcl - logging routines
#


package provide beepcore::log   1.0

package require mime
package require smtp


###############################################################################
#
# INVOCATION
#
#    debugN $function  args...
#    error  $function  $result
#    notify $function  $result
#    fatal  $errorCode $errorInfo $result
#    info   begin/end  args...
#    stats  $function  name value...
#    system $result
#    user   $result
#
#
###############################################################################

#
# state variables:
#
#    outputC: file-descriptor to log file
#    file:    file-path to log file
#    ident:   service name
#    originator: address to send critical events from
#    recipient: address to send critical events to
#    head: head-end entries
#    tail: tail-end entries
#


namespace eval ::beepcore::log {
    variable log
    array set log { uid 0 bgerror 0 }

    variable logpid ""

    namespace export init fin entry annotate
}

proc ::beepcore::log::init {file ident {recipient ""} {originator ""}} {
    variable log

    set token [namespace current]::[incr log(uid)]

    variable $token
    upvar 0 $token state

    variable logpid [format %06d [expr [pid]%65535]]

    set ident [string trim $ident]
    array set state [list outputC "" file $file ident [format %-8.8s $ident] \
                          originator $originator recipient $recipient \
                          head {} tail {}]

    return $token
}

proc ::beepcore::log::fin {token} {
    variable $token
    upvar 0 $token state

    if {[string compare $state(outputC) ""]} {
        catch { close $state(outputC) }
    }

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}


proc ::beepcore::log::entry {token level args} {
    global debugP
    global errorCode errorInfo

    variable $token
    upvar 0 $token state

    variable logpid

    set ecode $errorCode
    set einfo $errorInfo

    if {([string match debug* $level]) \
            && ((!$debugP) \
                    || (([scan $level debug%d x] == 1) && ($x > $debugP)))} {
        return
    }

    set now [clock seconds]

    if {(![string compare $state(outputC)  ""]) \
            && ([catch { open $state(file) { WRONLY CREAT APPEND } } \
                       state(outputC)])} {
        return
    }

    regsub -all "\n" $args " " msg
    if {[string length $msg] > 1200} {
        set msg [string range $msg 0 1197]...
    }

    set prefix [clock format $now -format "%m/%d %T"]
    append prefix " $state(ident) $logpid"
    catch {
        puts -nonewline $state(outputC) "$prefix [format %-6.6s $level] $msg\n"
        flush $state(outputC)
    }

    set suffix [join $args " "]
    switch -- $level {
        error
            -
        fatal
            -
        notify
            -
        system {
            regsub -all "\n" $einfo " " msg2
            if {[string length $msg2] > 200} {
                set msg [string range $msg2 0 197]...
            }

            if {[string length $msg2] > 0} {
                catch {
                    puts -nonewline $state(outputC) "$prefix trace  $msg2\n"
                    flush $state(outputC)
                }
            }

            catch { mail $token \
                       "[info hostname] [string trim $state(ident)] $level" \
                              "$prefix $level $suffix" $ecode $einfo }

            if {![string compare $level notify]} {
                syslog $token daemon warning \
                            [string trimright $state(ident)] $msg
            }
        }
    }

    set level [format %-6.6s $level]
    if {[llength $state(head)] < 5} {
        lappend state(head) "$prefix $level $suffix"
    } else {
        if {[llength $state(tail)] >= 5} {
            set state(tail) [lreplace $state(tail) 0 0]
        }
        lappend state(tail) "$prefix $level $suffix"
    }
}

proc ::beepcore::log::annotate {token data} {
    variable $token
    upvar 0 $token state

    if {[llength $state(head)] < 5} {
        lappend state(head) "\n$data\n"
    } else {
        if {[llength $state(tail)] >= 5} {
            set state(tail) [lreplace $state(tail) 0 0]
        }
        lappend state(tail) "\n$data\n"
    }
}

proc ::beepcore::log::mail {token subject text ecode einfo} {
    variable $token
    upvar 0 $token state

    if {![string compare [set from $state(recipient)] ""]} {
        return
    }
    if {[string compare $state(originator) ""]} {
        set from $state(originator)
    }

    set prefix ""
    foreach line $state(head) {
        append prefix $line "\n"
    }
    if {[llength $state(tail)] > 0} {
        append prefix "...\n"
        foreach line $state(tail) {
            append prefix $line "\n"
        }
    }
    set mime [mime::initialize \
                    -canonical text/plain \
                    -param     {charset us-ascii} \
                    -string    "$prefix$text

errorCode: $ecode

$einfo"]

    catch { 
        smtp::sendmessage $mime \
              -originator $state(originator) \
              -header     [list From    $from] \
              -header     [list To      $state(recipient)] \
              -header     [list Subject $subject]
    }

    mime::finalize $mime
}

proc ::beepcore::log::syslog {token facility priority tag message} {
    variable $token
    upvar 0 $token state

    if {[catch { exec logger -i -p $facility.$priority -t $tag \
                     -- $message } result]} {
        entry $token system $result
    }
}

if {[string compare [info commands bgerror] ""]} {
    return
}

proc bgerror {message} {
    if {$::beepcore::log::log(bgerror)} {
        return
    }

    set ::beepcore::log::log(bgerror) 1

    if {$::beepcore::log::log(uid) > 0} {
        catch { ::beepcore::log::entry ::beepcore::log::1 error bgerror \
                    [::info level] $message }
    }

    set ::beepcore::log::log(bgerror) 0
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
