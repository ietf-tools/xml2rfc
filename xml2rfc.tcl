#!/bin/sh
# the next line restarts using the correct interpreter \
exec tclsh "$0" "$0" "$@"


#
# xml2rfc.tcl - convert technical memos written using XML to TXT/HTML/NROFF
#
# (c) 1998-01 Invisible Worlds, Inc.
#

global prog prog_version
set prog "xml2rfc"
set prog_version "v1.29"

# "encoding system" is already set at this point and we want that
# because we print warnings and errors to the terminal.
# Now we want the C collation, month names, etc.
foreach v {LC_ALL LC_ADDRESS LC_COLLATE LC_CTYPE LC_IDENTIFICATION
           LC_MESSAGES LC_MEASUREMENT LC_MONETARY LC_NAME LC_NUMERIC
           LC_PAPER LC_TELEPHONE LC_TIME LANG LANGUAGE LINGUAS} {
    set env($v) C
}


#
# here begins TclXML 1.1.1
#


# earlier versions used to "package require xml 1.8", but because newer tcl
# installations have an incompatibly-versioned sgml package, this caused
# nothing but problems. hence, we just include TclXML-1.1.1 wholesale toward
# the end of the file...


# sgml.tcl --
#
#       This file provides generic parsing services for SGML-based
#       languages, namely HTML and XML.
#
#       NB.  It is a misnomer.  There is no support for parsing
#       arbitrary SGML as such.
#
# Copyright (c) 1998,1999 Zveno Pty Ltd
# http://www.zveno.com/
#
# Zveno makes this software available free of charge for any purpose.
# Copies may be made of this software but all of this notice must be included
# on any copy.
#
# The software was developed for research purposes only and Zveno does not
# warrant that it is error free or fit for any purpose.  Zveno disclaims any
# liability for all claims, expenses, losses, damages and costs any user may
# incur as a result of using, copying or modifying this software.
#
# Copyright (c) 1997 ANU and CSIRO on behalf of the
# participants in the CRC for Advanced Computational Systems ('ACSys').
#
# ACSys makes this software and all associated data and documentation
# ('Software') available free of charge for any purpose.  You may make copies
# of the Software but you must include all of this notice on any copy.
#
# The Software was developed for research purposes and ACSys does not warrant
# that it is error free or fit for any purpose.  ACSys disclaims any
# liability for all claims, expenses, losses, damages and costs any user may
# incur as a result of using, copying or modifying the Software.
#
# $Id$

package provide sgml 1.6

namespace eval sgml {
    namespace export tokenise parseEvent

    namespace export parseDTD

    # Convenience routine
    proc cl x {
        return "\[$x\]"
    }

    # Define various regular expressions
    # white space
    variable Wsp " \t\r\n"
    variable noWsp [cl ^$Wsp]

    # Various XML names
    variable nmtoken [cl -a-zA-Z0-9._]+
    variable name [cl a-zA-Z_][cl -a-zA-Z0-9._]*

    # Other
    variable ParseEventNum
    if {![info exists ParseEventNum]} {
        set ParseEventNum 0
    }
    variable ParseDTDnum
    if {![info exists ParseDTDNum]} {
        set ParseDTDNum 0
    }

    # table of predefined entities for XML

    variable EntityPredef
    array set EntityPredef {
        lt <   gt >   amp &   quot \"   apos '
    }

}

# sgml::tokenise --
#
#       Transform the given HTML/XML text into a Tcl list.
#
# Arguments:
#       sgml            text to tokenize
#       elemExpr        RE to recognise tags
#       elemSub         transform for matched tags
#       args            options
#
# Valid Options:
#       -final          boolean         True if no more data is to be supplied
#       -statevariable  varName         Name of a variable used to store info
#
# Results:
#       Returns a Tcl list representing the document.

proc sgml::tokenise {sgml elemExpr elemSub args} {
    array set options {-final 1}
    catch {array set options $args}
    set options(-final) [Boolean $options(-final)]

    # If the data is not final then there must be a variable to store
    # unused data.
    if {!$options(-final) && ![info exists options(-statevariable)]} {
        return -code error {option "-statevariable" required if not final}
    }

    # Pre-process stage
    #
    # Extract the internal DTD subset, if any

    catch {upvar #0 $options(-internaldtdvariable) dtd}
    if {[regexp {<!DOCTYPE[^[<]+\[([^]]+)\]} $sgml discard dtd]} {
        set text ""
        append text [string repeat "\n" [num_eols $dtd]]
        regsub {(<!DOCTYPE[^[<]+)(\[[^]]+\])} $sgml "\\1$text\\&xml:intdtd;" sgml
    }

    # Protect Tcl special characters
    regsub -all {([{}\\])} $sgml {\\\1} sgml

    # Do the translation

    if {[info exists options(-statevariable)]} {
        upvar #0 $opts(-statevariable) unused
        if {[info exists unused]} {
            regsub -all $elemExpr $unused$sgml $elemSub sgml
            unset unused
        } else {
            regsub -all $elemExpr $sgml $elemSub sgml
        }
        set sgml "{} {} {} {} \{$sgml\}"

        # Performance note (Tcl 8.0):
        #       Use of lindex, lreplace will cause parsing to list object

        if {[regexp {^([^<]*)(<[^>]*$)} [lindex $sgml end] x text unused]} {
            set sgml [lreplace $sgml end end $text]
        }

    } else {

        # Performance note (Tcl 8.0):
        #       In this case, no conversion to list object is performed

        regsub -all $elemExpr $sgml $elemSub sgml
        set sgml "{} {} {} {} \{$sgml\}"
    }

    return $sgml

}

# sgml::parseEvent --
#
#       Produces an event stream for a XML/HTML document,
#       given the Tcl list format returned by tokenise.
#
#       This procedure checks that the document is well-formed,
#       and throws an error if the document is found to be not
#       well formed.  Warnings are passed via the -warningcommand script.
#
#       The procedure only check for well-formedness,
#       no DTD is required.  However, facilities are provided for entity expansion.
#
# Arguments:
#       sgml            Instance data, as a Tcl list.
#       args            option/value pairs
#
# Valid Options:
#       -final                  Indicates end of document data
#       -elementstartcommand    Called when an element starts
#       -elementendcommand      Called when an element ends
#       -characterdatacommand   Called when character data occurs
#       -entityreferencecommand Called when an entity reference occurs
#       -processinginstructioncommand   Called when a PI occurs
#       -externalentityrefcommand       Called for an external entity reference
#
#       (Not compatible with expat)
#       -xmldeclcommand         Called when the XML declaration occurs
#       -doctypecommand         Called when the document type declaration occurs
#       -commentcommand         Called when a comment occurs
#
#       -errorcommand           Script to evaluate for a fatal error
#       -warningcommand         Script to evaluate for a reportable warning
#       -statevariable          global state variable
#       -normalize              whether to normalize names
#       -reportempty            whether to include an indication of empty elements
#
# Results:
#       The various callback scripts are invoked.
#       Returns empty string.
#
# BUGS:
#       If command options are set to empty string then they should not be invoked.

proc sgml::parseEvent {sgml args} {
    variable Wsp
    variable noWsp
    variable nmtoken
    variable name
    variable ParseEventNum

    array set options [list \
        -elementstartcommand            [namespace current]::noop       \
        -elementendcommand              [namespace current]::noop       \
        -characterdatacommand           [namespace current]::noop       \
        -processinginstructioncommand   [namespace current]::noop       \
        -externalentityrefcommand       [namespace current]::noop       \
        -xmldeclcommand                 [namespace current]::noop       \
        -doctypecommand                 [namespace current]::noop       \
        -commentcommand                 [namespace current]::noop       \
        -entityreferencecommand         {}                              \
        -warningcommand                 [namespace current]::noop       \
        -errorcommand                   [namespace current]::Error      \
        -final                          1                               \
        -emptyelement                   [namespace current]::EmptyElement       \
        -parseattributelistcommand      [namespace current]::noop       \
        -normalize                      1                               \
        -internaldtd                    {}                              \
        -reportempty                    0                               \
        -entityvariable                 [namespace current]::EntityPredef       \
    ]
    catch {array set options $args}

    if {![info exists options(-statevariable)]} {
        set options(-statevariable) [namespace current]::ParseEvent[incr ParseEventNum]
    }

    upvar #0 $options(-statevariable) state
    upvar #0 $options(-entityvariable) entities

    if {![info exists state]} {
        # Initialise the state variable
        array set state {
            mode normal
            haveXMLDecl 0
            haveDocElement 0
            context {}
            stack {}
            line 0
            lineo 0
            linet 0
        }
    }

    foreach {tag close empty param text} $sgml {

        # Keep track of lines (open, text, current/next) in the input
        set ::xdv::lineno $state(line)
        set state(lineo) $state(line)
        incr state(line) [regsub -all \n $param {} discard]
        set state(linet) $state(line)
        incr state(line) [regsub -all \n $text {} discard]

        # If the current mode is cdata or comment then we must undo what the
        # regsub has done to reconstitute the data

        switch $state(mode) {
            comment {
                # This had "[string length $param] && " as a guard -
                # can't remember why :-(
                if {[regexp ([cl ^-]*)--\$ $tag discard comm1]} {
                    # end of comment (in tag)
                    set tag {}
                    set close {}
                    set empty {}
                    set state(mode) normal
                    uplevel #0 $options(-commentcommand) [list $state(commentdata)<$comm1]
                    unset state(commentdata)
                } elseif {[regexp ([cl ^-]*)--\$ $param discard comm1]} {
                    # end of comment (in attributes)
                    uplevel #0 $options(-commentcommand) [list $state(commentdata)<$close$tag$empty>$comm1]
                    unset state(commentdata)
                    set tag {}
                    set param {}
                    set close {}
                    set empty {}
                    set state(mode) normal
                } elseif {[regexp ([cl ^-]*)-->(.*) $text discard comm1 text]} {
                    # end of comment (in text)
                    uplevel #0 $options(-commentcommand) [list $state(commentdata)<$close$tag$param$empty>$comm1]
                    unset state(commentdata)
                    set tag {}
                    set param {}
                    set close {}
                    set empty {}
                    set state(mode) normal
                } else {
                    # comment continues
                    append state(commentdata) <$close$tag$param$empty>$text
                    continue
                }
            }
            cdata {
                if {[string length $param] && [regexp ([cl ^\]]*)\]\][cl $Wsp]*\$ $tag discard cdata1]} {
                    # end of CDATA (in tag)
                    uplevel #0 $options(-characterdatacommand) [list $state(cdata)<$close$cdata1$text]
                    set text {}
                    set tag {}
                    unset state(cdata)
                    set state(mode) normal
                } elseif {[regexp ([cl ^\]]*)\]\][cl $Wsp]*\$ $param discard cdata1]} {
                    # end of CDATA (in attributes)
                    uplevel #0 $options(-characterdatacommand) [list $state(cdata)<$close$tag$cdata1$text]
                    set text {}
                    set tag {}
                    set param {}
                    unset state(cdata)
                    set state(mode) normal
                } elseif {[regexp ([cl ^\]]*)\]\][cl $Wsp]*>(.*) $text discard cdata1 text]} {
                    # end of CDATA (in text)
                    uplevel #0 $options(-characterdatacommand) [list $state(cdata)<$close$tag$param$empty>$cdata1$text]
                    set text {}
                    set tag {}
                    set param {}
                    set close {}
                    set empty {}
                    unset state(cdata)
                    set state(mode) normal
                } else {
                    # CDATA continues
                    append state(cdata) <$close$tag$param$empty>$text
                    continue
                }
            }
        }

        # default: normal mode

        # Bug: if the attribute list has a right angle bracket then the empty
        # element marker will not be seen

        set isEmpty [uplevel #0 $options(-emptyelement) [list $tag $param $empty]]
        if {[llength $isEmpty]} {
            foreach {empty tag param} $isEmpty break
        }

        switch -glob -- [string length $tag],[regexp {^\?|!.*} $tag],$close,$empty {

            0,0,, {
                # Ignore empty tag - dealt with non-normal mode above
            }
            *,0,, {

                # Start tag for an element.

                # Check for a right angle bracket in an attribute value
                # This manifests itself by terminating the value before
                # the delimiter is seen, and the delimiter appearing
                # in the text

                # BUG: If two or more attribute values have right angle
                # brackets then this will fail on the second one.

                if {[regexp [format {=[%s]*"[^"]*$} $Wsp] $param] && \
                        [regexp {([^"]*"[^>]*)>(.*)} $text discard attrListRemainder text]} {
                    append param >$attrListRemainder
                } elseif {[regexp [format {=[%s]*'[^']*$} $Wsp] $param] && \
                        [regexp {([^']*'[^>]*)>(.*)} $text discard attrListRemainder text]} {
                    append param >$attrListRemainder
                }

                # Check if the internal DTD entity is in an attribute
                # value
                regsub -all &xml:intdtd\; $param \[$options(-internaldtd)\] param

                ParseEvent:ElementOpen $tag $param options
                set state(haveDocElement) 1

            }

            *,0,/, {

                # End tag for an element.

                ParseEvent:ElementClose $tag options

            }

            *,0,,/ {

                # Empty element

                ParseEvent:ElementOpen $tag $param options -empty 1
                ParseEvent:ElementClose $tag options -empty 1

            }

            *,1,* {
                # Processing instructions or XML declaration
                switch -glob -- $tag {

                    {\?xml} {
                        # XML Declaration
                        if {$state(haveXMLDecl)} {
                            uplevel #0 $options(-errorcommand) "unexpected characters \"<$tag\" around line $state(lineo)"
                        } elseif {![regexp {\?$} $param]} {
                            uplevel #0 $options(-errorcommand) "XML Declaration missing characters \"?>\" around line $state(linet)"
                        } else {

                            # Get the version number
                            if {[regexp {[      ]*version="(-+|[a-zA-Z0-9_.:]+)"[       ]*} $param discard version] || [regexp {[       ]*version='(-+|[a-zA-Z0-9_.:]+)'[       ]*} $param discard version]} {
                                if {[string compare $version "1.0"]} {
                                    # Should we support future versions?
                                    # At least 1.X?
                                    uplevel #0 $options(-errorcommand) "document XML version \"$version\" is incompatible with XML version 1.0"
                                }
                            } else {
                                uplevel #0 $options(-errorcommand) "XML Declaration missing version information around line $state(lineo)"
                            }

                            # Get the encoding declaration
                            set encoding {}
                            regexp {[   ]*encoding="([A-Za-z]([A-Za-z0-9._]|-)*)"[      ]*} $param discard encoding
                            regexp {[   ]*encoding='([A-Za-z]([A-Za-z0-9._]|-)*)'[      ]*} $param discard encoding

                            # Get the standalone declaration
                            set standalone {}
                            regexp {[   ]*standalone="(yes|no)"[        ]*} $param discard standalone
                            regexp {[   ]*standalone='(yes|no)'[        ]*} $param discard standalone

                            # Invoke the callback
                            uplevel #0 $options(-xmldeclcommand) [list $version $encoding $standalone]

                        }

                    }

                    {\?*} {
                        # Processing instruction
                        if {   ![regsub {\?$} $param {} param]
                            && !(   ![string compare $param ""]
                                 && [regsub {\?$} $tag {} tag]
                                 && [string compare $tag ""])} {
                            uplevel #0 $options(-errorcommand) "PI: expected '?' character around line $state(linet)"
                        } else {
                            uplevel #0 $options(-processinginstructioncommand) [list [string range $tag 1 end] $param]
                        }
                    }

                    !DOCTYPE {
                        # External entity reference
                        # This should move into xml.tcl
                        # Parse the params supplied.  Looking for Name, ExternalID and MarkupDecl
                        regexp ^[cl $Wsp]*($name)(.*) $param x state(doc_name) param
                        set state(doc_name) [Normalize $state(doc_name) $options(-normalize)]
                        set externalID {}
                        set pubidlit {}
                        set systemlit {}
                        set externalID {}
                        if {[regexp -nocase ^[cl $Wsp]*(SYSTEM|PUBLIC)(.*) $param x id param]} {
                            switch [string toupper $id] {
                                SYSTEM {
                                    if {[regexp ^[cl $Wsp]+"([cl ^"]*)"(.*) $param x systemlit param] || [regexp ^[cl $Wsp]+'([cl ^']*)'(.*) $param x systemlit param]} {
                                        set externalID [list SYSTEM $systemlit] ;# "
                                    } else {
                                        uplevel #0 $options(-errorcommand) {{syntax error: SYSTEM identifier not followed by literal}}
                                    }
                                }
                                PUBLIC {
                                    if {[regexp ^[cl $Wsp]+"([cl ^"]*)"(.*) $param x pubidlit param] || [regexp ^[cl $Wsp]+'([cl ^']*)'(.*) $param x pubidlit param]} {
                                        if {[regexp ^[cl $Wsp]+"([cl ^"]*)"(.*) $param x systemlit param] || [regexp ^[cl $Wsp]+'([cl ^']*)'(.*) $param x systemlit param]} {
                                            set externalID [list PUBLIC $pubidlit $systemlit]
                                        } else {
                                            uplevel #0 $options(-errorcommand) "syntax error: PUBLIC identifier not followed by system literal around line $state(lineo)"
                                        }
                                    } else {
                                        uplevel #0 $options(-errorcommand) "syntax error: PUBLIC identifier not followed by literal around line $state(lineo)"
                                    }
                                }
                            }
                            if {[regexp -nocase ^[cl $Wsp]+NDATA[cl $Wsp]+($name)(.*) $param x notation param]} {
                                lappend externalID $notation
                            }
                        }

                        uplevel #0 $options(-doctypecommand) $state(doc_name) [list $pubidlit $systemlit $options(-internaldtd)]

                    }

                    !--* {

                        # Start of a comment
                        # See if it ends in the same tag, otherwise change the
                        # parsing mode

                        regexp {!--(.*)} $tag discard comm1
                        if {[regexp ([cl ^-]*)--[cl $Wsp]*\$ $comm1 discard comm1_1]} {
                            # processed comment (end in tag)
                            uplevel #0 $options(-commentcommand) [list $comm1_1]
                        } elseif {[regexp ([cl ^-]*)--[cl $Wsp]*\$ $param discard comm2]} {
                            # processed comment (end in attributes)
                            uplevel #0 $options(-commentcommand) [list $comm1$comm2]
                        } elseif {[regexp ([cl ^-]*)-->(.*) $text discard comm2 text]} {
                            # processed comment (end in text)
                            uplevel #0 $options(-commentcommand) [list $comm1$param>$comm2]
                        } else {
                            # start of comment
                            set state(mode) comment
                            set state(commentdata) "$comm1$param>$text"
                            continue
                        }
                    }

                    {!\[CDATA\[*} {

                        regexp {!\[CDATA\[(.*)} $tag discard cdata1
                        if {[regexp {(.*)]]$} $param discard cdata2]} {
                            # processed CDATA (end in attribute)
                            uplevel #0 $options(-characterdatacommand) [list $cdata1$cdata2$text]
                            set text {}
                        } elseif {[regexp {(.*)]]>(.*)} $text discard cdata2 text]} {
                            # processed CDATA (end in text)
                            uplevel #0 $options(-characterdatacommand) [list $cdata1$param$empty>$cdata2$text]
                            set text {}
                        } else {
                            # start CDATA
                            set state(cdata) "$cdata1$param>$text"
                            set state(mode) cdata
                            continue
                        }

                    }

                    !ELEMENT {
                        # Internal DTD declaration
                    }
                    !ATTLIST {
                    }
                    !ENTITY {
                    }
                    !NOTATION {
                    }


                    !* {
                        uplevel #0 $options(-processinginstructioncommand) [list $tag $param]
                    }
                    default {
                        uplevel #0 $options(-errorcommand) [list "unknown processing instruction \"<$tag>\" around line $state(lineo)"]
                    }
                }
            }
            *,1,* -
            *,0,/,/ {
                # Syntax error
                uplevel #0 $options(-errorcommand) [list [list syntax error: closed/empty tag: tag $tag param $param empty $empty close $close around line $state(lineo)]]
            }
        }

        # Process character data

        if {$state(haveDocElement) && [llength $state(stack)]} {

            # Check if the internal DTD entity is in the text
            regsub -all &xml:intdtd\; $text \[$options(-internaldtd)\] text

            # Look for entity references
            if {([array size entities] || [string length $options(-entityreferencecommand)]) && \
                [regexp {&[^;]+;} $text]} {

                # protect Tcl specials
                regsub -all {([][$\\])} $text {\\\1} text
                # Mark entity references
                regsub -all {&([^;]+);} $text [format {%s; %s {\1} ; %s %s} \}\} [namespace code [list Entity options $options(-entityreferencecommand) $options(-characterdatacommand) $options(-entityvariable)]] [list uplevel #0 $options(-characterdatacommand)] \{\{] text
                set text "uplevel #0 $options(-characterdatacommand) {{$text}}"
                eval $text
            } else {
                # Restore protected special characters
                regsub -all {\\([{}\\])} $text {\1} text
#                uplevel #0 $options(-characterdatacommand) [list $text]
                sgml::callback $state(lineo) \
                      $options(-characterdatacommand) [list $text]
            }
        } elseif {[string length [string trim $text]]} {
            uplevel #0 $options(-errorcommand) [list "unexpected text \"$text\" in document prolog around line $state(linet)"]
        }

    }

    # If this is the end of the document, close all open containers
    if {$options(-final) && [llength $state(stack)]} {
        eval $options(-errorcommand) [list [list element [lindex $state(stack) end] remains unclosed around line $state(line)]]
    }

    set ::xdv::lineno -1

    return {}
}

proc sgml::callback {lineno args} {
    global errorCode errorInfo

    set ::xdv::lineno $lineno
    if {[set code [catch { eval uplevel #0 $args } result]]} {
        append result " around line $lineno"
    }

    return -code $code -errorinfo $errorInfo -errorcode $errorCode $result
}

# sgml::ParseEvent:ElementOpen --
#
#       Start of an element.
#
# Arguments:
#       tag     Element name
#       attr    Attribute list
#       opts    Option variable in caller
#       args    further configuration options
#
# Options:
#       -empty boolean
#               indicates whether the element was an empty element
#
# Results:
#       Modify state and invoke callback

proc sgml::ParseEvent:ElementOpen {tag attr opts args} {
    upvar $opts options
    upvar #0 $options(-statevariable) state
    array set cfg {-empty 0}
    array set cfg $args

    if {$options(-normalize)} {
        set tag [string toupper $tag]
    }

    # Update state
    lappend state(stack) $tag

    # Parse attribute list into a key-value representation
    if {[string compare $options(-parseattributelistcommand) {}]} {
        if {[catch {uplevel #0 $options(-parseattributelistcommand) [list $attr]} attr]} {
            uplevel #0 $options(-errorcommand) [list $attr around line $state(lineo)]
            set attr {}
        }
    }

    set empty {}
    if {$cfg(-empty) && $options(-reportempty)} {
        set empty {-empty 1}
    }

    # Invoke callback
#    uplevel #0 $options(-elementstartcommand) [list $tag $attr] $empty
    sgml::callback $state(lineo) \
          $options(-elementstartcommand) [list $tag $attr] $empty

    return {}
}

# sgml::ParseEvent:ElementClose --
#
#       End of an element.
#
# Arguments:
#       tag     Element name
#       opts    Option variable in caller
#       args    further configuration options
#
# Options:
#       -empty boolean
#               indicates whether the element as an empty element
#
# Results:
#       Modify state and invoke callback

proc sgml::ParseEvent:ElementClose {tag opts args} {
    upvar $opts options
    upvar #0 $options(-statevariable) state
    array set cfg {-empty 0}
    array set cfg $args

    # WF check
    if {[string compare $tag [lindex $state(stack) end]]} {
        uplevel #0 $options(-errorcommand) [list "end tag \"$tag\" does not match open element \"[lindex $state(stack) end]\" around line $state(lineo)"]
        return
    }

    # Update state
    set state(stack) [lreplace $state(stack) end end]

    set empty {}
    if {$cfg(-empty) && $options(-reportempty)} {
        set empty {-empty 1}
    }

    # Invoke callback
#    uplevel #0 $options(-elementendcommand) [list $tag] $empty
    sgml::callback $state(lineo) \
          $options(-elementendcommand) [list $tag] $empty

    return {}
}

# sgml::Normalize --
#
#       Perform name normalization if required
#
# Arguments:
#       name    name to normalize
#       req     normalization required
#
# Results:
#       Name returned as upper-case if normalization required

proc sgml::Normalize {name req} {
    if {$req} {
        return [string toupper $name]
    } else {
        return $name
    }
}

# sgml::Entity --
#
#       Resolve XML entity references (syntax: &xxx;).
#
# Arguments:
#       opts            options array variable in caller
#       entityrefcmd    application callback for entity references
#       pcdatacmd       application callback for character data
#       entities        name of array containing entity definitions.
#       ref             entity reference (the "xxx" bit)
#
# Results:
#       Returns substitution text for given entity.

proc sgml::Entity {opts entityrefcmd pcdatacmd entities ref} {
    upvar 2 $opts options
    upvar #0 $options(-statevariable) state

    if {![string length $entities]} {
        set entities [namespace current EntityPredef]
    }

    switch -glob -- $ref {
        %* {
            # Parameter entity - not recognised outside of a DTD
        }
        #x* {
            # Character entity - hex
            if {[catch {format %c [scan [string range $ref 2 end] %x tmp; set tmp]} char]} {
                return -code error "malformed character entity \"$ref\""
            }
            uplevel #0 $pcdatacmd [list $char]

            return {}

        }
        #* {
            # Character entity - decimal
            if {[catch {format %c [scan [string range $ref 1 end] %d tmp; set tmp]} char]} {
                return -code error "malformed character entity \"$ref\""
            }
            uplevel #0 $pcdatacmd [list $char]

            return {}

        }
        default {
            # General entity
            upvar #0 $entities map
            if {[info exists map($ref)]} {

                if {![regexp {<|&} $map($ref)]} {

                    # Simple text replacement - optimise

                    uplevel #0 $pcdatacmd [list $map($ref)]

                    return {}

                }

                # Otherwise an additional round of parsing is required.
                # This only applies to XML, since HTML doesn't have general entities

                # Must parse the replacement text for start & end tags, etc
                # This text must be self-contained: balanced closing tags, and so on

                set tokenised [tokenise $map($ref) $::xml::tokExpr $::xml::substExpr]
                set final $options(-final)
                unset options(-final)
                eval parseEvent [list $tokenised] [array get options] -final 0
                set options(-final) $final

                return {}

            } elseif {[string length $entityrefcmd]} {

                uplevel #0 $entityrefcmd [list $ref]

                return {}

            }
        }
    }

    # If all else fails leave the entity reference untouched
    uplevel #0 $pcdatacmd [list &$ref\;]

    return {}
}

####################################
#
# DTD parser for SGML (XML).
#
# This DTD actually only handles XML DTDs.  Other language's
# DTD's, such as HTML, must be written in terms of a XML DTD.
#
# A DTD is represented as a three element Tcl list.
# The first element contains the content models for elements,
# the second contains the attribute lists for elements and
# the last element contains the entities for the document.
#
####################################

# sgml::parseDTD --
#
#       Entry point to the SGML DTD parser.
#
# Arguments:
#       dtd     data defining the DTD to be parsed
#       args    configuration options
#
# Results:
#       Returns a three element list, first element is the content model
#       for each element, second element are the attribute lists of the
#       elements and the third element is the entity map.

proc sgml::parseDTD {dtd args} {
    variable Wsp
    variable ParseDTDnum

    array set opts [list \
        -errorcommand           [namespace current]::noop \
        state                   [namespace current]::parseDTD[incr ParseDTDnum]
    ]
    array set opts $args

    set exp <!([cl ^$Wsp>]+)[cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*([cl ^>]*)>
    set sub {{\1} {\2} {\3} }
    regsub -all $exp $dtd $sub dtd

    foreach {decl id value} $dtd {
        catch {DTD:[string toupper $decl] $id $value} err
    }

    return [list [array get contentmodel] [array get attributes] [array get entities]]
}

# Procedures for handling the various declarative elements in a DTD.
# New elements may be added by creating a procedure of the form
# parse:DTD:_element_

# For each of these procedures, the various regular expressions they use
# are created outside of the proc to avoid overhead at runtime

# sgml::DTD:ELEMENT --
#
#       <!ELEMENT ...> defines an element.
#
#       The content model for the element is stored in the contentmodel array,
#       indexed by the element name.  The content model is parsed into the
#       following list form:
#
#               {}      Content model is EMPTY.
#                       Indicated by an empty list.
#               *       Content model is ANY.
#                       Indicated by an asterix.
#               {ELEMENT ...}
#                       Content model is element-only.
#               {MIXED {element1 element2 ...}}
#                       Content model is mixed (PCDATA and elements).
#                       The second element of the list contains the
#                       elements that may occur.  #PCDATA is assumed
#                       (ie. the list is normalised).
#
# Arguments:
#       id      identifier for the element.
#       value   other information in the PI

proc sgml::DTD:ELEMENT {id value} {
    dbgputs DTD_parse [list DTD:ELEMENT $id $value]
    variable Wsp
    upvar opts state
    upvar contentmodel cm

    if {[info exists cm($id)]} {
        eval $state(-errorcommand) element [list "element \"$id\" already declared"]
    } else {
        switch -- $value {
            EMPTY {
                set cm($id) {}
            }
            ANY {
                set cm($id) *
            }
            default {
                if {[regexp [format {^\([%s]*#PCDATA[%s]*(\|([^)]+))?[%s]*\)*[%s]*$} $Wsp $Wsp $Wsp $Wsp] discard discard mtoks]} {
                    set cm($id) [list MIXED [split $mtoks |]]
                } else {
                    if {[catch {CModelParse $state(state) $value} result]} {
                        eval $state(-errorcommand) element [list $result]
                    } else {
                        set cm($id) [list ELEMENT $result]
                    }
                }
            }
        }
    }
}

# sgml::CModelParse --
#
#       Parse an element content model (non-mixed).
#       A syntax tree is constructed.
#       A transition table is built next.
#
#       This is going to need alot of work!
#
# Arguments:
#       state   state array variable
#       value   the content model data
#
# Results:
#       A Tcl list representing the content model.

proc sgml::CModelParse {state value} {
    upvar #0 $state var

    # First build syntax tree
    set syntaxTree [CModelMakeSyntaxTree $state $value]

    # Build transition table
    set transitionTable [CModelMakeTransitionTable $state $syntaxTree]

    return [list $syntaxTree $transitionTable]
}

# sgml::CModelMakeSyntaxTree --
#
#       Construct a syntax tree for the regular expression.
#
#       Syntax tree is represented as a Tcl list:
#       rep {:choice|:seq {{rep list1} {rep list2} ...}}
#       where:  rep is repetition character, *, + or ?. {} for no repetition
#               listN is nested expression or Name
#
# Arguments:
#       spec    Element specification
#
# Results:
#       Syntax tree for element spec as nested Tcl list.
#
#       Examples:
#       (memo)
#               {} {:seq {{} memo}}
#       (front, body, back?)
#               {} {:seq {{} front} {{} body} {? back}}
#       (head, (p | list | note)*, div2*)
#               {} {:seq {{} head} {* {:choice {{} p} {{} list} {{} note}}} {* div2}}
#       (p | a | ul)+
#               + {:choice {{} p} {{} a} {{} ul}}

proc sgml::CModelMakeSyntaxTree {state spec} {
    upvar #0 $state var
    variable Wsp
    variable name

    # Translate the spec into a Tcl list.

    # None of the Tcl special characters are allowed in a content model spec.
    if {[regexp {\$|\[|\]|\{|\}} $spec]} {
        return -code error "illegal characters in specification"
    }

    regsub -all [format {(%s)[%s]*(\?|\*|\+)?[%s]*(,|\|)?} $name $Wsp $Wsp] $spec [format {%sCModelSTname %s {\1} {\2} {\3}} \n $state] spec
    regsub -all {\(} $spec "\nCModelSTopenParen $state " spec
    regsub -all [format {\)[%s]*(\?|\*|\+)?[%s]*(,|\|)?} $Wsp $Wsp] $spec [format {%sCModelSTcloseParen %s {\1} {\2}} \n $state] spec

    array set var {stack {} state start}
    eval $spec

    # Peel off the outer seq, its redundant
    return [lindex [lindex $var(stack) 1] 0]
}

# sgml::CModelSTname --
#
#       Processes a name in a content model spec.
#
# Arguments:
#       state   state array variable
#       name    name specified
#       rep     repetition operator
#       cs      choice or sequence delimiter
#
# Results:
#       See CModelSTcp.

proc sgml::CModelSTname {state name rep cs args} {
    if {[llength $args]} {
        return -code error "syntax error in specification: \"$args\""
    }

    CModelSTcp $state $name $rep $cs
}

# sgml::CModelSTcp --
#
#       Process a content particle.
#
# Arguments:
#       state   state array variable
#       name    name specified
#       rep     repetition operator
#       cs      choice or sequence delimiter
#
# Results:
#       The content particle is added to the current group.

proc sgml::CModelSTcp {state cp rep cs} {
    upvar #0 $state var

    switch -glob -- [lindex $var(state) end]=$cs {
        start= {
            set var(state) [lreplace $var(state) end end end]
            # Add (dummy) grouping, either choice or sequence will do
            CModelSTcsSet $state ,
            CModelSTcpAdd $state $cp $rep
        }
        :choice= -
        :seq= {
            set var(state) [lreplace $var(state) end end end]
            CModelSTcpAdd $state $cp $rep
        }
        start=| -
        start=, {
            set var(state) [lreplace $var(state) end end [expr {$cs == "," ? ":seq" : ":choice"}]]
            CModelSTcsSet $state $cs
            CModelSTcpAdd $state $cp $rep
        }
        :choice=| -
        :seq=, {
            CModelSTcpAdd $state $cp $rep
        }
        :choice=, -
        :seq=| {
            return -code error "syntax error in specification: incorrect delimiter after \"$cp\", should be \"[expr {$cs == "," ? "|" : ","}]\""
        }
        end=* {
            return -code error "syntax error in specification: no delimiter before \"$cp\""
        }
        default {
            return -code error "syntax error"
        }
    }

}

# sgml::CModelSTcsSet --
#
#       Start a choice or sequence on the stack.
#
# Arguments:
#       state   state array
#       cs      choice oir sequence
#
# Results:
#       state is modified: end element of state is appended.

proc sgml::CModelSTcsSet {state cs} {
    upvar #0 $state var

    set cs [expr {$cs == "," ? ":seq" : ":choice"}]

    if {[llength $var(stack)]} {
        set var(stack) [lreplace $var(stack) end end $cs]
    } else {
        set var(stack) [list $cs {}]
    }
}

# sgml::CModelSTcpAdd --
#
#       Append a content particle to the top of the stack.
#
# Arguments:
#       state   state array
#       cp      content particle
#       rep     repetition
#
# Results:
#       state is modified: end element of state is appended.

proc sgml::CModelSTcpAdd {state cp rep} {
    upvar #0 $state var

    if {[llength $var(stack)]} {
        set top [lindex $var(stack) end]
        lappend top [list $rep $cp]
        set var(stack) [lreplace $var(stack) end end $top]
    } else {
        set var(stack) [list $rep $cp]
    }
}

# sgml::CModelSTopenParen --
#
#       Processes a '(' in a content model spec.
#
# Arguments:
#       state   state array
#
# Results:
#       Pushes stack in state array.

proc sgml::CModelSTopenParen {state args} {
    upvar #0 $state var

    if {[llength $args]} {
        return -code error "syntax error in specification: \"$args\""
    }

    lappend var(state) start
    lappend var(stack) [list {} {}]
}

# sgml::CModelSTcloseParen --
#
#       Processes a ')' in a content model spec.
#
# Arguments:
#       state   state array
#       rep     repetition
#       cs      choice or sequence delimiter
#
# Results:
#       Stack is popped, and former top of stack is appended to previous element.

proc sgml::CModelSTcloseParen {state rep cs args} {
    upvar #0 $state var

    if {[llength $args]} {
        return -code error "syntax error in specification: \"$args\""
    }

    set cp [lindex $var(stack) end]
    set var(stack) [lreplace $var(stack) end end]
    set var(state) [lreplace $var(state) end end]
    CModelSTcp $state $cp $rep $cs
}

# sgml::CModelMakeTransitionTable --
#
#       Given a content model's syntax tree, constructs
#       the transition table for the regular expression.
#
#       See "Compilers, Principles, Techniques, and Tools",
#       Aho, Sethi and Ullman.  Section 3.9, algorithm 3.5.
#
# Arguments:
#       state   state array variable
#       st      syntax tree
#
# Results:
#       The transition table is returned, as a key/value Tcl list.

proc sgml::CModelMakeTransitionTable {state st} {
    upvar #0 $state var

    # Construct nullable, firstpos and lastpos functions
    array set var {number 0}
    foreach {nullable firstpos lastpos} [       \
        TraverseDepth1st $state $st {
            # Evaluated for leaf nodes
            # Compute nullable(n)
            # Compute firstpos(n)
            # Compute lastpos(n)
            set nullable [nullable leaf $rep $name]
            set firstpos [list {} $var(number)]
            set lastpos [list {} $var(number)]
            set var(pos:$var(number)) $name
        } {
            # Evaluated for nonterminal nodes
            # Compute nullable, firstpos, lastpos
            set firstpos [firstpos $cs $firstpos $nullable]
            set lastpos  [lastpos  $cs $lastpos  $nullable]
            set nullable [nullable nonterm $rep $cs $nullable]
        }       \
    ] break

    set accepting [incr var(number)]
    set var(pos:$accepting) #

    # var(pos:N) maps from position to symbol.
    # Construct reverse map for convenience.
    # NB. A symbol may appear in more than one position.
    # var is about to be reset, so use different arrays.

    foreach {pos symbol} [array get var pos:*] {
        set pos [lindex [split $pos :] 1]
        set pos2symbol($pos) $symbol
        lappend sym2pos($symbol) $pos
    }

    # Construct the followpos functions
    catch {unset var}
    followpos $state $st $firstpos $lastpos

    # Construct transition table
    # Dstates is [union $marked $unmarked]
    set unmarked [list [lindex $firstpos 1]]
    while {[llength $unmarked]} {
        set T [lindex $unmarked 0]
        lappend marked $T
        set unmarked [lrange $unmarked 1 end]

        # Find which input symbols occur in T
        set symbols {}
        foreach pos $T {
            if {$pos != $accepting && [lsearch $symbols $pos2symbol($pos)] < 0} {
                lappend symbols $pos2symbol($pos)
            }
        }
        foreach a $symbols {
            set U {}
            foreach pos $sym2pos($a) {
                if {[lsearch $T $pos] >= 0} {
                    # add followpos($pos)
                    if {$var($pos) == {}} {
                        lappend U $accepting
                    } else {
                        eval lappend U $var($pos)
                    }
                }
            }
            set U [makeSet $U]
            if {[llength $U] && [lsearch $marked $U] < 0 && [lsearch $unmarked $U] < 0} {
                lappend unmarked $U
            }
            set Dtran($T,$a) $U
        }

    }

    return [list [array get Dtran] [array get sym2pos] $accepting]
}

# sgml::followpos --
#
#       Compute the followpos function, using the already computed
#       firstpos and lastpos.
#
# Arguments:
#       state           array variable to store followpos functions
#       st              syntax tree
#       firstpos        firstpos functions for the syntax tree
#       lastpos         lastpos functions
#
# Results:
#       followpos functions for each leaf node, in name/value format

proc sgml::followpos {state st firstpos lastpos} {
    upvar #0 $state var

    switch -- [lindex [lindex $st 1] 0] {
        :seq {
            for {set i 1} {$i < [llength [lindex $st 1]]} {incr i} {
                followpos $state [lindex [lindex $st 1] $i]                     \
                        [lindex [lindex $firstpos 0] [expr $i - 1]]     \
                        [lindex [lindex $lastpos 0] [expr $i - 1]]
                foreach pos [lindex [lindex [lindex $lastpos 0] [expr $i - 1]] 1] {
                    eval lappend var($pos) [lindex [lindex [lindex $firstpos 0] $i] 1]
                    set var($pos) [makeSet $var($pos)]
                }
            }
        }
        :choice {
            for {set i 1} {$i < [llength [lindex $st 1]]} {incr i} {
                followpos $state [lindex [lindex $st 1] $i]                     \
                        [lindex [lindex $firstpos 0] [expr $i - 1]]     \
                        [lindex [lindex $lastpos 0] [expr $i - 1]]
            }
        }
        default {
            # No action at leaf nodes
        }
    }

    switch -- [lindex $st 0] {
        ? {
            # We having nothing to do here ! Doing the same as
            # for * effectively converts this qualifier into the other.
        }
        * {
            foreach pos [lindex $lastpos 1] {
                eval lappend var($pos) [lindex $firstpos 1]
                set var($pos) [makeSet $var($pos)]
            }
        }
    }

}

# sgml::TraverseDepth1st --
#
#       Perform depth-first traversal of a tree.
#       A new tree is constructed, with each node computed by f.
#
# Arguments:
#       state   state array variable
#       t       The tree to traverse, a Tcl list
#       leaf    Evaluated at a leaf node
#       nonTerm Evaluated at a nonterminal node
#
# Results:
#       A new tree is returned.

proc sgml::TraverseDepth1st {state t leaf nonTerm} {
    upvar #0 $state var

    set nullable {}
    set firstpos {}
    set lastpos {}

    switch -- [lindex [lindex $t 1] 0] {
        :seq -
        :choice {
            set rep [lindex $t 0]
            set cs [lindex [lindex $t 1] 0]

            foreach child [lrange [lindex $t 1] 1 end] {
                foreach {childNullable childFirstpos childLastpos} \
                        [TraverseDepth1st $state $child $leaf $nonTerm] break
                lappend nullable $childNullable
                lappend firstpos $childFirstpos
                lappend lastpos  $childLastpos
            }

            eval $nonTerm
        }
        default {
            incr var(number)
            set rep [lindex [lindex $t 0] 0]
            set name [lindex [lindex $t 1] 0]
            eval $leaf
        }
    }

    return [list $nullable $firstpos $lastpos]
}

# sgml::firstpos --
#
#       Computes the firstpos function for a nonterminal node.
#
# Arguments:
#       cs              node type, choice or sequence
#       firstpos        firstpos functions for the subtree
#       nullable        nullable functions for the subtree
#
# Results:
#       firstpos function for this node is returned.

proc sgml::firstpos {cs firstpos nullable} {
    switch -- $cs {
        :seq {
            set result [lindex [lindex $firstpos 0] 1]
            for {set i 0} {$i < [llength $nullable]} {incr i} {
                if {[lindex [lindex $nullable $i] 1]} {
                    eval lappend result [lindex [lindex $firstpos [expr $i + 1]] 1]
                } else {
                    break
                }
            }
        }
        :choice {
            foreach child $firstpos {
                eval lappend result $child
            }
        }
    }

    return [list $firstpos [makeSet $result]]
}

# sgml::lastpos --
#
#       Computes the lastpos function for a nonterminal node.
#       Same as firstpos, only logic is reversed
#
# Arguments:
#       cs              node type, choice or sequence
#       lastpos         lastpos functions for the subtree
#       nullable        nullable functions forthe subtree
#
# Results:
#       lastpos function for this node is returned.

proc sgml::lastpos {cs lastpos nullable} {
    switch -- $cs {
        :seq {
            set result [lindex [lindex $lastpos end] 1]
            for {set i [expr [llength $nullable] - 1]} {$i >= 0} {incr i -1} {
                if {[lindex [lindex $nullable $i] 1]} {
                    eval lappend result [lindex [lindex $lastpos $i] 1]
                } else {
                    break
                }
            }
        }
        :choice {
            foreach child $lastpos {
                eval lappend result $child
            }
        }
    }

    return [list $lastpos [makeSet $result]]
}

# sgml::makeSet --
#
#       Turn a list into a set, ie. remove duplicates.
#
# Arguments:
#       s       a list
#
# Results:
#       A set is returned, which is a list with duplicates removed.

proc sgml::makeSet s {
    foreach r $s {
        if {[llength $r]} {
            set unique($r) {}
        }
    }
    return [array names unique]
}

# sgml::nullable --
#
#       Compute the nullable function for a node.
#
# Arguments:
#       nodeType        leaf or nonterminal
#       rep             repetition applying to this node
#       name            leaf node: symbol for this node, nonterm node: choice or seq node
#       subtree         nonterm node: nullable functions for the subtree
#
# Results:
#       Returns nullable function for this branch of the tree.

proc sgml::nullable {nodeType rep name {subtree {}}} {
    switch -glob -- $rep:$nodeType {
        :leaf -
        +:leaf {
            return [list {} 0]
        }
        \\*:leaf -
        \\?:leaf {
            return [list {} 1]
        }
        \\*:nonterm -
        \\?:nonterm {
            return [list $subtree 1]
        }
        :nonterm -
        +:nonterm {
            switch -- $name {
                :choice {
                    set result 0
                    foreach child $subtree {
                        set result [expr $result || [lindex $child 1]]
                    }
                }
                :seq {
                    set result 1
                    foreach child $subtree {
                        set result [expr $result && [lindex $child 1]]
                    }
                }
            }
            return [list $subtree $result]
        }
    }
}

# These regular expressions are defined here once for better performance

namespace eval sgml {
    variable Wsp

    # Watch out for case-sensitivity

    set attlist_exp [cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*(#REQUIRED|#IMPLIED)
    set attlist_enum_exp [cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*\\(([cl ^)]*)\\)[cl $Wsp]*("([cl ^")])")? ;# "
    set attlist_fixed_exp [cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*(#FIXED)[cl $Wsp]*([cl ^$Wsp]+)

    set param_entity_exp [cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*([cl ^"$Wsp]*)[cl $Wsp]*"([cl ^"]*)"

    set notation_exp [cl $Wsp]*([cl ^$Wsp]+)[cl $Wsp]*(.*)

}

# sgml::DTD:ATTLIST --
#
#       <!ATTLIST ...> defines an attribute list.
#
# Arguments:
#       id      Element an attribute list is being defined for.
#       value   data from the PI.
#
# Results:
#       Attribute list variables are modified.

proc sgml::DTD:ATTLIST {id value} {
    variable attlist_exp
    variable attlist_enum_exp
    variable attlist_fixed_exp
    dbgputs DTD_parse [list DTD:ATTLIST $id $value]
    upvar opts state
    upvar attributes am

    if {[info exists am($id)]} {
        eval $state(-errorcommand) attlist [list "attribute list for element \"$id\" already declared"]
    } else {
        # Parse the attribute list.  If it were regular, could just use foreach,
        # but some attributes may have values.
        regsub -all {([][$\\])} $value {\\\1} value
        regsub -all $attlist_exp $value {[DTDAttribute {\1} {\2} {\3}]} value
        regsub -all $attlist_enum_exp $value {[DTDAttribute {\1} {\2} {\3}]} value
        regsub -all $attlist_fixed_exp $value {[DTDAttribute {\1} {\2} {\3} {\4}]} value
        subst $value
        set am($id) [array get attlist]
    }
}

# sgml::DTDAttribute --
#
#       Parse definition of a single attribute.
#
# Arguments:
#       name    attribute name
#       type    type of this attribute
#       default default value of the attribute
#       value   other information

proc sgml::DTDAttribute {name type default {value {}}} {
    upvar attlist al
    # This needs further work
    set al($name) [list $default $value]
}

# sgml::DTD:ENTITY --
#
#       <!ENTITY ...> PI
#
# Arguments:
#       id      identifier for the entity
#       value   data
#
# Results:
#       Modifies the caller's entities array variable

proc sgml::DTD:ENTITY {id value} {
    variable param_entity_exp
    dbgputs DTD_parse [list DTD:ENTITY $id $value]
    upvar opts state
    upvar entities ents

    if {[string compare % $id]} {
        # Entity declaration
        if {[info exists ents($id)]} {
            eval $state(-errorcommand) entity [list "entity \"$id\" already declared"]
        } else {
            if {![regexp {"([^"]*)"} $value x entvalue] && ![regexp {'([^']*)'} $value x entvalue]} {
                eval $state(-errorcommand) entityvalue [list "entity value \"$value\" not correctly specified"]
            } ;# "
            set ents($id) $entvalue
        }
    } else {
        # Parameter entity declaration
        switch -glob [regexp $param_entity_exp $value x name scheme data],[string compare {} $scheme] {
            0,* {
                eval $state(-errorcommand) entityvalue [list "parameter entity \"$value\" not correctly specified"]
            }
            *,0 {
                # SYSTEM or PUBLIC declaration
            }
            default {
                set ents($id) $data
            }
        }
    }
}

# sgml::DTD:NOTATION --

proc sgml::DTD:NOTATION {id value} {
    variable notation_exp
    upvar opts state

    if {[regexp $notation_exp $value x scheme data] == 2} {
    } else {
        eval $state(-errorcommand) notationvalue [list "notation value \"$value\" incorrectly specified"]
    }
}

### Utility procedures

# sgml::noop --
#
#       A do-nothing proc
#
# Arguments:
#       args    arguments
#
# Results:
#       Nothing.

proc sgml::noop args {
    return 0
}

# sgml::identity --
#
#       Identity function.
#
# Arguments:
#       a       arbitrary argument
#
# Results:
#       $a

proc sgml::identity a {
    return $a
}

# sgml::Error --
#
#       Throw an error
#
# Arguments:
#       args    arguments
#
# Results:
#       Error return condition.

proc sgml::Error args {
    uplevel return -code error [list $args]
}

### Following procedures are based on html_library

# sgml::zapWhite --
#
#       Convert multiple white space into a single space.
#
# Arguments:
#       data    plain text
#
# Results:
#       As above

proc sgml::zapWhite data {
    regsub -all "\[ \t\r\n\]+" $data { } data
    return $data
}

proc sgml::Boolean value {
    regsub {1|true|yes|on} $value 1 value
    regsub {0|false|no|off} $value 0 value
    return $value
}

proc sgml::dbgputs {where text} {
    variable dbg

    catch {if {$dbg} {puts stdout "DBG: $where ($text)"}}
}


# xml.tcl --
#
#       This file provides XML services.
#       These services include a XML document instance and DTD parser,
#       as well as support for generating XML.
#
# Copyright (c) 1998,1999 Zveno Pty Ltd
# http://www.zveno.com/
#
# Zveno makes this software and all associated data and documentation
# ('Software') available free of charge for non-commercial purposes only. You
# may make copies of the Software but you must include all of this notice on
# any copy.
#
# The Software was developed for research purposes and Zveno does not warrant
# that it is error free or fit for any purpose.  Zveno disclaims any
# liability for all claims, expenses, losses, damages and costs any user may
# incur as a result of using, copying or modifying the Software.
#
# Copyright (c) 1997 Australian National University (ANU).
#
# ANU makes this software and all associated data and documentation
# ('Software') available free of charge for non-commercial purposes only. You
# may make copies of the Software but you must include all of this notice on
# any copy.
#
# The Software was developed for research purposes and ANU does not warrant
# that it is error free or fit for any purpose.  ANU disclaims any
# liability for all claims, expenses, losses, damages and costs any user may
# incur as a result of using, copying or modifying the Software.
#
# $Id$

package provide xml 1.8

# package require sgml 1.6

namespace eval xml {

    # Procedures for parsing XML documents
    namespace export parser
    # Procedures for parsing XML DTDs
    namespace export DTDparser

    # Counter for creating unique parser objects
    variable ParserCounter 0

    # Convenience routine
    proc cl x {
        return "\[$x\]"
    }

    # Define various regular expressions
    # white space
    variable Wsp " \t\r\n"
    variable noWsp [cl ^$Wsp]

    # Various XML names and tokens

    # BUG: NameChar does not include CombiningChar or Extender
    variable NameChar [cl -a-zA-Z0-9._:]
    variable Name [cl a-zA-Z_:]$NameChar*
    variable Nmtoken $NameChar+

    # Tokenising expressions

    variable tokExpr <(/?)([cl ^$Wsp>]+)([cl $Wsp]*[cl ^>]*)>
    variable substExpr "\}\n{\\2} {\\1} {} {\\3} \{"

    # table of predefined entities

    variable EntityPredef
    array set EntityPredef {
        lt <   gt >   amp &   quot \"   apos '
    }

}


# xml::parser --
#
#       Creates XML parser object.
#
# Arguments:
#       args    Unique name for parser object
#               plus option/value pairs
#
# Recognised Options:
#       -final                  Indicates end of document data
#       -elementstartcommand    Called when an element starts
#       -elementendcommand      Called when an element ends
#       -characterdatacommand   Called when character data occurs
#       -processinginstructioncommand   Called when a PI occurs
#       -externalentityrefcommand       Called for an external entity reference
#
#       (Not compatible with expat)
#       -xmldeclcommand         Called when the XML declaration occurs
#       -doctypecommand         Called when the document type declaration occurs
#
#       -errorcommand           Script to evaluate for a fatal error
#       -warningcommand         Script to evaluate for a reportable warning
#       -statevariable          global state variable
#       -reportempty            whether to provide empty element indication
#
# Results:
#       The state variable is initialised.

proc xml::parser {args} {
    variable ParserCounter

    if {[llength $args] > 0} {
        set name [lindex $args 0]
        set args [lreplace $args 0 0]
    } else {
        set name parser[incr ParserCounter]
    }

    if {[info command [namespace current]::$name] != {}} {
        return -code error "unable to create parser object \"[namespace current]::$name\" command"
    }

    # Initialise state variable and object command
    upvar \#0 [namespace current]::$name parser
    set sgml_ns [namespace parent]::sgml
    array set parser [list name $name                   \
        -final 1                                        \
        -elementstartcommand ${sgml_ns}::noop           \
        -elementendcommand ${sgml_ns}::noop             \
        -characterdatacommand ${sgml_ns}::noop          \
        -processinginstructioncommand ${sgml_ns}::noop  \
        -externalentityrefcommand ${sgml_ns}::noop      \
        -xmldeclcommand ${sgml_ns}::noop                \
        -doctypecommand ${sgml_ns}::noop                \
        -warningcommand ${sgml_ns}::noop                \
        -statevariable [namespace current]::$name       \
        -reportempty 0                                  \
        internaldtd {}                                  \
    ]

    proc [namespace current]::$name {method args} \
        "eval ParseCommand $name \$method \$args"

    eval ParseCommand [list $name] configure $args

    return [namespace current]::$name
}

# xml::ParseCommand --
#
#       Handles parse object command invocations
#
# Valid Methods:
#       cget
#       configure
#       parse
#       reset
#
# Arguments:
#       parser  parser object
#       method  minor command
#       args    other arguments
#
# Results:
#       Depends on method

proc xml::ParseCommand {parser method args} {
    upvar \#0 [namespace current]::$parser state

    switch -- $method {
        cget {
            return $state([lindex $args 0])
        }
        configure {
            foreach {opt value} $args {
                set state($opt) $value
            }
        }
        parse {
            ParseCommand_parse $parser [lindex $args 0]
        }
        reset {
            if {[llength $args]} {
                return -code error "too many arguments"
            }
            ParseCommand_reset $parser
        }
        default {
            return -code error "unknown method \"$method\""
        }
    }

    return {}
}

# xml::ParseCommand_parse --
#
#       Parses document instance data
#
# Arguments:
#       object  parser object
#       xml     data
#
# Results:
#       Callbacks are invoked, if any are defined

proc xml::ParseCommand_parse {object xml} {
    upvar \#0 [namespace current]::$object parser
    variable Wsp
    variable tokExpr
    variable substExpr

    set parent [namespace parent]
    if {![string compare :: $parent]} {
        set parent {}
    }

    set tokenised [lrange \
            [${parent}::sgml::tokenise $xml \
            $tokExpr \
            $substExpr \
            -internaldtdvariable [namespace current]::${object}(internaldtd)] \
        5 end]

    eval ${parent}::sgml::parseEvent \
        [list $tokenised \
            -emptyelement [namespace code ParseEmpty] \
            -parseattributelistcommand [namespace code ParseAttrs]] \
        [array get parser -*command] \
        [array get parser -entityvariable] \
        [array get parser -reportempty] \
        -normalize 0 \
        -internaldtd [list $parser(internaldtd)]

    return {}
}

# xml::ParseEmpty --
#
#       Used by parser to determine whether an element is empty.
#       This should be dead easy in XML.  The only complication is
#       that the RE above can't catch the trailing slash, so we have
#       to dig it out of the tag name or attribute list.
#
#       Tcl 8.1 REs should fix this.
#
# Arguments:
#       tag     element name
#       attr    attribute list (raw)
#       e       End tag delimiter.
#
# Results:
#       "/" if the trailing slash is found.  Optionally, return a list
#       containing new values for the tag name and/or attribute list.

proc xml::ParseEmpty {tag attr e} {

    if {[string match */ [string trimright $tag]] && \
            ![string length $attr]} {
        regsub {/$} $tag {} tag
        return [list / $tag $attr]
    } elseif {[string match */ [string trimright $attr]]} {
        regsub {/$} [string trimright $attr] {} attr
        return [list / $tag $attr]
    } else {
        return {}
    }

}

# xml::ParseAttrs --
#
#       Parse element attributes.
#
# There are two forms for name-value pairs:
#
#       name="value"
#       name='value'
#
# Watch out for the trailing slash on empty elements.
#
# Arguments:
#       attrs   attribute string given in a tag
#
# Results:
#       Returns a Tcl list representing the name-value pairs in the
#       attribute string

proc xml::ParseAttrs attrs {
    variable Wsp
    variable Name

    # First check whether there's any work to do
    if {![string compare {} [string trim $attrs]]} {
        return {}
    }

    # Strip the trailing slash on empty elements
    regsub [format {/[%s]*$} " \t\n\r"] $attrs {} atList

    set mode name
    set result {}
    foreach component [split $atList =] {
        switch $mode {
            name {
                set component [string trim $component]
                if {[regexp $Name $component]} {
                    lappend result $component
                } else {
                    return -code error "invalid attribute name \"$component\""
                }
                set mode value:start
            }
            value:start {
                set component [string trimleft $component]
                set delimiter [string index $component 0]
                set value {}
                switch -- $delimiter {
                    \" -
                    ' {
                        if {[regexp [format {%s([^%s]*)%s(.*)} $delimiter $delimiter $delimiter] $component discard value remainder]} {
                            lappend result $value
                            set remainder [string trim $remainder]
                            if {[string length $remainder]} {
                                if {[regexp $Name $remainder]} {
                                    lappend result $remainder
                                    set mode value:start
                                } else {
                                    return -code error "invalid attribute name \"$remainder\""
                                }
                            } else {
                                set mode end
                            }
                        } else {
                            set value [string range $component 1 end]
                            set mode value:continue
                        }
                    }
                    default {
                        return -code error "invalid value for attribute \"[lindex $result end]\""
                    }
                }
            }
            value:continue {
                if {[regexp [format {([^%s]*)%s(.*)} $delimiter $delimiter] $component discard valuepart remainder]} {
                    append value = $valuepart
                    lappend result $value
                    set remainder [string trim $remainder]
                    if {[string length $remainder]} {
                        if {[regexp $Name $remainder]} {
                            lappend result $remainder
                            set mode value:start
                        } else {
                            return -code error "invalid attribute name \"$remainder\""
                        }
                    } else {
                        set mode end
                    }
                } else {
                    append value = $component
                }
            }
            end {
                return -code error "unexpected data found after end of attribute list"
            }
        }
    }

    switch $mode {
        name -
        end {
            # This is normal
        }
        default {
            return -code error "unexpected end of attribute list"
        }
    }

    return $result
}

proc xml::OLDParseAttrs {attrs} {
    variable Wsp
    variable Name

    # First check whether there's any work to do
    if {![string compare {} [string trim $attrs]]} {
        return {}
    }

    # Strip the trailing slash on empty elements
    regsub [format {/[%s]*$} " \t\n\r"] $attrs {} atList

    # Protect Tcl special characters
    #regsub -all {([[\$\\])} $atList {\\\1} atList
    regsub -all & $atList {\&amp;} atList
    regsub -all {\[} $atList {\&ob;} atList
    regsub -all {\]} $atList {\&cb;} atlist
    # NB. sgml package delivers braces and backslashes quoted
    regsub -all {\\\{} $atList {\&oc;} atList
    regsub -all {\\\}} $atList {\&cc;} atlist
    regsub -all {\$} $atList {\&dollar;} atList
    regsub -all {\\\\} $atList {\&bs;} atList

    regsub -all [format {(%s)[%s]*=[%s]*"([^"]*)"} $Name $Wsp $Wsp] \
            $atList {[set parsed(\1) {\2}; set dummy {}] } atList       ;# "
    regsub -all [format {(%s)[%s]*=[%s]*'([^']*)'} $Name $Wsp $Wsp] \
            $atList {[set parsed(\1) {\2}; set dummy {}] } atList

    set leftovers [subst $atList]

    if {[string length [string trim $leftovers]]} {
        return -code error "syntax error in attribute list \"$attrs\""
    }

    return [ParseAttrs:Deprotect [array get parsed]]
}

# xml::ParseAttrs:Deprotect --
#
#       Reverse map Tcl special characters previously protected
#
# Arguments:
#       attrs   attribute list
#
# Results:
#       Characters substituted

proc xml::ParseAttrs:Deprotect attrs {

    regsub -all &amp\; $attrs \\& attrs
    regsub -all &ob\; $attrs \[ attrs
    regsub -all &cb\; $attrs \] attrs
    regsub -all &oc\; $attrs \{ attrs
    regsub -all &cc\; $attrs \} attrs
    regsub -all &dollar\; $attrs \$ attrs
    regsub -all &bs\; $attrs \\\\ attrs

    return $attrs

}

# xml::ParseCommand_reset --
#
#       Initialize parser data
#
# Arguments:
#       object  parser object
#
# Results:
#       Parser data structure initialised

proc xml::ParseCommand_reset object {
    upvar \#0 [namespace current]::$object parser

    array set parser [list \
            -final 1            \
            internaldtd {}      \
    ]
}

# xml::noop --
#
# A do-nothing proc

proc xml::noop args {}

### Following procedures are based on html_library

# xml::zapWhite --
#
#       Convert multiple white space into a single space.
#
# Arguments:
#       data    plain text
#
# Results:
#       As above

proc xml::zapWhite data {
    regsub -all "\[ \t\r\n\]+" $data { } data
    return $data
}

#
# DTD parser for XML is wholly contained within the sgml.tcl package
#

# xml::parseDTD --
#
#       Entry point to the XML DTD parser.
#
# Arguments:
#       dtd     XML data defining the DTD to be parsed
#       args    configuration options
#
# Results:
#       Returns a three element list, first element is the content model
#       for each element, second element are the attribute lists of the
#       elements and the third element is the entity map.

proc xml::parseDTD {dtd args} {
    return [eval [expr {[namespace parent] == {::} ? {} : [namespace parent]}]::sgml::parseDTD [list $dtd] $args]
}


#
# here ends TclXML 1.1.1
#


#
# here begins textutil fragment
#

if {[catch { package require textutil }]} {
namespace eval textutil {
    namespace export strRepeat

    variable HaveStrRepeat [ expr {![ catch { string repeat a 1 } ]} ]

    if {0} {
        # Problems with the deactivated code:
        # - Linear in 'num'.
        # - Tests for 'string repeat' in every call!
        #   (Ok, just the variable, still a test every call)
        # - Fails for 'num == 0' because of undefined 'str'.

        proc StrRepeat { char num } {
            variable HaveStrRepeat
            if { $HaveStrRepeat == 0 } then {
                for { set i 0 } { $i < $num } { incr i } {
                    append str $char
                }
            } else {
                set str [ string repeat $char $num ]
            }
            return $str
        }
    }

}

if {$::textutil::HaveStrRepeat} {
    proc ::textutil::strRepeat {char num} {
        return [string repeat $char $num]
    }
} else {
    proc ::textutil::strRepeat {char num} {
        if {$num <= 0} {
            # No replication required
            return ""
        } elseif {$num == 1} {
            # Quick exit for recursion
            return $char
        } elseif {$num == 2} {
            # Another quick exit for recursion
            return $char$char
        } elseif {0 == ($num % 2)} {
            # Halving the problem results in O (log n) complexity.
            set result [strRepeat $char [expr {$num / 2}]]
            return "$result$result"
        } else {
            # Uneven length, reduce problem by one
            return "$char[strRepeat $char [incr num -1]]"
        }
    }
}


if {0} {
source [ file join [ file dirname [ info script ] ] adjust.tcl ]
source [ file join [ file dirname [ info script ] ] split.tcl ]
source [ file join [ file dirname [ info script ] ] tabify.tcl ]
source [ file join [ file dirname [ info script ] ] trim.tcl ]
}
namespace eval ::textutil {

    namespace eval adjust {

        variable StrRepeat [ namespace parent ]::strRepeat
        variable Justify  left
        variable Length   72
        variable FullLine 0
        variable StrictLength 0

        namespace export adjust

        # This will be redefined later. We need it just to let
        # a chance for the next import subcommand to work
        #
        proc adjust { text args } { }

    }

    namespace import -force adjust::adjust
    namespace export adjust

}

#########################################################################

proc ::textutil::adjust::adjust { text args } {

    if { [ string length [ string trim $text ] ] == 0 } then {
        return ""
    }

    Configure $args
    Adjust text newtext

    return $newtext
}

proc ::textutil::adjust::Configure { args } {
    variable Justify   left
    variable Length    72
    variable FullLine  0
    variable StrictLength 0

    set args [ lindex $args 0 ]
    foreach { option value } $args {
        switch -exact -- $option {
            -full {
                if { ![ StringIsBoolean -strict $value ] } then {
                    error "expected boolean but got \"$value\""
                }
                set FullLine [ StringIsTrue $value ]
            }
            -justify {
                set lovalue [ string tolower $value ]
                switch -exact -- $lovalue {
                    left -
                    right -
                    center -
                    plain {
                        set Justify $lovalue
                    }
                    default {
                        error "bad value \"$value\": should be center, left, plain or right"
                    }
                }
            }
            -length {
                if { ![ StringIsInteger $value ] } then {
                    error "expected positive integer but got \"$value\""
                }
                if { $value < 1 } then {
                    error "expected positive integer but got \"$value\""
                }
                set Length $value
            }
            -strictlength {
                if { ![ StringIsBoolean -strict $value ] } then {
                    error "expected boolean but got \"$value\""
                }
                set StrictLength [ StringIsTrue $value ]
            }
            default {
                error "bad option \"$option\": must be -full, -justify, -length, or -strictlength"
            }
        }
    }

    return ""
}

proc ::textutil::adjust::StringIsBoolean { arg value } {
    switch -- [string tolower $value] {
        0 - false - no - off { return 1 }
        default { return [StringIsTrue $value] }
    }
}

proc ::textutil::adjust::StringIsTrue { value } {
    switch -- [string tolower $value] {
        1 - true - yes - on { return 1 }
        default { return 0 }
    }
}

proc ::textutil::adjust::StringIsInteger { value } {
    if {[catch { incr value }]} {
        return 0
    }
    return 1
}

proc ::textutil::adjust::Adjust { varOrigName varNewName } {
    variable Length
    variable StrictLength

    upvar $varOrigName orig
    upvar $varNewName  text

    regsub -all -- "(\n)|(\t)"     $orig  " "  text
    regsub -all -- " +"            $text  " "  text
    regsub -all -- "(^ *)|( *\$)"  $text  ""   text

    set ltext [ split $text ]

    if { $StrictLength } then {

        # Limit the length of a line to $Length. If any single
        # word is long than $Length, then split the word into multiple
        # words.

        set i 0
        foreach tmpWord $ltext {
            if { [ string length $tmpWord ] > $Length } then {

                # Since the word is longer than the line length,
                # remove the word from the list of words.  Then
                # we will insert several words that are less than
                # or equal to the line length in place of this word.

                set ltext [ lreplace $ltext $i $i ]
                incr i -1
                set j 0

                # Insert a series of shorter words in place of the
                # one word that was too long.

                while { $j < [ string length $tmpWord ] } {

                    # Calculate the end of the string range for this word.

                    if { [ expr { [string length $tmpWord ] - $j } ] > $Length } then {
                        set end [ expr { $j + $Length - 1} ]
                    } else {
                        set end [ string length $tmpWord ]
                    }

                    set ltext [ linsert $ltext [ expr {$i + 1} ] [ string range $tmpWord $j $end ] ]
                    incr i
                    incr j [ expr { $end - $j + 1 } ]
                }
            }
            incr i
        }
    }

    set line [ lindex $ltext 0 ]
    set pos [ string length $line ]
    set text ""
    set numline 0
    set numword 1
    set words(0) 1
    set words(1) [ list $pos $line ]

    foreach word [ lrange $ltext 1 end ] {
        set size [ string length $word ]
        if { ( $pos + $size ) < $Length } then {
            append line " $word"
            incr numword
            incr words(0)
            set words($numword) [ list $size $word ]
            incr pos
            incr pos $size
        } else {
            if { [ string length $text ] != 0 } then {
                append text "\n"
            }
            append text [ Justification $line [ incr numline ] words ]
            set line "$word"
            set pos $size
            catch { unset words }
            set numword 1
            set words(0) 1
            set words(1) [ list $size $word ]
        }
    }
    if { [ string length $text ] != 0 } then {
        append text "\n"
    }
    append text [ Justification $line end words ]

    return $text
}

proc ::textutil::adjust::Justification { line index arrayName } {
    variable Justify
    variable Length
    variable FullLine
    variable StrRepeat

    upvar $arrayName words

    set len [ string length $line ]
    if { $Length == $len } then {
        return $line
    }

    # Special case:
    # for the last line, and if the justification is set to 'plain'
    # the real justification is 'left' if the length of the line
    # is less than 90% (rounded) of the max length allowed. This is
    # to avoid expansion of this line when it is too small: without
    # it, the added spaces will 'unbeautify' the result.
    #

    set justify $Justify
    if { ( "$index" == "end" ) && \
             ( "$Justify" == "plain" ) && \
             ( $len < round($Length * 0.90) ) } then {
        set justify left
    }

    # For a left justification, nothing to do, but to
    # add some spaces at the end of the line if requested
    #

    if { "$justify" == "left" } then {
        set jus ""
        if { $FullLine } then {
            set jus [ $StrRepeat " " [ expr { $Length - $len } ] ]
        }
        return "${line}${jus}"
    }

    # For a right justification, just add enough spaces
    # at the beginning of the line
    #

    if { "$justify" == "right" } then {
        set jus [ $StrRepeat " " [ expr { $Length - $len } ] ]
        return "${jus}${line}"
    }

    # For a center justification, add half of the needed spaces
    # at the beginning of the line, and the rest at the end
    # only if needed.

    if { "$justify" == "center" } then {
        set mr [ expr { ( $Length - $len ) / 2 } ]
        set ml [ expr { $Length - $len - $mr } ]
        set jusl [ $StrRepeat " " $ml ]
        set jusr [ $StrRepeat " " $mr ]
        if { $FullLine } then {
            return "${jusl}${line}${jusr}"
        } else {
            return "${jusl}${line}"
        }
    }

    # For a plain justiciation, it's a little bit complex:
    # if some spaces are missing, then
    # sort the list of words in the current line by
    # decreasing size
    # foreach word, add one space before it, except if
    # it's the first word, until enough spaces are added
    # then rebuild the line
    #

    if { "$justify" == "plain" } then {
        set miss [ expr { $Length - [ string length $line ] } ]
        if { $miss == 0 } then {
            return "${line}"
        }

        for { set i 1 } { $i < $words(0) } { incr i } {
            lappend list [ eval list $i $words($i) 1 ]
        }
        lappend list [ eval list $i $words($words(0)) 0 ]
        set list [ SortList $list decreasing 1 ]

        set i 0
        while { $miss > 0 } {
            set elem [ lindex $list $i ]
            set nb [ lindex $elem 3 ]
            incr nb
            set elem [ lreplace $elem 3 3 $nb ]
            set list [ lreplace $list $i $i $elem ]
            incr miss -1
            incr i
            if { $i == $words(0) } then {
                set i 0
            }
        }
        set list [ SortList $list increasing 0 ]
        set line ""
        foreach elem $list {
            set jus [ $StrRepeat " " [ lindex $elem 3 ] ]
            set word [ lindex $elem 2 ]
            if { [ lindex $elem 0 ] == $words(0) } then {
                append line "${jus}${word}"
            } else {
                append line "${word}${jus}"
            }
        }

        return "${line}"
    }

    error "Illegal justification key \"$justify\""
}

proc ::textutil::adjust::SortList { list dir index } {

    if { [ catch { lsort -integer -$dir -index $index $list } sl ] != 0 } then {
        error "$sl"
    }

    return $sl
}
}

#
# here ends textutil fragment
#



#
# top-level parsing
#


global parser
if {![info exists parser]} {
    set parser ""
}

proc xml2rfc {input {output ""} {remote ""}} {
    global prog
    global errorCode errorInfo
    global parser
    global passno
    global passmax
    global errorP
    global ifile mode ofile
    global out_fd
    global remoteP

    if {![string compare [file extension $input] ""]} {
        append input .xml
    }

    set in_fd [open $input { RDONLY }]
    catch { fconfigure $in_fd -encoding binary }
    set inputD [file dirname [set ifile $input]]

    if {![string compare $output ""]} {
        set output [file rootname $input].txt
    }
    if {[string compare $remote ""]} {
        set ofile $remote
        set remoteP 1
    } else {
        set ofile $output
        set remoteP 0
    }
    set ofile [file rootname [file tail $ofile]]

    if {![string compare $input $output]} {
        error "input and output files must be different"
    }

    if {[file exists [set file [file join $inputD .$prog.rc]]]} {
        source $file
    }

    switch -- [set mode [string range [file extension $output] 1 end]] {
        html -
        nr   -
        txt  {}

        xml {
            set out_fd [open $output { WRONLY CREAT TRUNC }]
            catch { fconfigure $out_fd -encoding utf-8 }

            puts -nonewline $out_fd [prexml [read $in_fd]]

            catch { close $out_fd }
            catch { close $in_fd }

            return
        }

        default {
            catch { close $in_fd }
            error "unsupported output type: $mode"
        }
    }

    set code [catch {
        if {![string compare $parser ""]} {
            global emptyA

            set parser [xml::parser]
            array set emptyA {}

            $parser configure \
                        -elementstartcommand          { begin               } \
                        -elementendcommand            { end                 } \
                        -characterdatacommand         { pcdata              } \
                        -processinginstructioncommand { pi                  } \
                        -xmldeclcommand               { xmldecl             } \
                        -doctypecommand               { doctype             } \
                        -entityreferencecommand       ""                      \
                        -errorcommand                 { unexpected error    } \
                        -warningcommand               { unexpected warning  } \
                        -entityvariable               emptyA                  \
                        -final                        1                       \
                        -reportempty                  0
        }

        set data [prexml [read $in_fd]]

        catch { close $in_fd }

        set errorP 0
        set passmax 2
        set out_fd ""
        for {set passno 1} {$passno <= $passmax} {incr passno} {
            if {$passno == 2} {
                set out_fd [open $output { WRONLY CREAT TRUNC }]
                catch { fconfigure $out_fd -encoding utf-8 }
            }
            pass start
            $parser parse $data
            pass end
            if {$errorP} {
                break
            }
        }
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    catch { close $out_fd }

    if {$code == 1} {
        set result [around2fl $result]

        catch {
            global stack
            global guiP

            if {[set i [llength $stack]] > 0} {
                set text \
  "Context (format:  \"file_basename:line_in_file:#elem_num:<elem ...>\"):"
                while {$i > 0} {
                    set frame [lindex $stack [incr i -1]]
                    catch { unset attrs }
                    array set attrs [list av ""]
                    array set attrs [lrange $frame 1 end]
                    append text "\n    "
                    append text [linefile::get_file $attrs(fnum) 1]:
                    append text $attrs(line):#$attrs(elemN):
                    append text "<[lindex $frame 0]"
                    foreach {k v} $attrs(av) {
                        regsub -all {"} $v {\&quot;} v
                        append text " $k=\"$v\""
                    }
                    append text ">"
                }
                append result "\n\n$text"
                if {$guiP < 0} {
                    append result "\n$einfo"
                }
            }
        }
    }

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc xml2txt {input} {
    xml2rfc $input [file rootname $input].txt
}

proc xml2html {input} {
    xml2rfc $input [file rootname $input].html
}

proc xml2nroff {input} {
    return [xml2rfc $input [file rootname $input].nr]
###
    puts stderr "making xml->txt"
    xml2rfc $input [file rootname $input].txt
    file rename -force [file rootname $input].txt  [file rootname $input].orig

    puts stderr "making xml->rf"
    xml2rfc $input [file rootname $input].nr

    puts stderr "making rf->txt"
    exec nroff -ms < [file rootname $input].nr \
       | /usr/users/mrose/docs/fix.pl \
       | sed -e 1,3d \
       > [file rootname $input].txt
}

proc xml2ref {input output {formats {}} {item ""}} {
    global prog
    global errorCode errorInfo

    if {![string compare $input $output]} {
        error "input and output files must be different"
    }

    if {[file exists [set file [file join [set inputD [file dirname $input]] \
                                          .$prog.rc]]]} {
        source $file
    }

    set refT [ref::init]
    if {[set code [catch { ref::transform $refT $input $formats } result]]} {
        set ecode $errorCode
        set einfo $errorInfo

        catch { ref::fin $refT }

        return -code $code -errorinfo $einfo -errorcode $ecode $result
    }
    ref::fin $refT

    array set ref $result

    set out_fd [open $output { WRONLY CREAT TRUNC }]
    catch { fconfigure $out_fd -encoding utf-8 }

    set code [catch {
        puts -nonewline $out_fd $ref(body)
        flush $out_fd
    } result]
    set ecode $errorCode
    set einfo $errorInfo

    catch { close $out_fd }

    if {($code == 0) \
            && ([string compare $item ""]) \
            && ([string compare $ref(info) ""])} {
        set out_fd [open $item { WRONLY CREAT TRUNC }]
        catch { fconfigure $out_fd -encoding utf-8 }

        set code [catch {
            puts -nonewline $out_fd $ref(info)
            flush $out_fd
        } result]
        set ecode $errorCode
        set einfo $errorInfo

        catch { close $out_fd }

#       catch { file mtime $item $ref(mtime) }
    }

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

global httpP
set httpP 0

global xml_library_path
set xml_library_path {.}

proc prexml {stream} {
    global env tcl_platform
    global extentities extfiles exturis
    global httpP
    global xml_library_path
    global ifile

    if {[catch { set xml_library_path $env(XML_LIBRARY) }]} {
        set xml_library_path [list [file dirname $ifile]]
    }
    switch -- $tcl_platform(platform) {
        windows {
            set c ";"
        }

        default {
            set c ":"
        }
    }
    set xml_library_path [split $xml_library_path $c]

    set stream [prexml_cdata $stream]
    linefile::new_file $ifile

    array set intentities {}
    array set extentities {}
    array set extfiles {}
    array set exturis {}

    if {[catch { package require http 2 }]} {
        set httpP 0
    } else {
        set httpP 1
    }

    if {   [regexp -- {^<\?xml[ \t\r\n]} $stream]
        && ([set plen [string first "?>" $stream]] >= 0)} {

        set XMLDecl [string range $stream 0 [incr plen]]
        set stream [string range $stream [incr plen] end]
    } else {
        error "input file \"$ifile\" does not begin with an XML declaration"
    }

    set stream [prexml_convert $XMLDecl $stream $ifile]
    # Now that we are in UTF-8.
    set stream [str_norm_eol $stream \
                [expr   [regexp -- {[ \t\r\n]version="1\.[1-9][0-9]*"} $XMLDecl] \
                     || [regexp -- {[ \t\r\n]version='1\.[1-9][0-9]*'} $XMLDecl]]]

    linefile::init

    set n [num_eols $XMLDecl]
    set XMLDecl "<?xml version=\"1.0\" encoding=\"UTF-8\"[string repeat \n $n]?>"

    return $XMLDecl[prexml_stream $stream $ifile [expr 1 + $n]]
}

proc prexml_convert {XMLDecl stream file} {
    if {   [regexp -- {[ \t\r\n]encoding="([A-Za-z][A-Za-z0-9._-]*)"} $XMLDecl x charset]
        || [regexp -- {[ \t\r\n]encoding='([A-Za-z][A-Za-z0-9._-]*)'} $XMLDecl x charset]} {
            if {![string compare [set enc [cs2enc $charset]] ""]} {
                set enc ascii
                unexpected warning \
  "unknown encoding/charset \"$charset\" in XML declaration of file \"$file\"; trying US-ASCII"
            }
    } else {
        set enc utf-8
    }

    catch { set stream [encoding convertfrom $enc $stream] }
    return $stream
}

proc prexml_cdata {stream} {
    set litN [string length [set litS "<!\[CDATA\["]]
    set litO [string length [set litT "\]\]>"]]

    set data ""
    while {[set x [string first $litS $stream]] >= 0} {
        append data [string range $stream 0 [expr $x-1]]
        set stream [string range $stream [expr $x+$litN] end]
        if {[set x [string first $litT $stream]] < 0} {
            error "missing close to CDATA"
        }
        set y [string range $stream 0 [expr $x-1]]
        regsub -all {&} $y {\&amp;} y
        regsub -all {<} $y {\&lt;}  y
        regsub -all {>} $y {\&gt;}  y
        append data $y
        set stream [string range $stream [expr $x+$litO] end]
    }
    append data $stream

    return $data
}

proc prexml_stream {stream myfile {myline 1} {no_initial_pi 0}} {
    global extentities intentities

    if {[info level] > 32} {
        error "recursion detected in XML preprocessing of included files and entities"
    }

    # Some useful regexp literals.
    set wsp  {[ \t\r\n]}
    set dqev \"(\[^\"\]*)\"
    set sqev \'(\[^\'\]*)\'
    set nme  {([A-Za-z_:][A-Za-z0-9._:-]*)}
    set rem  (.*)

    if {$no_initial_pi} {
        linefile::set_file $myfile
        set data ""
    } else {
        set data [linefile::make_pi $myfile $myline 1]
    }

    # We don't modify stream but scan across it and build data.

    for {
        # Loop Initialization.
        set pending_pi 0
        set new_data ""
        set new_lines 0
        set blank_lines 0
        set includes ""
        set start 0

        # Loop test.
    } {[regexp -indices -start $start -- {<\?rfc|<!ENTITY|&} $stream x]} {

        # Loop continuation.
        prexml_flush_new
        prexml_flush_includes
    } {
        # Loop body.
        set a [lindex $x 0]
        set b [lindex $x 1]
        set m [string range $stream $a $b]
        if {$a > $start} {
            prexml_flush_blank
            prexml_flush_pi
            set initial [string range $stream $start [expr $a - 1]]
            incr myline [num_eols $initial]
            append data $initial
            unset initial
        }
        incr b
        switch -- $m {
            <?rfc {
                if {![regexp -indices -start $b -- {\?>} $stream x]} {
                    error \
  "missing close to $m around input line $myline in \"$myfile\""
                }
                set c [lindex $x 0]
                set pi [string range $stream $b [expr $c - 1]]
                incr new_lines [num_eols $pi]
                set start [incr c 2]
                # We'll normally append new_data later,
                # after $pi has been tweaked.
                if {![regexp -- ^$wsp $pi]} {
                    append new_data $m $pi ?>
                    continue
                }
                prexml_flush_pi
                set kept_pi_dirs 0
                set pil [string length $pi]
                set pi2 $pi
                while {1} {
                    set pi2s [expr $pil - [set pi2l [string length $pi2]]]
                    set l [pi_rfc_next $pi2]
                    set key [lindex $l 0]
                    set val [lindex $l 1]
                    set pi2 [lindex $l 2]
                    if {![string compare $key ""]} {
                        global mode

                        # We may be able to provide a better message later.
                        if {   [string compare $val ""]
                            && ![string compare $mode xml]} {
                            error \
  "stopped preprocessing faulty rfc-PI at \"$val\" around input line $myline in \"$myfile\""
                        }
                        # This makes sure the faulty rfc-PI is kept for later stages.
                        incr kept_pi_dirs
                        break
                    }
                    switch -- $key {
                        include {
                            set pi [streplace $pi $pi2s [expr $pi2l - [string length $pi2] + 1] "" 3]
                            set l [prexml_find_file $val]
                            set file    [lindex $l 0]
                            set include [lindex $l 1]

                            set include [prexml_tweak_include $include $file]
                            if {[string compare $include ""]} {
                                append includes [prexml_stream $include $file 1]
                            }
                        }

                        linefile {
                            incr kept_pi_dirs
                            if {![regexp -- {^([0-9]+)(:(.*))?$} \
                                         $val a b c d]} {
                                # Type of message must not attempt to
                                # supply its own line information which
                                # is not set up at this point.
                                unexpected warning \
  "ignoring invalid rfc-PI linefile-directive value \"$val\" around input line $myline in \"$myfile\""
                                continue
                            }
                            prexml_flush_blank
                            if {[string length $c]} {
                                # May be empty.  User's choice!
                                set new_myfile $d
                            }
                            set new_myline $b
                        }

                        default {
                            incr kept_pi_dirs
                        }
                    }
                }

                # Do this after processing the whole PI so that
                # intermixed error or warning messages are not affected.
                if {[info exists new_myline]} {
                    if {[info exists new_myfile]} {
                        set myfile $new_myfile
                        unset new_myfile
                    }
                    set myline $new_myline
                    unset new_myline
                    set new_lines 0
                }

                if {$kept_pi_dirs} {
                    prexml_flush_blank
                    append new_data $m $pi ?>
                } else {
                    incr blank_lines $new_lines
                    set new_lines 0
                }
            }

            <!ENTITY {
                if {![regexp -indices -start $b -- {>} $stream x]} {
                    error \
  "missing close to $m around input line $myline in \"$myfile\""
                }
                set c [lindex $x 0]
                set entdecl [string range $stream $b [expr $c - 1]]
                set n [num_eols $entdecl]
                set start [incr c]
                if {![regexp -- ^$wsp $entdecl]} {
                    append new_data $m $entdecl >
                    incr new_lines $n
                    continue
                }
                if {$n} {
                    prexml_flush_pi
                }
                # These are _new_ blank lines.
                incr blank_lines $n
                set entdecl [string trimleft $entdecl]

                if {[string first "%" $entdecl] == 0} {
                    set entdecl [string trimleft [string range $entdecl 1 end]]
                }
                if {![regexp -- ^$nme$rem $entdecl x entity entdef]} {
                    error \
  "expecting $m entity-name ... around input line $myline in \"$myfile\""
                }

                if {   [regexp -- ^$wsp+$dqev$rem $entdef x arg1 y]
                    || [regexp -- ^$wsp+$sqev$rem $entdef x arg1 y]} {
                    set file $myfile
                    set include [prexml_cdata $arg1]
                    set line [expr $myline + $new_lines + $blank_lines \
                                   - [num_eols $include$y]]
                    set intentities($entity) [prexml_prep_entity]
                    continue
                }

                if {![regexp -nocase -- \
                             ^$wsp*(SYSTEM|PUBLIC)$rem \
                             $entdef x idtype entid]} {
                    error \
  "expecting $m $entity SYSTEM, PUBLIC, 'def', or \"def\" around input line $myline in \"$myfile\""
                }
                if {   ![regexp -- ^$wsp+$dqev$rem $entid x arg1 arg2]
                    && ![regexp -- ^$wsp+$sqev$rem $entid x arg1 arg2]} {
                    error \
  "expecting literal after $m $entity $idtype around input line $myline in \"$myfile\""
                }
                set idtype [string toupper $idtype]
                set convert_file ""
                switch -- $idtype {
                    SYSTEM {
                        if {[string first "http://" $arg1] == 0} {
                            set l [prexml_find_uri $arg1]
                        } else {
                            set l [prexml_find_file $arg1]
                            set convert_file [lindex $l 0]
                        }
                    }

                    PUBLIC {
                        if {   ![regexp -- ^$wsp+$dqev $arg2 z arg2]
                            && ![regexp -- ^$wsp+$sqev $arg2 z arg2]} {
                            error \
  "expecting literal after $m $entity $idtype around input line $myline in \"$myfile\""
                        }
                        set l [prexml_find_uri $arg2]
                    }
                }
                set file    [lindex $l 0]
                set include [lindex $l 1]
                set include [prexml_tweak_include $include $convert_file]
                set line 1
                set extentities($entity) [prexml_prep_entity]
            }

            & {
                set start $b
                if {![regexp -indices -start $b -- {;} $stream x]} {
                    append new_data &
                    continue
                }
                set c [lindex $x 0]
                set entity [string trim [string range $stream $b [expr $c - 1]]]
                if {[info exists intentities($entity)]} {
                    set l $intentities($entity)
                } elseif {[info exists extentities($entity)]} {
                    set l $extentities($entity)
                } else {
                    append new_data &
                    continue
                }
                set include [lindex $l 2]
                if {[string compare $include ""]} {
                    append includes [linefile::make_pi [lindex $l 0] [lindex $l 1]]
                    append includes $include
                    linefile::set_file [lindex $l 3]
                }
                set start [incr c]
            }
        }
    }

    prexml_flush_blank
    if {$start < [string length $stream]} {
        prexml_flush_pi
        append data [string range $stream $start end]
    }

    return $data
}

# These uplevel procs are all meant for use by prexml_stream.

proc prexml_flush_blank {} {
    uplevel 1 {
        if {$blank_lines} {
            incr myline $blank_lines
            append data <!-- [string repeat "\n" $blank_lines] -->
            set blank_lines 0
        }
    }
}

proc prexml_flush_new {} {
    uplevel 1 {
        if {[string compare $new_data ""]} {
            prexml_flush_blank
            prexml_flush_pi
            incr myline $new_lines
            append data $new_data
            set new_data ""
            set new_lines 0
        }
    }
}

proc prexml_flush_pi {} {
    uplevel 1 {
        if {$pending_pi} {
            prexml_flush_blank
            append data [linefile::make_pi $myfile $myline]
            set pending_pi 0
        }
    }
}

proc prexml_flush_includes {} {
    uplevel 1 {
        if {[string compare $includes ""]} {
            prexml_flush_blank
            append data $includes
            set includes ""
            set pending_pi 1
        }
    }
}

proc prexml_prep_entity {} {
    uplevel 1 {
        set saved_file [linefile::get_file]
        if {[string compare $include ""]} {
            set include [prexml_stream $include $file $line 1]
            set end_file [linefile::get_file]
        } else {
            set end_file $myfile
        }
        linefile::set_file $saved_file
        return [list $file $line $include $end_file]
    }
}

# Back to regular, non-uplevel, support procs for prexml_stream.

proc prexml_find_file {f} {
    global extfiles
    global xml_library_path

    if {[info exists extfiles($f)]} {
        return $extfiles($f)
    }

    set foundP 0
    foreach dir $xml_library_path {
        if {   ![file exists [set file [file join $dir [set fx $f]]]]
            && ![file exists [set file [file join $dir [set fx $f.xml]]]]} {
            continue
        }
        set fd [open $file { RDONLY }]
        catch { fconfigure $fd -encoding binary }
        set content [prexml_cdata [read $fd]]
        catch { close $fd }
        set foundP 1
        break
    }
    if {!$foundP} {
        error "unable to find external file \"$f\" or \"$f.xml\""
    }

    linefile::new_file $fx

    return [set extfiles($f) [list $fx $content]]
}

proc prexml_find_uri {u} {
    global exturis
    global httpP

    if {[info exists exturis($u)]} {
        return $exturis($u)
    }

    if {!$httpP} {
        error "unable to find http package"
    }
    set code [http::code [set httpT [http::geturl [set file $u]]]]
    if {![string compare [lindex $code 1] 404]} {
        set code [http::code [set httpT [http::geturl [set file $file.xml]]]]
    }
    if {[string compare [lindex $code 1] 200]} {
        error "$file: $code"
    }
    set content [prexml_cdata [http::data $httpT]]
    http::cleanup $httpT

    linefile::new_file $file

    return [set exturis($u) [list $file $content]]
}

proc prexml_tweak_include {include {convert_file ""}} {
    set XMLDecl ""
    set body [string trimleft $include]
    if {   [regexp -nocase -- {^<\?xml[ \t\r\n]} $body]
        && [set len [string first "?>" $body]] >= 0} {

        set start [expr [string length $include] - [string length $body]]
        set end [expr $start + $len + 1]
        set XMLDecl [string range $include $start $end]
        set len [string length $include]
        set include [streplace $include $start $end "" 2]

        set start [expr $end + 1 + [string length $include] - $len]
        set body [string trimleft [string range $include $start end]]
    }
    if {[string compare $convert_file ""]} {
        set body [prexml_convert $XMLDecl $body $convert_file]
    }
    # Now that we are in UTF-8.
    set body [str_norm_eol $body \
                [expr   [regexp -- {[ \t\r\n]version="1\.[1-9][0-9]*"} $XMLDecl] \
                     || [regexp -- {[ \t\r\n]version='1\.[1-9][0-9]*'} $XMLDecl]]]
    if {   [regexp -nocase -- {^<!DOCTYPE[ \t\r\n]} $body]
        && [set len [string first ">" $body]] >= 0} {

        if {   [set len2 [string first {[} $body]] < $len
            && [string first {]} $body] > $len} {

            set start [expr [string length $include] - [string length $body]]
            set include [streplace $include $start [expr $start + $len2] "" 2]

            set start [string first {]} $include]
            set len [string first ">" [string range $include $start end]]
            set include [streplace $include $start [expr $start + $len] "" 2]
        } else {
            set start [expr [string length $include] - [string length $body]]
            set end [expr $start + $len]
            set include [streplace $include $start $end "" 2]
        }
    }

    return $include
}


#
# General stuff.
#

proc num_eols {text} {
    # Number of "\n" in $text, even if last line unterminated.
    return [regexp -all -- "\n" $text]
}

proc around2fl {result} {
    global pcdata_line_offset
    global ifile

    set y [regexp -nocase -- { around line ([1-9][0-9]*)} \
                  $result x lineno]
    if {$y > 1} {
        return $result
    } elseif {$y == 0} {
        if {[set lineno $::xdv::lineno] < 0} {
            return $result
        }
        append result [set x " around line $lineno"]
    }

    set file [linefile::get_file]
    set line [linefile::get_line [expr $lineno + $pcdata_line_offset]]

    set tail " around input line $line"
    if {[string compare $file $ifile]} {
        append tail " in \"$file\""
    }
    regsub $x $result $tail result

    return $result
}


#
# The linefile stuff in its own namespace.
#

namespace eval linefile {
    variable offset 1 fnum 0 fncache {{}}
}

proc linefile::init {} {
    variable offset
    variable fnum

    set offset 1
    set fnum 0
}

proc linefile::get_line {{lineno -1}} {
    variable offset

    if {$lineno < 0} {
        set lineno $::xdv::lineno
    }

    return [expr $lineno + $offset]
}

proc linefile::set_line {line} {
    variable offset

    set offset [expr $line - $::xdv::lineno]
}

proc linefile::new_file {file} {
    variable fncache

    if {[set num [lsearch -exact $fncache $file]] < 0} {
        set num [llength $fncache]
        lappend fncache $file
    }

    return $num
}

proc linefile::get_fnum {} {
    variable fnum

    return $fnum
}

proc linefile::get_file {{num -1} {basename 0}} {
    variable fncache

    if {$num < 0} {
        variable fnum

        set num $fnum
    }
    set file [lindex $fncache $num]

    if {$basename} {
        # Only keep base name of file.
        regsub -- "^.*[file join \[/ \]]" $file {} file
    }

    return $file
}

proc linefile::set_fnum {num} {
    variable fnum

    set fnum $num
}

proc linefile::set_file {file} {
    variable fnum

    return [set fnum [new_file $file]]
}

proc linefile::make_pi {file line {force_file 0}} {
    variable fnum

    set num [new_file $file]
    if {$force_file || $num != $fnum} {
        set fnum $num
        regsub -all -- & $file {\&amp;} file
        if {[string first \" $file] < 0} {
            set lcf \"$line:$file\"
        } elseif {[string first \' $file] < 0} {
            set lcf \'$line:$file\'
        } else {
            regsub -all -- \" $file {\&quot;} file
            set lcf \"$line:$file\"
        }
    } else {
        set lcf \"$line\"
    }

    return "<?rfc linefile=$lcf?>"
}


#
# XML linkage
#


# globals used in parsing
#
#     counter - used for generating reference numbers
#       depth -  ..
#       elemN - index of current element
#        elem - array, indexed by elemN, having:
#               list of element attributes,
#               plus ".CHILDREN", ".COUNTER", ".CTEXT", ".NAME",
#                    ".ANCHOR", ".EDITNO"
#      passno - 1 or 2 (or maybe 3, if generating a TOC)
#       stack - the stack of elements, each frame having:
#               { element-name "elemN" elemN "children" { elemN... }
#                 "ctext" yes-or-no }
#        xref - array, indexed by anchor, having:
#               { "type" element-name "elemN" elemN "value" reference-number }

proc pass {tag} {
    global options
    global counter depth elemN elem passno stack xref
    global anchorN
    global elemZ
    global crefs erefs
    global root

    switch -- $tag {
        start {
            unexpected notice "pass $passno..."
            if {$passno == 1} {
                catch { unset counter }
                catch { unset depth }
                catch { unset elem }
                catch { unset xref }
                catch { unset crefs }
                catch { unset erefs }
                set anchorN 0
                set root [list {}]
            }
            catch { unset counter(references) }
            set elemN 0
            catch { unset options }
            # "subcompact" must not be on this list.
            array set options [list autobreaks  yes \
                                    background  ""  \
                                    colonspace  no  \
                                    comments    no  \
                                    compact     no  \
                                    editing     no  \
                                    emoticonic  no  \
                                    footer      ""  \
                                    header      ""  \
                                    inline      no  \
                                    iprnotified no  \
                                    linkmailto  yes \
                                    private     ""  \
                                    slides      no  \
                                    sortrefs    no  \
                                    strict      no  \
                                    symrefs     no  \
                                    toc         no  \
                                    tocdepth    3   \
                                    tocindent   yes \
                                    tocompact   yes \
                                    topblock    yes \
                                    useobject   no]
            normalize_options
            catch { unset stack }
            linefile::init
        }

        end {
            set elemZ $elemN

            if {($passno == 1) && ($options(.STRICT))} {
                xdv::validate_tree [lindex [lindex $root 0] 0] \
                     rfc2629.cmodel  rfc2629.rattrs rfc2629.oattrs \
                     rfc2629.anchors rfc2629.pcdata

            }
        }
    }
}


# begin element

global required ctexts categories

# This must be kept in lexicographical order for string compare.
set required {
               appendix   { title  }
               date       { year }
               eref       { target }
               format     { type }
               iref       { item }
               note       { title  }
               section    { title  }
# backwards-compatibility... (the attributes are actually mandatory)
#              seriesInfo { name value }
               xref       { target }
             }

set ctexts   { area artwork city code country cref email eref facsimile
               keyword organization phone postamble preamble region seriesInfo
               spanx street t title ttcol uri workgroup xref }

set categories \
             { {std  "Standards Track" STD
"This document specifies an Internet standards track protocol for the Internet
community, and requests discussion and suggestions for improvements.
Please refer to the current edition of the &ldquo;Internet Official Protocol
Standards&rdquo; (STD&nbsp;1) for the standardization state and status of this
protocol.
Distribution of this memo is unlimited."}

               {bcp      "Best Current Practice" BCP
"This document specifies an Internet Best Current Practices for the Internet
Community, and requests discussion and suggestions for improvements.
Distribution of this memo is unlimited."}

               {info     "Informational" FYI
"This memo provides information for the Internet community.
It does not specify an Internet standard of any kind.
Distribution of this memo is unlimited."}

               {exp      "Experimental" EXP
"This memo defines an Experimental Protocol for the Internet community.
It does not specify an Internet standard of any kind.
Discussion and suggestions for improvement are requested.
Distribution of this memo is unlimited."}

               {historic "Historic" ""
"This memo describes a historic protocol for the Internet community.
It does not specify an Internet standard of any kind.
Distribution of this memo is unlimited."} }

set iprstatus \
             { {full2026
"This document is an Internet-Draft and is
in full conformance with all provisions of Section&nbsp;10 of RFC&nbsp;2026."}

               {noDerivativeWorks2026
"This document is an Internet-Draft and is
in full conformance with all provisions of Section&nbsp;10 of RFC&nbsp;2026
except that the right to produce derivative works is not granted."}

               {noDerivativeWorksNow
"This document is an Internet-Draft and is
in full conformance with all provisions of Section&nbsp;10 of RFC&nbsp;2026
except that the right to produce derivative works is not granted.
(If this document becomes part of an IETF working group activity,
then it will be brought into full compliance with Section&nbsp;10 of RFC&nbsp;2026.)"}

               {none
"This document is an Internet-Draft and is
NOT offered in accordance with Section&nbsp;10 of RFC&nbsp;2026,
and the author does not provide the IETF with any rights other
than to publish as an Internet-Draft."}

               {full3667
"This document is an Internet-Draft and is subject to all provisions
of Section&nbsp;3 of RFC&nbsp;3667.
By submitting this Internet-Draft,
each author represents that any applicable patent or other IPR claims of which
he or she is aware have been or will be disclosed,
and any of which he or she become aware will be disclosed,
in accordance with RFC&nbsp;3668."}

               {noModification3667
"This document is an Internet-Draft and is subject to all provisions
of Section&nbsp;3 of RFC&nbsp;3667.
By submitting this Internet-Draft,
each author represents that any applicable patent or other IPR claims of which
he or she is aware have been or will be disclosed,
and any of which he or she become aware will be disclosed,
in accordance with RFC&nbsp;3668.
This document may not be modified,
and derivative works of it may not be created,
except to publish it as an RFC and to translate it into languages other
than English%IPREXTRACT%."}

               {noDerivatives3667
"This document is an Internet-Draft and is subject to all provisions
of Section&nbsp;3 of RFC&nbsp;3667 except for the right to produce derivative works.
By submitting this Internet-Draft,
each author represents that any applicable patent or other IPR claims of which
he or she is aware have been or will be disclosed,
and any of which he or she become aware will be disclosed,
in accordance with RFC&nbsp;3668.
This document may not be modified,
and derivative works of it may not be created%IPREXTRACT%."}

               {full3978
"By submitting this Internet-Draft,
each author represents that any applicable patent or other IPR claims of which
he or she is aware have been or will be disclosed,
and any of which he or she becomes aware will be disclosed,
in accordance with Section&nbsp;6 of BCP&nbsp;79."}

               {noModification3978
"By submitting this Internet-Draft,
each author represents that any applicable patent or other IPR claims of which
he or she is aware have been or will be disclosed,
and any of which he or she becomes aware will be disclosed,
in accordance with Section&nbsp;6 of BCP&nbsp;79.
This document may not be modified,
and derivative works of it may not be created,
except to publish it as an RFC and to translate it into languages other
than English%IPREXTRACT%."}

               {noDerivatives3978
"By submitting this Internet-Draft,
each author represents that any applicable patent or other IPR claims of which
he or she is aware have been or will be disclosed,
and any of which he or she becomes aware will be disclosed,
in accordance with Section&nbsp;6 of BCP&nbsp;79.
This document may not be modified,
and derivative works of it may not be created%IPREXTRACT%."} }

proc begin {name {av {}}} {
    global counter depth elemN elem passno stack xref
    global anchorN
    global options
    global required ctexts categories iprstatus
    global root

# because TclXML... quotes attribute values containing "]"
    set kv ""
    foreach {k v} $av {
        lappend kv $k
        regsub -all {\\\[} $v {[} v
        lappend kv $v
    }
    set av $kv

    incr elemN

    if {$passno == 1} {
        set elem($elemN) $av
        array set attrs $av

        set attrs(.lineno) $::xdv::lineno
        lappend root [list $name [array get attrs]]
        unset attrs(.lineno)

        foreach { n a } $required {
            switch -- [string compare $n $name] {
                -1 {
                     continue
                }

                0 {
                    foreach v $a {
                        if {[catch { set attrs($v) }]} {
                            unexpected error \
                                "missing $v attribute in #$elemN:<$name> element"
                        }
                    }
                    break
                }

                1 {
                    break
                }
            }
        }

        switch -- [set type $name] {
            rfc {
                if {![catch { set attrs(category) }]} {
                    if {[lsearch0 $categories $attrs(category)] < 0} {
                        unexpected error \
                            "category=\"$attrs(category)\" attribute unknown in #$elemN:<rfc>"
                    }
                    if {(![string compare $attrs(category) historic]) \
                            && (![catch { set attrs(seriesNo) }])} {
                        unexpected error \
                            "historic documents have no document series in #$elemN:<rfc>"
                    }
                }
                if {![catch { set attrs(ipr) }]} {
                    if {[lsearch0 $iprstatus $attrs(ipr)] < 0} {
                        unexpected error \
                            "ipr=\"$attrs(ipr)\" attribute unknown in #$elemN:<rfc>"
                    }
                }
                global entities oentities mode nbsp
                if {[ catch { set number $attrs(number) }]} {
                    set number XXXX
                }
                set entities [linsert $oentities 0 "&rfc.number;" $number]
                switch -- $mode {
                    nr
                        -
                    txt {
                        set nbsp "\xa0"
                        set entities [linsert $entities 0 "&nbsp;" $nbsp]
                        set entities [linsert $entities 0 "&#160;" $nbsp]
                    }
                }
            }

            back {
                catch { unset depth(section) }
            }

            abstract {
                if {[lsearch0 $stack back] < 0} {
                    set counter(abstract) 1
                }
            }

            section
                -
            appendix {
                if {[lsearch0 $stack back] >= 0} {
                    set type appendix
                }
                if {![string compare $type section]} {
                    if {[catch { incr depth(section) }]} {
                        set depth(section) 1
                        set counter(section) 0
                    }
                } elseif {[catch { incr depth(appendix) }]} {
                    set depth(appendix) 1
                    set counter(appendix) 0
                }
                set counter($type) \
                         [counting $counter($type) $depth($type)]
                set l [split $counter($type) .]
                if {![string compare $type appendix]} {
                    set type appendix
                    set l [lreplace $l 0 0 \
                                [string index " ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                                    [lindex $l 0]]]
                }
                set attrs(.COUNTER) [set value [join $l .]]
                if {[catch { set attrs(anchor) }]} {
                    set attrs(anchor) anchor[incr anchorN]
                }
                set attrs(.ANCHOR) $attrs(anchor)
                if {[catch { set attrs(toc) }]} {
                    set attrs(toc) default
                }
                set elem($elemN) [array get attrs]
                switch -- [set t [string tolower $attrs(title)]] {
                    "iana considerations"
                        -
                    "security considerations" {
                        set counter($t) 1
                    }
                }
            }

            list {
                if {[catch { incr depth(list) }]} {
                    set depth(list) 1
                    set counter(list) 0
                }
            }

            t {
                if {[catch { incr counter(editno) }]} {
                    set counter(editno) 1
                }
                set attrs(.EDITNO) $counter(editno)
                set elem($elemN) [array get attrs]
                if {[lsearch0 $stack list] >= 0} {
                    set counter(list) [counting $counter(list) $depth(list)]
                    set attrs(.COUNTER) $counter(list)
                    set elem($elemN) [array get attrs]
                    set value $attrs(.COUNTER)
                } else {
                    set frame [lindex $stack end]
                    set value 1
                    foreach child [lindex $frame 4] {
                        array set c $elem($child)
                        if {![string compare $c(.NAME) t]} {
                            incr value
                        }
                    }
                }
            }

            figure {
                if {[catch { incr counter(figure) }]} {
                    set counter(figure) 1
                }
                set attrs(.COUNTER) [set value $counter(figure)]
                set elem($elemN) [array get attrs]
            }

            preamble
                -
            postamble {
                if {[catch { incr counter(editno) }]} {
                    set counter(editno) 1
                }
                set attrs(.EDITNO) $counter(editno)
                set elem($elemN) [array get attrs]
            }

            texttable {
                if {[catch { incr counter(table) }]} {
                    set counter(table) 1
                }
                set attrs(.COUNTER) [set value $counter(table)]
                set elem($elemN) [array get attrs]
            }

            references {
                if {[catch { incr depth(references) }]} {
                    set depth(references) 1
                    if {[catch { set counter(section) }]} {
                        set counter(section) 0
                    }
                    set counter(section) [counting $counter(section) 1]
                }
                set counter(section) [counting $counter(section) 2]
                set l [split $counter(section) .]
                set attrs(.COUNTER) [set value [join $l .]]
                if {[catch { set attrs(anchor) }]} {
                    set attrs(anchor) anchor[incr anchorN]
                }
                set attrs(.ANCHOR) $attrs(anchor)
                if {[catch { set attrs(toc) }]} {
                    set attrs(toc) default
                }
                set elem($elemN) [array get attrs]
                if {[info exists attrs(title)]} {
                    switch -- [set t [string tolower $attrs(title)]] {
                        "normative reference"
                            -
                        "normative references" {
                            set counter(normative) 1
                        }

                        "informative reference"
                            -
                        "informative references" {
                            set counter(informative) 1
                        }
                    }
                }
            }

            reference {
                if {$options(.SYMREFS)} {
                    set value $attrs(anchor)
                } else {
                    if {[catch { incr counter(reference) }]} {
                        set counter(reference) 1
                    }
                    set value $counter(reference)
                }
                set attrs(.COUNTER) $value
                set elem($elemN) [array get attrs]
            }

            eref {
                if {($options(.STRICT)) && ([lsearch0 $stack abstract] >= 0)} {
                    unexpected error "eref element in abstract"
                }
            }

            xref {
                if {($options(.STRICT)) && ([lsearch0 $stack abstract] >= 0)} {
                    unexpected error "xref element in abstract"
                }
                set target $attrs(target)
                if {(![info exists counter(firstxref)]) \
                        || [lsearch -exact $counter(firstxref) $target] < 0} {
                    lappend counter(firstxref) $target
                }
            }

            cref {
                if {[catch { set attrs(anchor) }]} {
                    set attrs(anchor) anchor[incr anchorN]
                }
                if {$options(.SYMREFS)} {
                    set value $attrs(anchor)
                } else {
                    if {[catch { incr counter(comment) }]} {
                        set counter(comment) 1
                    }
                    set value Comment.$counter(comment)
                }
                set attrs(.COUNTER) $value
                set elem($elemN) [array get attrs]
            }
        }

        if {![catch { set anchor $attrs(anchor) }]} {
            if {![catch { set xref($anchor) }]} {
                array set x $xref($anchor)
                unexpected error \
  "anchor=\"$anchor\" attribute currently points to #$x(elemN):<$x(type)> and cannot be redefined in new #$elemN:<$name>"
            }
            set xref($anchor) [list type $type elemN $elemN value $value]
        }

        if {$elemN > 1} {
            set frame [lindex $stack end]
            set children [lindex $frame 4]
            lappend children $elemN
            set frame [lreplace $frame 4 4 $children]
            set stack [lreplace $stack end end $frame]
        }
    } else {
        if {0 && (![string compare $passno/$name 2/eref])} {
            array set attrs $elem($elemN)

            if {[catch { incr counter(reference) }]} {
                set counter(reference) 1
            }
            set attrs(.COUNTER) $counter(reference)
            set elem($elemN) [array get attrs]
        }
        switch -- $name {
            rfc
                -
            annotation {
                pass2begin_$name $elemN
            }

            front
                -
            abstract
                -
            note
                -
            section
                -
            appendix
                -
            t
                -
            list
                -
            figure
                -
            artwork
                -
            preamble
                -
            postamble
                -
            texttable
                -
            ttcol
                -
            c
                -
            iref
                -
            vspace
                -
            back {
                if {[lsearch0 $stack references] < 0} {
                    pass2begin_$name $elemN
                }
            }

            xref
                -
            eref
                -
            cref
                -
            spanx {
                if {([lsearch0 $stack references] < 0) \
                        || ([lsearch0 $stack annotation] >= 0)} {
                    pass2begin_$name $elemN
                }
            }
        }
    }

    if {[lsearch -exact $ctexts $name] >= 0} {
        set ctext yes
        if {$passno == 1} {
            set attrs(.CTEXT) ""
            set elem($elemN) [array get attrs]
        }
    } else {
        set ctext no
    }
    lappend stack [list $name elemN $elemN children "" ctext $ctext av $av \
                        line [linefile::get_line] fnum [linefile::get_fnum]]
}

proc counting {tcount tdepth} {
    set x [llength [set l [split $tcount .]]]

    if {$x > $tdepth} {
        set l [lrange $l 0 [expr $tdepth-1]]
        set x $tdepth
    } elseif {$x < $tdepth} {
        lappend l 0
        incr x
    }
    incr x -1
    set l [lreplace $l $x $x [expr [lindex $l $x]+1]]
    return [join $l .]
}

# end element

proc end {name} {
    global counter depth elemN elem passno stack xref
    global root

    set frame [lindex $stack end]
    set stack [lreplace $stack end end]

    array set av [lrange $frame 1 end]
    set elemX $av(elemN)

    if {$passno == 1} {
        set f2 [lindex $root end]
        set root [lreplace $root end end]
        set parent [lindex $root end]
        lappend parent $f2
        set root [lreplace $root end end $parent]

        array set attrs $elem($elemX)

        set attrs(.CHILDREN) $av(children)
        set attrs(.NAME) $name
        set elem($elemX) [array get attrs]

        switch -- $name {
            section
                -
            appendix {
                if {[lsearch0 $stack back] >= 0} {
                    set name appendix
                }
                incr depth($name) -1
            }

            list {
                if {[incr depth(list) -1] == 0} {
                    set counter(list) 0
                }
            }

            back {
                if {[llength [set c [find_element references \
                                                     $attrs(.CHILDREN)]]] \
                        == 1} {
                    array set cv $elem($c)
                    set cv(.COUNTER) [lindex [split $cv(.COUNTER) .] 0]
                    set elem($c) [array get cv]
                }
            }
        }

        return
    }

    switch -- $name {
        rfc
            -
        front
            -
        t
            -
        list
            -
        figure
            -
        artwork
            -
        preamble
            -
        postamble
            -
        texttable
            -
        c {
            if {[lsearch0 $stack references] < 0} {
                pass2end_$name $elemX
            }
        }

        annotation {
            pass2end_$name $elemX
        }
    }
}


# character data

proc pcdata {text} {
    global counter depth elemN elem passno stack xref
    global mode
    global root

    if {[string length $text] <= 0} {
        # Really empty.
        return
    }

    set chars [string trim $text]

    set text [str_norm_eol $text]

    set frame [lindex $stack end]

    if {([lsearch0 $stack references] >= 0) \
            && ([lsearch0 $stack annotation] < 0)} {
        set pre -1
    } else {
        switch -- [lindex $frame 0] {
            artwork {
                if {$passno == 1} {
                    set pre 1
                } else {
                    # Will end up positive by incrementation.
                    set pre 0
                    set elemX [lindex $frame 2]
                    # It won't work to get attrs from $frame.
                    array set attrs $elem($elemX)
                    if {[info exists attrs(.TEXTWIDTH)]} {
                        set align [current_align]
                        set tw $attrs(.TEXTWIDTH)
                        switch -- $align {
                            left - "" {}
                            center { incr pre [expr (69 - $tw + 1)/2] }
                            right  { incr pre [expr (69 - $tw)] }

                            default {
                                unexpected error \
                                    "align=\"$align\" attribute is invalid"
                            }
                        }
                        if {$pre < 0} {
                            set pre 0
                        }
                    }
                    incr pre 3
                }
            }

            t
                -
            preamble
                -
            postamble
                -
            c
                -
            annotation {
                set pre 0
            }

            default {
                set pre -1
            }
        }
    }

    if {$passno == 1} {
        if {$pre < 0 && [string length $chars] <= 0} {
            # Just white space.  Pass 1 doesn't want to see
            # PCDATA in the wrong places, but further passes
            # *need* some among it to generate correct output.
            return
        }
        array set attrs [lindex [set f2 [lindex $root end]] 1]
        set attrs(.pcdata) 1
        set root [lreplace $root end end \
                           [lreplace $f2 1 1 [array get attrs]]]
        catch { array unset attrs }

        array set av [lrange $frame 1 end]

        set elemX $av(elemN)
        array set attrs $elem($elemX)
        if {![string compare $av(ctext) yes]} {
            if {[lsearch0 $stack spanx] < 0} {
                append attrs(.CTEXT) $chars
            } else {
                append attrs(.CTEXT) $text
            }
        }
        set elem($elemX) [array get attrs]

        return
    }

    if {$pre < 0} {
        return
    }

    pcdata_$mode $text $pre
}


# processing instructions

proc pi {args} {
    global options
    global passno stack
    global mode

    switch -- [lindex $args 0]/[llength $args] {
        xml/2 {
            if {([string first "version=\"1.0\"" [lindex $args 1]] < 0) \
                    && ([string first "version='1.0'" [lindex $args 1]] < 0)} {
                unexpected error "unexpected <?xml ...?>"
            }
        }

        DOCTYPE/4 {
            if {[info exists stack]} {
                return
            }

            if {![regexp -- {^-public -system (|.*/)rfc.*\.dtd$} \
                         [lrange $args 1 end]]} {
                unexpected error "unexpected DOCTYPE: [lrange $args 1 end]"
            }
        }

        rfc/2 {
            set n 0
            set text [lindex $args 1]
            set lines [num_eols $text]
            while {1} {
                set l [pi_rfc_next $text]
                set key  [lindex $l 0]
                set val  [lindex $l 1]
                set text [lindex $l 2]
                if {![string compare $key ""]} {
                    if {[string compare $val ""]} {
                        unexpected error \
                            "stopped processing faulty rfc-PI at \"$val\""
                    }
                    break
                }
                switch -- $key {
                    include { continue }

                    linefile {
                        if {![regexp -- {^([0-9]+)(:(.*))?$} \
                                     $val a b c d]} {
                            unexpected warning \
  "ignoring invalid rfc-PI linefile-directive value \"$val\""
                            continue
                        }
                        if {[string length $c]} {
                            # May be empty.  User's choice!
                            set new_file $d
                        }
                        set new_line $b
                        continue
                    }
                }
                if {   [info exists options($key)]
                    || (   [string is lower $key]
                        && [info exists options(.[string toupper $key])])} {
                    set options($key) $val
                    incr n
                } elseif {$passno > 1} {
                    if {[catch { pi_$mode $key $val }]} {
                        regsub -all -- \" $val {\"} val
                        unexpected error \
                            "invalid rfc-PI directive: $key=\"$val\""
                    }
                }
            }
            if {$n > 0} {
                normalize_options
            }
            # Do this at the end so that intermixed
            # error or warning messages are not affected.
            if {[info exists new_line]} {
                if {[info exists new_file]} {
                    linefile::set_file $new_file
                }
                linefile::set_line [expr $new_line - $lines]
            }
        }

        default {
            if {![string compare [lindex $args 0] xml-stylesheet]} {
                return
            }
            set text [string trim [join $args " "]]
            unexpected warning "unknown PI: $text"
        }
    }
}

proc pi_rfc_next {text} {
    set text [string trimleft $text]
    set key ""
    set val $text

    # Some useful regexp literals.
    set wsp  {[ \t\r\n]}
    set dqev \"(\[^\"\]*)\"
    set sqev \'(\[^\'\]*)\'
    set nme  {([A-Za-z_:][A-Za-z0-9._:-]*)}
    set rem  (.*)

    if {   [regexp -- ^$nme=$dqev$rem$ $text x k v rest]
        || [regexp -- ^$nme=$sqev$rem$ $text x k v rest]
        || [regexp -- ^$nme=${nme}($|$wsp)$rem$ $text x k v y rest]} {
        set key $k
        set val [chars_expand $v]
        set text [string trimleft $rest]
    }

    return [list $key $val $text]
}

proc normalize_options {} {
    global passmax
    global options
    global mode
    global remoteP

    if {$remoteP} {
        set options(slides) no
    }
    foreach {o O} [list autobreaks  .AUTOBREAKS  \
                        colonspace  .COLONSPACE  \
                        compact     .COMPACT     \
                        comments    .COMMENTS    \
                        editing     .EDITING     \
                        emoticonic  .EMOTICONIC  \
                        inline      .INLINE      \
                        iprnotified .IPRNOTIFIED \
                        linkmailto  .LINKMAILTO  \
                        slides      .SLIDES      \
                        sortrefs    .SORTREFS    \
                        strict      .STRICT      \
                        subcompact  .SUBCOMPACT  \
                        symrefs     .SYMREFS     \
                        toc         .TOC         \
                        tocompact   .TOCOMPACT   \
                        tocindent   .TOCINDENT   \
                        topblock    .TOPBLOCK    \
                        useobject   .USEOBJECT] {
        if {![info exists options($o)]} {
            continue
        }
        switch -- $options($o) {
            yes - true - 1 {
                set options($O) 1
            }

            default {
                set options($O) 0
            }
        }
    }

    foreach {o O} [list tocdepth .TOCDEPTH] {
        if {[catch { incr options($o) 0 }]} {
            unexpected error "invalid $o value '$options($o)'"
        }
        set options($O) $options($o)
    }

    foreach {o O} [list footer  .FOOTER \
                        header  .HEADER  \
                        private .PRIVATE] {
        set options($O) 0
        if {[string compare $options($o) ""]} {
            set options($O) 1
        }
    }
    switch -- $mode {
        nr  -
        txt {
# needed for annotations with mark-up to work correctly...
            set passmax 3
        }

        html {
            if {$options(.SLIDES)} {
                set options(.TOC) 0
            }
            if {1 || ($options(.SLIDES))} {
                set passmax 3
            }
        }
    }
    if {!$options(.COMMENTS)} {
        set options(.INLINE) 0
    }
    if {![info exists options(subcompact)]} {
        set options(.SUBCOMPACT) $options(.COMPACT)
    }
    if {$options(.PRIVATE)} {
        set options(.HEADER) 1
        set options(.FOOTER) 1
    }
}


# xml and dtd declaration

proc xmldecl {version encoding standalone} {
    if {[string compare $version 1.0]} {
        unexpected error "invalid XML version: $version"
    }
}


proc doctype {element public system internal} {
    global stack

    if {[info exists stack]} {
        return
    }

    if {[string compare $element rfc] \
            || [string compare $public ""] \
            || (![regexp -- {^(|.*/)rfc.*\.dtd$} $system])} {
        unexpected error "invalid DOCTYPE: $element+$public+$system+$internal"
    }
}


# the unexpected ...

global already_warned
array set already_warned {}

proc unexpected {args} {
    global prog
    global guiP

    set text [join [lrange $args 1 end] " "]

    switch -- [set type [lindex $args 0]] {
        error {
            global errorP

            set errorP 1
            if {$guiP != 1} {
                set text "$prog: error: $text"
            }
            return -code error $text
        }

        notice {
            if {$guiP == -1} {
                puts stdout $text
            }
        }

        default {
            global already_warned

            append text [around2fl ""]
            if {[info exists already_warned($text)]} {
                return
            }
            set already_warned($text) 1
            #append text [around2fl ""]
            switch -- $guiP {
                1 {
                    tk_dialog .unexpected "$prog: $type" $text $type 0 OK
                }

                0 {
                    global env

                    if {[llength [array names env REQUEST_METHOD]] <= 0} {
                        # Not under CGI.
                        puts stderr "$prog: $type: $text"
                    }
                }

                -1 {
                    puts stdout "$type: $text"
                }
            }
        }
    }
}

proc unex_condtype {} {
    global options

    if {$options(.STRICT)} {
        return error
    } else {
        return warning
    }
}


#
# specific elements
#


# the whole document

global validity

set validity {
"This document and the information contained herein are provided
on an &ldquo;AS IS&rdquo; basis and THE CONTRIBUTOR,
THE ORGANIZATION HE/SHE REPRESENTS OR IS SPONSORED BY (IF ANY),
THE INTERNET SOCIETY AND THE INTERNET ENGINEERING TASK FORCE DISCLAIM
ALL WARRANTIES,
EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE
INFORMATION HEREIN WILL NOT INFRINGE ANY RIGHTS OR ANY IMPLIED
WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE."
}

global copylong1 copylong2

set copylong1 {
"Copyright &copy; The Internet Society (%YEAR%). All Rights Reserved."

"This document and translations of it may be copied and furnished to
others, and derivative works that comment on or otherwise explain it
or assist in its implementation may be prepared, copied, published and
distributed, in whole or in part, without restriction of any kind,
provided that the above copyright notice and this paragraph are
included on all such copies and derivative works. However, this
document itself may not be modified in any way, such as by removing
the copyright notice or references to the Internet Society or other
Internet organizations, except as needed for the purpose of
developing Internet standards in which case the procedures for
copyrights defined in the Internet Standards process must be
followed, or as required to translate it into languages other than
English."

"The limited permissions granted above are perpetual and will not be
revoked by the Internet Society or its successors or assignees."

"This document and the information contained herein is provided on an
&ldquo;AS IS&rdquo; basis and THE INTERNET SOCIETY AND THE INTERNET ENGINEERING
TASK FORCE DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION
HEREIN WILL NOT INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF
MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE."
}

set copylong2 {
"Copyright &copy; The Internet Society (%YEAR%).
This document is subject to the rights,
licenses and restrictions contained in BCP&nbsp;78,
and except as set forth therein,
the authors retain all their rights."
}

global iprlong1 iprlong2 iprurl ipremail

set iprurl "http://www.ietf.org/ipr"
set ipremail "ietf-ipr@ietf.org"

set iprlong1 {
"The IETF takes no position regarding the validity or scope of
any intellectual property or other rights that might be claimed
to  pertain to the implementation or use of the technology
described in this document or the extent to which any license
under such rights might or might not be available; neither does
it represent that it has made any effort to identify any such
rights. Information on the IETF's procedures with respect to
rights in standards-track and standards-related documentation
can be found in BCP&nbsp;11. Copies of claims of rights made
available for publication and any assurances of licenses to
be made available, or the result of an attempt made
to obtain a general license or permission for the use of such
proprietary rights by implementors or users of this
specification can be obtained from the IETF Secretariat."

"The IETF invites any interested party to bring to its
attention any copyrights, patents or patent applications, or
other proprietary rights which may cover technology that may be
required to practice this standard. Please address the
information to the IETF Executive Director."
}

set iprlong2 {
"The IETF takes no position regarding the validity or scope of any
Intellectual Property Rights or other rights that might be claimed
to pertain to the implementation or use of the technology
described in this document or the extent to which any license
under such rights might or might not be available; nor does it
represent that it has made any independent effort to identify any
such rights.
Information on the procedures with respect to
rights in RFC documents can be found in BCP&nbsp;78 and BCP&nbsp;79."

"Copies of IPR disclosures made to the IETF Secretariat and any
assurances of licenses to be made available,
or the result of an attempt made to obtain a general license or
permission for the use of such proprietary rights by implementers or
users of this specification can be obtained from the IETF on-line IPR
repository at %IPRURL%."

"The IETF invites any interested party to bring to its attention
any copyrights,
patents or patent applications,
or other
proprietary rights that may cover technology that may be required
to implement this standard.
Please address the information to the IETF at %IPREMAIL%."
}

global iprextra

set iprextra {
"The IETF has been notified of intellectual property rights
claimed in regard to some or all of the specification contained
in this document. For more information consult the online list
of claimed rights."
}

global funding

set funding \
"Funding for the RFC Editor function is currently provided by the
Internet Society."


proc pass2begin_rfc {elemX} {
    global counter elem passno xref
    global options copyrightP iprP
    global copyshort copyshort1 copyshort2

    array set attrs [list number     ""   obsoletes "" updates "" \
                          category   info seriesNo  "" ipr     "" \
                          iprExtract ""   xml:lang  en]
    array set attrs $elem($elemX)
    set elem($elemX) [array get attrs]

    if {(!$options(.PRIVATE)) \
            && (![string compare $attrs(number) ""]) \
            && (![string compare $attrs(ipr) ""])} {
        unexpected error \
                   "rfc element needs either a number or an ipr attribute"
    }
    if {![string compare $attrs(ipr) none]} {
        set copyrightP 0
    } else {
        set copyrightP 1
        if {(![string compare $attrs(number) ""]) \
                || (![string compare $attrs(category) std])} {
            set iprP 1
        } else {
            set iprP 0
        }
    }

    set newP 1
    if {[string compare $attrs(number) ""]} {
        if {$attrs(number) <= 3707} {
            set newP 0
        }
    } elseif {[string compare $attrs(ipr) ""]} {
        if {   [string first "3667" $attrs(ipr)] < 0
            && [string first "3978" $attrs(ipr)] < 0} {
            set newP 0
        }
    }
    if {$newP} {
        set copyshort $copyshort2
    } else {
        set copyshort $copyshort1
    }

    set firstxref [list ""]
    if {[info exists counter(firstxref)]} {
        foreach target $counter(firstxref) {
            if {(![catch { array set av $xref($target) }]) \
                    && (![string compare $av(type) reference])} {
                lappend firstxref $target
            }
        }
    }

    if {($passno == 2) \
            && $options(.SORTREFS) \
            && !$options(.SYMREFS) \
            && ([info exists counter(firstxref)]) \
            && ([llength [set back [find_element back $attrs(.CHILDREN)]]] \
                    == 1)} {
        catch { unset bv }
        array set bv $elem($back)

        set offset 0
        foreach refs [find_element references $bv(.CHILDREN)] {
            catch { unset sv }
            array set sv $elem($refs)

            foreach ref [find_element reference $sv(.CHILDREN)] {
                catch { unset rv }
                array set rv $elem($ref)
                if {[set x [lsearch $firstxref $rv(anchor)]] < 0} {
                    set x [llength $firstxref]
                    lappend firstxref $rv(anchor)
                }
                set rv(.COUNTER) $x
                set elem($ref) [array get rv]
            }

            foreach ref [lsort -command sort_references \
                                [find_element reference $sv(.CHILDREN)]] {
                catch { unset rv }
                array set rv $elem($ref)
                set rv(.COUNTER) [incr offset]
                set elem($ref) [array get rv]

                set target $rv(anchor)
                catch { unset xv }
                array set xv $xref($target)
                set xv(value) $offset
                set xref($target) [array get xv]
            }
        }
    }
}

proc pass2end_rfc {elemX} {
    global elem
    global elemZ
    global mode
    global copylong1 copylong2 iprlong1 iprlong2 iprextra
    global options
    global pageno

    array set attrs $elem($elemX)

    set front [find_element front $attrs(.CHILDREN)]
    array set fv $elem($front)

    set date [find_element date $fv(.CHILDREN)]
    array set dv $elem($date)

    set newP 1
    if {[string compare $attrs(number) ""]} {
        if {$attrs(number) <= 3707} {
            set newP 0
        }
    } elseif {[string compare $attrs(ipr) ""]} {
        if {   [string first "3667" $attrs(ipr)] < 0
            && [string first "3978" $attrs(ipr)] < 0} {
            set newP 0
        }
    }
    if {$newP} {
        set copylong $copylong2
    } else {
        set copylong $copylong1
    }
    regsub -all %YEAR% $copylong $dv(year) copying

    if {![catch { set who $attrs(disclaimant) }]} {
        lappend copying \
"%WHO% expressly disclaims any and all warranties regarding this
contribution including any warranty that (a) this contribution does
not violate the rights of others, (b) the owners, if any, of other
rights in this contribution have been informed of the rights and
permissions granted to IETF herein, and (c) any required
authorizations from such owners have been obtained.
This document and the information contained herein is provided on
an &ldquo;AS IS&rdquo; basis and %UWHO% DISCLAIMS ALL WARRANTIES, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE
OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY RIGHTS OR ANY
IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR
PURPOSE." \
 \
"IN NO EVENT WILL %UWHO% BE LIABLE TO ANY OTHER PARTY INCLUDING
THE IETF AND ITS MEMBERS FOR THE COST OF PROCURING SUBSTITUTE GOODS
OR SERVICES, LOST PROFITS, LOSS OF USE, LOSS OF DATA, OR ANY
INCIDENTAL, CONSEQUENTIAL, INDIRECT, OR SPECIAL DAMAGES WHETHER
UNDER CONTRACT, TORT, WARRANTY, OR OTHERWISE, ARISING IN ANY WAY
OUT OF THIS OR ANY OTHER AGREEMENT RELATING TO THIS DOCUMENT,
WHETHER OR NOT SUCH PARTY HAD ADVANCE NOTICE OF THE POSSIBILITY OF
SUCH DAMAGES."

        regsub -all %WHO% $copying $who copying
        regsub -all %UWHO% $copying [string toupper $who] copying
    }

    if {$newP} {
        set iprstmt $iprlong2
    } else {
        set iprstmt $iprlong1
    }
    if {$options(.IPRNOTIFIED)} {
        set iprstmt [concat $iprstmt $iprextra]
    }

    array set index ""
    for {set elemY 1} {$elemY <= $elemZ} {incr elemY} {
        catch { unset iv }
        array set iv $elem($elemY)

        if {[string compare $iv(.NAME) iref]} {
            continue
        }
        lappend index($iv(item)+$iv(subitem)+$iv(flags)) $iv(.ANCHOR)
    }
    set items [lsort -dictionary [array names index]]

    set irefs ""
    set L ""
    set K ""
    foreach item $items {
        set iref ""
        foreach {key subkey flags} [split $item +] { break }
        if {[string compare [set c [string toupper [string index $key 0]]] \
                    $L]} {
            lappend iref [set L $c]
            set K ""
        } else {
            lappend iref ""
        }
        if {[string compare $key $K]} {
            lappend iref [set K $key]
        } else {
            lappend iref ""
        }
        lappend iref $subkey
        lappend iref $flags
        lappend iref $index($item)
        lappend irefs $iref
    }

    set attrs(.ANCHOR) [rfc_$mode $irefs $iprstmt $copying $newP]
    set elem($elemX) [array get attrs]

    if {([string compare $mode html]) \
            && ($options(.STRICT)) && (!$options(.TOC)) \
            && ($pageno > 15)} {
        unexpected error "no table of contents, but $pageno pages"
    }
}


# the front (either for the rfc or a reference)

global copyshort copyshort1 copyshort2 idinfo idaburl idshurl

set idaburl "http://www.ietf.org/ietf/1id-abstracts.txt"
set idshurl "http://www.ietf.org/shadow.html"

set copyshort1 \
"Copyright &copy; The Internet Society (%YEAR%). All Rights Reserved."

set copyshort2 \
"Copyright &copy; The Internet Society (%YEAR%)."

set idinfo {
"%IPR%"

"Internet-Drafts are working documents of the Internet Engineering
Task Force (IETF), its areas, and its working groups.
Note that other groups may also distribute working documents as
Internet-Drafts."

"Internet-Drafts are draft documents valid for a maximum of six months
and may be updated, replaced, or obsoleted by other documents at any time.
It is inappropriate to use Internet-Drafts as reference material or to cite
them other than as &ldquo;work in progress.&rdquo;"

"The list of current Internet-Drafts can be accessed at
%IDABURL%."

"The list of Internet-Draft Shadow Directories can be accessed at
%IDSHURL%."

"This Internet-Draft will expire on %EXPIRES%."
}

proc pass2begin_front {elemX} {
    global counter elem xref
    global options
    global mode ofile
    global categories copyshort idinfo idaburl idshurl iprstatus

    if {$options(.COLONSPACE)} {
        set colonspace " "
    } else {
        set colonspace ""
    }

    array set attrs $elem($elemX)

    set title [find_element title $attrs(.CHILDREN)]
    array set tv [list abbrev ""]
    array set tv $elem($title)
    set title [list $tv(.CTEXT)]

    set date [find_element date $attrs(.CHILDREN)]
    array set dv $elem($date)
    set three [clock format [clock seconds] -format "%B %Y %d"]
    if {(![info exists dv(month)]) || (![string compare $dv(month) ""])} {
        set dv(month) [lindex $three 0]
        set dv(day) [string trimleft [lindex $three 2] 0]
    } elseif {[catch { set dv(day) }]} {
        if {(![string compare $dv(month) [lindex $three 0]]) \
                && (![string compare $dv(year) [lindex $three 1]])} {
            set dv(day) [string trimleft [lindex $three 2] 0]
        }
    }
    set elem($date) [array get dv]

    array set rv $elem(1)
    catch { set ofile $rv(docName) }

    if {$options(.PRIVATE)} {
        lappend left $options(private)

        set status ""
    } else {
        set first ""
        if {(![string compare $rv(number) ""]) \
                && ([string compare \
                             [set workgroup [lindex [find_element workgroup \
                                 $attrs(.CHILDREN)] 0]] ""])} {
            array set wv $elem($workgroup)
            set first [string trim $wv(.CTEXT)]
        }
        if {![string compare $first ""]} {
            set first "Network Working Group"
        }
        lappend left $first

        if {[string compare $rv(number) ""]} {
            lappend left "Request for Comments:$colonspace $rv(number)"

            set cindex [lsearch0 $categories $rv(category)]
            if {[string compare $rv(seriesNo) ""]} {
                lappend left \
                        "[lindex [lindex $categories $cindex] 2]:$colonspace $rv(seriesNo)"
            }

            if {[string compare $rv(updates) ""]} {
                lappend left "Updates:$colonspace $rv(updates)"
            }
            if {[string compare $rv(obsoletes) ""]} {
                lappend left "Obsoletes:$colonspace $rv(obsoletes)"
            }

            set category [lindex [lindex $categories $cindex] 1]
            lappend left "Category:$colonspace $category"
            set status [list [lindex [lindex $categories $cindex] 3]]
        } else {
            if {$options(.STRICT)} {
                foreach t [list Abstract "Security Considerations"] {
                    if {![info exists counter([string tolower $t])]} {
                        unexpected error "missing $t"
                    }
                }
                if {([info exists counter(reference)]) \
                        && ($counter(reference))} {
                    set hitP 0
                    foreach t [list normative informative] {
                        if {[info exists counter([string tolower $t])]} {
                            set hitP 1
                        }
                    }
                    if {!$hitP} {
                        unexpected error \
                                   "missing Normative/Informative References"
                    }
                }
            }

            lappend left "Internet-Draft"

            if {[string compare $rv(updates) ""]} {
                lappend left "Updates:$colonspace $rv(updates) (if approved)"
            }
            if {[string compare $rv(obsoletes) ""]} {
                lappend left "Obsoletes:$colonspace $rv(obsoletes) (if approved)"
            }

            if {[catch { set day $dv(day) }]} {
                set day 1
            }
            set secs [clock scan "$dv(month) $day, $dv(year)" -gmt true]
            incr secs [expr (185*86400)]
            set day [string trimleft \
                            [clock format $secs -format "%d" -gmt true] 0]
            set expires [clock format $secs -format "%B $day, %Y" -gmt true]
            lappend left "Expires:$colonspace $expires"
            set category "Expires $expires"
            set status $idinfo
            regsub -all "&" [lindex [lindex $iprstatus \
                                            [lsearch0 $iprstatus \
                                                      $rv(ipr)]] 1] \
                        "\\\\\\&" ipr
            regsub -all %IPR% $status $ipr status
            if {![string compare $mode html]} {
                regsub -all %IDABURL% $status "<a href='$idaburl'>$idaburl</a>" status
                regsub -all %IDSHURL% $status "<a href='$idshurl'>$idshurl</a>" status
            } else {
                regsub -all %IDABURL% $status $idaburl status
                regsub -all %IDSHURL% $status $idshurl status
            }
            if {[string compare [set anchor $rv(iprExtract)] ""]} {
                set extract ", other than to extract "
                append extract [xref_$mode "" $xref($anchor) $anchor "" 1]
                append extract " as-is for separate use"
            } else {
                set extract ""
            }
            regsub -all %IPREXTRACT% $status $extract status
            regsub -all %EXPIRES% $status $expires status
        }
    }

    set authors ""
    set names ""
    foreach child [find_element author $attrs(.CHILDREN)] {
        array set av [list initials "" surname "" fullname "" role ""]
        array set av $elem($child)

        switch -- $av(role) {
            editor
                -
            "" {
            }

            default {
                unexpected error "invalid role attribute: $av(role)"
            }
        }

        set organization [find_element organization $av(.CHILDREN)]
        array set ov [list abbrev ""]
        if {[string compare $organization ""]} {
            array set ov $elem($organization)
        }
        if {![string compare $ov(abbrev) ""]} {
            set ov(abbrev) $ov(.CTEXT)
        }

        if {[string compare $av(initials) ""]} {
            set av(initials) [lindex [split $av(initials) .] 0].
        }
        set av(abbrev) "$av(initials) $av(surname)"
        if {[string length $av(abbrev)] == 1} {
            set av(abbrev) ""
            lappend names $ov(abbrev)
        } else {
            lappend names $av(surname)
            if {![string compare $av(role) editor]} {
                append av(abbrev) ", Ed."
            }
        }
        set authors [linsert $authors 0 [list $av(abbrev) $ov(abbrev)]]
    }

    set lastO ""
    set right ""
    foreach author $authors {
        if {[string compare [set value [lindex $author 1]] $lastO]} {
            set right [linsert $right 0 [set lastO $value]]
        }
        if {[string compare [set value [lindex $author 0]] ""]} {
            set right [linsert $right 0 $value]
        }
    }
    set day ""
    if {(![string compare $rv(number) ""]) \
            && (![catch { set day $dv(day) }])} {
        set day "$day, "
    }
    lappend right "$dv(month) $day$dv(year)"

    if {$options(.HEADER)} {
        lappend top $options(header)
    } elseif {[string compare $rv(number) ""]} {
        lappend top "RFC&nbsp;$rv(number)"
    } else {
        lappend top "Internet-Draft"
        lappend title $ofile
    }
    set l [string length [lindex $top end]]
    lappend top "$dv(month) $dv(year)"
    set l2 [string length [lindex $top end]]
    if {$l < $l2} {
        set l $l2
    }
    set l [expr 72 - 2 * ($l + 4)]
    incr l [expr $l2 < $l]
    if {[set l2 [string length $tv(abbrev)]] <= 0} {
        if {[string length $tv(.CTEXT)] > $l} {
            unexpected error "<title> element needs an abbrev attribute of at most $l characters"
        } else {
            set tv(abbrev) $tv(.CTEXT)
        }
    } elseif {$l2 > $l} {
        unexpected error "abbrev attribute of <title> element is still too long ($l2 > $l)"
    }
    set top [linsert $top 1 $tv(abbrev)]

    switch -- [llength $names] {
        1 {
            lappend bottom [lindex $names 0]
        }

        2 {
            lappend bottom "[lindex $names 0] &amp; [lindex $names 1]"
        }

        default {
            lappend bottom "[lindex $names 0], et al."
        }
    }
    if {$options(.FOOTER)} {
        lappend bottom $options(footer)
    } else {
        lappend bottom $category
    }

    regsub -all %YEAR% $copyshort $dv(year) copying

    set keywords {}
    foreach child [find_element keyword $attrs(.CHILDREN)] {
        array set kv $elem($child)
        lappend keywords $kv(.CTEXT)
    }

    front_${mode}_begin $left $right $top $bottom $title $status $copying \
                        $keywords $rv(xml:lang)
}

proc pass2end_front {elemX} {
    global elem passno
    global elemZ
    global options copyrightP noticeT
    global mode
    global crefs

    set toc ""
    set refs 0
    set irefP 0
    if {$options(.TOC)} {
        set last ""
        for {set elemY 1} {$elemY <= $elemZ} {incr elemY} {
            catch { unset cv }
            array set cv $elem($elemY)

            switch -- $cv(.NAME) {
                rfc {
                    if {(!$options(.PRIVATE)) && $copyrightP} {
                        set anchor ""
                        if {($passno == 3) && (![string compare $mode html])} {
                            set anchor rfc.copyright
                            set label "&#167;"
                        } else {
                            catch { set anchor $cv(.ANCHOR) }
                            set label ""
                        }
                        set noticeT "Intellectual Property and Copyright Statements"
                        set last [list $label $noticeT $anchor]
                    } else {
                        set noticeT ""
                    }
                }

                section
                    -
                appendix {
                    set x [llength [split [set label $cv(.COUNTER)] .]]
                    switch -- $cv(toc) {
                        include {
                        }

                        exclude {
                            continue
                        }

                        default {
                            if {$x > $options(.TOCDEPTH)} {
                                continue
                            }
                        }
                    }
                    if {[string first . $label] < 0} {
                        append label .
                    }
                    if {($options(.TOCINDENT)) && ($x > 1)} {
                        set x [expr ($x-1)*2]
                        set label [format "%*.*s" $x $x ""]$label
                    }
                    lappend toc [list $label $cv(title) $cv(.ANCHOR)]
                }

                back {
                    if {(!$options(.INLINE)) && ([array size crefs] > 0)} {
                        set anchor ""
                        if {($passno == 3) && (![string compare $mode html])} {
                            set anchor rfc.comments
                            set label "&#167;"
                        } else {
                            catch { set anchor $cv(.ANCHOR) }
                            set label ""
                        }
                        lappend toc [list $label "Editorial Comments" $anchor]
                    }

                    set anchor ""
                    if {($passno == 3) && (![string compare $mode html])} {
                        set anchor rfc.authors
                        set label "&#167;"
                    } else {
                        catch { set anchor $cv(.ANCHOR) }
                        set label ""
                    }
                    array set fv $elem(2)
                    set n [llength [find_element author $fv(.CHILDREN)]]
                    if {$n == 1} {
                        set title "Author's Address"
                    } else {
                        set title "Authors' Addresses"
                    }
                    lappend toc [list $label $title $anchor]
                }

                references {
                    set anchor ""
                    if {($passno == 3) && (![string compare $mode html])} {
                        set anchor rfc.references[incr refs]
                    } else {
                        catch { set anchor $cv(.ANCHOR) }
                    }
                    set label $cv(.COUNTER)
                    if {[catch { set title $cv(title) }]} {
                        set title References
                    }
                    if {(!$options(.INLINE)) && ([array size crefs] > 0)} {
                        set offset 2
                    } else {
                        set offset 1
                    }
                    set l [split $label .]
                    if {([llength $l] == 2) \
                            && (![string compare [lindex $l 1] 1])} {
                        set toc [linsert $toc [expr [llength $toc]-$offset] \
                                         [list [lindex $l 0]. \
                                               References $anchor]]
                    }
                    if {[string first . $label] < 0} {
                        append label .
                    } elseif {($options(.TOCINDENT))} {
                        set x [expr ($x-1)*2]
                        set label [format "%*.*s" 2 2 ""]$label
                    }
                    set toc [linsert $toc [expr [llength $toc]-$offset] \
                                     [list $label $title $anchor]]
                }

                iref {
                    set irefP 1
                }
            }
        }
        if {[string compare $last ""]} {
            lappend toc $last
        }
    }

    front_${mode}_end $toc $irefP
}

# the abstract/note elements

proc pass2begin_abstract {elemX} {
    global mode
    abstract_$mode
}

proc pass2begin_note {elemX} {
    global elem stack
    global mode

    set d 0
    foreach frame $stack {
        if {![string compare [lindex $frame 0] note]} {
            incr d
        }
    }

    array set attrs $elem($elemX)

    note_$mode $attrs(title) $d
}

# the section element

proc pass2begin_section {elemX {appendP 0}} {
    global elem stack
    global mode

    array set attrs [list anchor ""]
    array set attrs $elem($elemX)

    if {([lsearch0 $stack appendix] < 0) && ([lsearch0 $stack section] < 0)} {
        set top 1
    } else {
        set top 0
    }

    set prefix ""
    set s $attrs(.COUNTER)
    if {$top} {
        append s .
    }
    if {($appendP) || (([lsearch0 $stack back] >= 0) && ($top))} {
        set prefix "Appendix "
    }
    set title $attrs(title)

    set lines 0
    if {[llength $attrs(.CHILDREN)] > 0} {
        set elemY [lindex $attrs(.CHILDREN) 0]
        array set cv $elem($elemY)

        switch -- $cv(.NAME) {
            figure
                -
            texttable {
                incr lines [pass2begin_$cv(.NAME) $elemY 1]
            }

            default {
                incr lines 2
            }
        }
    }

    set attrs(.ANCHOR) \
        [section_$mode $prefix$s $top $title $lines $attrs(anchor)]

    set elem($elemX) [array get attrs]
}

proc pass2begin_appendix {elemX {appendP 0}} {
    pass2begin_section $elemX 1
}

proc section_title {elemX} {
    global elem

    array set attrs [list anchor "" title ""]
    array set attrs $elem($elemX)

    return $attrs(title)
}


# the t element

proc pass2begin_t {elemX} {
    global counter elem stack
    global mode

    array set attrs [list .COUNTER "" style "" hangText "" \
                          hangIndent "" anchor   ""]
    array set attrs $elem($elemX)
    set elem($elemX) [array get attrs]

    if {[string compare $attrs(.COUNTER) ""]} {
        set frame [lindex $stack end]
        array set av [lrange $frame 1 end]

        set elemY $av(elemN)
        array set av $elem($elemY)

        set attrs(hangIndent) $av(hangIndent)
        if {![string compare [set attrs(style) $av(style)] format]} {
            set attrs(style) hanging
            set format $av(format)
            set c $av(counter)

            if {![string compare $attrs(hangText) ""]} {
                if {[string first "%d" $format] >= 0} {
                    set attrs(hangText) \
                        [format $format [incr counter($c)]]
                } else {
                    set attrs(hangText) \
                        [format $format \
                                [offset2letters [incr counter($c)] 1]]
                }
            }
        }
        set elem($elemX) [array get attrs]
    }

    t_$mode begin $attrs(.COUNTER) $attrs(style) $attrs(hangText) \
            $attrs(.EDITNO)
}

proc pass2end_t {elemX} {
    global elem
    global mode

    array set attrs $elem($elemX)

    t_$mode end $attrs(.COUNTER) $attrs(style) $attrs(hangText) ""
}

# the list element

proc pass2begin_list {elemX} {
    global counter elem stack
    global mode

    set style empty
    set format ""
    set c ""
    set hangIndent 0
    foreach frame $stack {
        if {[string compare [lindex $frame 0] list]} {
            continue
        }
        array set av [lrange $frame 1 end]

        set elemY $av(elemN)
        array set av $elem($elemY)

        set style $av(style)
        set format $av(format)
        set hangIndent $av(hangIndent)
    }
    array set attrs [list counter ""]
    array set attrs $elem($elemX)
    catch { set hangIndent $attrs(hangIndent) }
    set attrs(hangIndent) $hangIndent
    catch {
        if {[string first "format " [set style $attrs(style)]]} {
            set format $attrs(format)
        } else {
            set style format
            if {[string compare \
                        [set format [string trimleft \
                                            [string range $attrs(style) 7 \
                                            end]]] ""]} {
                if {[set x [string first [set c "%d"] $format]] >= 0} {
                } elseif {[set x [string first [set c "%c"] $format]] >= 0} {
                    set format [streplace $format $x [expr $x+1] %s]
                } else {
                    unexpected error "missing %d/%c in format style"
                }
                if {[string first $c [string range $format $x end]] > 0} {
                    unexpected error "too many $c's in format style"
                }
                if {![string compare [set c $attrs(counter)] ""]} {
                    set c $format
                } elseif {[set x [string first "%d" $c]] >= 0} {
                } elseif {[set x [string first "%c" $c]] >= 0} {
                    set c  [streplace $c $x [expr $x+1] %s]
                }
                if {![info exists counter($c)]} {
                    set counter($c) 0
                }
            } else {
                set style hanging
                set format ""
            }
        }
    }
    array set attrs [list style $style format $format counter $c]
    set elem($elemX) [array get attrs]

    set counters ""
    set hangText ""
    foreach child [find_element t $attrs(.CHILDREN)] {
        array set tv $elem($child)

        lappend counters $tv(.COUNTER)
        catch { set hangText $tv(hangText) }
    }

    list_$mode begin $counters $attrs(style) $attrs(hangIndent) $hangText \
               [lsearch0 $stack t]
}

proc pass2end_list {elemX} {
    global elem stack
    global mode

    array set attrs $elem($elemX)

    list_$mode end "" $attrs(style) "" "" [lsearch0 $stack t]
}


# the figure and artwork elements

proc pass2begin_figure {elemX {internal 0}} {
    global elem
    global mode

    array set attrs [list anchor "" title ""]
    array set attrs $elem($elemX)

    catch { push_align $attrs(align) }

    set lines 0
    foreach p {preamble postamble} {
        if {[llength [find_element $p $attrs(.CHILDREN)]] == 1} {
            incr lines 3
        }
    }
    if {$lines > 5} {
        set lines 5
    }

    set artwork [find_element artwork $attrs(.CHILDREN)]
    array set av $elem($artwork)

    # <artwork> may be empty!
    catch { incr lines [llength [split $av(.CTEXT) "\n"]] }

    if {$internal} {
        return $lines
    }

    figure_$mode begin $lines $attrs(anchor) $attrs(title) [array get attrs]
}

proc pass2end_figure {elemX} {
    global elem
    global mode

    array set attrs [list anchor "" title ""]
    array set attrs $elem($elemX)

    figure_$mode end "" $attrs(anchor) $attrs(title) [array get attrs]

    if {[info exists attrs(align)]} {
        pop_align
    }
}

proc pass2begin_artwork {elemX} {
    global elem
    global mode

    array set attrs $elem($elemX)

    catch { push_align $attrs(align) }
    set align [current_align]

    catch {
        set lines 0
        # <artwork> may be empty!
        set ctext [split $attrs(.CTEXT) "\n"]
        set lines [llength $ctext]
        if {   ![string compare $mode html]
            || ![catch {set x $attrs(.TEXTWIDTH)}]
            || ![string compare $align ""]
            || ![string compare $align "left"]} {
            # break from catch
            error ""
        }
        set textwidth 0
        foreach l $ctext {
            set ll [string length [string trimright [chars_expand $l]]]
            if {$ll > $textwidth} {
                set textwidth $ll
            }
        }
        set attrs(.TEXTWIDTH) $textwidth
        set elem($elemX) [array get attrs]
    }

    artwork_$mode begin $lines [array get attrs]
}

proc pass2end_artwork {elemX} {
    global elem
    global mode

    array set attrs $elem($elemX)

    artwork_$mode end 0 [array get attrs]

    if {[info exists attrs(align)]} {
        pop_align
    }
}


# the preamble/postamble elements

proc pass2begin_preamble {elemX} {
    global elem
    global mode

    array set attrs $elem($elemX)

    preamble_$mode begin $attrs(.EDITNO)
}

proc pass2end_preamble {elemX} {
    global mode

    preamble_$mode end
}

proc pass2begin_postamble {elemX} {
    global elem
    global mode

    array set attrs $elem($elemX)

    postamble_$mode begin $attrs(.EDITNO)
}

proc pass2end_postamble {elemX} {
    global mode

    postamble_$mode end
}


# the texttable element

proc pass2begin_texttable {elemX {internal 0}} {
    global elem
    global mode
    global options

    array set attrs [list anchor "" title ""]
    array set attrs $elem($elemX)

    set lines 0
    foreach p {preamble postamble} {
        if {[llength [find_element $p $attrs(.CHILDREN)]] == 1} {
            incr lines 3
        }
    }
    if {$lines > 5} {
        set lines 5
    }

    set cols {}
    set aligns {}
    set empty 0
    set width 0
    set didP 0
    set ttcols [find_element ttcol $attrs(.CHILDREN)]
    foreach ttcol $ttcols {
        catch { unset cv }
        array set cv [list width "" align left]
        array set cv $elem($ttcol)

        switch -glob -- $cv(width) {
            "" {
                lappend cols ""
                incr empty
            }

            {[100]%}
                -
            {[1-9][0-9]%}
                -
            {[1-9]%} {
                lappend cols [string range $cv(width) 0 \
                                     [expr [string length $cv(width)]-2]]
                incr width [lindex $cols end]
                set didP 1
            }

            default {
                unexpected error "invalid width attribute: $cv(width)"
            }
        }

        lappend aligns $cv(align)
    }
    if {($width+$empty) > 100} {
        unexpected error "combined width greater than 100%"
    } elseif {$empty > 0} {
        set pct [expr (100-$width)/$empty]
        set pct1 [expr 100-($width+$pct*($empty-1))]

        set ncols {}
        foreach col $cols {
            if {![string compare $col ""]} {
                set col $pct1
                set pct1 $pct
            }
            lappend ncols $col
        }
        set cols $ncols
    } elseif {$width != 100} {
        unexpected error "combined width doesn't total 100%"
    }

    set colmax [llength $cols]
    set children [find_element c $attrs(.CHILDREN)]
    set rowmax [expr [llength $children]/$colmax]
    incr lines [expr 4 + $rowmax + ($options(.COMPACT) ? 0 : ($rowmax - 1))]

    if {$internal} {
        return $lines
    }

    set attrs(.COLS) $cols
    set elem($elemX) [array get attrs]

    set colno 0
    set aligns {}
    foreach ttcol $ttcols {
        catch { unset cv }
        array set cv [list width "" align left]
        array set cv $elem($ttcol)

        set cv(.WIDTH) [lindex $cols $colno]
        lappend aligns $cv(align)
        set cv(.COLNO) [list [incr colno] $colmax]

        set elem($ttcol) [array get cv]
    }

    set colno 0
    foreach c $children {
        catch { unset cv }
        array set cv $elem($c)

        set offset [expr $colno%$colmax]
        set cv(.ROWNO) [list [expr 1+($colno/$colmax)] $rowmax]
        set cv(.WIDTH) [lindex $cols $offset]
        set cv(.ALIGN) [lindex $aligns $offset]
        set cv(.COLNO) [list [incr offset] $colmax]
        incr colno

        set elem($c) [array get cv]
    }

    texttable_$mode begin $lines $attrs(anchor) $attrs(title) $didP
}

proc pass2end_texttable {elemX} {
    global elem
    global mode

    array set attrs [list anchor "" title ""]
    array set attrs $elem($elemX)

    texttable_$mode end "" $attrs(anchor) $attrs(title)
}

proc pass2begin_ttcol {elemX} {
    global elem
    global mode

    array set attrs [list width "" align left]
    array set attrs $elem($elemX)
    switch -- $attrs(align) {
        left
            -
        center
            -
        right {
        }

        default {
            unexpected error \
                "invalid value for align attribute: $attrs(align)"
        }
    }

    ttcol_$mode $attrs(.CTEXT) $attrs(align) $attrs(.COLNO) $attrs(.WIDTH)
}

proc pass2begin_c {elemX} {
    global elem
    global mode

    array set attrs $elem($elemX)
    c_$mode begin $attrs(.ROWNO) $attrs(.COLNO) $attrs(.ALIGN)
}

proc pass2end_c {elemX} {
    global elem
    global mode

    array set attrs $elem($elemX)
    c_$mode end $attrs(.ROWNO) $attrs(.COLNO) $attrs(.ALIGN)
}


# the xref element

proc pass2begin_xref {elemX} {
    global elem xref
    global mode

# pageno is ignored for now...
    array set attrs [list pageno false format default]
    array set attrs $elem($elemX)

    set anchor $attrs(target)
    xref_$mode $attrs(.CTEXT) $xref($anchor) $anchor $attrs(format)
}


# the eref element

proc pass2begin_eref {elemX} {
    global counter elem passno
    global mode

    array set attrs $elem($elemX)
    set t $attrs(target)

    if {$passno == 2} {
        if {![info exists counter(reference)]} {
            set counter(reference) 0
        }

        set c -1

        if {([string first "#" $t] < 0) \
                && ([string compare $attrs(.CTEXT) $t])} {
            switch -- $mode {
                nr  -
                txt {
                    global erefs

                    foreach {n tn} [array get erefs] {
                        if {![string compare $t $tn]} {
                            set c $n
                            break
                        }
                    }
                    if {$c < 0} {
                        set c [incr counter(reference)]
                    }
                }
            }
        }
        set attrs(.COUNTER) $c
        set elem($elemX) [array get attrs]
    }

    eref_$mode $attrs(.CTEXT) $attrs(.COUNTER) $t
}


# the cref element

proc pass2begin_cref {elemX} {
    global elem
    global mode
    global options

    array set attrs [list anchor "" source ""]
    array set attrs $elem($elemX)

    if {!$options(.COMMENTS)} {
        return
    }

    set text ""
    set attrs(.CTEXT) [string trim $attrs(.CTEXT)]
    while {[set x [string first "\n" $attrs(.CTEXT)]] >= 0} {
        if {$x > 0} {
            append text [string range $attrs(.CTEXT) 0 [expr $x-1]]
        }
        set attrs(.CTEXT) [string trimleft \
                                  [string range $attrs(.CTEXT) $x end]]
        if {[string length $attrs(.CTEXT)] > 0} {
            append text " "
        }
    }
    append text $attrs(.CTEXT)

    cref_$mode $text $attrs(.COUNTER) $attrs(source) $attrs(anchor)
}

proc cref_title {elemX} {
    global elem

    array set attrs [list anchor "" source ""]
    array set attrs $elem($elemX)

    return $attrs(.CTEXT)
}



# the iref element

proc pass2begin_iref {elemX} {
    global elem
    global mode

    array set attrs [list subitem "" primary false]
    array set attrs $elem($elemX)
    set flags [list primary $attrs(primary)]
    unset attrs(primary)
    set attrs(flags) $flags

    set attrs(.ANCHOR) [iref_$mode $attrs(item) $attrs(subitem) $flags]

    set elem($elemX) [array get attrs]
}


# the vspace element

proc pass2begin_vspace {elemX} {
    global elem
    global mode

    array set attrs [list blankLines 0]
    array set attrs $elem($elemX)
    set elem($elemX) [array get attrs]

    vspace_$mode $attrs(blankLines)
}


# the spanx element

proc pass2begin_spanx {elemX} {
    global elem
    global mode

    array set attrs [list style emph]
    array set attrs $elem($elemX)
    set elem($elemX) [array get attrs]

    spanx_$mode $attrs(.CTEXT) $attrs(style)
}


# the references/reference elements

# we intercept the back element so we can put the Author's addresses
# after the References section (if any) and before any Appendices

proc pass2begin_back {elemX} {
    global elem
    global mode
    global crefs erefs
    global options

    array set attrs $elem($elemX)

    if {[llength [set children [find_element references $attrs(.CHILDREN)]]] \
            == 1} {
        set erefP 1
    } else {
        set erefP 0
    }
    foreach child $children {
        pass2begin_references $child $erefP
    }
    if {(!$erefP) && ([array size erefs] > 0)} {
        erefs_$mode URIs
    }
    if {(!$options(.INLINE)) && ([array size crefs] > 0)} {
        crefs_$mode "Editorial Comments"
    }

    array set fv $elem(2)

    set authors ""
    foreach child [find_element author $fv(.CHILDREN)] {
        array set av [list initials "" surname "" fullname "" role ""]
        array set av $elem($child)

        set organization [find_element organization $av(.CHILDREN)]
        array set ov [list abbrev ""]
        if {[string compare $organization ""]} {
            array set ov $elem($organization)
        }

        set block1 ""
        if {[string compare $av(fullname) ""]} {
            if {![string compare $av(role) editor]} {
                append av(fullname) " (editor)"
            }
            lappend block1 $av(fullname)
        }
        if {[string compare $ov(.CTEXT) ""]} {
            lappend block1 $ov(.CTEXT)
        }

        set address [find_element address $av(.CHILDREN)]
        set block2 ""
        if {[llength $address] == 1} {
            array set bv $elem($address)

            set postal [find_element postal $bv(.CHILDREN)]
            if {[llength $postal] == 1} {
                array set pv $elem($postal)

                foreach street [find_element street $pv(.CHILDREN)] {
                    array set sv $elem($street)

                    if {[string compare $sv(.CTEXT) ""]} {
                        lappend block1 $sv(.CTEXT)
                    }
                }

                set s ""
                foreach e {city region code} t {"" ", " "  "} {
                    set f [find_element $e $pv(.CHILDREN)]
                    if {[llength $f] == 1} {
                        catch { unset fv }
                        array set fv $elem($f)

                        if {[string compare $s ""]} {
                            append s $t
                        }
                        append s $fv(.CTEXT)
                    }
                }
                if {[string compare $s ""]} {
                    lappend block1 $s
                }
                set f [find_element country $pv(.CHILDREN)]
                if {[llength $f] == 1} {
                    catch { unset fv }
                    array set fv $elem($f)

                    lappend block1 $fv(.CTEXT)
                }
            }

            set block2 ""
            foreach e {phone facsimile email uri} {
                set f [find_element $e $bv(.CHILDREN)]
                if {[llength $f] == 1} {
                    catch { unset fv }
                    array set fv $elem($f)

                    lappend block2 [list $e $fv(.CTEXT)]
                }
            }
        }

        lappend authors [list $block1 $block2]
    }


    if {($options(.STRICT)) && ([set l [llength $authors]] > 5)} {
        unexpected error "$l authors, maximum of 5 allowed"
    }

    set attrs(.ANCHOR) [back_$mode $authors]
    set elem($elemX) [array get attrs]
}

proc pass2begin_references {elemX erefP} {
    global elem
    global mode
    global options

    array set attrs [list title References]
    array set attrs $elem($elemX)

    if {[llength [split [set prefix $attrs(.COUNTER)] .]] == 1} {
        append prefix .
    }
    set attrs(.ANCHOR) [references_$mode begin $prefix $attrs(title)]
    set elem($elemX) [array get attrs]
    set children [find_element reference $attrs(.CHILDREN)]
    if {$options(.SORTREFS)} {
        set children [lsort -command sort_references $children]
    }
    set width 0
    foreach child $children {
        array set x $elem($child)
        if {[set y [string length $x(.COUNTER)]] > $width} {
            set width $y
        }

        unset x
    }
    if {$width > 7} {
        set width 7
    }
    foreach child $children {
        pass2begin_reference $child $width
    }
    references_$mode end $erefP
}

proc sort_references {elemX elemY} {
    global elem
    global options

    array set attrX $elem($elemX)
    array set attrY $elem($elemY)
    if {$options(.SYMREFS)} {
        return [string compare $attrX(anchor) $attrY(anchor)]
    } else {
        return [expr $attrX(.COUNTER)-$attrY(.COUNTER)]
    }
}

proc pass2begin_reference {elemX width} {
    global elem
    global mode

    array set attrs [list anchor "" target "" target2 ""]
    array set attrs $elem($elemX)
    if {![info exists attrs(.ANNOTATIONS)]} {
        set attrs(.ANNOTATIONS) {}
        set elem($elemX) [array get attrs]
    }

    set front [find_element front $attrs(.CHILDREN)]
    array set fv $elem($front)

    set names [ref_names $elemX]
    set title [ref_title $elemX]

    set series ""
    foreach child [find_element seriesInfo $attrs(.CHILDREN)] {
# backwards-compatibility... (the attributes are actually mandatory)
        catch { unset sv }
        array set sv $elem($child)
        if {([info exists sv(name)]) && ([info exists sv(value)])} {
            lappend series "$sv(name)&nbsp;$sv(value)"
        } else {
            lappend series $sv(.CTEXT)
        }
    }

    set formats {}
    foreach child [find_element format $attrs(.CHILDREN)] {
        lappend formats $elem($child)
    }

    set date [ref_date $elemX]

    reference_$mode $attrs(.COUNTER) $names $title $series $formats $date \
                    $attrs(anchor) $attrs(target) $attrs(target2) $width \
                    $attrs(.ANNOTATIONS)
}

proc ref_names {elemX} {
    global elem

    array set attrs [list anchor "" target "" target2 ""]
    array set attrs $elem($elemX)

    set front [find_element front $attrs(.CHILDREN)]
    array set fv $elem($front)

    set childN [llength [set children [find_element author $fv(.CHILDREN)]]]

    set childA 0
    set names {}
    foreach child [find_element author $fv(.CHILDREN)] {
        incr childA

        array set av [list initials "" surname "" fullname "" role ""]
        array set av $elem($child)

        set organization [find_element organization $av(.CHILDREN)]
        array set ov [list .CTEXT "" abbrev ""]
        if {[string compare $organization ""]} {
            array set ov $elem($organization)
            if {![string compare $ov(abbrev) ""]} {
                set ov(abbrev) $ov(.CTEXT)
            }
        }

        set mref ""
        set uref ""
        set address [find_element address $av(.CHILDREN)]
        if {[llength $address] == 1} {
            array set bv $elem($address)

            foreach {k v p} {email mref mailto: uri uref ""} {
                set u [find_element $k $bv(.CHILDREN)]
                if {[llength $u] == 1} {
                    catch { unset uv }
                    array set uv $elem($u)

                    set $v $p$uv(.CTEXT)
                }
            }
        }
        if {![string compare $mref ""]} {
            set mref $uref
        } elseif {![string compare $uref ""]} {
            set uref $mref
        }

        if {[string compare $av(initials) ""]} {
            set av(initials) [lindex [split $av(initials) .] 0].
        }
        if {($childA > 1) && ($childA == $childN)} {
            set av(abbrev) [string trimleft "$av(initials) $av(surname)"]
        } elseif {[string compare $av(initials) ""]} {
            set av(abbrev) "$av(surname), $av(initials)"
        } else {
            set av(abbrev) $av(surname)
        }
        if {[string length $av(abbrev)] == 0} {
            lappend names [list $ov(.CTEXT) $uref]
        } else {
            if {![string compare $av(role) editor]} {
                append av(abbrev) ", Ed."
            }
            lappend names [list $av(abbrev) $mref]
        }
    }
    set hack $names

    set names {}
    foreach name $hack {
        if {[string compare [lindex $name 0] ""]} {
            lappend names $name
        }
    }

    return $names
}

proc ref_title {elemX} {
    global elem

    array set attrs [list anchor "" target "" target2 ""]
    array set attrs $elem($elemX)

    set front [find_element front $attrs(.CHILDREN)]
    array set fv $elem($front)

    set title [find_element title $fv(.CHILDREN)]
    array set tv [list abbrev ""]
    array set tv $elem($title)

    return $tv(.CTEXT)
}

proc ref_date {elemX} {
    global elem

    array set attrs [list anchor "" target "" target2 ""]
    array set attrs $elem($elemX)

    set front [find_element front $attrs(.CHILDREN)]
    array set fv $elem($front)

    set date [find_element date $fv(.CHILDREN)]
    if {[catch { array set dv $elem($date) }]} {
        return ""
    }
    if {([info exists dv(month)]) && ([string compare $dv(month) ""])} {
        set date "$dv(month)&nbsp;$dv(year)"
    } else {
        set date $dv(year)
    }

    return $date
}

proc pass2begin_annotation {elemX} {
    global mode

    annotation_$mode begin
}

proc pass2end_annotation {elemX} {
    global elem stack
    global mode

    set frame [lindex $stack end]
    array set av [lrange $frame 1 end]
    set elemY $av(elemN)
    array set av $elem($elemY)

    lappend av(.ANNOTATIONS) [annotation_$mode end]

    set elem($elemY) [array get av]
}

proc find_element {name children} {
    global elem

    set result ""
    foreach child $children {
        array set attrs $elem($child)

        if {![string compare $attrs(.NAME) $name]} {
            lappend result $child
        }
    }

    return $result
}

# could use "lsearch -glob" followed by a "string compare", but there are
# some amusing corner cases with that...

proc lsearch0 {list exact} {
    set x 0
    foreach elem $list {
        if {![string compare [lindex $elem 0] $exact]} {
            return $x
        }
        incr x
    }

    return -1
}


#
# Here is the page model for both the txt and nr rendering engines.
#
# Each line has at most 72 columns from the left edge, including any
# left margin, but excluding the line terminator.  Every output character
# is from the ASCII repertoire and the only control character used is
# the line-feed (LF); the character-tabulation (HT) character is never
# used.
#
# Each page has the following lines (0-based lineno variable):
#    0:  header line (blank line on first page)
#    1:  blank line
#    2:  blank line
#    3:  1st line of content
#   ...
#   50:  48th line of content
#   51:  blank line
#   52:  blank line
#   53:  blank line
#   54:  footer line
#   55:  form-feed character (followed by line terminator)
# Once processed through nroff and the fix.sh script (from
# 2-nroff.template), the nr output differs from this in two ways. It
# has three extra blank lines (that could be numbered -3, -2, and -1,
# for a total of six) at the very beginning of the document (so the first
# page is that much longer). It also has no line terminator following the
# very last form-feed character of the file. These differences originate
# in the design of the fix.sh script.
#
# Header and footer lines each have three parts:  left, center, and right.
#
# Output line numbers, when reported to the user, should be 1-based.
#


#
# text output
#


proc rfc_txt {irefs iprstmt copying newP} {
    global options copyrightP iprP
    global funding validity
    global pageno
    global indexpg

    end_page_txt

    if {[llength $irefs] > 0} {
        set indexpg $pageno

        write_line_txt "Index"

        push_indent 9
        foreach iref $irefs {
            foreach {L item subitem flags pages} $iref { break }

            if {[string compare $L ""]} {
                write_line_txt ""
                push_indent -9
                write_text_txt $L
                flush_text
                pop_indent
            }

            set subitem [chars_expand $subitem]
            if {[string compare $item ""]} {
                push_indent -6
                write_text_txt [chars_expand $item]
                if {[string compare $subitem ""]} {
                    flush_text
                    pop_indent
                    push_indent -3
                    write_text_txt $subitem
                }
            } else {
                push_indent -3
                write_text_txt $subitem
            }
            pop_indent

            write_text_txt "  [collapsed_num_list $pages]"
            flush_text
        }
        pop_indent

        end_page_txt
    }

    if {(!$options(.PRIVATE)) && $copyrightP} {
        set result $pageno

        if {$iprP} {
            global iprurl ipremail

            write_line_txt "Intellectual Property Statement"

            regsub -all %IPRURL% $iprstmt $iprurl iprstmt
            regsub -all %IPREMAIL% $iprstmt $ipremail iprstmt

            foreach para $iprstmt {
                write_line_txt ""
                pcdata_txt $para
            }
            write_line_txt "" -1
            write_line_txt "" -1
        }

        if {$newP} {
            if {![have_lines 4]} {
                end_page_txt
            }

            write_line_txt "Disclaimer of Validity"

            foreach para $validity {
                write_line_txt ""
                pcdata_txt $para
            }
            write_line_txt "" -1
            write_line_txt "" -1
        }

        if {![have_lines 4]} {
            end_page_txt
        }

        if {$newP} {
            write_line_txt "Copyright Statement"
        } else {
            write_line_txt "Full Copyright Statement"
        }

        foreach para $copying {
            write_line_txt ""
            pcdata_txt $para
        }
        write_line_txt "" -1
        write_line_txt "" -1

        if {![have_lines 4]} {
            end_page_txt
        }

        write_line_txt "Acknowledgment"
        write_line_txt ""
        pcdata_txt $funding

        end_page_txt
    } else {
        set result ""
    }

    return $result
}

proc front_txt_begin {left right top bottom title status copying keywords
                      lang} {
    global options copyrightP
    global header footer lineno pageno blankP
    global eatP
    global passno indexpg
    global indent

    set header [three_parts $top]
    set footer [string trimright [three_parts $bottom]]
    write_it ""
    set lineno 1
    set pageno 1
    set blankP 1
    set eatP 0

    if {$passno == 2} {
        set indexpg 0
    }

    for {set i 0} {$i < 2} {incr i} {
        write_line_txt "" -1
    }

    set indent 0

    if {$options(.TOPBLOCK)} {
        set left [munge_long $left]
        set right [munge_long $right]
        foreach l $left r $right {
            set l [chars_expand $l]
            set r [chars_expand $r]
            set len [expr 72-[string length $l]]
            write_line_txt [format %s%*.*s $l $len $len $r]
        }
        write_line_txt "" -1
        write_line_txt "" -1
    }

    foreach line $title {
        write_text_txt [chars_expand $line] c
    }

    write_line_txt "" -1

    set indent 3

    if {!$options(.PRIVATE)} {
        write_line_txt "Status of this Memo"
        foreach para $status {
            write_line_txt ""
            pcdata_txt $para
        }
    }

    if {(!$options(.PRIVATE)) && $copyrightP} {
        write_line_txt "" -1
        write_line_txt "Copyright Notice"
        write_line_txt "" -1
        pcdata_txt $copying
    }
}

proc three_parts {stuff} {
    set result [nbsp_expand_txt [chars_expand [lindex $stuff 0]]]
    set len [string length $result]

    set text [nbsp_expand_txt [chars_expand [lindex $stuff 1]]]
    set len [expr (72-[string length $text]+1)/2-$len]
    if {$len < 4} {
        set len 4
    }
    append result [format %*.*s%s $len $len "" $text]
    set len [string length [set text [nbsp_expand_txt [chars_expand [lindex $stuff 2]]]]]
    set len [expr (72-[string length $result])-$len]
    append result [format %*.*s%s $len $len "" $text]

    return $result
}

proc front_txt_end {toc irefP} {
    global options noticeT
    global lineno
    global indexpg

    if {$options(.TOC)} {
        set last [lindex $toc end]
        if {[string compare [lindex $last 1] $noticeT]} {
            set last ""
        } else {
            set toc [lreplace $toc end end]
        }
        if {$irefP} {
            lappend toc [list "" Index $indexpg]
        }
        if {[string compare $last ""]} {
            lappend toc $last
        }

        if {(![have_lines [expr [llength $toc]+3]]) || ($lineno > 17)} {
            end_page_txt
        } else {
            write_line_txt "" -1
        }
        write_line_txt "Table of Contents"
        write_line_txt "" -1

        set len1 0
        set len2 0
        foreach c $toc {
            if {[set x [string length [lindex $c 0]]] > $len1} {
                set len1 $x
            }
            if {[set x [string length [lindex $c 2]]] > $len2} {
                set len2 $x
            }
        }
        set len3 [expr 5-$len2]
        set len2 5
        set mid [expr 72-($len1+$len2+5)]

        set lenX $len1
        set midX $mid
        set oddX [expr $mid%2]
        foreach c $toc {
            if {!$options(.TOCOMPACT)} {
                if {[string last . [lindex $c 0]] \
                        == [expr [string length [lindex $c 0]]-1]} {
                    write_line_txt ""
                }
            }
            if {$options(.TOCINDENT)} {
                set len1 [expr [set y [string length [lindex $c 0]]]+1]
                if {$y == 0} {
                    incr len1 2
                }
                set mid [expr $midX+$lenX-$len1]
                set oddP [expr $mid%2]
                if {$oddP != $oddX} {
                    incr len1 1
                    incr mid -1
                }
            }
            set s1 [format "   %-*.*s " $len1 $len1 [lindex $c 0]]
            set s2 [format " %*.*s" $len2 $len2 [lindex $c 2]]
            set title [chars_expand [string trim [lindex $c 1]]]
            while {[set i [string length $title]] > $mid} {
                set phrase [string range $title 0 [expr $mid-1]]
                if {[set x [string last " " $phrase]] < 0} {
                    if {[set x [string first " " $title]] < 0} {
                        break
                    }
                }
                write_toc_txt $s1 [string range $title 0 [expr $x-1]] \
                        [format " %-*.*s" $len2 $len2 ""] $mid 0
                set s1 [format "   %-*.*s " $len1 $len1 ""]
                set title [string trimleft [string range $title $x end]]
            }
            if {$len3 > 0} {
                set s2 [string range $s2 $len3 end]
            }
            write_toc_txt $s1 $title $s2 [expr $mid+$len3] 1
        }
    }

    if {($options(.TOC) || !$options(.COMPACT))} {
        end_page_txt
    }
}

proc write_toc_txt {s1 title s2 len dot} {
    global mode

    set x [string length $title]
    if {($dot) && ($x < $len)} {
        if {$x%2} {
            append title " "
            incr x
        }
        while {$x < $len} {
            append title " ."
            incr x 2
        }
    }

    write_line_$mode [format "%s%-*.*s%s" $s1 $len $len $title $s2]
}

proc abstract_txt {} {
    write_line_txt "" -1
    write_line_txt "Abstract"
    write_line_txt "" -1
}

proc note_txt {title depth} {
    write_line_txt "" -1
    write_line_txt [chars_expand $title]
    write_line_txt "" -1
}

proc section_txt {prefix top title lines anchor} {
    global options
    global pageno

    if {($top && !$options(.COMPACT)) || (![have_lines [expr $lines+2]])} {
        end_page_txt
    } else {
        write_line_txt "" -1
    }

    push_indent -3
    write_text_txt "$prefix  "
    push_indent [expr [string length $prefix]+2]
    write_text_txt [chars_expand $title]
    flush_text
    pop_indent
    pop_indent

    return $pageno
}

proc t_txt {tag counter style hangText editNo} {
    global options
    global eatP

    if {$eatP < 0} {
        set eatP 1
    }
    if {![string compare $tag end]} {
        return
    }

    if {[string compare $counter ""]} {
        set pos [pop_indent]
        set l [split $counter .]
        set lines 3
        switch -- $style {
            letters {
                set counter [offset2letters [lindex $l end] [llength $l]]
                # prevent two_spaces from kicking in.
                append counter ".\xA0"
            }

            numbers {
                # prevent two_spaces from kicking in.
                set counter "[lindex $l end].\xA0"
            }

            symbols {
                set counter "[lindex { - o * + } [expr [llength $l]%4]] "
            }

            hanging {
                # prevent two_spaces from kicking in.
                set counter "[chars_expand $hangText]\xA0"
                set lines 5
            }

            default {
                set counter "  "
            }
        }
        if {![have_lines $lines]} {
            end_page_txt
        }
        if {$options(.EDITING)} {
            write_editno_txt $editNo
        } elseif {!$options(.SUBCOMPACT)} {
            write_line_txt ""
        }
        write_text_txt [format "%-[expr $pos-0]s" $counter]
        push_indent $pos
    } else {
        if {$options(.EDITING)} {
            write_editno_txt $editNo
        } else {
            write_line_txt ""
        }
    }

    set eatP 1
}

proc offset2letters {offset depth} {
    set alpha [lindex [list "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                            "abcdefghijklmnopqrstuvwxyz"] [expr $depth%2]]
    set letters ""
    for {} {$offset > 0} {set offset [expr $offset/26]} {
        incr offset -1
        set letters [string index $alpha [expr $offset%26]]$letters
    }

    return $letters
}

proc list_txt {tag counters style hangIndent hangText suprT} {
    global options
    global eatP

    switch -- $tag {
        begin {
            switch -- $style {
                letters {
                  set i [expr int(log([llength $counters])/log(26))+2]
                }

                numbers {
                    set i 0
                    foreach counter $counters {
                        if {[set j [string length \
                                           [lindex [split $counter .] end]]] \
                                > $i} {
                            set i $j
                        }
                    }
                    incr i 1
                }

                format {
                    set i [expr [string length [chars_expand $hangText]]-1]
                }

                default {
                    set i 1
                }
            }
            if {[incr i 2] > $hangIndent} {
                push_indent [expr $i+0]
            } else {
                push_indent [expr $hangIndent+0]
            }
        }

        end {
            flush_text
            if {!$options(.SUBCOMPACT)} {
                write_line_txt ""
            }
            pop_indent

            set eatP 1
        }
    }
}

proc figure_txt {tag lines anchor title {av {}}} {
    global xref
    global mode

    switch -- $tag {
        begin {
            if {[string compare $anchor ""]} {
                array set av2 $xref($anchor)
                set x [string length $av2(value)]
                incr x 7
                if {[string compare $title ""]} {
                    incr x [string length [chars_expand $title]]
                    incr x 2
                }
                # Approximation based on a line length of 69 with a
                # weighted average of half-word lengths of 3.7 (4).
                incr lines [expr 1 + ($x + 64) / 65]
            }
            if {![have_lines $lines]} {
                end_page_$mode
            }
            flush_text
        }

        end {
            if {[string compare $anchor ""]} {
                array set av2 $xref($anchor)
                set prefix "Figure\xA0$av2(value)"
                if {[string compare $title ""]} {
                    append prefix ": [chars_expand $title]"
                }
                write_line_$mode ""
                write_text_$mode $prefix c
                write_line_$mode ""
            }
        }
    }
}

proc artwork_txt {tag lines {av {}}} {
    global mode

    switch -- $tag {
        begin {
            # This was done for the whole figure, but let's
            # try it for the artwork alone, just in case.
            if {![have_lines $lines]} {
                end_page_$mode
            }
        }
    }
}

proc preamble_txt {tag {editNo ""}} {
    global options
    global eatP
    global mode

    switch -- $tag {
        begin {
            set eatP 1
            if {$options(.EDITING)} {
                write_editno_$mode $editNo
            } else {
                write_line_$mode ""
            }
        }
    }
}

proc postamble_txt {tag {editNo ""}} {
    global options
    global eatP
    global mode

    switch -- $tag {
        begin {
            cellE
            set eatP 1
            if {$options(.EDITING)} {
                write_editno_$mode $editNo
            }
        }
    }
}

proc texttable_txt {tag lines anchor title {didP 0}} {
    global xref
    global mode

    switch -- $tag {
        begin {
            if {[string compare $anchor ""]} {
                array set av $xref($anchor)
                set x [string length $av(value)]
                incr x 6
                if {[string compare $title ""]} {
                    incr x [string length [chars_expand $title]]
                    incr x 2
                }
                # Approximation based on a line length of 69 with a
                # weighted average of half-word lengths of 3.7 (4).
                incr lines [expr 1 + ($x + 64) / 65]
            }
            if {![have_lines $lines]} {
                end_page_$mode
            }
            flush_text

            cellB $didP
        }

        end {
            cellE

            if {[string compare $anchor ""]} {
                array set av $xref($anchor)
                set prefix "Table $av(value)"
                if {[string compare $title ""]} {
                    append prefix ": [chars_expand $title]"
                }
                write_line_$mode ""
                write_text_$mode $prefix c
                write_line_$mode ""
            }
        }
    }
}

proc ttcol_txt {text align col width} {
    cellP $text 0 [lindex $col 0] $width $align
}

proc c_txt {tag row col align} {
    if {![string compare $tag begin]} {
        cellP "" [lindex $row 0] [lindex $col 0]
    }
}

proc cellB {didP} {
    global cellW

    set cellW $didP
}

proc cellE {} {
    global options
    global mode
    global rowNo colNo cells cellW

    if {[llength [array names cells]] == 0} {
        return
    }

    set overhead [expr [llength [set cols $cells(width)]]*3+1]
    set colNo $cells(maxcol)

    set max {}
    foreach col $cols {
        lappend max 0
    }
    for {set row 0} {$row <= $rowNo} {incr row} {
        for {set column 1} {$column <= $colNo} {incr column} {
            if {![info exists cells($row,$column)]} {
                set cells($row,$column) ""
            }
            set x [string length $cells($row,$column)]
            if {$x > [lindex $max [set y [expr $column-1]]]} {
                set max [lreplace $max $y $y $x]
            }
        }
    }

    set width 0
    foreach x $max {
        incr width $x
    }
    if {($cellW) || ($width+$overhead > 72)} {
        set width 0
        foreach col $cols {
            incr width $col
        }
        set prefix "   "
        incr overhead 3
    } else {
        set cols $max
        set x [expr (72-($width+$overhead))/2]
        set prefix [format "%*.*s" $x $x ""]
    }

    if {$width+$overhead > 72} {
        set actual [expr 72-$overhead]
        set ncols {}
        set width 0
        set lo 101
        set hi 0
        foreach col $cols {
            if {[set ncol [expr round($col*($actual/100.0))]] < 3} {
                set ncol 3
            }
            if {$ncol > 3} {
                if {$ncol > $hi} { set hi $ncol }
                if {$ncol < $lo} { set lo $ncol }
            } else {
                set ncol $col
            }
            lappend ncols $ncol
            incr width $ncol
        }
        set cols $ncols

        while {$width != $actual} {
            set ncols {}
            if {$width < $actual} {
                set didP 1
                set didC $lo
            } else {
                set didP -1
                set didC $hi
            }
            set width 0
            set lo 101
            set hi 0
            foreach ncol $cols {
                if {($didP != 0) && ($ncol == $didC)} {
                    set ncol [expr $ncol+($didP)]
                    set didP 0
                }
                if {$ncol > $hi} { set hi $ncol }
                if {$ncol < $lo} { set lo $ncol }
                lappend ncols $ncol
                incr width $ncol
            }
            set cols $ncols
             if {$didP != 0} {
                unexpected error "unable to normalize column widths"
            }
        }
    }

    if {![string compare $mode nr]} {
        condwrite_nf_nr
    }

    set allP 0
    set halfP 0
    set colC " "
    set dashC "-"
    set rowC " "
    switch -- [set cellR full] {
        none {
            set dashC " "
        }

        headers {
            set halfP 1
        }

        full {
            set allP 1
            set colC "|"
            set rowC "+"
        }
    }

    foreach cell [array names cells *,*] {
        set column [expr [lindex [split $cell ,] 1]-1]
        set cells($cell) [::textutil::adjust::adjust $cells($cell) \
                              -justify      [lindex $cells(align) $column] \
                              -length       [set w [lindex $cols $column]] \
                              -full         true \
                              -strictlength true]
# ...adjust really needs some work
        set pad [format %*.*s $w $w ""]
        if {[string first "$pad\n" $cells($cell)] == 0} {
            set cells($cell) [string range $cells($cell) [expr $w+1] end]
        }

# this will work only for left-justified errors...
        if {[set nlines [llength [set lines [split $cells($cell) "\n"]]]] \
                > 1} {
            set pre ""
            set post ""
            for {set lineno 0} {$lineno < $nlines} {incr lineno} {
                set line $post[lindex $lines $lineno]
                set post ""
                if {[string length $line] > $w} {
                    append pre [string range $line 0 [expr $w-1]]
                    set post [string range $line $w end]
                } else {
                    append pre $line
                }
                append pre "\n"
            }
            if {[string compare $post ""]} {
                append pre "$post\n"
            }
            set cells($cell) [string trimright $pre]
        }
    }
    catch { unset pre post }
    catch { unset line }

    # Precompute number of lines in each row.
    set row_lines {}
    for {set row 0} {$row <= $rowNo} {incr row} {
        set lines 0
        foreach cell [array name cells $row,*] {
            if {[set x [llength [split $cells($cell) "\n"]]] > $lines} {
                set lines $x
            }
        }
        lappend row_lines $lines
    }

    write_line_$mode ""

    # Attempt to fit header (row 0) and row 1 in same page.
    if {$rowNo >= 1} {
        set lines $allP
        incr lines [lindex $row_lines 0]
        incr lines [expr   (   !$options(.COMPACT) \
                            ||  [string compare $cellR none]) \
                         + (   ($rowNo == 1) \
                            && ![string compare $cellR full])]
        incr lines [lindex $row_lines 1]

        if {![have_lines $lines]} {
            end_page_$mode
        }
    }

    # Write top line.
    if {$allP} {
        set image $prefix
        foreach col $cols {
            append image "+-[::textutil::strRepeat "-" $col]-"
        }
        append image "+"
        write_line_$mode $image
    }

    # Precompute separator line.
    set hit_image $prefix
    foreach col $cols {
        append hit_image \
               "$rowC$dashC[::textutil::strRepeat $dashC $col]$dashC"
    }
    append hit_image $rowC

    # Precompute blank line.
    set blank_image $prefix
    for {set column 1} {$column <= $colNo} {incr column} {
        set width [lindex $cols [expr $column-1]]
        append blank_image [format "$colC %-*.*s " $width $width ""]
    }
    append blank_image $colC

    # Generate each cell row.
    for {set row 0} {$row <= $rowNo} {incr row} {
        set lines [lindex $row_lines $row]

        set hitP 0
        switch -- $cellR {
            none    { if {$row == 0 && !$options(.COMPACT)} { set hitP 1 } }
            headers { if {$row == 0}                        { set hitP 1 } }
            full    { if {$row == 0 || $row == $rowNo}      { set hitP 1 } }
        }

        if {![is_at_page_start]} {
            set blkP [expr ($row > 1) && !$options(.COMPACT)]
            if {![have_lines [expr $blkP + $lines + $hitP]]} {
                if {$blkP && [have_lines 1]} {
                    # Totally optional.  Only if a line is available.
                    write_line_$mode $blank_image
                }
                end_page_$mode
            } elseif {$blkP} {
                write_line_$mode $blank_image
            }
        }

        for {set line 0} {$line < $lines} {incr line} {
            set image $prefix
            for {set column 1} {$column <= $colNo} {incr column} {
                set width [lindex $cols [expr $column-1]]
                set data [format "%-*.*s" $width $width \
                                 [lindex [split $cells($row,$column) "\n"] \
                                         $line]]
                append image "$colC $data "
            }
            append image $colC
            write_line_$mode $image
        }

        if {$hitP} {
            write_line_$mode $hit_image
        }
    }
    write_line_$mode ""

    unset cells
}

proc cellP {data {row -1} {col -1} {width -1} {align ""}} {
    global rowNo colNo cells
    global mode
    global annoP

    if {[info exists annoP]} {
        if {[string compare $mode html]} {
            set data [chars_expand $data 0]
        }
        append cells(0,0) $data
        return 1
    }

    if {$row == -1} {
        if {[llength [array names cells]] == 0} {
            return 0
        }
    } else {
        set rowNo $row
        set colNo $col
        if {$width > 0} {
            lappend cells(width) $width
            lappend cells(align) $align
            set cells(maxcol) $col
        }
    }

    append cells($rowNo,$colNo) [chars_expand $data 0]
    return 1
}


proc xref_txt {text av target format {hackP 0}} {
    global elem
    global eatP
    global mode

    array set attrs $av

    set elemY $attrs(elemN)
    array set tv [list title ""]
    array set tv $elem($elemY)

    switch -- $attrs(type) {
        section {
            set line "Section\xA0$attrs(value)"
        }

        appendix {
            set line "Appendix\xA0$attrs(value)"
        }

        figure {
            set line "Figure\xA0$attrs(value)"
        }

        texttable {
            set line "Table\xA0$attrs(value)"
        }

        cref {
            set line "Comment\xA0$attrs(value)"
        }

        t {
            set line "Paragraph\xA0$attrs(value)"
        }

        default {
            set line "\[$attrs(value)\]"
        }
    }
    if {$hackP} {
        return $line
    }

    if {![string compare $format none]} {
        if {![string compare [set line [chars_expand $text]] ""]} {
            set eatP -1
            return
        }
    } elseif {[string compare $text ""]} {
        switch -- $attrs(type) {
            section
                -
            appendix
                -
            figure
                -
            texttable {
                set line "[chars_expand $text] ($line)"
            }

            default {
                set line "[chars_expand $text] $line"
            }
        }
    } else {
        switch -- $format {
            counter {
                set line $attrs(value)
            }

            title {
                set line $tv(title)
            }

            default {
            }
        }
    }

    if {![cellP $line]} {
        set eatP 0
        write_text_$mode $line
    }

    set eatP -1
}

proc eref_txt {text counter target} {
    global eatP
    global erefs
    global mode

    if {![string compare $text ""]} {
        set line "<$target>"
    } elseif {([string first "#" $target] < 0) \
                  && ([string compare $text $target])} {
        set erefs($counter) $target
        set line "$text\xA0\[$counter\]"
    } else {
        set line $text
    }
    if {![cellP $line]} {
        set eatP 0
        write_text_$mode [chars_expand $line]
    }

    set eatP -1
}

proc cref_txt {text counter source anchor} {
    global options
    global eatP
    global crefs
    global mode

    set comments ""
    if {[string compare $source ""]} {
        set comments "${source}: "
    }
    append comments $text
    set crefs($counter) [list $anchor $source $text $comments]

    if {$options(.INLINE)} {
        set line "\[\[$counter: $text"
        if {[string compare $source ""]} {
            append line " --$source"
        }
        append line "\]\]"
    } else {
        set line "\[$counter\]"
    }
    if {![cellP $line]} {
        set eatP 0
        pcdata_$mode $line
    }

    set eatP -1
}

proc iref_txt {item subitem flags} {
    global pageno

    return $pageno
}

proc vspace_txt {lines} {
    global lineno
    global eatP
    global mode

    if {[is_at_page_start]} {
        return
    }
    if {$lineno + $lines >= 51} {
        # l+l == 51 would fit, but leave nothing.
        end_page_$mode
    } else {
        switch -- $mode {
            txt {
                while {[incr lines -1] >= 0} {
                    write_it ""
                    incr lineno
                }
            }

            nr {
                if {$lines > 0} {
                    write_it ".sp $lines"
                    incr lineno $lines
                } else {
                    write_it ".br"
                }
            }
        }
    }

    set eatP 1
}

# can be reset in rc file to override or add styles; e.g.,
#   global spanx_txt_styles
#   set spanx_txt_styles [linsert $spanx_txt_styles 0 {verb "<" ">"}]
global spanx_txt_styles
set spanx_txt_styles {
    {emph "_"}      # as in makeinfo(1)
    {vemph "_"}
    {strong "*"}    # as in makeinfo(1)
    {vstrong "*"}
    {verb "\""}
    {vbare ""}
    {vdeluxe "*_" "_*"}
}

proc spanx_txt {text style} {
    global spanx_txt_styles
    global mode
    global eatP

    set i [lsearch0 $spanx_txt_styles $style]
    if {$i < 0} {
        set c1 ""
        set c2 ""
    } else {
        set sts [lindex $spanx_txt_styles $i]
        set c1 [lindex $sts 1]
        if {[llength $sts] >=3} {
            set c2 [lindex $sts 2]
        } else {
            set c2 $c1
        }
    }

    set line $c1[chars_expand $text]$c2

    if {![cellP $line]} {
        set eatP 0
        write_text_$mode $line
    }

    set eatP -1
}

proc references_txt {tag args} {
    global counter depth
    global pageno

    switch -- $tag {
        begin {
            set prefix [lindex $args 0]
            set title [lindex $args 1]
            if {($depth(references) > 1) \
                    && (![info exists counter(references)])} {
                set counter(references) 0
                section_txt [lindex [split $prefix .] 0]. 1 References 0 ""
            }
            if {![have_lines 5]} {
                end_page_txt
            } else {
                write_line_txt "" -1
            }

            push_indent -3
            write_text_txt "$prefix  "
            push_indent [expr [string length $prefix]+1]
            write_text_txt [chars_expand $title]
            flush_text
            pop_indent
            pop_indent

            return $pageno
        }

        end {
            set erefP [lindex $args 0]
            if {$erefP} {
                erefs_txt
            } else {
                flush_text
            }
        }
    }
}

proc erefs_txt {{title ""}} {
    global erefs
    global options

    if {[string compare $title ""]} {
        if {$options(.COMPACT)} {
            write_line_txt ""
        } else {
            end_page_txt
        }
        write_line_txt $title
    }

    set names  [lsort -integer [array names erefs]]
    set width [expr [string length [lindex $names end]]+2]
    foreach eref $names {
        write_line_txt ""

        set i [expr [string length \
                            [set prefix \
                                 [format %-*.*s $width $width \
                                         "\[$eref\]"]]+2]]
        write_text_txt $prefix

        push_indent $i

        write_text_txt "  "
        write_url $erefs($eref)

        pop_indent
    }

    flush_text
}

proc crefs_txt {title} {
    global crefs
    global options

    if {[string compare $title ""]} {
        if {$options(.COMPACT)} {
            write_line_txt ""
        } else {
            end_page_txt
        }
        write_line_txt $title
    }

    set names  [lsort -dictionary [array names crefs]]
    set width 0
    foreach cref $names {
        set x [string length $cref]
        if {$x > $width} {
            set width $x
        }
    }
    incr width 2
    foreach cref $names {
        write_line_txt ""

        set i [expr [string length \
                            [set prefix \
                                 [format %-*.*s $width $width \
                                         "\[$cref\]"]]+2]]
        write_text_txt $prefix

        push_indent $i

        write_text_txt "  "
        write_text_txt [lindex $crefs($cref) 3]
        pop_indent
    }

    flush_text
}

proc reference_txt {prefix names title series formats date anchor target
                    target2 width annotations} {
    write_line_txt ""

    incr width 2
    set i [expr [string length \
                        [set prefix \
                             [format %-*s $width "\[$prefix\]"]]+2]]
    write_text_txt $prefix

    if {$i > 11} {
        set i 11
        set s ""
        flush_text
    } else {
        set s "  "
    }

    push_indent $i

    set nameA 1
    set nameN [llength $names]
    foreach name $names {
        incr nameA
        write_text_txt $s[chars_expand [lindex $name 0]]
        set s [list_sep_str $nameA $nameN]
    }
    write_text_txt "$s\"[chars_expand $title]\""
    foreach serial $series {
        if {[regexp -nocase -- "internet-draft&nbsp;(draft-.*)" $serial x n] == 1} {
            set serial "$n (work in progress)"
        }
        write_text_txt ", [chars_expand $serial]"
    }
    if {[string compare $date ""]} {
        write_text_txt ", [chars_expand $date]"
    }
    if {[string compare $target ""]} {
        write_text_txt ", "
        write_url $target
    }
    write_text_txt .

    while {[llength $annotations] > 0} {
        write_line_txt ""
        pcdata_txt [lindex $annotations 0]
        set annotations [lrange $annotations 1 end]
    }

    pop_indent
}

proc annotation_txt {tag} {
    global annoP
    global cells

    switch -- $tag {
        begin {
            set annoP 1
        }

        end {
            unset annoP

            set text [string trim $cells(0,0)]
            unset cells

            return $text
        }
    }
}

proc back_txt {authors} {
    global options
    global lineno pageno
    global contacts

    set lines 5
    set author [lindex $authors 0]
    incr lines [llength [lindex $author 0]]
    incr lines [llength [lindex $author 1]]
    if {![have_lines $lines]} {
        end_page_txt
    } elseif {$lineno != 3} {
        write_line_txt "" -1
        write_line_txt "" -1
    }
    set result $pageno

    switch -- [llength $authors] {
        0 {
            return $result
        }

        1 {
            set s1 "'s"
            set s2 ""
        }

        default {
            set s1 "s'"
            set s2 "es"
        }
    }
    set s "Author$s1 Address$s2"

    set firstP 1
    foreach author $authors {
        set block1 [lindex $author 0]
        set block2 [lindex $author 1]

        set lines 4
        incr lines [llength $block1]
        incr lines [llength $block2]
        if {![have_lines $lines]} {
            end_page_txt
        }

        if {[string compare $s ""]} {
            write_line_txt $s
            set s ""
        } else {
            write_line_txt "" -1
        }
        write_line_txt "" -1

        foreach line $block1 {
            write_line_txt "   [chars_expand $line]"
        }

        if {[llength $block2] > 0} {
            write_line_txt ""
            foreach contact $block2 {
                set key [lindex $contact 0]
                set value [lindex [lindex $contacts \
                                          [lsearch0 $contacts $key]] 1]
                set value [format %-6s $value:]
                if {$options(.COLONSPACE)} {
                    append value " "
                }
                write_line_txt "   $value [chars_expand [lindex $contact 1]]"
            }
        }
    }

    return $result
}

global pcdata_line_offset
set pcdata_line_offset 0

proc pcdata_txt {text {pre 0}} {
    global eatP
    global options
    global pcdata_line_offset

    if {(!$pre) && ($eatP > 0)} {
        set text [string trimleft $text]
    }
    if {[string length $text] <= 0} {
        # Was only white space, but got trimmed.
        return
    }
    set eatP 0

    if {!$pre} {
        regsub -all "\n\[ \t\n\]*" $text "\n" text
        regsub -all "\[ \t\]*\n\[ \t\]*" $text "\n" text
        set prefix ""

        if {$options(.EMOTICONIC)} {
            set text [emoticonic_txt $text]
        }
    }

    if {[cellP $text]} {
        return
    }

    set pcdata_line_offset 0
    foreach line [split $text "\n"] {
        set line [chars_expand $line]
        if {$pre} {
            write_line_txt [string trimright $line] $pre
        } else {
            write_pcdata_txt $prefix$line
            set prefix " "
        }
        incr pcdata_line_offset
    }
    set pcdata_line_offset 0

    if {[regexp -- {[ \t\n]$} $text]} {
        set eatP 1
    }
}

proc emoticonic_txt {text} {
    foreach {ei begin end} [list  *   *   * \
                                  '   '   ' \
                                 {"} {"} {"}] {
        set body ""
        while {[set x [string first "|$ei" $text]] >= 0} {
            if {$x > 0} {
                append body [string range $text 0 [expr $x-1]]
            }
            append body "$begin"
            set text [string range $text [expr $x+2] end]
            if {[set x [string first "|" $text]] < 0} {
                error "missing close for |$ei"
            }
            if {$x > 0} {
                set inline [string range $text 0 [expr $x-1]]
                if {[string first $begin $inline] == 0} {
                    set inline [string range $inline [string length $begin] \
                                       end]
                }
                set tail [expr [string length $inline]-[string length $end]]
                if {[string last $end $inline] == $tail} {
                    set inline [string range $inline 0 [expr $tail-1]]
                }

                append body $inline
            }
            append body "$end"
            set text [string range $text [expr $x+1] end]
        }
        append body $text
        set text $body
    }

    return $text
}

proc start_page_txt {} {
    global header lineno blankP

    write_it $header
    write_it ""
    write_it ""
    set lineno 3
    set blankP 1
}

proc end_page_txt {} {
    global footer lineno pageno

    flush_text

    if {$lineno <= 3} {
        return
    }
    while {$lineno < 54} {
        write_it ""
        incr lineno
    }

    set text [format "\[Page %d\]" $pageno]
    incr pageno
    set len [string length $text]
    set len [expr (72-[string length $footer])-$len]
    if {$len < 4} {
        set len 4
    }
    write_it [format %s%*.*s%s $footer $len $len "" $text]
    write_it "\f"

    set lineno 0
}

proc write_pcdata_txt {text} {
    global buffer buffer_align
    global indent
    global mode

    if {![string compare $buffer ""]} {
        set buffer [format %*.*s $indent $indent ""]
        set buffer_align [current_align]
    }
    append buffer $text
    set buffer [two_spaces $buffer]

    write_text_$mode ""
}

proc write_editno_txt {editNo} {
    global buffer

    if {[string compare $buffer ""]} {
        flush_text
    }
    set buffer <$editNo>
    flush_text
}

global buffer_rest buffer_align
set buffer_rest ""
set buffer_align ""

proc fold_text_txt {} {
    global buffer buffer_rest
    global indent

    set buflen [string length $buffer]
    if {$buflen > 72} {
        set x [string last " " [string range $buffer 0 72]]
        if {   $x != 72
            && [regexp -indices \
                       -start [expr $x + 1] \
                       -- { *([^ ]+)} $buffer y wi]
            && [set w0 [lindex $wi 0]] < 72} {

            # Get word across edge.
            set w1 [lindex $wi 1]
            set word [string range $buffer $w0 $w1]
            set wlen [expr $w1 - $w0 + 1]
            set ww [string range $word 0 [expr 71 - $w0]]

            set must_break [expr (   ($w0 <= $indent) \
                                  || ($indent + $wlen > 72))]

            # Don't bother with short words that cannot possibly
            # produce a good break.
            # Don't break a URI (or other things that are nice to
            # copy&paste in their entirety) if it would entirely
            # fit in its own line (the next line).
            # Don't bother wasting our time on frequent purely
            # alphanumerical non-opportunities.
            if {   $must_break
                || (   ($w0 < 70)
                    && ($wlen >= 6)
                    && ![regexp -- {^[A-Za-z0-9_\xA0]+$} $ww]
                    && ![regexp -expanded -- { ://
                                              |\m(mailto|urn|news|tel):
                                              |\mdraft-[a-z0-9]+-
                                              |\m[A-Za-z0-9._-]+@[a-z0-9.-]+\M
                                             } $word]
                   )} {

                set best_left -1
                set best_middle -1
                set best_right $wlen

                # Bad:       a-zzzzzzz
                # Ok:       aa-zzzzzzz
                # Bad:  aaaaaa-zz
                # Ok:   aaaaaa-zzz
                foreach d {/ @ & | - + # % :} {
                    set y [string last $d $ww]
                    while {   $y >= 0
                           && [regexp -start $y -- "\\A.\[\])>\}'\"/@+:&|#%-\]" $word]} {
                        # Not a good break based on first character after it.
                        set y [string last $d [string range $ww 0 [expr $y - 1]]]
                    }

                    if {$y < 0 || $w0 + $y < $indent} {
                        # Not usable.
                    } elseif {   $y < 2
                              || [regexp -all -- {[A-Za-z0-9_]} \
                                         [string range $word \
                                                 0 [expr $y - 1]]] < 2} {
                        # Keep best of the indesirable left cuts.
                        if {$y > $best_left} {
                            set best_left $y
                        }
                    } elseif {   $y > $wlen - 4
                              || [regexp -all -- {[A-Za-z0-9_]} \
                                         [string range $word \
                                                 [expr $y + 1] end]] < 3} {
                        # Keep best of the indesirable right cuts.
                        if {$y < $best_right} {
                            set best_right $y
                        }
                    } else {
                        # The first good middle position gets it,
                        # because it's a better character.
                        if {$best_middle < 0} {
                            set best_middle $y
                            # Bonus early break.
                            break
                        }

                        ## The best middle position gets it,
                        ## even if it's a worst character.
                        #if {$y > $best_middle} {
                        #    set best_middle $y
                        #}
                    }
                }

                if {$best_middle >= 0} {
                    set x [expr $w0 + $best_middle + 1]
                } elseif {$must_break} {
                    # All undesirable, so start at right.
                    if {$best_right < $wlen} {
                        set x [expr $w0 + $best_right + 1]
                    } elseif {$best_left >= 0} {
                        set x [expr $w0 + $best_left + 1]
                    } else {
                        set x 72
                    }

                    global lineno pageno
                    regsub -all -- {"} [string range $buffer $w0 [expr $x - 1]] {\"} wa
                    regsub -all -- {"} [string range $buffer $x $w1] {\"} wz
                    unexpected warning \
 "output line $lineno (on page $pageno) breaks badly between \"$wa\" and \"$wz\""
                }
                # Else, we keep the first x we found
                # so we don't break the word.
            }
        }
        set text [string range $buffer 0 [expr $x-1]]
        set rest [string trimleft [string range $buffer $x end]]
    } else {
        set text $buffer
        set rest ""
    }
    # This would be done anyway by flush_text,
    # which is now (and must be) a no-op.
    set buffer ""

    # It is up to the caller to restore buffer with $buffer_rest,
    # after having printed text with write_line_$mode.
    if {[string compare $rest ""]} {
        set buffer_rest [format %*.*s%s $indent $indent "" $rest]
    } else {
        set buffer_rest ""
    }

    return [string trimright $text]
}

proc justify_text_txt {text direction} {
    global indent

    set t [string trimleft $text]

    switch -- $direction {
        c - center {
            set len [expr $indent + (72 - [string length $t] - $indent)/2]
        }

        r - right {
            set len [expr 72 - [string length $t]]
        }

        default {
            return $text
        }
    }

    return [format %*.*s%s $len $len "" $t]
}

proc write_text_txt {text {direction l}} {
    global buffer buffer_rest buffer_align
    global indent
    global eatP

    if {$eatP < 0} {
        set text " $text"
    }
    if {![string compare $buffer ""]} {
        set buffer [format %*.*s $indent $indent ""]
        set buffer_align [current_align]
    }
    append buffer $text

    set flush [string compare $direction l]
    while {([string length $buffer] > 72) || ($flush)} {
        set text [fold_text_txt]

        switch -- $direction {
            c - r { set buffer_align $direction }
        }
        set text [justify_text_txt $text $buffer_align]
        write_line_txt $text

        if {![string compare [set buffer $buffer_rest] ""]} {
            set buffer_align ""
            break
        }
    }
}

proc write_line_txt {line {pre 0}} {
    global lineno blankP

    flush_text
    if {$lineno == 0} {
        start_page_txt
    }
    if {![set x [string compare $line ""]]} {
        set blankO $blankP
        set blankP 1
        if {($blankO) && (!$pre || $lineno == 3)} {
            return
        }
    } else {
        set blankP 0
    }
    if {($pre) && ($x)} {
        if {$pre < 0} {
            set pre "   "
        } else {
            set pre [format %*.*s $pre $pre ""]
            set line [tabs_expand_pre $line]
        }
    } else {
        set pre ""
    }
    set line [nbsp_expand_txt $line]
    write_it [set line [string trimright $pre$line]]
    incr lineno
    if {[set len [string length $line]] > 72} {
        global pageno

        regsub -all -- {"} [string range $line 72 end] {\"} excess
        unexpected [unex_condtype] \
            "output line $lineno (on page $pageno) has $len > 72 characters (excess string is \"$excess\")"
    }
    if {$lineno >= 51} {
        end_page_txt
    }
}

proc nbsp_expand_txt {s} {
    global nbsp

    regsub -all "$nbsp" [string trimright $s] " " s
    return $s
}

proc two_spaces {glop} {
    global options

    set post ""

    # Work around a bug in tcl-8.4.9 and possibly others.
    # Don't ask, it's a mystery anyway.
    set foo "x$glop"

    if {$options(.COLONSPACE)} {
        set re {([.?!][])'"]*|:) }
    } else {
        set re {[.?!][])'"]* }
    }

    while {[string length $glop] > 0} {
        # The double quotes will also match the end of a spanx-verb, which
        # may not be the end of a sentence.  Impossible to tell apart.  :-(
        if {![regexp -indices $re $glop x]} {
            append post $glop
            break
        }

        set pre [string range $glop 0 [lindex $x 1]]
        set glop [string trimleft [string range $glop [expr [lindex $x 1] + 1] end]]
        append post $pre

        # Get rid of the colon case quickly.
        if {   $options(.COLONSPACE)
            && [regexp -- {: $} $pre]} {
            append post " "
            continue
        }

        # A special case.  Author wouldn't normally put a period after that.
        if {[regexp -- {[Aa](nne|ppendi)x[ \xA0][A-Z][])'"]*[.?!][])'"]* $} $pre]} {
            append post " "
            continue
        }

        # Check for likely abbreviation.  Do not insert two spaces in
        # this case.
        # "e.g." and "i.e." are never directly followed by spaces.
        # "etc. " and "et al. " will often be the end of the sentence anyway.
        if {[regexp -expanded {(^|[^A-Za-z\xA0-])
                               (  [A-Z]\.[])'"]*
                                | (  [A-Z][a-z][a-z]
                                   | Fig | Tbl | Eq
                                   | [Cc]f | vs | resp
                                   | [JS]r | M[rs] | Messrs | Mrs | Mmes
                                   | Drs? | Profs?
                                   | Rep | Sen | Gov
                                   | St | Rev
                                   | Gen | Col | Maj | Cap | Lt)
                                  \.)
                               \ $} $pre]} {
            continue
        }

        # Check if what follows doesn't look like the beginning of a sentence.
        if {[regexp -- {^["'([]*[^A-Z"'([]} $glop]} {
            continue
        }

        # Otherwise, we assume that we are in between two sentences.
        append post " "
    }

    return $post
}

proc pi_txt {key value} {
    global mode
    global passno

    switch -- $key {
        needLines {
            global buffer

            set x [string compare $buffer ""]
            if {![have_lines $value]} {
                end_page_$mode
            } elseif {$x && ![string compare $mode nr]} {
                # We might have flushed early, so now make it stick.
                write_it ".br"
            }
        }

        typeout {
            if {$passno == 2} {
                puts stdout $value
            }
        }

        default {
            error ""
        }
    }
}


#
# html output
#


# don't need to return anything even though rfc_txt does...

proc rfc_html {irefs iprstmt copying newP} {
    global options copyrightP iprP
    global funding validity

    if {$options(.SLIDES) && [end_rfc_slides]} {
        return
    }

    if {[llength $irefs] > 0} {
        toc_html rfc.index
        write_html "<h3>Index</h3>"

        write_html "<table>"
        foreach iref $irefs {
            foreach {L item subitem flags pages} $iref { break }

            if {[string compare $L ""]} {
                write_html "<tr><td><span class=\"strong\">$L</span></td><td>&nbsp;</td></tr>"
            }

            if {[string compare $subitem ""]} {
                if {[string compare $item ""]} {
                    write_html "<tr><td>&nbsp;</td><td>$item</td></tr>"
                }
                set key $subitem
                set t "&nbsp;&nbsp;"
            } else {
                set key $item
                set t ""
            }

            array set iflags $flags
            if {![string compare $iflags(primary) true]} {
                set key "<b>$key</b>"
            }

            if {[llength $pages] == 1} {
                set key "<a href=\"#[lindex $pages 0]\">$key</a>"
            } else {
                set i 0
                set s "  "
                foreach page $pages {
                    append key "$s<a href=\"#$page\">[incr i]</a>"
                    set s ", "
                }
            }

            write_html "<tr><td>&nbsp;</td><td>$t$key</td></tr>"
        }
        write_html "</table>"
    }

    if {(!$options(.PRIVATE)) && $copyrightP} {
        toc_html rfc.copyright
        if {$iprP} {
            global iprurl ipremail

            write_html "<h3>Intellectual Property Statement</h3>"

            regsub -all %IPRURL% $iprstmt "<a href='$iprurl'>$iprurl</a>" iprstmt
            if {$options(.LINKMAILTO)} {
                regsub -all %IPREMAIL% $iprstmt "<a href='mailto:$ipremail'>$ipremail</a>" iprstmt
            } else {
                regsub -all %IPREMAIL% $iprstmt $ipremail iprstmt
            }

            foreach para $iprstmt {
                write_html "<p class='copyright'>"
                pcdata_html $para
                write_html "</p>"
            }
        }

        if {$newP} {
            write_html "<h3>Disclaimer of Validity</h3>"

            foreach para $validity {
                write_html "<p class='copyright'>"
                pcdata_html $para
                write_html "</p>"
            }
        }

        if {$newP} {
            write_html "<h3>Copyright Statement</h3>"
        } else {
            write_html "<h3>Full Copyright Statement</h3>"
        }

        foreach para $copying {
            write_html "<p class='copyright'>"
            pcdata_html $para
            write_html "</p>"
        }

        write_html "<h3>Acknowledgment</h3>"
        write_html "<p class='copyright'>"
        pcdata_html $funding
        write_html "</p>"
    }

    write_html "</body></html>"

    return ""
}

global htmlstyle

set htmlstyle \
"<style type='text/css'>
<!--
    body {
        font-family: verdana, charcoal, helvetica, arial, sans-serif;
        margin: 2em;
        font-size: small ; color: #000000 ; background-color: #ffffff ; }
    .title { color: #990000; font-size: x-large ;
        font-weight: bold; text-align: right;
        font-family: helvetica, monaco, \"MS Sans Serif\", arial, sans-serif;
        background-color: transparent; }
    .filename { color: #666666; font-size: 18px; line-height: 28px;
        font-weight: bold; text-align: right;
        font-family: helvetica, arial, sans-serif;
        background-color: transparent; }
    td.rfcbug { background-color: #000000 ; width: 30px ; height: 30px ;
        text-align: justify; vertical-align: middle ; padding-top: 2px ; }
    td.rfcbug span.RFC { color: #666666; font-weight: bold; text-decoration: none;
        background-color: #000000 ;
        font-family: monaco, charcoal, geneva, \"MS Sans Serif\", helvetica, verdana, sans-serif;
        font-size: x-small ; }
    td.rfcbug span.hotText { color: #ffffff; font-weight: normal; text-decoration: none;
        text-align: center ;
        font-family: charcoal, monaco, geneva, \"MS Sans Serif\", helvetica, verdana, sans-serif;
        font-size: x-small ; background-color: #000000; }
/* info code from SantaKlauss at http://www.madaboutstyle.com/tooltip2.html */
    div#counter{margin-top: 100px}

    a.info{
        position:relative; /*this is the key*/
        z-index:24;
        text-decoration:none}

    a.info:hover{z-index:25; background-color:#990000 ; color: #ffffff ;}

    a.info span{display: none}

    a.info:hover span.info{ /*the span will display just on :hover state*/
        display:block;
        position:absolute;
        font-size: smaller ;
        top:2em; left:2em; width:15em;
        padding: 2px ;
        border:1px solid #333333;
        background-color:#eeeeee; color:#990000;
        text-align: left ;}

     A { font-weight: bold; }
     A:link { color: #990000; background-color: transparent ; }
     A:visited { color: #333333; background-color: transparent ; }
     A:active { color: #333333; background-color: transparent ; }

    p { margin-left: 2em; margin-right: 2em; }
    p.copyright { font-size: x-small ; }
    p.toc { font-size: small ; font-weight: bold ; margin-left: 3em ;}

    span.emph { font-style: italic; }
    span.strong { font-weight: bold; }
    span.verb, span.vbare { font-family: \"Courier New\", Courier, monospace ; }

    span.vemph { font-style: italic; font-family: \"Courier New\", Courier, monospace ; }
    span.vstrong { font-weight: bold; font-family: \"Courier New\", Courier, monospace ; }
    span.vdeluxe { font-weight: bold; font-style: italic; font-family: \"Courier New\", Courier, monospace ; }

    ol.text { margin-left: 2em; margin-right: 2em; }
    ul.text { margin-left: 2em; margin-right: 2em; }
    li { margin-left: 3em;  }

    pre { margin-left: 3em; color: #333333;  background-color: transparent;
        font-family: \"Courier New\", Courier, monospace ; font-size: small ;
        text-align: left;
        }

    h3 { color: #333333; font-size: medium ;
        font-family: helvetica, arial, sans-serif ;
        background-color: transparent; }
    h4 { font-size: small; font-family: helvetica, arial, sans-serif ; }

    table.bug { width: 30px ; height: 15px ; }
    td.bug { color: #ffffff ; background-color: #990000 ;
        text-align: center ; width: 30px ; height: 15px ;
         }
    td.bug A.link2 { color: #ffffff ; font-weight: bold;
        text-decoration: none;
        font-family: monaco, charcoal, geneva, \"MS Sans Serif\", helvetica, sans-serif;
        font-size: x-small ; background-color: transparent }

    td.header { color: #ffffff; font-size: x-small ;
        font-family: arial, helvetica, sans-serif; vertical-align: top;
        background-color: #666666 ; width: 33% ; }
    td.author { font-weight: bold; margin-left: 4em; font-size: x-small ; }
    td.author-text { font-size: x-small; }
    table.data { vertical-align: top ; border-collapse: collapse ;
        border-style: solid solid solid solid ;
        border-color: black black black black ;
        font-size: small ; text-align: center ; }
    table.data th { font-weight: bold ;
        border-style: solid solid solid solid ;
        border-color: black black black black ; }
    table.data td {
        border-style: solid solid solid solid ;
        border-color: #333333 #333333 #333333 #333333 ; }

    hr { height: 1px }
-->
</style>"


proc front_html_begin {left right top bottom title status copying keywords
                       lang} {
    global prog prog_version
    global options copyrightP
    global htmlstyle
    global doingP hangP needP
    global imgP

    set doingP 0
    set hangP 0
    set needP 0
    set imgP 0

    if {$options(.SLIDES) \
            && [front_slides_begin $left $right $top $bottom $title]} {
        return
    }

    write_html "<\!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">"
    write_html -nonewline "<html lang=\"$lang\"><head><title>"
    if {($options(.PRIVATE)) \
            && ([string compare [string trim $options(private)] ""])} {
        pcdata_html "$options(private): "
    }
    pcdata_html [lindex $title 0]
    write_html "</title>"
    if {$options(.PRIVATE)} {
        write_html -nonewline "<meta http-equiv=\"Expires\" content=\""
        write_html -nonewline [clock format [clock seconds] \
                                     -format "%a, %d %b %Y %T +0000" \
                                     -gmt true]
        write_html "\">"
    }
# begin new meta tags

    write_html "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">"
    write_html -nonewline "<meta name=\"description\" content=\""
    regsub -all {"} [lindex $title 0] {\&quot;} t0
    pcdata_html $t0
    write_html "\">"

#   write out meta tag with keywords if they exist
    if {[llength $keywords] > 0} {
        write_html -nonewline "<meta name=\"keywords\" content=\""
        set s ""
        foreach kw $keywords {
            pcdata_html $s$kw
            set s ", "
        }
        write_html "\">"
    }

     write_html -nonewline "<meta name=\"generator\" content=\"$prog $prog_version "
     write_html "(http://xml.resource.org/)\">"
#end new meta tags

    write_html "$htmlstyle\n</head>"
    write_html -nonewline "<body"
    if {[string compare $options(background) ""]} {
        write_html -nonewline " background=\"$options(background)\""
    }
    write_html ">"

    xxxx_html

    if {$options(.TOPBLOCK)} {
        write_html "<table summary=\"layout\" width=\"66%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\"><tr><td><table summary=\"layout\" width=\"100%\" border=\"0\" cellpadding=\"2\" cellspacing=\"1\">"
        set left [munge_long $left]
        set right [munge_long $right]
        set lc ""
        set rc ""
        foreach l $left r $right {
            if {[string compare $l ""]} {
                set l $l
            } else {
                set l "&nbsp;"
            }
            if {[string compare $r ""]} {
                set r $r
            } else {
                set r "&nbsp;"
            }
            write_html "<tr><td class=\"header\">$l</td><td class=\"header\">$r</td></tr>"
        }
        write_html "</table></td></tr></table>"
    }

    set class title
    foreach line $title {
        write_html -nonewline "<div align=\"right\"><span class=\"$class\"><br />"
        pcdata_html $line
        write_html "</span></div>"
        set size 2
    }

    if {!$options(.PRIVATE)} {
        write_html ""
        write_html "<h3>Status of this Memo</h3>"
        foreach para $status {
            write_html "<p>"
            pcdata_html $para
            write_html "</p>"
        }
    }

    if {(!$options(.PRIVATE)) && $copyrightP} {
        write_html ""
        write_html "<h3>Copyright Notice</h3>"
        write_html "<p>"
        pcdata_html $copying
        write_html "</p>"
    }
}

proc front_html_end {toc irefP} {
    global options noticeT

    if {!$options(.TOC)} {
        return
    }

    xxxx_html toc

    write_html "<h3>Table of Contents</h3>"
    write_html "<p class=\"toc\">"
    set last [lindex $toc end]
    if {[string compare [lindex $last 1] $noticeT]} {
        set last ""
    } else {
        set toc [lreplace $toc end end]
    }
    if {$irefP} {
        lappend toc [list "&#167;" Index rfc.index]
    }
    if {[string compare $last ""]} {
        lappend toc $last
    }
    foreach c $toc {
        set text [lindex $c 0]
        if {$options(.TOCINDENT)} {
            set len [string length $text]
            set text [string trimleft $text]
            for {set x [expr $len-[string length $text]]} \
                    {$x > 0} \
                    {incr x -1} {
                write_html -nonewline "&nbsp;&nbsp;"
            }
        }
        write_html -nonewline "<a href=\"#[lindex $c 2]\">"
        pcdata_html $text
        write_html "</a>&nbsp;"
        pcdata_html [lindex $c 1]
        write_html "<br />"
    }
    write_html "</p>"
    write_html "<br clear=\"all\" />"
}

proc abstract_html {} {
    global options

    if {$options(.SLIDES) && [end_page_slides]} {
        start_page_slides Abstract
    } else {
        write_html ""
        write_html "<h3>Abstract</h3>"
    }
}

proc note_html {title depth} {
    global options

    if {$options(.SLIDES) && [end_page_slides]} {
        start_page_slides $title
    } else {
        incr depth 3

        write_html ""
        write_html -nonewline "<h$depth>"
        pcdata_html $title
        write_html "</h$depth>"
    }
}

proc section_html {prefix top title {lines 0} anchor} {
    global options

    if {$options(.SLIDES) && [end_page_slides]} {
        start_page_slides $title

        return $anchor
    }

    set anchor2 [string trimright $prefix .]
    if {[string first "Appendix " $anchor2] == 0} {
        set anchor2 [string range $anchor2 9 end]
    }
    set anchor2 rfc.section.$anchor2

    write_html ""
    if {[string match *. $prefix]} {
        toc_html $anchor
        write_html -nonewline "<a name=\"$anchor2\"></a>"
        write_html -nonewline "<h3>$prefix&nbsp;"
        pcdata_html $title
        write_html "</h3>"
    } else {
        write_html -nonewline "<a name=\"$anchor2\"></a>"
        write_html -nonewline "<h4><a name=\"$anchor\">$prefix</a>&nbsp;"
        pcdata_html $title
        write_html "</h4>"
    }

    return $anchor
}

proc t_html {tag counter style hangText editNo} {
    global options
    global doingP hangP needP

    if {[string compare $tag begin]} {
        set s /
        set needP 0
    } else {
        set s ""
    }
    write_html ""
    if {![string compare $style "hanging"]} {
        if {![string compare $tag begin]} {
            write_html "<dt>$hangText</dt>"
        }
        write_html -nonewline "<${s}dd>"

        set hangP 1
    } elseif {![string compare $style "letters"]} {
        if {![string compare $tag begin]} {
            set l [split $counter .]
            write_html "<dt>[offset2letters [lindex $l end] [llength $l]]</dt>"
        }
        write_html -nonewline "<${s}dd>"

        set hangP 1
    } elseif {([string compare $counter ""]) \
                    && ([string compare $style empty])} {
        write_html -nonewline "<${s}li>"

        set hangP 0
    } else {
        set sta ""
        if {[string compare $tag end]} {
            set doingP 1
            switch -- [set a [current_align]] {
                left - center - right {
                   set sta " style='text-align: $a'"
                }
            }
        }
        if {$doingP} {
            set doingP [string compare $tag end]
            write_html -nonewline "<${s}p${sta}>"
        }

        set hangP 0
    }
    if {$options(.EDITING) \
            && (![string compare $tag begin]) \
            && ([string compare $editNo ""])} {
        write_html -nonewline "<sup><small>$editNo</small></sup>"
    }
}

proc list_html {tag counters style hangIndent hangText suprT} {
    global doingP hangP needP

    if {[string compare $tag begin]} {
        set s /
        set c ""
    } else {
        set s ""
        set c " class=\"text\""
        if {$doingP} {
            write_html -nonewline "</p>"
            set doingP 0
        }
    }
    write_html ""
    switch -- $style {
        numbers {
            write_html -nonewline "<${s}ol$c>"
        }

        symbols {
            write_html -nonewline "<${s}ul$c>"
        }

        letters
            -
        hanging {
            if {[string compare $tag begin]} {
                write_html -nonewline "</dl></blockquote>"
            } else {
                write_html -nonewline "<blockquote$c><dl>"
            }
        }

        default {
            write_html -nonewline "<${s}blockquote$c>"
        }
    }

    if {($suprT >= 0) && ([string compare $tag begin])} {
        set needP 1
    }
    set hangP 0
}

proc figure_html {tag lines anchor title {av {}}} {
    global xref

    switch -- $tag {
        begin {
            if {[string compare $title ""]} {
                write_html "<br /><hr />"
            }
            if {[string compare $anchor ""]} {
                write_html "<a name=\"$anchor\"></a>"
            }
            img_html begin 1 $av
        }

        end {
            img_html end 1 $av
            if {[string compare $anchor ""]} {
                array set av2 $xref($anchor)
                set prefix "Figure&nbsp;$av2(value)"
                if {[string compare $title ""]} {
                    set title "$prefix: $title"
                } else {
                    set title $prefix
                }
            }
            if {[string compare $title ""]} {
                write_html "<table border=\"0\" cellpadding=\"0\" cellspacing=\"2\" align=\"center\"><tr><td align=\"center\"><font face=\"monaco, MS Sans Serif\" size=\"1\"><b>&nbsp;$title&nbsp;</b></font><br /></td></tr></table><hr size=\"1\" shade=\"0\">"
            }
        }
    }
}

proc artwork_html {tag lines {av {}}} {
    img_html $tag 2 $av
}

proc img_html {tag bit {av {}}} {
    global imgP
    global options

    if {[set x [lsearch -exact $av src]] < 0 || $x % 2} {
        return
    }

    switch -- $tag {
        begin {
            if {$imgP} {
                return
            }
            set line "<div"
            set attrs ""
            set seen_alt 0
            foreach {k v} $av {
                # "name": file name to use for storing the content.
                # "type": not a MIME type; e.g., "abnf".
                regsub -all "\"" $v {\&quot;} v
                switch -- $k {
                    width - height {
                        append attrs " $k=\"$v\""
                    }

                    src {
                        if {$options(.USEOBJECT)} {
                            append attrs " data=\"$v\""
                        } else {
                            append attrs " src=\"$v\""
                        }
                    }

                    alt {
                        if {!$options(.USEOBJECT)} {
                            append attrs " alt=\"$v\""
                            set seen_alt 1
                        }
                    }

                    align {
                        switch -- $v {
                            left - center - right {
                                append line " style='text-align: $v'"
                            }

                            default {
                                unexpected error \
                                    "align=\"$align\" attribute is invalid"
                            }
                        }
                    }
                }
            }
            if {$options(.USEOBJECT)} {
                append line "><object"
            } else {
                append line "><img"
            }
            append line $attrs
            if {$options(.USEOBJECT)} {
                append line ">"
            } else {
                if {!$seen_alt} {
                    if {$options(.STRICT)} {
                        unexpected error \
                            "use of the \"src\" attribute in img graphics also requires \"alt\" attribute"
                    } else {
                        unexpected warning \
                            "also showing text content for img graphics with \"src\" but not \"alt\" attribute"
                        append line { alt="[graphic image equivalent to the textual content below]"}
                    }
                } else {
                    set imgP [expr $imgP | $bit]
                }
                append line " /></div>"
            }
            write_html $line
        }

        end {
            if {[set imgP [expr $imgP & ~$bit]]} {
                return
            }
            set line ""
            if {$options(.USEOBJECT)} {
                append line "</object>"
            }
            append line "</div>"
            write_html $line
        }
    }
}

proc preamble_html {tag {editNo ""}} {
    t_html $tag "" "" "" $editNo
}

proc postamble_html {tag {editNo ""}} {
    t_html $tag "" "" "" $editNo
}

proc texttable_html {tag lines anchor title {didP 0}} {
    global xref

    switch -- $tag {
        begin {
            if {[string compare $title ""]} {
                write_html "<br /><hr />"
            }
            if {[string compare $anchor ""]} {
                write_html "<a name=\"$anchor\"></a>"
            }
        }

        end {
            if {[string compare $anchor ""]} {
                array set av $xref($anchor)
                set prefix "Table $av(value)"
                if {[string compare $title ""]} {
                    set title "$prefix: $title"
                } else {
                    set title $prefix
                }
            }
            if {[string compare $title ""]} {
                write_html "<table border=\"0\" cellpadding=\"0\" cellspacing=\"2\" align=\"center\"><tr><td align=\"center\"><font face=\"monaco, MS Sans Serif\" size=\"1\"><b>&nbsp;$title&nbsp;</b></font><br /></td></tr></table><hr size=\"1\" shade=\"0\">"
            }
        }
    }
}

proc ttcol_html {text align col width} {
    if {[lindex $col 0] == 1} {
        write_html "<table class=\"data\" align=\"center\" border=\"1\" cellpadding=\"2\" cellspacing=\"2\">"
        write_html "<tr>"
    }
    write_html -nonewline "<th align=\"$align\" width=\"$width%\">"
    pcdata_html $text
    write_html "</th>"
    if {[lindex $col 0] == [lindex $col 1]} {
        write_html "</tr>"
    }
}

proc c_html {tag row col align} {
    global emptyP

    switch -- $tag {
        begin {
            if {[lindex $col 0] == 1} {
                write_html "<tr>"
            }
            write_html -nonewline "<td align=\"$align\">"
            set emptyP 1
        }

        end {
            if {$emptyP} {
                write_html -nonewline "&nbsp;"
            }
            write_html "</td>"
            if {[lindex $col 0] == [lindex $col 1]} {
                write_html "</tr>"
                if {[lindex $row 0] == [lindex $row 1]} {
                    write_html "</table>"
                }
            }
        }
    }
}

proc xref_html {text av target format {hackP 0}} {
    global elem
    global options

    array set attrs $av

    set elemY $attrs(elemN)
    array set tv [list title ""]
    array set tv $elem($elemY)

    set title ""
    switch -- $attrs(type) {
        section {
            set line "Section&nbsp;$attrs(value)"
            set title [section_title $elemY]
        }

        appendix {
            set line "Appendix&nbsp;$attrs(value)"
            set title [section_title $elemY]
        }

        figure {
            set line "Figure&nbsp;$attrs(value)"
            set title [section_title $elemY]
        }

        texttable {
            set line "Table&nbsp;$attrs(value)"
            set title [section_title $elemY]
        }

        cref {
            set line "Comment&nbsp;$attrs(value)"
            set title [cref_title $elemY]
        }

        t {
            set line "Paragraph&nbsp;$attrs(value)"
            set title ""
        }

        reference {
            set line "\[$attrs(value)\]"

            set s ""
            set nameA 1
            set nameN [llength [set names [ref_names $elemY]]]
            foreach name $names {
                incr nameA
                set name [lindex $name 0]
                append title $s$name
                set s [list_sep_str $nameA $nameN]
            }
            append title ", &ldquo;[ref_title $elemY],&rdquo; [ref_date $elemY]."
        }

        default {
            set line "\[$attrs(value)\]"
        }
    }
    regsub -all {"} $title {\&quot;} title
    regsub -all "\r" $title { } title
    regsub -all "\n" $title { } title
if {0} {
    set title " title=\"$title\""
}

    if {![string compare $format none]} {
        if {![string compare $text ""]} {
            return
        }
    } elseif {![string compare $text ""]} {
        switch -- $format {
            counter {
                set text $attrs(value)
            }

            title {
                set text $tv(title)
            }

            default {
            }
        }
    } elseif {$options(.EMOTICONIC)} {
        set text [emoticonic_html $text]
    }

    set post ""
    if {[string compare $text ""]} {
        switch -- $attrs(type) {
            section
                -
            appendix
                -
            figure
                -
            texttable {
            }

            default {
                if {![string compare $format default]} {
                    set post $line
                }
            }
        }
    } else {
        set text $line
    }
if {0} {
    set line "<a href=\"#$target\"$title>$text</a>$post"
} else {
    set line "<a class=\"info\" href=\"#$target\">$text"
    if {[string compare $title ""]} {
        append line "<span> (</span><span class=\"info\">$title</span><span>)</span>"
    }
    append line "</a>$post"
}
    if {$hackP} {
        return $line
    }
    if {![cellP $line]} {
        write_html -nonewline $line
    }
}

proc eref_html {text counter target} {
    global options

    if {![string compare $text ""]} {
        set text $target
    } elseif {$options(.EMOTICONIC)} {
        set text [emoticonic_html $text]
    }

    set line "<a href=\"$target\">$text</a>"
    if {![cellP $line]} {
        write_html -nonewline $line
    }
}

proc cref_html {text counter source anchor} {
    global crefs

    set comments ""
    if {[string compare $source ""]} {
        set comments "${source}: "
    }
    append comments $text
    set crefs($counter) [list $anchor $source $text $comments]

    regsub -all {"} $comments {\&quot;} comments
    regsub -all "\r" $comments { } comments
    regsub -all "\n" $comments { } comments

if {0} {
    set line "<a href=\"#comment.$counter\" title=\"$comments\">\[$counter\]</a>"
} else {
    set line "<a class=\"info\" href=\"#comment.$counter\">\[$counter\]<span> (</span><span class=\"info\">$comments</span><span>)</span></a>"
}
    append line "<a name=\"$anchor\"></a>"

    if {![cellP $line]} {
        write_html -nonewline $line
    }
}

proc iref_html {item subitem flags} {
    global anchorN

    set anchor anchor[incr anchorN]

    write_html -nonewline "<a name=\"$anchor\"></a>"

    return $anchor
}

proc vspace_html {lines} {
    global options
    global hangP

    if {$lines > 5} {
        if {$options(.SLIDES) && [end_page_slides]} {
            start_page_slides
        }

        return
    }
    incr lines -$hangP
    while {$lines >= 0} {
        incr lines -1
        write_html "<br />"
    }

    set hangP 0
}

proc spanx_html {text style} {
    write_html -nonewline "<span class=\"$style\">$text</span>"
}

# don't need to return anything even though txt/nr versions do...

proc references_html {tag args} {
    global counter depth
    global options

    if {$options(.SLIDES) \
            && (![string compare $tag begin]) \
            && [end_page_slides]} {
        start_page_slides References
        return
    }

    switch -- $tag {
        begin {
            set prefix [lindex $args 0]
            set title [lindex $args 1]
            if {($depth(references) > 1) \
                    && (![info exists counter(references)])} {
                set counter(references) 0
                section_html [lindex [split $prefix .] 0]. 1 References 0 \
                             rfc.references
            }

            write_html ""
            if {![info exists counter(references)]} {
                set suffix 1
            } else {
                set suffix [incr counter(references)]
            }
            toc_html rfc.references$suffix
            write_html -nonewline "<h3>$prefix&nbsp;"
            pcdata_html $title
            write_html "</h3>"

            write_html "<table width=\"99%\" border=\"0\">"
        }

        end {
            write_html "</table>"
        }
    }
}

proc reference_html {prefix names title series formats date anchor target
                     target2 width annotations} {
    global rfcTxtHome idTxtHome

    if {[string compare $target2 ""]} {
        set prefix "<a href=\"$target2\">$prefix</a>"
    }
    if {[string compare $anchor ""]} {
        set prefix "<a name=\"$anchor\">\[$prefix\]</a>"
    }
    write_html "<tr><td class=\"author-text\" valign=\"top\">$prefix</td>"

    set text ""

    set s ""
    set nameA 1
    set nameN [llength $names]
    foreach name $names {
        incr nameA
        if {[string compare [set eref [lindex $name 1]] ""]} {
            set name "<a href=\"$eref\">[lindex $name 0]</a>"
        } else {
            set name [lindex $name 0]
        }
        append text $s$name
        set s [list_sep_str $nameA $nameN]
    }

    if {(![string compare $target ""]) && ([llength $formats] == 1)} {
        array set fv [lindex $formats 0]
        set target $fv(target)
        set formats {}
    }

    if {![string compare $target ""]} {
        foreach serial $series {
            if {[regexp -nocase -- "rfc&nbsp;(\[0-9\]*)" $serial x n] == 1} {
                set target $rfcTxtHome/rfc$n.txt
                break
            }
            if {[regexp -nocase -- "internet-draft&nbsp;(draft-.*)" $serial x n] \
                    == 1} {
                set target $idTxtHome/$n.txt
                break
            }
        }
    }
    if {[string compare $target ""]} {
        set title "<a href=\"$target\">$title</a>"
    }
    append text "$s&ldquo;$title"
    set r "&rdquo;"
    foreach serial $series {
        if {[regexp -nocase -- "internet-draft&nbsp;(draft-.*)" $serial x n] == 1} {
            set serial "$n (work in progress)"
        }
        append text ",$r $serial"
        set r ""
    }
    if {[string compare $date ""]} {
        append text ",$r $date"
        set r ""
    }

    set s "$r ("
    set t ".$r"
    foreach format $formats {
        catch { unset fv }
        array set fv $format
        if {[info exists fv(target)]} {
            append text "$s<a href=\"$fv(target)\">$fv(type)</a>"
            set s ", "
            set t ")."
        }
    }
    append text $t

    write_html -nonewline "<td class=\"author-text\">"
    pcdata_html $text

    while {[llength $annotations] > 0} {
        write_html "<p>"
        write_html [lindex $annotations 0]
        write_html "</p>"
        set annotations [lrange $annotations 1 end]
    }

    write_html "</td></tr>"
}

proc crefs_html {title} {
    global crefs

    write_html ""
    toc_html rfc.comments
    write_html -nonewline "<h3>"
    pcdata_html $title
    write_html "</h3>"

    write_html "<table border=\"0\">"

    set names [lsort -dictionary [array names crefs]]
    foreach cref $names {
if {0} {
        write_html "<tr><td class=\"author-text\" valign=\"top\">"
        write_html "<a href=\"#[lindex $crefs($cref) 0]\" title=\"$cref\">"
        pcdata_html [lindex $crefs($cref) 1]
        write_html "</a><a name=\"comment.$cref\"></a>:"
        write_html "</td><td class=\"author-text\">"
        pcdata_html [lindex $crefs($cref) 2]
        write_html "</td></tr>"
} else {
        write_html "<tr><td class=\"author-text\" valign=\"top\">"
        write_html "<a class=\"info\" href=\"#[lindex $crefs($cref) 0]\">"
        write_html "$cref</a><a name=\"comment.$cref\"></a>:"
        write_html "</td><td class=\"author-text\">"
        if {[string compare [set source [lindex $crefs($cref) 1]] ""]} {
            write_html -nonewline "${source}: "
        }
        pcdata_html [lindex $crefs($cref) 2]
        write_html "</td></tr>"
}
    }

    write_html "</table>"
}

proc annotation_html {tag} {
    annotation_txt $tag
}

# don't need to return anything even though back_txt does...

proc back_html {authors} {
    global contacts
    global options

    switch -- [llength $authors] {
        0 {
            return
        }

        1 {
            set s1 "'s"
            set s2 ""
        }

        default {
            set s1 "s'"
            set s2 "es"
        }
    }
    write_html ""

    toc_html rfc.authors
    write_html "<h3>Author$s1 Address$s2</h3>"

    write_html \
         "<table width=\"99%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">"
    set s ""
    foreach author $authors {
        set block1 [lindex $author 0]
        set block2 [lindex $author 1]

        if {[string compare $s ""]} {
            write_html $s
        }
        foreach line $block1 {
            write_html "<tr><td class=\"author-text\">&nbsp;</td>"
            write_html "<td class=\"author-text\">$line</td></tr>"
        }
        foreach contact $block2 {
            set key [lindex $contact 0]
            set value [lindex [lindex $contacts \
                                      [lsearch0 $contacts $key]] 1]
            write_html "<tr><td class=\"author\" align=\"right\">$value:&nbsp;</td>"
            set value [lindex $contact 1]
            switch -- $key {
                email {
                    if {$options(.LINKMAILTO)} {
                        set value "<a href=\"mailto:$value\">$value</a>"
                    }
                }

                uri {
                    set value "<a href=\"$value\">$value</a>"
                }
            }
            write_html "<td class=\"author-text\">$value</td></tr>"
        }
        set s "<tr cellpadding=\"3\"><td>&nbsp;</td><td>&nbsp;</td></tr>"
    }
    write_html "</table>"

    return ""
}

proc xxxx_html {{anchor {}}} {
    global elem
    global options

    if {$options(.PRIVATE)} {
        toc_html $anchor
        return
    } else {
        array set rv $elem(1)
        if {![string compare [set number $rv(number)] ""]} {
            toc_html $anchor
            return
        }
    }

    if {[string compare $anchor ""]} {
        write_html "<a name=\"$anchor\"></a><hr />"
    }

    write_html "
<table border=\"0\" cellpadding=\"0\" cellspacing=\"2\" width=\"30\" align=\"right\">
    <tr>
        <td class=\"rfcbug\">
                <span class=\"RFC\">&nbsp;RFC&nbsp;</span><br /><span class=\"hotText\">&nbsp;$number&nbsp;</span>
        </td>
    </tr>"

    if {$options(.TOC)} {
        write_html "    <tr><td class=\"bug\"><a href=\"#toc\" class=\"link2\">&nbsp;TOC&nbsp;</a><br /></td></tr>"
    }
    write_html "</table>"
}

proc toc_html {anchor} {
    global options

    if {[string compare $anchor ""]} {
        write_html "<a name=\"$anchor\"></a><br /><hr />"
    }

    if {!$options(.TOC)} {
        return
    }

    if {[string compare $anchor toc]} {
        write_html "<table summary=\"layout\" cellpadding=\"0\" cellspacing=\"2\" class=\"bug\" align=\"right\"><tr><td class=\"bug\"><a href=\"#toc\" class=\"link2\">&nbsp;TOC&nbsp;</a></td></tr></table>"
    }
}

proc pcdata_html {text {pre 0}} {
    global entities
    global options
    global doingP needP
    global imgP
    global emptyP

    if {$imgP} {
        return
    }

    set lines ""

    regsub -all -nocase {&apos;} $text {\&#039;} text
    regsub -all "&rfc.number;" $text [lindex $entities 1] text
    if {$pre} {
        set needP 0
        regsub -line -all {[ \t]*$} $text "" text
        if {![slide_pre $text]} {
            if {$doingP} {
                append lines "</p>\n"
            }
            append lines [pre_tag_html begin]
            append lines $text
            append lines [pre_tag_html end]
            if {$doingP} {
                append lines "<p>\n"
            }
        }
    } else {
        if {$options(.EMOTICONIC)} {
            set text [emoticonic_html $text]
        }

        append lines $text
    }
    if {![cellP $lines]} {
        if {$needP} {
            set doingP 1
            set needP 0
            write_html -nonewline "<p>"
        }
        write_html -nonewline $lines
        set emptyP 0
    }
}

proc emoticonic_html {text} {
    foreach {ei begin end} [list *  <strong> </strong> \
                                 '  <b>      </b>      \
                                {"} <b>      </b>] {
        set body ""
        while {[set x [string first "|$ei" $text]] >= 0} {
            if {$x > 0} {
                append body [string range $text 0 [expr $x-1]]
            }
            append body "$begin"
            set text [string range $text [expr $x+2] end]
            if {[set x [string first "|" $text]] < 0} {
                error "missing close for |$ei"
            }
            if {$x > 0} {
                append body [string range $text 0 [expr $x-1]]
            }
            append body "$end"
            set text [string range $text [expr $x+1] end]
        }
        append body $text
        set text $body
    }

    return $text
}


#
# slides sub-mode
#

catch {
    package require Trf
}

set leftGif \
"R0lGODlhFAAWAKEAAP///8z//wAAAAAAACH+TlRoaXMgYXJ0IGlzIGluIHRoZSBwdWJsaWMgZG9t
YWluLiBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQuY29tLCBTZXB0ZW1iZXIgMTk5NQAh+QQBAAAB
ACwAAAAAFAAWAAACK4yPqcvN4h6MSViK7MVBb+p9TihKZERqaDqNKfbCIdd5dF2CuX4fbQ9kFAAA
Ow=="

set rightGif \
"R0lGODlhFAAWAKEAAP///8z//wAAAAAAACH+TlRoaXMgYXJ0IGlzIGluIHRoZSBwdWJsaWMgZG9t
YWluLiBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQuY29tLCBTZXB0ZW1iZXIgMTk5NQAh+QQBAAAB
ACwAAAAAFAAWAAACK4yPqcsd4pqAUU1az8V58+h9UtiFomWeSKpqZvXCXvZsdD3duF7zjw/UFQAA
Ow=="

set upGif \
"R0lGODlhFAAWAKEAAP///8z//wAAAAAAACH+TlRoaXMgYXJ0IGlzIGluIHRoZSBwdWJsaWMgZG9t
YWluLiBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQuY29tLCBTZXB0ZW1iZXIgMTk5NQAh+QQBAAAB
ACwAAAAAFAAWAAACI4yPqcvtD6OcTQgarJ1ax949IFiNpGKaSZoeLIvF8kzXdlAAADs="

proc end_rfc_slides {} {
    global ifile
    global passno
    global slideno slidewd slidemx

    if {$passno != 2} {
        end_page_slides
        return 1
    }

    set slidemx $slideno
    set slidewd [expr int(log10($slideno))+1]
    foreach file [glob -nocomplain [file rootname $ifile]-*.html] {
        catch { file delete -force $file }
    }

    if {![string compare [info commands base64] base64]} {
        set inputD [file dirname $ifile]

        foreach gif {left right up} {
            global ${gif}Gif

            if {![file exists [set file [file join $inputD ${gif}.gif]]]} {
                set fd [open $file {WRONLY CREAT TRUNC}]
                fconfigure $fd -translation binary

                puts -nonewline $fd [base64 -mode decode -- [set ${gif}Gif]]

                close $fd
            }
        }
    }

    return 0
}

proc front_slides_begin {left right top bottom title} {
    global passno
    global out_fd
    global slideno slideft

    set slideno 0
    start_page_slides [set slideft [lindex $title 0]]

    if {$passno == 2} {
        return 0
    }

    set size 4
    puts $out_fd "<br /><br /><br /><br /><p align=\"right\">"
    puts $out_fd "<table width=\"75%\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">"
    puts $out_fd "<tr><td>"
    puts $out_fd "<table width=\"100%\" border=\"0\" cellpadding=\"2\" cellspacing=\"1\">"
    set left [munge_long $left]
    set right [munge_long $right]
    set lc ""
    set rc ""
    foreach l $left r $right {
        if {[string compare $l ""]} {
            set l $l
        } else {
            set l "&nbsp;"
        }
        if {[string compare $r ""]} {
            set r $r
        } else {
            set r "&nbsp;"
        }
        puts $out_fd "<tr valign=\"top\">"
        puts $out_fd "<td width=\"33%\"><font color=\"#006600\" size=\"+$size\">$l</font></td>"
        puts $out_fd "<td width=\"33%\"><font color=\"#006600\" size=\"+$size\">$r</font></td>"
        puts $out_fd "</tr>"

        set size 3
    }
    puts $out_fd "</table>"
    puts $out_fd "</td></tr>"
    puts $out_fd "</table>"
    puts $out_fd "</p>"

    return 1
}

proc start_page_slides {{title ""}} {
    global passno
    global ifile
    global out_fd
    global slideno slidenm

    if {$passno < 3} {
        return
    }

    if {$slideno == 0} {
        catch { close $out_fd }
        catch { file delete -force [file rootname].html }
    }

    set out_fd [open [file rootname $ifile]-[set p [slide_foo $slideno]].html \
                     { WRONLY CREAT TRUNC }]
    catch { fconfigure $out_fd -encoding utf-8 }

    if {[string compare $title ""]} {
        set slidenm $title
    } else {
        set title "$slidenm (continued)"
    }
    if {$slideno != 0} {
        append p ": "
    } else {
        set p ""
    }
    write_html "<\!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">"
    puts $out_fd "<html><head><title>"
    pcdata_html $p$title
    puts $out_fd "</title></head>"
    puts $out_fd "<body text=\"#000000\" vlink=\"#006600\" alink=\"#ccddcc\" link=\"#006600\"\n      bgcolor=\"#ffffff\">"
    puts $out_fd "<font face=\"arial, helvetica, sans-serif\">"
    puts $out_fd "<table height=\"100%\" cellspacing=\"0\" cellpadding=\"0\" width=\"100%\" border=\"0\">"
    puts $out_fd "<tbody><tr><td valign=\"top\">"

    puts $out_fd "<table height=\"100%\" cellspacing=\"0\" cellpadding=\"0\" width=\"100%\" border=\"0\">"
    puts $out_fd "<tbody><tr><td valign=\"top\">"
    puts $out_fd "<p><font color=\"#006600\" size=\"+5\">$title</font></p>"

    puts $out_fd "<br /><br />"
    puts $out_fd "<font size=\"+3\">"
}

proc end_page_slides {} {
    global passno
    global ifile
    global out_fd
    global slideno slidemx slideft

    if {$passno < 3} {
        incr slideno
        return 0
    }

    set up [file rootname [file tail $ifile]]-[slide_foo 0].html
    if {[set left [expr $slideno-1]] < 0} {
        set left $slidemx
    }
    set left [file rootname [file tail $ifile]]-[slide_foo $left].html
    if {[set right [expr $slideno+1]] > $slidemx} {
        set right 0
    }
    set right [file rootname [file tail $ifile]]-[slide_foo $right].html

    puts $out_fd "</font>"
    puts $out_fd "</td></tr></tbody>"
    puts $out_fd "</table>"
    puts $out_fd "</td><td valign=\"bottom\" align=\"right\">"
    puts -nonewline \
         $out_fd "<p align=\"right\"><nobr>"
    puts -nonewline \
         $out_fd "<a href=\"$left\"><img src=\"left.gif\" border=\"0\" width=\"20\" height=\"22\" /></a>"
    puts -nonewline \
         $out_fd "<a href=\"$up\"><img src=\"up.gif\" border=\"0\" width=\"20\" height=\"22\" /></a>"
    puts -nonewline \
         $out_fd "<a href=\"$right\"><img src=\"right.gif\" border=\"0\" /></a>"
    puts $out_fd "</nobr></p>"
    puts $out_fd "</td></tr>"
    puts $out_fd "<tr><td align=\"right\" colspan=\"2\">"
    puts $out_fd "<font color=\"#006600\" size=\"-3\">"
    pcdata_html $slideft
    pcdata_html "</font>"
    puts $out_fd "</td></tr></tbody>"
    puts $out_fd "</table>"
    puts $out_fd "</font></body></html>"

    catch { close $out_fd }
    set out_fd ""

    incr slideno
    return 1
}

proc slide_pre {text} {
    global passno
    global out_fd
    global doingP needP

    if {$passno < 3} {
        return 0
    }

    set needP 0
    if {$doingP} {
        puts $out_fd "</p>"
    }
    set    t [pre_tag_html begin]
    append t $text
    append t [pre_tag_html end]
    puts $out_fd $t
    if {$doingP} {
        puts $out_fd "<p>"
    }

    return 1
}

proc slide_foo {n} {
    global slidewd

    return [format %*.*d $slidewd $slidewd $n]
}


proc pre_tag_html {tag} {
    set str ""

    switch -- $tag {
        begin {
            #set table "<table border='0' cellspacing='0' cellpadding='0' width='100%'>"
            set table "<div style='display: table; width: 0px; margin-left: auto; margin-right:"
            #set st "<tbody><tr><td></td><td>"
            switch -- [current_align] {
                #center { append str "$table<col width='50%' /><col /><col width='50%'>$st" }
                center { append str "$table auto'>" }
                #right  { append str "$table<col width='100%' /><col />$st" }
                right  { append str "$table 0px'>" }
            }
            append str "<pre>"
        }

        end {
            append str "</pre>"
            #set et "</td></tr></tbody></table>"
            switch -- [current_align] {
                #center { append str "</td><td>$et" }
                #right  { append str $et }
                center - right { append str "</div>" }
            }
        }
    }

    return $str
}

proc pi_html {key value} {
    switch -- $key {
        needLines {}

        typeout {
            global passno

            if {$passno == 2} {
                puts stdout $value
            }
        }

        default {
            error ""
        }
    }
}

proc write_html {a1 {a2 ""}} {
    global options
    global passno
    global out_fd

    if {($options(.SLIDES)) || ($passno == 3)} {
        set command [list puts]
        if {![string compare $a1 -nonewline]} {
            lappend command -nonewline
            set a1 $a2
        }
        eval $command [list $out_fd $a1]
    }
}


#
# nroff output
#

proc rfc_nr {irefs iprstmt copying newP} {
    global options copyrightP iprP
    global funding validity
    global pageno
    global indexpg

    flush_text

    if {[llength $irefs] > 0} {
        end_page_nr

        set indexpg $pageno

        condwrite_in_nr 0 1
        write_line_nr "Index"

        condwrite_in_nr 12 1
        foreach iref $irefs {
            foreach {L item subitem flags pages} $iref { break }

            if {[string compare $L ""]} {
                write_it ".br"
                write_line_nr ""
                write_it ".ti 3"
                write_line_nr $L
            }

            set subitem [chars_expand $subitem]
            if {[string compare $item ""]} {
                write_it ".br"
                do_indent_text_nr [chars_expand $item] 6
                if {[string compare $subitem ""]} {
                    flush_text
                    write_it ".br"
                    do_indent_text_nr $subitem 9
                }
            } else {
                write_it ".br"
                do_indent_text_nr $subitem 9
            }

            write_text_nr "  [collapsed_num_list $pages]"
            flush_text
        }

        #condwrite_in_nr 0 1
    }

    if {(!$options(.PRIVATE)) && $copyrightP} {
        end_page_nr

        set result $pageno

        condwrite_in_nr 3 1

        if {$iprP} {
            global iprurl ipremail

            write_it ".ti 0"
            write_line_nr "Intellectual Property Statement"

            regsub -all %IPRURL% $iprstmt $iprurl iprstmt
            regsub -all %IPREMAIL% $iprstmt $ipremail iprstmt

            foreach para $iprstmt {
                write_line_nr ""
                pcdata_nr $para
            }
            write_line_nr "" -1
            write_line_nr "" -1
        }

        if {$newP} {
            if {![have_lines 4]} {
                end_page_nr
            }

            write_it ".ti 0"
            write_line_nr "Disclaimer of Validity"

            foreach para $validity {
                write_line_nr ""
                pcdata_nr $para
            }
            write_line_nr "" -1
            write_line_nr "" -1
        }

        if {![have_lines 4]} {
            end_page_nr
        }

        write_it ".ti 0"
        if {$newP} {
            write_line_nr "Copyright Statement"
        } else {
            write_line_nr "Full Copyright Statement"
        }

        foreach para $copying {
            write_line_nr ""
            pcdata_nr $para
        }
        write_line_nr "" -1
        write_line_nr "" -1

        if {![have_lines 4]} {
            end_page_nr
        }

        write_it ".ti 0"
        write_line_nr "Acknowledgment"
        write_line_nr ""
        pcdata_nr $funding

        flush_text
    } else {
        set result ""
    }

    return $result
}

proc front_nr_begin {left right top bottom title status copying keywords
                     lang} {
    global prog prog_version
    global options copyrightP
    global lineno pageno blankP
    global eatP nofillP indent lastin
    global passno indexpg

    set lineno 1
    set pageno 1
    set blankP 0
    set eatP 0
    set lastin -1

    write_it [clock format [clock seconds] \
                    -format ".\\\" automatically generated by $prog $prog_version on %Y-%m-%dT%H:%M:%SZ" \
                    -gmt true]
    write_it ".\\\" "
    write_it ".pl 10.0i"
    write_it ".po 0"
    write_it ".ll 7.2i"
    write_it ".lt 7.2i"
    write_it ".nr LL 7.2i"
    write_it ".nr LT 7.2i"
    write_it ".ds LF [nbsp_expand_nr [chars_expand [lindex $bottom 0]]]"
    write_it ".ds RF FORMFEED\[Page %]"
    write_it ".ds CF [nbsp_expand_nr [chars_expand [lindex $bottom 1]]]"
    write_it ".ds LH [nbsp_expand_nr [chars_expand [lindex $top 0]]]"
    write_it ".ds RH [nbsp_expand_nr [chars_expand [lindex $top 2]]]"
    write_it ".ds CH [nbsp_expand_nr [chars_expand [lindex $top 1]]]"
    write_it ".hy 0"
    write_it ".nh"
    write_it ".ad l"
    set nofillP -1
    condwrite_nf_nr

    if {$passno == 2} {
        set indexpg 0
    }

    incr lineno 2

    condwrite_in_nr 0 1

    if {$options(.TOPBLOCK)} {
        set left [munge_long $left]
        set right [munge_long $right]
        foreach l $left r $right {
            set l [chars_expand $l]
            set r [chars_expand $r]
            set len [expr 72-[string length $l]]
            write_line_nr [format %s%*.*s $l $len $len $r]
        }
        write_line_nr "" -1
        write_line_nr "" -1
    }

    foreach line $title {
        write_text_nr [chars_expand $line] c
    }

    write_line_nr "" -1

    condwrite_in_nr 3 1

    if {!$options(.PRIVATE)} {
        write_it ".ti 0"
        write_line_nr "Status of this Memo"
        foreach para $status {
            write_line_nr ""
            pcdata_nr $para
        }
    }

    if {(!$options(.PRIVATE)) && $copyrightP} {
        write_line_nr "" -1
        write_it ".ti 0"
        write_line_nr "Copyright Notice"
        write_line_nr "" -1
        pcdata_nr $copying
    }
}

proc front_nr_end {toc irefP} {
    global options noticeT
    global lineno
    global indents
    global indexpg

    if {$options(.TOC)} {
        set last [lindex $toc end]
        if {[string compare [lindex $last 1] $noticeT]} {
            set last ""
        } else {
            set toc [lreplace $toc end end]
        }
        if {$irefP} {
            lappend toc [list "" Index $indexpg]
        }
        if {[string compare $last ""]} {
            lappend toc $last
        }

        if {(![have_lines [expr [llength $toc]+3]]) || ($lineno > 17)} {
            end_page_nr
        } else {
            write_line_nr "" -1
        }
        condwrite_in_nr 0 1
        set indents {}
        write_line_nr "Table of Contents"
        write_line_nr "" -1

        condwrite_nf_nr

        set len1 0
        set len2 0
        foreach c $toc {
            if {[set x [string length [lindex $c 0]]] > $len1} {
                set len1 $x
            }
            if {[set x [string length [lindex $c 2]]] > $len2} {
                set len2 $x
            }
        }
        set len3 [expr 5-$len2]
        set len2 5
        set mid [expr 72-($len1+$len2+5)]

        set lenX $len1
        set midX $mid
        set oddX [expr $mid%2]
        foreach c $toc {
            if {!$options(.TOCOMPACT)} {
                if {[string last . [lindex $c 0]] \
                        == [expr [string length [lindex $c 0]]-1]} {
                    write_line_nr ""
                }
            }
            if {$options(.TOCINDENT)} {
                set len1 [expr [set y [string length [lindex $c 0]]]+1]
                if {$y == 0} {
                    incr len1 2
                }
                set mid [expr $midX+$lenX-$len1]
                set oddP [expr $mid%2]
                if {$oddP != $oddX} {
                    incr len1 1
                    incr mid -1
                }
            }
            set s1 [format "   %-*.*s " $len1 $len1 [lindex $c 0]]
            set s2 [format " %*.*s" $len2 $len2 [lindex $c 2]]
            set title [chars_expand [string trim [lindex $c 1]]]
            while {[set i [string length $title]] > $mid} {
                set phrase [string range $title 0 [expr $mid-1]]
                if {[set x [string last " " $phrase]] < 0} {
                    if {[set x [string first " " $title]] < 0} {
                        break
                    }
                }
                write_toc_nr $s1 [string range $title 0 [expr $x-1]] \
                        [format " %-*.*s" $len2 $len2 ""] $mid 0
                set s1 [format "   %-*.*s " $len1 $len1 ""]
                set title [string trimleft [string range $title $x end]]
            }
            if {$len3 > 0} {
                set s2 [string range $s2 $len3 end]
            }
            write_toc_nr $s1 $title $s2 [expr $mid+$len3] 1
        }
    }

    if {($options(.TOC) || !$options(.COMPACT))} {
        end_page_nr
    }
}

proc write_toc_nr {s1 title s2 len dot} {
    write_toc_txt $s1 $title $s2 $len $dot
}

proc abstract_nr {} {
    write_line_nr "" -1
    write_it ".ti 0"
    write_line_nr "Abstract"
    write_line_nr "" -1
}

proc note_nr {title depth} {
    write_line_nr "" -1
    write_it ".ti 0"
    write_line_nr [chars_expand $title]
    write_line_nr "" -1
}

proc section_nr {prefix top title lines anchor} {
    global options
    global pageno

    if {($top && !$options(.COMPACT)) || (![have_lines [expr $lines+2]])} {
        end_page_nr
    } else {
        write_line_nr "" -1
    }

    indent_text_nr "$prefix  " 0
    write_text_nr [chars_expand $title]
    flush_text
    pop_indent

    condwrite_in_nr 3 1

    return $pageno
}

proc t_nr {tag counter style hangText editNo} {
    global options
    global eatP

    if {$eatP < 0} {
        set eatP 1
    }
    if {![string compare $tag end]} {
        return
    }

    if {[string compare $counter ""]} {
        set pos [pop_indent]
        set l [split $counter .]
        set left -1
        set lines 3
        switch -- $style {
            letters {
                set counter [offset2letters [lindex $l end] [llength $l]]
                # prevent two_spaces from kicking in.
                append counter ".\xA0"
            }

            numbers {
                # prevent two_spaces from kicking in.
                set counter "[lindex $l end].\xA0"
            }

            symbols {
                set counter "[lindex { - o * + } [expr [llength $l]%4]] "
            }

            hanging {
                # prevent two_spaces from kicking in.
                set counter "[chars_expand $hangText]\xA0"
                set left ""
                set lines 5
            }

            default {
                set counter "  "
                set left -2
            }
        }
        if {![have_lines $lines]} {
            end_page_nr
        }
        if {$options(.EDITING)} {
            write_editno_nr $editNo
        } elseif {!$options(.SUBCOMPACT)} {
            write_line_nr ""
        }
        indent_text_nr [format "%-[expr $pos-0]s" $counter] $left
        pop_indent
        push_indent $pos
    } else {
        if {$options(.EDITING)} {
            write_editno_nr $editNo
        } else {
            write_line_nr ""
        }
    }

    set eatP 1
}

proc list_nr {tag counters style hangIndent hangText suprT} {
    global options
    global eatP
    global indent

    switch -- $tag {
        begin {
            switch -- $style {
                letters {
                  set i [expr int(log([llength $counters])/log(26))+2]
                }

                numbers {
                    set i 0
                    foreach counter $counters {
                        if {[set j [string length \
                                           [lindex [split $counter .] end]]] \
                                > $i} {
                            set i $j
                        }
                    }
                    incr i 1
                }

                format {
                    set i [expr [string length [chars_expand $hangText]]-1]
                }

                default {
                    set i 1
                }
            }
            if {[incr i 2] > $hangIndent} {
                push_indent [expr $i+0]
            } else {
                push_indent [expr $hangIndent+0]
            }
        }

        end {
            flush_text
            if {!$options(.SUBCOMPACT)} {
                write_line_nr ""
            }
            pop_indent

            set eatP 1

            condwrite_in_nr $indent
        }
    }
}

proc figure_nr {tag lines anchor title {av {}}} {
    figure_txt $tag $lines $anchor $title $av
}

proc artwork_nr {tag lines {av {}}} {
    artwork_txt $tag $lines $av
}

proc preamble_nr {tag {editNo ""}} {
    preamble_txt $tag $editNo
}

global tblindent
set tblindent 0

proc postamble_nr {tag {editNo ""}} {
    global tblindent

    postamble_txt $tag $editNo

    if {![string compare $tag "begin"] && ($tblindent > 0)} {
        condwrite_in_nr $tblindent
    }
    set tblindent 0
}

proc texttable_nr {tag lines anchor title {didP 0}} {
    global tblindent

    texttable_txt $tag $lines $anchor $title $didP
    if {![string compare $tag "end"] && ($tblindent > 0)} {
        condwrite_in_nr $tblindent
    }
    set tblindent 0
}

proc ttcol_nr {text align col width} {
    global tblindent indent

    if {$tblindent == 0} {
        flush_text
        set tblindent $indent
        condwrite_in_nr 0
    }
    ttcol_txt $text $align $col $width
}

proc c_nr {tag row col align} {
    c_txt $tag $row $col $align
}

proc xref_nr {text av target format {hackP 0}} {
    condwrite_fi_nr
    xref_txt $text $av $target $format $hackP
}

proc eref_nr {text counter target} {
    condwrite_fi_nr
    eref_txt $text $counter $target
}

proc cref_nr {text counter source anchor} {
    condwrite_fi_nr
    cref_txt $text $counter $source $anchor
}

proc iref_nr {item subitem flags} {
    global pageno

    return $pageno
}

proc vspace_nr {lines} {
    vspace_txt $lines
}

proc spanx_nr {text style} {
    condwrite_fi_nr
    spanx_txt $text $style
}

proc references_nr {tag args} {
    global counter depth
    global pageno

    switch -- $tag {
        begin {
            set prefix [lindex $args 0]
            set title [lindex $args 1]
            if {($depth(references) > 1) \
                    && (![info exists counter(references)])} {
                set counter(references) 0
                section_nr [lindex [split $prefix .] 0]. 1 References 0 ""
            }
            if {![have_lines 5]} {
                end_page_nr
            } else {
                write_line_nr "" -1
            }

            indent_text_nr "$prefix  " 0
            write_text_nr [chars_expand $title]
            flush_text
            pop_indent

            condwrite_in_nr 3 1

            return $pageno
        }

        end {
            set erefP [lindex $args 0]
            if {$erefP} {
                erefs_nr
            } else {
                flush_text
            }
        }
    }
}

proc erefs_nr {{title ""}} {
    global erefs
    global options

    if {[string compare $title ""]} {
        if {$options(.COMPACT)} {
            write_line_nr ""
        } else {
            end_page_nr
        }
        condwrite_fi_nr
        write_it ".ti 0"
        write_line_nr $title
    }

    set names  [lsort -integer [array names erefs]]
    set width [expr [string length [lindex $names end]]+2]
    foreach eref $names {
        write_line_nr ""

        indent_text_nr "[format %-*.*s $width $width "\[$eref\]"]  " -1

        write_url $erefs($eref)
        flush_text

        pop_indent
    }

    flush_text
}

proc crefs_nr {title} {
    global crefs
    global options

    if {[string compare $title ""]} {
        if {$options(.COMPACT)} {
            write_line_nr ""
        } else {
            end_page_nr
        }
        condwrite_fi_nr
        write_it ".ti 0"
        write_line_nr $title
    }

    set names  [lsort -dictionary [array names crefs]]
    set width 0
    foreach cref $names {
        set x [string length $cref]
        if {$x > $width} {
            set width $x
        }
    }
    incr width 2
    foreach cref $names {
        write_line_nr ""

        indent_text_nr "[format %-*.*s $width $width "\[$cref\]"]  " -1

        write_text_nr [lindex $crefs($cref) 3]
        flush_text

        pop_indent
    }

    flush_text
}

proc reference_nr {prefix names title series formats date anchor target
                   target2 width annotations} {
    write_line_nr ""

    incr width 2
    set i [expr [string length \
                        [set prefix \
                             [format %-*s $width "\[$prefix\]"]]+2]]

    if {$i > 11} {
# the indent_text_nr abstraction isn't robust enough to figure this out...

        global indent

        flush_text
        condwrite_fi_nr

        push_indent 14

        condwrite_in_nr [set indent 14]
        write_it ".ti 3"
        write_line_nr $prefix
        write_it ".br"
    } else {
        indent_text_nr "$prefix  " 3
    }

    set s ""
    set nameA 1
    set nameN [llength $names]
    foreach name $names {
        incr nameA
        write_text_nr $s[chars_expand [lindex $name 0]]
        set s [list_sep_str $nameA $nameN]
    }
    write_text_nr "$s\"[chars_expand $title]\""
    foreach serial $series {
        if {[regexp -nocase -- "internet-draft&nbsp;(draft-.*)" $serial x n] == 1} {
            set serial "$n (work in progress)"
        }
        write_text_nr ", [chars_expand $serial]"
    }
    if {[string compare $date ""]} {
        write_text_nr ", [chars_expand $date]"
    }
    if {[string compare $target ""]} {
        write_text_nr ", "
        write_url $target
    }
    write_text_nr .

    while {[llength $annotations] > 0} {
        write_line_nr ""
        pcdata_nr [lindex $annotations 0]
        set annotations [lrange $annotations 1 end]
    }

    pop_indent
}

proc annotation_nr {tag} {
    annotation_txt $tag
}

proc back_nr {authors} {
    global options
    global lineno pageno
    global contacts

    set lines 5
    set author [lindex $authors 0]
    incr lines [llength [lindex $author 0]]
    incr lines [llength [lindex $author 1]]
    if {![have_lines $lines]} {
        end_page_nr
    } elseif {$lineno != 3} {
        write_line_nr "" -1
        write_line_nr "" -1
    }
    set result $pageno

    condwrite_in_nr 3 1
    condwrite_nf_nr

    switch -- [llength $authors] {
        0 {
            return $result
        }

        1 {
            set s1 "'s"
            set s2 ""
        }

        default {
            set s1 "s'"
            set s2 "es"
        }
    }
    set s "Author$s1 Address$s2"

    set firstP 1
    foreach author $authors {
        set block1 [lindex $author 0]
        set block2 [lindex $author 1]

        set lines 4
        incr lines [llength $block1]
        incr lines [llength $block2]
        if {![have_lines $lines]} {
            end_page_nr
        }

        if {[string compare $s ""]} {
            write_it ".ti 0"
            write_line_nr $s
            set s ""
        } else {
            write_line_nr "" -1
        }
        write_line_nr "" -1

        foreach line $block1 {
            write_line_nr [chars_expand $line]
        }

        if {[llength $block2] > 0} {
            write_line_nr ""
            foreach contact $block2 {
                set key [lindex $contact 0]
                set value [lindex [lindex $contacts \
                                          [lsearch0 $contacts $key]] 1]
                set value [format %-6s $value:]
                if {$options(.COLONSPACE)} {
                    append value " "
                }
                write_line_nr "$value [chars_expand [lindex $contact 1]]"
            }
        }
    }

    return $result
}

proc pcdata_nr {text {pre 0}} {
    global eatP
    global options
    global pcdata_line_offset

    if {(!$pre) && ($eatP > 0)} {
        set text [string trimleft $text]
    }
    if {[string length $text] <= 0} {
        # Was only white space, but got trimmed.
        return
    }
    set eatP 0

    if {!$pre} {
        regsub -all "\n\[ \t\n\]*" $text "\n" text
        regsub -all "\[ \t\]*\n\[ \t\]*" $text "\n" text
        set prefix ""

        if {$options(.EMOTICONIC)} {
            set text [emoticonic_txt $text]
        }
    }

    if {$pre} {
        condwrite_nf_nr
    } else {
        condwrite_fi_nr
    }
    if {[cellP $text]} {
        return
    }

    set pcdata_line_offset 0
    foreach line [split $text "\n"] {
        set line [chars_expand $line]
        if {$pre} {
            write_line_nr [string trimright $line] $pre
        } else {
            write_pcdata_nr $prefix$line
            set prefix " "
        }
        incr pcdata_line_offset
    }
    if {$pre} {
        condwrite_in_nr 3
    }
    set pcdata_line_offset 0

    if {[regexp -- {[ \t\n]$} $text]} {
        set eatP 1
    }
}


proc start_page_nr {} {
    global lineno blankP

    set lineno 3
    set blankP 1
}

proc end_page_nr {} {
    global lineno pageno

    flush_text

    if {$lineno <= 3} {
        return
    }

    incr pageno
    set lineno 0

    write_it ".bp"
}

proc indent_text_nr {prefix {left ""}} {
    global indent

    flush_text
    condwrite_fi_nr

    if {![string compare $left ""]} {
        set left $indent
        while {![string compare [string index $prefix 0] " "]} {
            incr left
            set prefix [string range $prefix 1 end]
        }
        push_indent 3
    } elseif {$left < 0} {
        if {$left == -1} {
            set left $indent
        }
        push_indent [string length $prefix]
        if {$left == -2} {
            set left $indent
            set prefix ""
        }
    } else {
        push_indent [expr $left+[string length $prefix]-$indent]
    }
    condwrite_in_nr $indent
    do_indent_text_nr $prefix $left
}

proc do_indent_text_nr {text left} {
    global buffer
    global indent

    write_it ".ti $left"
    # In case $left==0, we have to put $text in buffer ourselves now,
    # otherwise the next write_text_nr will prepend an indent and screw
    # the line-breaking algorithm (nroff can undo that) but more
    # importantly the value of lineno.  The page could end up shorter
    # as a result of an over-inflated lineno.
    set buffer [format %*.*s%s $left $left "" $text]
    if {$indent != 0 && [string length $buffer] == 0} {
        unexpected error "internal bug triggered in do_indent_text_nr; report it!"
    }
    write_text_nr ""
}

proc write_pcdata_nr {text} {
    global buffer

    if {![string compare $buffer ""]} {
        setup_align_nr begin [current_align]
    }

    write_pcdata_txt $text
}

proc write_editno_nr {editNo} {
    global buffer

    if {[string compare $buffer ""]} {
        flush_text
    }
    write_it ".ti 0"
    write_it <$editNo>
    write_it ".br"
}

proc write_text_nr {text {direction l} {magic 0}} {
    global buffer buffer_rest buffer_align
    global indent
    global eatP

    if {$eatP < 0} {
        set text " $text"
    }
    switch -- $direction {
        c - r { flush_text }
    }
    if {![string compare $buffer ""]} {
        condwrite_in_nr $indent
        switch -- $direction {
            c - r {}
            default {
                setup_align_nr begin [set buffer_align [current_align]]
            }
        }
        set buffer [format %*.*s $indent $indent ""]
    }
    append buffer $text

    set flush [string compare $direction l]
    while {([string length $buffer] > 72) || ($flush)} {
        set text [fold_text_txt]

        setup_align_nr oneshot $direction
        write_line_nr [string trimleft $text] 0 $magic

        if {![string compare [set buffer $buffer_rest] ""]} {
            setup_align_nr end $buffer_align
            set buffer_align ""
            break
        }
    }
}

proc write_line_nr {line {pre 0} {magic 0}} {
    global lineno blankP

    flush_text
    if {$lineno == 0} {
        start_page_nr
    }
    if {![set x [string length [set orig_line $line]]]} {
        set blankO $blankP
        set blankP 1
        if {($blankO) && (!$pre || $lineno == 3)} {
            return
        }
    } else {
        set blankP 0
    }
    if {($pre) && ($x)} {
        condwrite_in_nr [expr $pre > 0 ? $pre : 3]
        if {$pre > 0} {
            set line [tabs_expand_pre $line]
            set x [string length [set orig_line $line]]
        }
    }
    if {!$magic} {
        regsub -all "\\\\" $line "\\\\\\" line
    }
    regsub -all "'" $line "\\'" line
    set line [nbsp_expand_nr $line]
    if {[string first "." $line] == 0} {
        set line "\\&$line"
    }
    if {!($pre)} {
        regsub -all "\[^ \t\n\]*-" $line "\\%\&" line
    }
    write_it $line
    incr lineno
    if {$pre > 0 && [set len [expr $pre + $x]] > 72} {
        global pageno

        regsub -all -- {"} [string range $orig_line [expr 72 - $pre] end] {\"} excess
        unexpected [unex_condtype] \
            "output line $lineno (on page $pageno) has $len > 72 characters (excess string is \"$excess\")"
    }
    if {$lineno >= 51} {
        end_page_nr
    }
}

proc nbsp_expand_nr {s} {
    global nbsp

    regsub -all "$nbsp" [string trimright $s] "\\\\0" s
    return $s
}

proc pi_nr {key value} {
    pi_txt $key $value
}

# Only proc allowed to write a ".fi" or set nofillP to zero.
proc condwrite_fi_nr {} {
    global nofillP
    #global lastin

    if {$nofillP != 0} {
        flush_text
        write_it ".fi"
        set nofillP 0
        # Is the next line necessary on some nroff's???
        #set lastin -1
    }
}

# Only proc allowed to write a ".nf" or set nofillP positive.
proc condwrite_nf_nr {} {
    global nofillP

    if {$nofillP <= 0} {
        flush_text
        write_it ".nf"
        set nofillP 1
    }
}

# Only proc allowed to write a ".in" or update lastin.
proc condwrite_in_nr {in {reset 0}} {
    global lastin

    if {$lastin != $in} {
        flush_text
        write_it ".in [set lastin $in]"
        if {$reset} {
            global indents indent

            set indent $in
            set indents {}
        }
    }
}

# Assumes flush has been done.  Must NOT be done again.
proc setup_align_nr {tag dir} {
    switch -- $dir {
        c - center { set xx ce }
        r - right  { set xx rj }
        default    { return }
    }
    switch -- $tag {
        begin    { set v " 8192" }
        oneshot  { set v "" }
        end      { set v " 0" }
    }
    write_it ".$xx$v"
}


#
# low-level formatting
#


global contacts

set contacts { {phone Phone} {facsimile Fax} {email Email} {uri URI} }


global buffer indent indents

set buffer ""
set indent 3
set indents {}

global rfcTxtHome idTxtHome

set rfcTxtHome ftp://ftp.isi.edu/in-notes
set idTxtHome http://www.ietf.org/internet-drafts


global oentities entities

# Hex entities (&#x3F;) are first converted to dec entities (&#63;) elsewhere.
# Only put dec entities or (case-sensitive) named entities here.
# &amp; and &#38; must always be last and specified simultaneously.
# &nbsp; and &#160; are handled elsewhere and must not be put here.
set oentities { {&lt;}     {<} {&gt;}     {>}
                {&lpar;}   {(} {&rpar;}   {)}
                {&lsqb;}   {[} {&rsqb;}   {]}
                {&lcub;}   "{" {&rcub;}   "}"
                {&sol;}    {/} {&percnt;} {%}
                {&num;}    {#} {&dollar;} {$}
                {&ast;}    {*} {&hyphen;} {-}
                {&plus;}   {+} {&equals;} {=}
                {&comma;}  {,} {&period;} {.}
                {&colon;}  {:} {&semi;}   {;}
                {&excl;}   {!} {&quest;}  {?}
                {&commat;} {@} {&lowbar;} {_}
                {&circ;}   {^} {&grave;}  {`}
                {&bsol;}  "\\" {&verbar;} {|}
                {&apos;}   {'} {&quot;}   {"}
                {&lsquo;}  {'} {&rsquo;}  {'}
                {&#8216;}  {'} {&#8217;}  {'}
                {&ldquo;}  {"} {&rdquo;}  {"}
                {&#8220;}  {"} {&#8221;}  {"}
                {&#8211;}  {-} {&#8212;}  {--}
                {&#151;}   {--}
                {&ndash;}  {-} {&mdash;}  {--}
                {&#161;}     {!}
                {&#162;}     {[cents]}
                {&#163;}     {[pounds]}
                {&#164;}     {[currency units]}
                {&#165;}     {[yens]}
                {&#166;}     {|}
                {&#167;}     {S.}
                {&#168;}     {"}
                {&#169;}     {(C)}
                {&#170;}     {a}
                {&#171;}     {<<}
                {&#172;}     {[not]}
                {&#173;}     {-}
                {&#174;}     {(R)}
                {&#175;}     {_}
                {&#176;}     {o}
                {&#177;}     {+/-}
                {&#178;}     {^2}
                {&#179;}     {^3}
                {&#180;}     {'}
                {&#181;}     {[micro]}
                {&#182;}     {P.}
                {&#183;}     {.}
                {&#184;}     {,}
                {&#185;}     {^1}
                {&#186;}     {o}
                {&#187;}     {>>}
                {&#188;}     {1/4}
                {&#189;}     {1/2}
                {&#190;}     {3/4}
                {&#191;}     {?}
                {&#19[2-7];} {A}
                {&#198;}     {AE}
                {&#199;}     {C}
                {&#20[0-3];} {E}
                {&#20[4-7];} {I}
                {&#208;}     {[ETH]}
                {&#209;}     {N}
                {&#21[0-4];} {O}
                {&#215;}     {x}
                {&#216;}     {O}
                {&#21[7-9];} {U}
                {&#220;}     {U}
                {&#221;}     {Y}
                {&#222;}     {[THORN]}
                {&#223;}     {ss}
                {&#22[4-9];} {a}
                {&#230;}     {ae}
                {&#231;}     {c}
                {&#23[2-5];} {e}
                {&#23[6-9];} {i}
                {&#240;}     {[eth]}
                {&#241;}     {n}
                {&#24[2-6];} {o}
                {&#247;}     {/}
                {&#248;}     {o}
                {&#249;}     {u}
                {&#25[0-2];} {u}
                {&#253;}     {y}
                {&#254;}     {[thorn]}
                {&#255;}     {y}
                {&OElig;}    {OE}
                {&#338;}     {OE}
                {&oelig;}    {oe}
                {&#339;}     {oe}
                {&Yuml;}     {Y}
                {&#376;}     {Y}
                {&dagger;}   {*}
                {&#8224;}    {*}
                {&Dagger;}   {*}
                {&#8225;}    {*}
                {&bull;}     {o}
                {&#8226;}    {o}
                {&hellip;}   {...}
                {&#8230;}    {...}
                {&euro;}     {[euros]}
                {&#8364;}    {[euros]}
                {&trade;}    {[TM]}
                {&#8482;}    {[TM]} }

set l1entities {}
set c 161
foreach e {       iexcl  cent   pound  curren yen    brvbar sect
           uml    copy   ordf   laquo  not    shy    reg    macr
           deg    plusmn sup2   sup3   acute  micro  para   middot
           cedil  sup1   ordm   raquo  frac14 frac12 frac34 iquest
           Agrave Aacute Acirc  Atilde Auml   Aring  AElig  Ccedil
           Egrave Eacute Ecirc  Euml   Igrave Iacute Icirc  Iuml
           ETH    Ntilde Ograve Oacute Ocirc  Otilde Ouml   times
           Oslash Ugrave Uacute Ucirc  Uuml   Yacute THORN  szlig
           agrave aacute acirc  atilde auml   aring  aelig  ccedil
           egrave eacute ecirc  euml   igrave iacute icirc  iuml
           eth    ntilde ograve oacute ocirc  otilde ouml   divide
           oslash ugrave uacute ucirc  uuml   yacute thorn  yuml} {
    # Rewrite named as dec.
    lappend l1entities "&$e;" "\\&#$c;"
    incr c
}
# ISO Latin 1 named entities must appear before corresponding dec entities.
set oentities [concat $l1entities $oentities]

for {set c 32} {$c < 127} {incr c} {
    if {$c == 38} {
        # Must skip ampersand.
        continue
    }
    lappend oentities "&#$c;" [format %c $c]
}
lappend oentities     {&(amp|#38);} {\&}
set entities $oentities


global charsets
# We only list those that start with a 1-octet ASCII subset,
# and prefer those registered with the IANA.
# Format:  tcl-encoding {iana-charset...}
set charsets {
    utf-8       {UTF-8}
    ascii       {US-ASCII ASCII ANSI_X3.4-1968 iso-ir-6 ANSI_X3.4-1986 ISO_646.irv:1991 ISO646-US us IBM367 cp367 csASCII}
    iso8859-1   {ISO-8859-1 ISO_8859-1:1987 iso-ir-100 ISO_8859-1 latin1 l1 IBM819 CP819 csISOLatin1}
    iso8859-2   {ISO-8859-2 ISO_8859-2:1987 iso-ir-101 ISO_8859-2 latin2 l2 csISOLatin2}
    iso8859-3   {ISO-8859-3 ISO_8859-3:1988 iso-ir-109 ISO_8859-3 latin3 l3 csISOLatin3}
    iso8859-4   {ISO-8859-4 ISO_8859-4:1988 iso-ir-110 ISO_8859-4 latin4 l4 csISOLatin4}
    iso8859-5   {ISO-8859-5 ISO_8859-5:1988 iso-ir-144 ISO_8859-5 cyrillic csISOLatinCyrillic}
    iso8859-6   {ISO-8859-6 ISO_8859-6:1987 iso-ir-127 ISO_8859-6 arabic ECMA-114 ASMO-708 csISOLatinArabic}
    iso8859-7   {ISO-8859-7 ISO_8859-7:1987 iso-ir-126 ISO_8859-7 greek greek8 ELOT_928 ECMA-118 csISOLatinGreek}
    iso8859-8   {ISO-8859-8 ISO_8859-8:1988 iso-ir-138 ISO_8859-8 hebrew csISOLatinHebrew}
    iso8859-9   {ISO-8859-9 ISO_8859-9:1989 iso-ir-148 ISO_8859-9 latin5 l5 csISOLatin5}
    iso8859-10  {ISO-8859-10 ISO_8859-10:1992 iso-ir-157 latin6 l6 csISOLatin6}
    iso8859-13  {ISO-8859-13}
    iso8859-14  {ISO-8859-14 ISO_8859-14:1998 iso-ir-199 ISO_8859-14 latin8 l8 iso-celtic}
    iso8859-15  {ISO-8859-15 ISO_8859-15 Latin-9}
    iso8859-16  {ISO-8859-16 ISO_8859-16:2001 iso-ir-226 ISO_8859-16 latin10 l10}
    iso2022     {JIS_Encoding}
    iso2022-jp  {ISO-2022-JP csISO2022JP}
    iso2022-kr  {ISO-2022-KR csISO2022KR}
    euc-cn      {}
    euc-jp      {EUC-JP Extended_UNIX_Code_Packed_Format_for_Japanese csEUCPkdFmtJapanese}
    euc-kr      {EUC-KR csEUCKR}
    big5        {Big5 csBig5}
    gb1988      {GB_1988-80 iso-ir-57 cn ISO646-CN csISO57GB1988}
    gb2312      {GB2312 csGB2312}
    jis0201     {JIS_X0201 X0201 csHalfWidthKatakana}
    koi8-r      {KOI8-R csKOI8R}
    koi8-u      {KOI8-U}
    shiftjis    {Shift_JIS MS_Kanji csShiftJIS}
    tis-620     {TIS-620}
    macRoman    {macintosh mac csMacintosh}
    macCentEuro {}
    macCroatian {}
    macCyrillic {}
    macGreek    {}
    macIceland  {}
    macJapan    {}
    macRomania  {}
    macThai     {}
    macTurkish  {}
    macUkraine  {}
    cp437       {IBM437 cp437 437 csPC8CodePage437}
    cp737       {}
    cp775       {IBM775 cp775 csPC775Baltic}
    cp850       {IBM850 cp850 850 csPC850Multilingual}
    cp852       {IBM852 cp852 852 csPCp852}
    cp855       {IBM855 cp855 855 csIBM855}
    cp857       {IBM857 cp857 857 csIBM857}
    cp860       {IBM860 cp860 860 csIBM860}
    cp861       {IBM861 cp861 861 cp-is csIBM861}
    cp862       {IBM862 cp862 862 csPC862LatinHebrew}
    cp863       {IBM863 cp863 863 csIBM863}
    cp864       {IBM864 cp864 csIBM864}
    cp865       {IBM865 cp865 865 csIBM865}
    cp866       {IBM866 cp866 866 csIBM866}
    cp869       {IBM869 cp869 869 cp-gr csIBM869}
    cp874       {}
    cp932       {}
    cp936       {GBK CP936 MS936 windows-936}
    cp949       {}
    cp950       {}
    cp1250      {windows-1250}
    cp1251      {windows-1251}
    cp1252      {windows-1252}
    cp1253      {windows-1253}
    cp1254      {windows-1254}
    cp1255      {windows-1255}
    cp1256      {windows-1256}
    cp1257      {windows-1257}
    cp1258      {windows-1258}
}

proc cs2enc {charset} {
    global charsets

    foreach {enc csl} $charsets {
        foreach cs $csl {
            if {![string compare -nocase $charset $cs]} {
                return $enc
            }
        }
        if {![string compare -nocase $charset $enc]} {
            set encx $enc
        }
    }
    if {[info exists encx]} {
        return $encx
    }

    return ""
}


proc push_indent {pos} {
    global indent indents

    lappend indents $pos
    incr indent $pos
}

proc pop_indent {} {
    global indent indents

    set pos [lindex $indents end]
    set indent [expr $indent - $pos]
    set indents [lreplace $indents end end]

    return $pos
}

global aligns
set aligns {}

proc push_align {a} {
    global aligns

    switch -- $a {
        left - center - right {
            lappend aligns $a
        }

        default {
            unexpected error \
                "align=\"$a\" attribute is invalid"
        }
    }
}

proc pop_align {} {
    global aligns

    set a [lindex $aligns end]
    set aligns [lreplace $aligns end end]

    return $a
}

proc current_align {} {
    global aligns

    if {[llength $aligns] > 0} {
        return [lindex $aligns end]
    }

    return ""
}

proc flush_text {} {
    global buffer buffer_align
    global mode

    if {[string compare $buffer ""]} {
        set rest $buffer
        set buffer ""
        switch -- $mode {
            txt     { set rest [justify_text_txt $rest $buffer_align] }
            default { set rest [string trim $rest] }
        }
        write_line_$mode $rest
        switch -- $mode {
            nr { setup_align_nr end $buffer_align }
        }
        set buffer_align ""
    }
}

proc munge_long {lines} {
    global mode

    set result ""

    foreach buffer $lines {
        set linkP 0
        if {(![string compare $mode html]) \
                && (([string match Obsoletes:* $buffer])
                        || ([string match Updates:* $buffer]))} {
            set linkP 1
        }
        while {[set i [string length $buffer]] > 34} {
            set line [string range $buffer 0 34]
            if {[set x [string last " " $line]] < 0} {
                if {[set x [string first " " $buffer]] < 0} {
                    break
                }
            }
            set line [string range $buffer 0 [expr $x-1]]
            if {$linkP} {
                set line [munge_line $line]
            }
            lappend result $line
            set buffer [string trimleft [string range $buffer $x end]]
        }

        if {$linkP} {
            set buffer [munge_line $buffer]
        }
        lappend result $buffer
    }

    return $result
}

proc munge_line {line} {
    global rfcTxtHome

    if {[set y [string first : $line]] >= 0} {
        set start [string range $line 0 $y]
        set line [string range $line [expr $y+1] end]
    } else {
        set start ""
    }

    if {[set y [string first " (" $line]] >= 0} {
        set tail [string range $line $y end]
        set line [string range $line 0 [expr $y-1]]
    } else {
        set tail ""
    }

    set s ""
    foreach n [split $line ,] {
        set n [string trim $n]
        append start $s "<a href='$rfcTxtHome/rfc$n.txt'>$n</a>"
        set s ", "
    }

    return $start$tail
}

proc write_url {url} {
    global mode

    write_text_$mode <[chars_expand $url]>
}

proc is_at_page_start {} {
    global lineno
    global mode

    flush_text
    if {$lineno == 0} {
        start_page_$mode
    }

    return [expr $lineno <= 3]
}

proc have_lines {cnt} {
    global lineno
    global options

    if {[is_at_page_start] || !$options(.AUTOBREAKS)} {
        return 1
    }
    if {($cnt <= 48) && ($lineno + $cnt > 51)} {
        return 0
    }
    return 1
}

proc write_it {line} {
    global passno
    global passmax
    global out_fd

    if {$passno == $passmax} {
        puts $out_fd $line
    }
}

proc collapsed_num_list {nums} {
    set r ""
    if {[llength $nums] == 0} {
        return $r
    }
    set s ""

    # Assume nums are non-negative and ordered.
    set i -1

    # Add sentinel.
    lappend nums [expr [lindex $nums end] + 2]

    foreach n $nums {
        if {$i < 0} {
            set j [set i $n]
            continue
        }
        if {$n == $j} {
            continue
        }
        if {$n == $j + 1} {
            set j $n
            continue
        }
        if {$i == $j} {
            append r "$s$i"
        } else {
            append r "$s$i-$j"
        }
        set j [set i $n]
        set s ", "
    }

    return $r
}

proc list_sep_str {i n} {
    if {$i == $n} {
        if {$n > 2} {
            return ", and "
        } else {
            return " and "
        }
    } else {
        return ", "
    }
}

proc chars_expand {text {flatten 1}} {
    global entities

    if {[regsub -all -- {[\0-\010\013\014\016-\037\177]+} $text {*?*} text]} {
        # DELETE and every C0 control char except \t, \n, and \r.
        unexpected error \
            "illegal use of hardcoded ASCII control character(s) in \"$text\""
    }

    if {[regsub -all -- {[\x80-\x9F]+} $text {*?*} text]} {
        # Every C1 control char.
        unexpected error \
            "illegal use of hardcoded C1 control character(s) (U+0080..U+009F) possibly instead of standard entities (e.g., &mdash; or &rsquo;) in \"$text\""
    }

    # Convert other hardcoded non-ASCII characters
    # (except no-break space) as dec entities.
    while {[regexp -- {[^\0-\xA0]} $text x]} {
        regsub -all -- $x $text "\\&#[scan $x %c];" text
    }

    # Process hex here to avoid cluttering $entities, to support
    # leading zeros, and most importantly to have -nocase.
    while {[regexp -nocase -- {&#x([0-9A-Z]+);} $text x y]} {
        # Rewrite hex as dec.
        regsub -all -nocase -- $x $text "\\&#[scan $y %x];" text
    }

    if {[regexp -- {&#1(2[89]|[345][0-9]);} $text]} {
        # Possibly just a warning for backward compatibility.
        unexpected [unex_condtype] \
            "non-standard use of entities between &#128; and &#159; as printable characters (really C1 control characters) instead of standard entities (e.g., &mdash; or &rsquo;) in \"$text\""
    }

    if {[regexp -- {&#0+;} $text]} {
        # All versions of XML prohibit this.
        unexpected error \
            "illegal use of &#0; entity in \"$text\""
    }

    # Remaining entities are case sensitive (or just dec).
    foreach {entity chars} $entities {
        regsub -all -- $entity $text $chars text
    }
    if {$flatten} {
        regsub -all "\n\[ \t\]*" $text " " text
    }

    return $text
}

proc tabs_expand_pre {line} {
    global pageno lineno

    set msg "pre-formatted output line [expr $lineno + 1] (on page $pageno)"

    if {[regexp -- {[\t]} $line]} {
        unexpected warning \
            "$msg contained tab characters which were expanded"

        while {[set x [string first "\t" $line]] >= 0} {
            set new [string range $line 0 [expr $x - 1]]
            append new [string repeat " " [expr 8 - ($x % 8)]]
            set line $new[string range $line [expr $x + 1] end]
        }
    }
    if {[regexp -- {[^ -~\xA0]} $line]} {
        # No-break spaces will be expanded later and are OK.
        unexpected error \
            "$msg contains illegal characters (control or otherwise)"
    }

    return $line
}


#
# xml2ref support
#

namespace eval ref {
    variable ref
    array set ref { uid 0 }

    variable parser [xml::parser]

    variable context
    #              element       verbatim        beginF  endF
    set context { {dummy/-1}
                  {rfc/0         no              yes     yes}
                  {front/1}
                  {title/2}
                  {author/2}
                  {organization/3}
                  {address/3}
                  {postal/4}
                  {street/5}
                  {city/5}
                  {region/5}
                  {code/5}
                  {country/5}
                  {phone/4}
                  {facsimile/4}
                  {email/4}
                  {uri/4}
                  {date/2}
                  {area/2}
                  {workgroup/2}
                  {keyword/2}
                  {abstract/2    yes}
                  {note/2        yes}
                }

    namespace export init fin transform
}

proc ref::init {} {
    variable ref

    set token [namespace current]::[incr ref(uid)]

    variable $token
    upvar 0 $token state

    array set state {}

    return $token
}

proc ref::fin {token} {
    variable $token
    upvar 0 $token state

    foreach name [array names state] {
        unset state($name)
    }
    unset $token
}

proc ref::transform {token file {formats {}}} {
    global errorCode errorInfo
    global ifile

    variable $token
    upvar 0 $token state

    array set emptyA {}

    variable parser
    $parser configure \
            -elementstartcommand    "ref::element_start $token" \
            -elementendcommand      "ref::element_end   $token" \
            -characterdatacommand   "ref::cdata         $token" \
            -entityreferencecommand ""                          \
            -errorcommand           ref::oops                   \
            -entityvariable         emptyA                      \
            -final                  1                           \
            -reportempty            1

    set fd [open $file { RDONLY }]
    catch { fconfigure $fd -encoding binary }
    set ifile $file
    set data [prexml [read $fd]]

    if {[catch { close $fd } result]} {
        log::entry $logT system $result
    }

    set state(stack)    ""
    set state(body)     ""
    set state(number)   0
    set state(authors)  0
    set state(keywords) 0
    set state(verbatim) 0
    set state(silent)   0
    set state(formats)  $formats
    set state(info)     ""
    set state(mtime)    0
    set state(tprefix)  ""
    set state(tsuffix)  ""
    set state(descr)    ""

    set code [catch { $parser parse $data } result]
    set ecode $errorCode
    set einfo $errorInfo

    switch -- $code {
        0 {
            set result [list body  $state(body) \
                             info  $state(info) \
                             mtime $state(mtime)]
        }

        1 {
            if {[set i [llength $state(stack)]] > 0} {
                set text "File:    $file\nContext:"
                while {$i > 0} {
                    set frame [lindex $state(stack) [incr i -1]]
                    catch { unset attrs }
                    append text "\n    <[lindex $frame 0]"
                    foreach {k v} [lindex $frame 1] {
                        regsub -all {"} $v {\&quot;} v
                        append text " $k=\"$v\""
                    }
                    append text ">"
                }
                append result "\n\n$text"
            }
        }
    }

    unset state(stack)    \
          state(body)     \
          state(number)   \
          state(authors)  \
          state(keywords) \
          state(verbatim) \
          state(silent)   \
          state(formats)  \
          state(info)     \
          state(mtime)    \
          state(tprefix)  \
          state(tsuffix)  \
          state(descr)

    return -code $code -errorinfo $einfo -errorcode $ecode $result
}

proc ref::element_start {token name {av {}} args} {
    global rfcitems

    variable $token
    upvar 0 $token state

    variable context

    array set options [list -empty 0]
    array set options $args

    set depth [llength $state(stack)]

    if {[set idx [lsearch -glob $context $name/$depth*]] >= 0} {
        set info [lindex $context $idx]
        if {[string compare [lindex $info 0] $name/$depth]} {
            set idx -1
        } elseif {![string compare [lindex $info 1] yes]} {
            set state(verbatim) 1
        }
    }

    set state(silent) 0
    if {($idx < 0) && ($state(verbatim))} {
        set idx 0
        set info ""
        if {[lsearch -exact {xref eref cref iref vspace} $name] >= 0} {
            set state(silent) 1
        }
    }

# format*
# is-also: BCP70
    if {$idx >= 0} {
        if {![string compare [lindex $info 2] yes]} {
            ref::start_$name $token $av
        } elseif {!$state(silent)} {
            switch -- $name {
                author {
                    incr state(authors)
                    set k $state(number),author$state(authors)
                    if {[info exists rfcitems($k)]} {
                        array set kv $rfcitems($k)
                        if {[info exists $kv(name)]} {
                            set name $kv(name)
# update initials/surname when rfc-index.xml is more robust...
                        }
                    }

                    array set nv $av
                    if {[info exists nv(fullname)]} {
                        append state(tsuffix) ", " $nv(fullname)
                    }
                }

                date {
                    set k $state(number)
                    array set nv $av
                    foreach n [list day year month] {
                        if {[info exists rfcitems($k,$n)]} {
                            set nv($n) $rfcitems($k,$n)
                        }
                    }
                    set av [array get nv]

                    array set dv [list day 1 year "" month ""]
                    array set dv $av
                    if {[string first "<dc:date>" $state(info)] < 0} {
                        catch {
                            set state(mtime) \
                                [clock scan "$dv(month) $dv(day), $dv(year)"]
                            append state(info) \
                                   "    <dc:date>" \
                                   [clock format $state(mtime) \
                                        -format "%Y-%m-%dT%T-00:00" \
                                        -gmt true] \
                                   "</dc:date>
"
                        }
                    }
                }

                note {
                    if {[string first "</description>" $state(info)] < 0} {
                        append state(info) "    <description></description>
"
                    }
                }
            }
            append state(body) "\n<$name"
            foreach {n v} $av {
                regsub -all {'} $v {\&apos;} v
                append state(body) " $n='$v'"
            }
            if {$options(-empty)} {
                append state(body) " /"
            }
            append state(body) >

            switch -- $name {
                title {
                    set k $state(number)
                    if {[info exists rfcitems($k,doc-title)]} {
                        append state(body) $rfcitems($k,doc-title)

                        if {[string first "<title>" $state(info)] < 0} {
                            append state(info) "    <title>" \
                                   $state(tprefix) \
                                   $rfcitems($k,doc-title) \
                                   "</title>
"
                        }
                    }
                }
            }
        }
    }

    lappend state(stack) [list $name $av $idx ""]
}

proc ref::element_end {token name args} {
    variable $token
    upvar 0 $token state

    variable context

    array set options [list -empty 0]
    array set options $args

    set frame [lindex $state(stack) end]
    set state(stack) [lreplace $state(stack) end end]

    if {[set idx [lindex $frame 2]] >= 0} {
        set info [lindex $context $idx]
        if {![string compare [lindex $info 3] yes]} {
            ref::end_$name $token $frame
        } elseif {!$state(silent) && !$options(-empty)} {
            append state(body) </$name>
        }

        if {![string compare [lindex $info 1] yes]} {
            set state(verbatim) 0
        }
    }
    set state(silent) 0

    switch -- $name {
        title {
            if {([string first "<title>" $state(info)] >= 0)
                    && ([string first "</title>" $state(info)] < 0)} {
                append state(info) "</title>
"
            }
        }

        t {
        }

        front
            -
        abstract {
            if {[string first "</description>" $state(info)] < 0} {
                if {[string first "<description>" $state(info)] >= 0} {
                    append state(info) "</description>
"
                } else {
                    append state(info) "    <description></description>
"
                }
            }
        }
    }
}

proc ref::cdata {token text} {
    global rfcitems

    variable $token
    upvar 0 $token state

    if {[string length [string trim $text]] <= 0} {
        return
    }

    set frame [lindex $state(stack) end]
    if {[set idx [lindex $frame 2]] < 0} {
        return
    }

    switch -- [lindex $frame 0] {
        title {
            set k $state(number)
            if {[info exists rfcitems($k,doc-title)]} {
                return
            }
        }
    }

    regsub -all "\r" $text "\n" text

    append state(body) $text

    switch -- [lindex $frame 0] {
        title {
            if {![info exists rfcitems($k,doc-title)]} {
                if {[string first "<title>" $state(info)] < 0} {
                    append state(info) "    <title>" $state(tprefix) $text
                } elseif {[string first "</title>" $state(info)] < 0} {
                    append state(info) $text
                }
            }
        }

        t {
            if {[string first "<description>" $state(info)] < 0} {
                append state(info) "    <description>" $text
            } elseif {[string first "</description>" $state(info)] < 0} {
                append state(info) $text
            }
        }
    }
}

proc ref::oops {args} {
    return -code error [join $args " "]
}

proc ref::start_rfc {token av} {
    variable $token
    upvar 0 $token state

    array set rfc [list obsoletes "" updates "" category info seriesNo ""]
    array set rfc $av
    if {[catch { set rfc(number) }]} {
        ref::oops "missing number attribute in rfc element"
    }
    set state(number) $rfc(number)

    set state(body) "<?xml version='1.0' encoding='UTF-8'?>

<reference anchor='RFC[format %04d $rfc(number)]'>
"

    set state(tprefix) "RFC&nbsp;$rfc(number): "
}

proc ref::end_rfc {token frame} {
    global rfcitems

    variable $token
    upvar 0 $token state

    array set rfc [list obsoletes "" updates "" category info seriesNo ""]
    array set rfc [lindex $frame 1]

    set k $state(number)
    if {[info exists rfcitems($k,is-also)]} {
        array set rfc [list category [string range $rfcitems($k,is-also) 0 2] \
                            seriesNo [string range $rfcitems($k,is-also) 3 end]]
    }

    append state(body) "

"
    if {([string compare [set x $rfc(category)] info]) \
            && ([string compare [set y $rfc(seriesNo)] ""])} {
        append state(body) "<seriesInfo name='[string toupper $x]' "
        append state(body) "value='$y' />
"
    }
    append state(body) "<seriesInfo name='RFC' value='$rfc(number)' />
"
    foreach format $state(formats) {
        append state(body) "<format"
        foreach {k v} $format {
            append state(body) " $k='$v'"
        }
        append state(body) " />
"
    }
    append state(body) "</reference>
"

    set url ""
    foreach format $state(formats) {
        catch { unset fv }
        array set fv $format
        set url $fv(target)
        if {![string compare $fv(type) TXT]} {
            break
        }
    }
    if {[string compare $url ""]} {
        regsub -all {&} $url {\&amp;} url
        regsub -all {'} $url {\&apos;} url
        if {([string compare $state(tsuffix) ""]) \
                && ([set x [string first "</title>" $state(info)]] > 0)} {
            set info [string range $state(info) 0 [expr $x-1]]
            append info $state(tsuffix) [string range $state(info) $x end]
            set state(info) $info
        }
        set state(info) "
<item rdf:about='$url'>
    <link>$url</link>
$state(info)</item>
"
    } else {
        set state(info) ""
    }
}


proc stindex {sindex len} {
    switch -regexp -- $sindex {
        {^[Ee][Nn][Dd]*$} {
            incr len -1

            return [expr $len[string range $sindex 3 end]]
        }

        {^[Ll][Ee][Nn]*$} {
            return [expr $len[string range $sindex 3 end]]
        }

        default {
            return $sindex
        }
    }
}

proc streplace {string first last {newstring ""} {magic 0}} {
    set first [stindex $first [set len [string length $string]]]
    set last [stindex $last $len]
    if {($first > $last) || ($first > $len) || ($last < 0)} {
        return $string
    }

    if {$first > 0} {
        set left [string range $string 0 [expr $first-1]]
    } else {
        set left ""
    }

    if {$magic} {
        set oldstring [string range $string \
                              [expr (($first) >= 0) ? ($first) : 0] \
                              [expr (($last) < $len) ? ($last) : $len-1]]
        if {$magic == 1} {
            regsub -all -- {[^\t\r\n]} $oldstring { } newstring
        } elseif {$magic >= 2} {
            # Remove, but preserve the line count.
            set newstring ""
            # EOL normalization is necessary with XML 1.1.
            set n [num_eols [str_norm_eol $oldstring]]
            if {$n > 0} {
                if {$magic == 2} {
                    append newstring {<!--} [string repeat "\n" $n] {-->}
                } else {
                    # $magic == 3
                    set newstring [string repeat "\n" $n]
                }
            }
        }
    }

    if {$last < $len} {
        set right [string range $string [expr $last+1] end]
    } else {
        set right ""
    }

    return $left$newstring$right
}

proc str_norm_eol {string {xml11 0}} {
    if {$xml11} {
        regsub -all -- "(\r\n|\r\x85|\x85|\x2028|\r)" $string "\n" string
    } else {
        regsub -all -- "\r\n?" $string "\n" string
    }
    return $string
}



#
# pity i didn't build this into xml2rfc initially,
# because integrating properly would be a lot of work...
#

namespace eval xdv {
    variable dtd
    # This ::xdv::lineno is 0-based.
    variable lineno -1

    array set dtd {}
}

# strict content model does not allow section in back...
set xdv::dtd(rfc2629.cmodel) \
    [list rfc           [list front             ""   \
                              middle            ""   \
                              back              "?"] \
          front         [list title             ""   \
                              author            "+"  \
                              date              ""   \
                              area              "*"  \
                              workgroup         "*"  \
                              keyword           "*"  \
                              abstract          "?"  \
                              note              "*"] \
          middle        [list section           "+"  \
                              appendix          "*"  \
                              section           "*"] \
          back          [list references        "*"  \
                              section           "*"] \
          title         {}                           \
          author        [list organization      ""   \
                              address           "*"] \
          organization  {}                           \
          address       [list postal            "?"  \
                              phone             "?"  \
                              facsimile         "?"  \
                              email             "?"  \
                              uri               "?"] \
          postal        [list street            "+"  \
                              [list city             \
                                    region           \
                                    code             \
                                    country]    *]   \
          street        {}                           \
          city          {}                           \
          region        {}                           \
          code          {}                           \
          country       {}                           \
          phone         {}                           \
          facsimile     {}                           \
          email         {}                           \
          uri           {}                           \
          date          {}                           \
          area          {}                           \
          workgroup     {}                           \
          keyword       {}                           \
          abstract      [list t                 "+"] \
          note          [list t                 "+"] \
          section       [list [list t                \
                                    figure           \
                                    texttable        \
                                    iref             \
                                    section]    "*"] \
          appendix      [list [list t                \
                                    figure           \
                                    texttable        \
                                    iref             \
                                    appendix]   "*"] \
          t             [list [list list             \
                                    figure           \
                                    xref             \
                                    eref             \
                                    iref             \
                                    cref             \
                                    vspace           \
                                    spanx]      "*"] \
          list          [list t                 "+"] \
          xref          {}                           \
          eref          {}                           \
          iref          {}                           \
          cref          {}                           \
          vspace        {}                           \
          spanx         {}                           \
          figure        [list preamble          "?"  \
                              artwork           ""   \
                              postamble         "?"] \
          preamble      [list [list xref             \
                                    eref             \
                                    iref             \
                                    cref             \
                                    spanx]      "*"] \
          artwork       {}                           \
          postamble     [list [list xref             \
                                    eref             \
                                    iref             \
                                    cref             \
                                    spanx]      "*"] \
          texttable     [list preamble          "?"  \
                              ttcol             "+"  \
                              c                 "*"  \
                              postamble         "?"] \
          ttcol         {}                           \
          c             [list [list xref             \
                                    eref             \
                                    iref             \
                                    cref             \
                                    spanx]      "*"] \
          references    [list reference         "+"] \
          reference     [list front             ""   \
                              seriesInfo        "*"  \
                              format            "*"  \
                              annotation        "*"] \
          seriesInfo    {}                           \
          format        {}                           \
          annotation    [list [list xref             \
                                    eref             \
                                    iref             \
                                    cref             \
                                    spanx]      "*"]]

set xdv::dtd(rfc2629.pcdata) \
    [list annotation   \
          area         \
          artwork      \
          c            \
          city         \
          code         \
          country      \
          cref         \
          email        \
          eref         \
          facsimile    \
          keyword      \
          organization \
          phone        \
          postamble    \
          preamble     \
          region       \
          spanx        \
          street       \
          t            \
          ttcol        \
          title        \
          uri          \
          workgroup    \
          xref]

set xdv::dtd(rfc2629.rattrs) \
    [list date          [list year]   \
          note          [list title]  \
          section       [list title]  \
          appendix      [list title]  \
          xref          [list target] \
          eref          [list target] \
          iref          [list item]   \
          seriesInfo    [list name    \
                              value]  \
          format        [list type]]

set xdv::dtd(rfc2629.oattrs) \
    [list rfc           [list number      \
                              obsoletes   \
                              updates     \
                              category    \
                              seriesNo    \
                              ipr         \
                              iprExtract  \
                              docName     \
                              xml:lang]   \
          title         [list abbrev]     \
          author        [list initials    \
                              surname     \
                              fullname    \
                              role]       \
          organization  [list abbrev]     \
          date          [list day         \
                              month]      \
          section       [list anchor      \
                              toc]        \
          appendix      [list anchor      \
                              toc]        \
          t             [list anchor      \
                              hangText]   \
          list          [list style       \
                              hangIndent  \
                              counter]    \
          xref          [list pageno      \
                              format]     \
          iref          [list subitem     \
                              primary]    \
          cref          [list anchor      \
                              source]     \
          spanx         [list xml:space   \
                              style]      \
          vspace        [list blankLines] \
          figure        [list anchor      \
                              title       \
                              align       \
                              src         \
                              alt         \
                              width       \
                              height]     \
          artwork       [list xml:space   \
                              name        \
                              type        \
                              align       \
                              src         \
                              alt         \
                              width       \
                              height]     \
          texttable     [list anchor      \
                              title]      \
          ttcol         [list width       \
                              align]      \
          references    [list title]      \
          reference     [list anchor      \
                              target]     \
          seriesInfo    [list name        \
                              value]      \
          format        [list target      \
                              octets]]  \

set xdv::dtd(rfc2629.anchors) \
    [list anchor]


proc xdv::validate_tree {root CM RA OA AN PC} {
    variable anchorX {}

    validate_tree_aux $root $CM $RA $OA $AN $PC {}
}

proc xdv::validate_tree_aux {parent CM RA OA AN PC stack} {
    variable anchorX
    variable dtd

    set name [lindex $parent 0]
    array set attrs [lindex $parent 1]
    set children [lrange $parent 2 end]

    lappend stack [list $name [array get attrs]]

    array set cmodel $dtd($CM)
    if {![info exists cmodel($name)]} {
        report "not expecting <$name> element" $stack
    }

    array set required $dtd($RA)
    if {[info exists required($name)]} {
        foreach k [set expected $required($name)] {
            if {![info exists attrs($k)]} {
                report "missing $k attribute in <$name> element" $stack
            }
        }
    } else {
        set expected {}
    }

    array set optional $dtd($OA)
    if {[catch { set optional($name) } possible]} {
        set possible {}
    }
    foreach k [array names attrs] {
        if {([string first . $k] < 0) \
                && ([lsearch -exact $expected $k] < 0) \
                && ([lsearch -exact $possible $k] < 0)} {
            report "unexpected $k attribute in <$name> element" $stack
        }
    }

    foreach {k v} [array get attrs] {
        if {[lsearch -exact $dtd($AN) $name/$k] >= 0} {
            if {[lsearch -exact $anchorX $v] >= 0} {
                report "duplicate anchor '$v'" $stack
            }
            lappend anchorX $v
        }
    }

    if {([info exists attrs(.pcdata)]) \
            && ([lsearch $dtd($PC) $name] < 0)} {
        report "not expecting pcdata in <$name> element" $stack
    }

    if {[catch { validate_cmodel $children $cmodel($name) } result]} {
        report $result $stack
    }

    foreach child $children {
        validate_tree_aux $child $CM $RA $OA $AN $PC $stack
    }
}

proc xdv::validate_cmodel {children cmodel} {
    set elems [lindex $cmodel 0]
    set quant [lindex $cmodel 1]
    set cmodel [lrange $cmodel 2 end]

    set i 0
    foreach child $children {
        set e [lindex $child 0]
        if {[lsearch -exact $elems $e] >= 0} {
            switch -- $quant {
                + {
                    set quant "*"
                }
                ? - "" {
                    set elems [lindex $cmodel 0]
                    set quant [lindex $cmodel 1]
                    set cmodel [lrange $cmodel 2 end]
                }
            }
        } else {
            switch -- $quant {
                ? - * {
                    return [validate_cmodel [lrange $children $i end] \
                                            $cmodel]
                }

                default {
                    switch -- [llength $elems] {
                        0 {
                            error "not expecting <$e>"
                        }

                        1 {
                            error "expecting <$elems> element, not <$e>"
                        }

                        default {
                            error "expecting any of $elems, not <$e>"
                        }
                    }
                }
            }
        }
        incr i
    }
    if {([llength $elems] == 0) \
            || ([lsearch -exact {? *} $quant] >= 0)} {
        return
    } else {
        switch -- [llength $elems] {
            1 {
                error "expecting <$elems> element"
            }

            default {
                error "expecting any of $elems"
            }
        }
    }
}

proc xdv::report {result stack} {
    if {[set i [llength $stack]] > 0} {
        array set attrs [lindex [lindex $stack end] 1]
        if {[info exists attrs(.lineno)]} {
            append result " around line $attrs(.lineno)"
        }

        set text "Syntax:"
        while {$i > 0} {
            set frame [lindex $stack [incr i -1]]
            array set attrs [lindex $frame 1]
            append text "\n    "
            if {[info exists attrs(.lineno)]} {
                append text [expr $attrs(.lineno) + 1]:
            }
            append text <[lindex $frame 0]
            foreach {k v} [lindex $frame 1] {
                if {[string first . $k] < 0} {
                    regsub -all {"} $v {\&quot;} v
                    append text " $k=\"$v\""
                }
            }
            append text ">"
        }
        append result "\n\n$text"
    }

    error $result
}


#
# tclsh/wish linkage
#


global guiP
if {[info exists guiP]} {
    return
}
set guiP 0
# load and initialize tk if possible
catch {package require -exact Tk [info tclversion]}
if {[llength $argv] > 1} {
    if {[catch {
        switch -- [llength $argv] {
            2 {
                set file [lindex $argv 1]
                if {![string compare $tcl_platform(platform) \
                             windows]} {
                    set f ""
                    foreach c [split $file ""] {
                        switch -- $c {
                            "\\" { append f "\\\\" }

                            "\a" { append f "\\a" }

                            "\b" { append f "\\b" }

                            "\f" { append f "\\f" }

                            "\n" { append f "\\n" }

                            "\r" { append f "\\r" }

                            "\v" { append f "\\v" }

                            default {
                                append f $c
                            }
                        }
                    }
                    set file $f
                }

                eval [file tail [file rootname [lindex $argv 0]]] \
                           $file
            }

            3 {
                xml2rfc [lindex $argv 1] [lindex $argv 2]
            }
        }
    } result]} {
        if {[info exists tk_version]} {
            bgerror $result
        } else {
            puts stderr $result
        }
        exit 1
    }

    exit 0
} elseif {![info exists tk_version]} {
    set guiP -1
    puts stdout ""
    puts stdout "invoke as \"xml2rfc   input-file output-file\""
    puts stdout "       or \"xml2txt   input-file\""
    puts stdout "       or \"xml2html  input-file\""
    puts stdout "       or \"xml2nroff input-file\""
} else {
    set guiP 1

    proc convert {w} {
        global prog
        global tcl_platform

        if {![string compare [set input [.input.ent get]] ""]} {
            tk_dialog .error "$prog: oops!" "no input filename specified" \
                      error 0 OK
            return
        }
        set output [.output.ent get]

        if {[catch { xml2rfc $input $output } result]} {
            tk_dialog .error "$prog: oops!" $result error 0 OK
        } elseif {![string compare $tcl_platform(platform) windows]} {
            tk_dialog .ok xml2rfc "Finished." "" 0 OK
        }
    }

    proc fileDialog {w ent operation} {
        set input {
            {"XML files"                .xml                    }
            {"All files"                *                       }
        }
        set output {
            {"TeXT files"               .txt                    }
            {"HTML files"               .html                   }
            {"NRoff files"              .nr                     }
        }
        if {![string compare $operation "input"]} {
            set file [tk_getOpenFile -filetypes $input -parent $w]
        } else {
            if {[catch { set input [.input.ent get] }]} {
                set input Untitled
            } else {
                set input [file rootname $input]
            }
            set file [tk_getSaveFile -filetypes $output -parent $w \
                            -initialfile $input -defaultextension .txt]
        }
        if [string compare $file ""] {
            $ent delete 0 end
            $ent insert 0 $file
            $ent xview end
        }
    }

    eval destroy [winfo child .]

    wm title . $prog
    wm iconname . $prog
    wm geometry . +300+300

    label .msg -font "Helvetica 14" -wraplength 4i -justify left \
          -text "Convert XML to RFC"
    pack .msg -side top

    frame .buttons
    pack .buttons -side bottom -fill x -pady 2m
    pack \
        [button .buttons.code -text Convert -command "convert ."] \
        [button .buttons.dismiss -text Quit -command "destroy ."] \
        -side left -expand 1

    foreach i {input output} {
        set f [frame .$i]
        label $f.lab -text "Select $i file: " -anchor e -width 20
        entry $f.ent -width 20
        button $f.but -text "Browse ..." -command "fileDialog . $f.ent $i"
        pack $f.lab -side left
        pack $f.ent -side left -expand yes -fill x
        pack $f.but -side left
        pack $f -fill x -padx 1c -pady 3
    }
}

# vi: set sw=4 et si sta:
