# profile-sudsy.tcl - the SOAP profile
#
#
# listener for SOAP over BEEP
#
# 1. install TclSOAP (http://sourceforge.net/projects/tclsoap)
#
# 2. mkdir /usr/pkg/beepd/soap/
#
#    put soapmap.dat file there
#    put method-scripts/ directory there
#
# 3. reconfigure the server, e.g.,
#
#    cd /usr/pkg/beepd
#    etc/beepd-boot.tcl . no yes
#
# 4. authorize users accordingly:
#
#      scope - soap:$resource
#    actions - invoke
#
# e.g.,
#
#    <elem key="authorization">
#        <elem key="acl">
#            <elem key="soap:urn:soapinterop">
#                <elem key="scope">soap:urn:soapinterop</elem>
#                <elem key="privs">invoke</elem>
#            </elem>
#        </elem>
#    </elem>
#


package provide beepcore::profile::sudsy  1.0

package require beepcore::log
package require beepcore::peer
package require beepcore::sasl

package require mime


#
# state variables:
#
#    logT: token for logging package
#    resource: the resource we're talking to
#    features: the features that are enabled
#


namespace eval beepcore::profile::sudsy {
    variable sudsy
    array set sudsy { uid 0 }

    namespace export info boot init fin exch2
}


proc beepcore::profile::sudsy::info {logT} {
    return [list 0 \
                 [list http://iana.org/beep/soap         \
                       http://clipcode.org/beep/soap]    \
                 [list bootV  [namespace current]::boot  \
                       initV  [namespace current]::init  \
                       exch2V [namespace current]::exch2 \
                       finV   [namespace current]::fin]]
}


proc beepcore::profile::sudsy::boot {logT} {
    global debugP

    foreach pkg [list dom SOAP SOAP::CGI SOAP::Utils] {
        if {[catch { package require $pkg } result]} {
            return -code 7 [list code 451 diagnostic $result]
        }
    }

    set SOAP::CGI::soapdir     soap/method-scripts
    set SOAP::CGI::soapmapfile soap/soapmap.dat
    set SOAP::CGI::logfile     logs/soap.log
    if {$debugP} {
        set SOAP::CGI::debugging 1
    } else {
        set SOAP::CGI::debugging 0
    }
}


proc beepcore::profile::sudsy::init {logT serverD clientA upcallV uri} {
    variable sudsy

    set token [namespace current]::[incr sudsy(uid)]

    variable $token
    upvar 0 $token state

    array set state [list logT $logT resource "" features {}]

    return $token
}


proc beepcore::profile::sudsy::fin {token status} {
    variable $token
    upvar 0 $token state

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}



proc beepcore::profile::sudsy::exch2 {peerT token mimeT} {
    global env

    variable $token
    upvar 0 $token state

    set content [mime::getproperty $mimeT content]
    set data [mime::getbody $mimeT]
    mime::finalize $mimeT

    if {$state(resource) == {}} {
        if {[catch { dom::DOMImplementation parse $data } doc]} {
            return -code 7 [beepcore::peer::errfmt $peerT 500 \
                                "bootmsg is invalid xml: $data"]
        }

        if {[set node [SOAP::Utils::selectNode $doc /bootmsg]] != {}} {
            if {[catch {
                set state(resource) \
                    [set [dom::node cget $node -attributes](resource)]

                if {$state(resource) == {}} {
                    set state(resource) /
                }
            }]} {
                set reason "bootmsg missing resource attribute"
            }

            catch {
                set features \
                    [set [dom::node cget $node -attributes](features)]

                if {$features != {}} {
                    beepcore::log::entry $state(logT) info requested $features
                }
            }
        } else {
            set reason "expecting bootmsg"
        }

        dom::DOMImplementation destroy $doc

        if {$state(resource) == {}} {
            return -code 7 [beepcore::peer::errfmt $peerT 500 $reason]
        }
        switch -- $state(resource) {
            / {
            }

            default {
                if {[string first / $state(resource)] == 0} {
                    set state(resource) \
                        urn:[string range $state(resource) 1 end]
                }
                if {[catch { SOAP::CGI::soap_implementation \
                                 $state(resource) }]} {
                    return -code 7 [beepcore::peer::errfmt $peerT 550 \
                                        "resource unavailable"]
                                                     
                }
            }
        }

        beepcore::log::entry $state(logT) info resource $state(resource)

        if {[catch { beepcore::sasl::allowP $state(logT) \
                         invoke soap:$state(resource) } result]} {     
            return -code 7 [beepcore::peer::errfmt3 $peerT $result]
        }

        set doc [dom::DOMImplementation create]
        set bootrpy [dom::document createElement $doc bootrpy]
        dom::element setAttribute $bootrpy features $state(features)
        set data [dom::DOMImplementation serialize $doc]
        if {[set x [string first [set y "<!DOCTYPE bootrpy>\n"] $data]] \
                >= 0 } {
            set data [string range $data [expr $x+[string length $y]] end]
        }
        dom::DOMImplementation destroy $doc

        return [mime::initialize -canonical application/xml -string $data]
    }

    if {[string compare $content application/xml]} {
        return -code 7 \
               [beepcore::peer::errfmt $peerT 500 \
                    "expecting application/xml in request, not $content"]
    }

    set SOAP::CGI::debuginfo {}

    set doc {}

    set code [catch {
        switch -- $state(resource) {
            / {
                set env(HTTP_SOAPACTION) {}
            }

            default {
                set env(HTTP_SOAPACTION) $state(resource)
            }
        }

        SOAP::CGI::soap_invocation \
            [set doc [dom::DOMImplementation parse $data]]
    } result]

    catch { dom::DOMImplementation destroy $doc }

    foreach item $SOAP::CGI::debuginfo {
        beepcore::log::entry $state(logT) debug SOAP::CGI $item
    }

    if {$code && ([string first "<?xml " $result] != 0)} {
        return -code 7 [beepcore::peer::errfmt $peerT 500 $result]
    }

    if {[set x [string first [set y "?>\n"] $result]] >= 0 } {
        set result [string range $result [expr $x+[string length $y]] end]
    }

    return [mime::initialize -canonical application/xml -string $result]
}
