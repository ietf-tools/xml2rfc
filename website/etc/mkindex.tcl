#!/bin/sh
# the next line restarts using wish \
exec tclsh "$0" "$0" "$@"


package require xml 1.8


global emptyA

set parserX [xml::parser]
array set emptyA {}

$parserX configure \
            -elementstartcommand          { element begin } \
            -elementendcommand            { element end   } \
            -characterdatacommand         { pcdataX       } \
            -entityreferencecommand       ""                \
            -errorcommand                 error             \
            -entityvariable               emptyA            \
            -final                        yes               \
            -reportempty                  yes

proc element {tag name {av {}} args} {
    global depthX fd file

    array set options [list -empty 0]
    switch -- $tag {
        begin {
            array set options $args
            incr depthX

            if {[lsearch -exact [list reference address abstract note t] \
                         $name] >= 0} {
                puts $fd ""
            }
            puts -nonewline $fd "<$name"

            set kv {}
            foreach {k v} $av {
                lappend kv $k
                regsub -all {\\\[} $v {[} v
                lappend kv $v
            }
            array set attrs $kv
            if {$depthX == 1} {
                set attrs(target2) $file
            }
            foreach {k v} [array get attrs] {
                regsub -all {&} $v {\&amp;}  v
                regsub -all {'} $v {\&apos;} v
                puts -nonewline $fd " $k='$v'"
            }
            if {$options(-empty)} {
                puts -nonewline $fd " />"
                puts $fd ""
            } else {
                puts -nonewline $fd ">"
            }
            if {[lsearch -exact [list reference front author address postal] \
                         $name] >= 0} {
                puts $fd ""
            }
        }

        end {
            array set options [concat $av $args]
            incr depthX -1

            if {$options(-empty)} {
                return
            }
            puts $fd "</$name>"
            if {[lsearch -exact [list reference front author postal] \
                         $name] >= 0} {
                puts $fd ""
            }
        }
    }
}

proc pcdataX {text} {
    global fd file

    if {[string compare [string trim $text] ""]} {
        puts -nonewline $fd $text
    }
}



array set options [list -dir "" -title "Index" -subtitle " " -output index.xml]
array set options [lrange $argv 1 end]

set now [clock seconds]

set date [clock format $now -format "%B %Y %d"]
set month [lindex $date 0]
set year [lindex $date 1]
set day [string trimleft [lindex $date 2] 0]

regsub -all {&} $options(-title)    {\&amp;}  abbrev
regsub -all {'} $abbrev             {\&apos;} abbrev
regsub -all {&} $options(-subtitle) {\&amp;}  subtitle
regsub -all {'} $subtitle           {\&apos;} subtitle

set preamble \
"<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE rfc SYSTEM 'rfc2629.dtd'>

<?rfc private=' '?>
<?rfc symrefs='yes'?>
<?rfc topblock='no'?>

<rfc>
<front>
<title abbrev='$abbrev'>$options(-title) (as of $month $day, $year)</title>

<date month='$month' day='$day' year='$year' />
</front>

<middle />

<back>
<references title='$subtitle'>
"

set postamble \
"</references>
</back>
</rfc>
"


global depthX fd file

set fd [open $options(-output) { WRONLY CREAT TRUNC }]
puts $fd $preamble

set filesN 0
foreach file [lsort -dictionary \
                    [glob -nocomplain -- [file join $options(-dir) \
                                               reference.*.xml]]] {
    if {[catch {
        set xd ""
        set data [read [set xd [open $file { RDONLY }]]]
        close $xd
    } result]} {
        puts stderr "$file: $result"
        catch { close $xd }
        continue
    }

    set depthX 0
    if {[catch { $parserX parse $data } result]} {
        puts stderr "$file: $result"
        continue
    }
    incr filesN
}

if {[catch { 
    puts $fd $postamble

    close $fd
} result]} {
    puts stderr "$result
}
