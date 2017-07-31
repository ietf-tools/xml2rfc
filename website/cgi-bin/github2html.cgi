#!/usr/bin/perl -T

use strict vars;
use CGI;

$ENV{PATH} = "/bin:/usr/bin";
my $fn = "/" . untaint($ENV{PATH_INFO});
$fn =~ s(^/*)();
$fn =~ s(/../)(/)g;
$fn =~ s/['"]//gi;

print("Content-type: text/html\n\n");
print("<meta http-equiv='refresh' content='0;URL=/cgi-bin/xml2rfc-dev.cgi?url=https://raw.githubusercontent.com/$fn?modeAsFormat=html/ascii'>\n");


####### use a given pattern to untaint a value
####### default to the entire value
sub untaint {
    my $str = shift;
    my $pat = shift;
    $pat = "(.*)" if !defined($pat);
    return $1 if ($str =~ /$pat/);
    return undef;
}
