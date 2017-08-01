#!/usr/bin/perl -T

use strict vars;
use CGI;

$ENV{PATH} = "/bin:/usr/bin";
my $fn = "/" . untaint($ENV{PATH_INFO});
$fn =~ s(^/*)();
$fn =~ s(/../)(/)g;
$fn =~ s/['"]//gi;

if ($fn eq '') {
    print "Content-Type: text/plain\n\n";
    print "You lose. No path information provided\n";
} else {
    $ENV{XML2RFC_URL} = "https://raw.githubusercontent.com/$fn";
    if ($fn =~ /[.]mk?d/) {
        $ENV{XML2RFC_INPUTTYPE} = 'kramdown';
	print "using kramdown\n";
    } else {
        $ENV{XML2RFC_INPUTTYPE} = 'xml2rfc';
	print "using xml\n";
    }
    $ENV{XML2RFC_MODEASFORMAT} = 'txt/ascii';
    system("./xml2rfc-dev.cgi");
}

####### use a given pattern to untaint a value
####### default to the entire value
sub untaint {
    my $str = shift;
    my $pat = shift;
    $pat = "(.*)" if !defined($pat);
    return $1 if ($str =~ /$pat/);
    return undef;
}
