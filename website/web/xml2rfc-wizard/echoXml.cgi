#!/usr/bin/perl -T

use strict vars;
use CGI;
my $q = CGI->new;
my $xml = $q->param('xml');

my $fn = $ENV{PATH_INFO};
$fn =~ s/^.*\///;
$fn =~ s/[^a-z0-9.-]//gi;

print "Content-Type: text/plain\n";
print "Content-Disposition: attachment; filename=\"$fn\"\n";
print "\n";
print $xml;
