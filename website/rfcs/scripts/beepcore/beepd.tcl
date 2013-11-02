#!/bin/sh
# the following restarts using tclsh \
exec /usr/pkg/bin/tclsh8.3 "$0" "$@"


#
# beepd.tcl - prototype BEEP server
#


if {[catch {


if {($argc < 3) || ($argc > 4)} {
    error "expecting argc=3 (homeD serverD loggingF)\nnot expecting $argc ($argv)"
}

cd [set homeD [lindex $argv 0]]
set serverD [lindex $argv 1]

global options
array set options {
    -port 10288
    -ip ""
    -mailName nobody@localhost
    -debug 0
    }
set options(-ip) $serverD
global mailName 
set mailName $options(-mailName)

global debugP

if {![info exists debugP]} {
    set debugP $options(-debug)
}

global auto_path

if {[lsearch -exact $auto_path $homeD/scripts] < 0} {
    lappend auto_path $homeD/scripts
}


package require beepcore::server
package require beepcore::log
package require beepcore::util

# for fstat
package require Tclx


# clean-up and exit

proc adios {status level args} {
    global debugP logT

    if {[string compare $level ""]} {
        eval beepcore::log::entry $logT $level $args
    }

    beepcore::log::entry $logT info end $status
    beepcore::log::fin $logT

    exit $status
}


# and... we're off!

global logT

set logT [beepcore::log::init [lindex $argv 2] beepd $mailName]


if {$argc > 3} {
    set stdout [set stdin [lindex $argv 3]]
} else {
    set stdin stdin
    set stdout stdout
    # set debugP 1
    # Actually, using stdin and stdout this way breaks TLS,
    # which expects a single bidirectional channel.
    # So we dup the channel with TclX, which gives us
    # a bidirectional channel for TLS.
    set stdin [dup 0]
    set stdout $stdin
}


if {[file exists shutdown]} {
    fconfigure $stdout -translation binary
    set payload [beepcore::util::xml_reply 421 "$serverD BEEP unavailable"]
    puts -nonewline $stdout \
         "RPY 0 0 . 0 [string length $payload]\r\n${payload}END"
    flush $stdout

    exit 0
}

if {([catch { fconfigure $stdin -peername } clientL]) \
                && ([catch { fstat $stdin remotehost } clientL])} {
    global env

    beepcore::log::entry $logT system $clientL

    if {[info exists env(USER)]} {
        set addr $env(USER)
    } elseif {$debugP} {
        set addr debug
    } else {
        set addr unknown
    }
    set clientL [list $addr "" ""]
} elseif {[string first "remote=" [set client [lindex $clientL 0]]] == 0} {
    set clientL [lreplace $clientL 0 0 [string range $client 8 end]]
}
array set clientA [list address [lindex $clientL 0] \
                        domain  [lindex $clientL 1] \
                        port    [lindex $clientL 2]]

beepcore::log::entry $logT info begin $clientA(address)


source [file join scripts beepd-plaintext.tcl]
if {[file exists [set encryptedF [file join scripts beepd-encrypted.tcl]]]} {
    source $encryptedF
} else {
    set encrypted ""
}

if {[file exists etc/debugP]} {
    set debugP 3
}

beepcore::util::timer_init
if {[file exists etc/clickZ]} {
    beepcore::util::timer_start
}

switch -- [catch { beepcore::server::loop [beepcore::server::init $logT \
                                             $serverD [array get clientA] \
                                             $stdin $stdout $plaintext \
                                             $encrypted] } result] {
    0 {
        beepcore::util::timer_fin $logT
        adios 0 ""
    }

    7 {
        adios 1 user $result
    }

    8 {
        adios 1 user "This shouldn't happen: $result"
    }

    default {
        adios 1 system $result
    }
}


} result]} {
    catch {
        global errorCode errorInfo
        global logT

        beepcore::log::entry $logT fatal $errorCode $errorInfo $result
    }

    catch {
        fconfigure stdout -translation binary
        set payload [beepcore::util::xml_reply 421 \
                         "$serverD BEEP unavailable\r\n\t$result"]
        puts -nonewline stdout \
             "RPY 0 0 . 0 [string length $payload]\r\n${payload}END"
        flush stdout
    }

    exit 0
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
