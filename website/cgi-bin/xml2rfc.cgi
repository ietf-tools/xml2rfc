#!/bin/sh
# the following restarts using tclsh \
PATH=/usr/bin:/bin:/usr/pkg/bin:/usr/local/bin:/sbin:/usr/sbin \
LD_LIBRARY_PATH=/usr/pkg/lib:/usr/lib:/usr/local/lib \
export PATH LD_LIBRARY_PATH; exec tclsh "$0" "$@"


#
# xml2rfc.cgi - convert XML source files to the RFC format
#
# (c) 1999 Invisible Worlds, Inc.
# Not for Distribution or Citation
#


if {![info exists env(DOCUMENT_ROOT)]} {
    set env(DOCUMENT_ROOT) web
}
if {[string match */cgi-bin [set pwd [pwd]]]} {
    cd [file dirname $pwd]
}


package require cgi 1.10
# cgi_debug -on

if {![string compare [cgi_debug] -on]} {
    set debugP 1

    catch { unset _cgi _cgi_uservar _cgi_userfile }
    set _cgi(debug) -on
    set _cgi(tmpdir) [pwd]

    set env(CONTENT_TYPE) \
        "multipart/form-data; boundary=---------------------------7cf021f78"
} else {
    set debugP 0
}

cgi_name xml2rfc
cgi_mail_relay localhost
global env
# set env(SERVER_ADMIN) mrose+dbc.xml2rfc@drakken.dbc.mtview.ca.us
set env(SERVER_ADMIN) webmaster@tools.ietf.org
catch { cgi_admin_mail_addr $env(SERVER_ADMIN) }
catch { cgi_mail_addr $env(SERVER_ADMIN) }


global guiP

set guiP 0

source etc/xml2rfc.tcl


proc mail_error {{inputF ""}} {
    global _cgi env
    global errorInfo

    set _cgi(errorInfo) $errorInfo

    catch {
        cgi_mail_start $_cgi(admin_email)
        cgi_mail_add "Subject: [cgi_name] CGI problem"
        cgi_mail_add
        cgi_mail_add "CGI environment:"
        cgi_mail_add "REQUEST_METHOD: $env(REQUEST_METHOD)"
        cgi_mail_add "SCRIPT_NAME: $env(SCRIPT_NAME)"
        if {[string compare $inputF ""]} {
            cgi_mail_add "INPUT_FILE: $iputF"
        }
        # this next few things probably don't need
        # a catch but I'm not positive
        catch {cgi_mail_add "HTTP_USER_AGENT: $env(HTTP_USER_AGENT)"}
        catch {cgi_mail_add "HTTP_REFERER: $env(HTTP_REFERER)"}
        catch {cgi_mail_add "HTTP_HOST: $env(HTTP_HOST)"}
        catch {cgi_mail_add "REMOTE_HOST: $env(REMOTE_HOST)"}
        catch {cgi_mail_add "REMOTE_ADDR: $env(REMOTE_ADDR)"}
        cgi_mail_add "cgi.tcl version: 1.4.3"
        cgi_mail_add "input:"
        catch {cgi_mail_add $_cgi(input)}
        cgi_mail_add "cookie:"
        catch {cgi_mail_add $env(HTTP_COOKIE)}
        cgi_mail_add "errorInfo:"
        cgi_mail_add "$_cgi(errorInfo)"
        cgi_mail_end
    }
}

proc system_error {reason {info ""}} {
    global env errorInfo

    if {![string compare $info ""]} {
        set info $errorInfo
    }

    cgi_title "Service Problem"

    cgi_h1 "Service Problem"
    cgi_puts "[cgi_bold Reason:] [cgi_quote_html $reason]"
    cgi_br
    cgi_br
    cgi_puts [cgi_bold Stack:]
    cgi_preformatted { cgi_puts [cgi_quote_html $info] }
    cgi_hr
    catch {
        cgi_puts "You may contact the [cgi_url administrator \
                                               href=mailto:$env(SERVER_ADMIN)]."
    }
    catch { cgi_puts $env(SERVER_SIGNATURE) }

    if {!$debugP} {
        cgi_exit
    }
}

proc user_error {event info} {
    global debugP env

    cgi_title "You lose"

    cgi_h1 [cgi_quote_html $event]
    cgi_preformatted { cgi_puts [cgi_quote_html $info] }
    cgi_hr
    catch { cgi_puts $env(SERVER_SIGNATURE) }

    if {!$debugP} {
        cgi_exit
    }
}


