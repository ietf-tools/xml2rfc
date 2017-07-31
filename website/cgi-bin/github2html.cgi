#!/usr/bin/perl -T

use strict vars;
use CGI;

$ENV{PATH} = "/bin:/usr/bin";
my $fn = "/" . untaint($ENV{PATH_INFO});
$fn =~ s(^/*)();
$fn =~ s(/../)(/)g;
$fn =~ s/['"]//gi;

$ENV{XML2RFC_URL} = "https://raw.githubusercontent.com/$fn";
$ENV{XML2RFC_MODEASFORMAT} = 'html/ascii';
system("./xml2rfc-dev.cgi");

####### use a given pattern to untaint a value
####### default to the entire value
sub untaint {
    my $str = shift;
    my $pat = shift;
    $pat = "(.*)" if !defined($pat);
    return $1 if ($str =~ /$pat/);
    return undef;
}