#
# invoking form has two fields:
#       radiobutton "mode" - either txt, html, nr, unpg, or xml
#       file "input" - contains the XML file
#

cgi_eval {
    global errorInfo env

    if {$debugP} {
        cgi_input etc/debug.txt
    } elseif {[catch { cgi_input }]} {
        return [user_error "Invocation Error" "error parsing CGI parameters"]
    }

    if {[catch { cgi_import type }]} {
        set type ascii
    }
    switch -- $type {
        ascii {
            set typeP 0
        }

        binary {
            set typeP 1
        }

        default {
            return [user_error "Invocation Error" "unknown type: $type"]
        }
    }

    if {[catch { cgi_import_as mode outmode }]} {
        set outmode txt
    }
    switch -- $outmode {
        nr
            -
        txt
            -
        unpg {
            set htmlP 0
        }

        xml {
            set htmlP 0
            set typeP 1 
        }

        html {
            set htmlP 1
        }

        default {
            return [user_error "Invocation Error" "unknown mode: $outmode"]
        }
    }

    if {[catch { cgi_import input
        set inputF [cgi_import_file -server input]
        set remoteF \
            [file rootname [cgi_import_file -client input]].$outmode
    }]} {
        catch { 
            global _cgi _cgi_uservar

            set fd [open /tmp/xml2rfc.log { WRONLY CREAT APPEND }]
            catch { puts $fd errorInfo=$errorInfo }
            catch { puts $fd cgi_import_list=[cgi_import_list] }
            catch { 
                foreach {k v} [array get _cgi] {
                    if {[string compare $k body]} {
                        puts $fd "_cgi($k)=$v"
                    }
                }
            }
            catch { 
                foreach {k v} [array get _cgi_uservar] {
                    puts $fd "_cgi_uservar($k)=$v"
                }
            }
            close $fd
        }
        return [user_error "Invocation Error" "input file not provided"]
    }
# awful hack for cross-platform stuff...
    if {[set x [string last "\\" $remoteF]] >= 0} {
        set remoteF [string range $remoteF [expr $x+1] end]
    }

    set env(XML_LIBRARY) [file join [pwd] web public rfc bibxml]
    foreach d [glob [file join [pwd] web public rfc bibxml?]] {
        append env(XML_LIBRARY) : $d
    }

    set code [catch { xml2rfc $inputF $inputF.xml } result]
    file delete -- $inputF
    if {$code} {
        catch { file delete -- $inputF.xml }
        mail_error
        return [user_error "Unable to Convert File" $result]
    }
    file rename $inputF.xml $inputF

    set tmpF ""
    set code [catch {
        set xml4j /usr/pkg/java/XML4J-3_2_1
        file copy etc/rfc2629.dtd [set tmpF $_cgi(tmpdir)/rfc2629.dtd]
        exec /usr/pkg/java/bin/jre -cp \
             $xml4j/xerces.jar:$xml4j/xercesSamples.jar sax.SAXCount -v $inputF
    } result]
    if {[string compare $tmpF ""]} {
        file delete -- $tmpF
    }
    if {([string first {[Fatal Error]} $result] < 0) \
            && ([set x [string first {[Error]} $result]] >= 0)} {
        file delete -- $inputF

        set result [string range $result $x end]
        set remoteF [file rootname $remoteF].xml
        catch { regsub -all $inputF $result $remoteF result }
        catch { regsub -all [file tail $inputF] $result $remoteF result }
        return [user_error "Unable to Validate File" $result]
    }

    set outputF $inputF.$outmode
    set code [catch { xml2rfc $inputF $outputF $remoteF } result]
###    file delete -- $inputF
    if {$code} {
        catch { file delete -- $outputF }
        mail_error $inputF
        return [user_error "Unable to Convert File" $result]
    }

    if {[catch { set fd [open $outputF { RDONLY }] } result]} {
        set info $errorInfo

        catch { file delete -- $outputF }
        return [system_error $result $info]
    }
    set body [read $fd]
    catch { close $fd }
    file delete -- $outputF

    if {$typeP} {
        cgi_http_head {
            cgi_content_type "unknown/exe"
#           cgi_content_type "application/octet-stream; name=\"$remoteF\""
            cgi_puts "Content-Disposition: attachment; filename=\"$remoteF\""
        }
    } else {
        cgi_http_head {
            if {$htmlP} {
                cgi_content_type {text/html}
            } else {
                cgi_content_type {text/plain; charset="us-ascii"}
            }
        }
    }
    cgi_puts $body
}
