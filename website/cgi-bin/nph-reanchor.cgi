#!/usr/bin/perl 

# auto-generate IANA references in bibxml format.
# e.g. http://xml2rfc.ietf.org/public/rfc/bibxml-iana/reference.IANA.service-names-port-numbers.xml

# http://xml2rfc.ietf.org/public/rfc/bibxml-iana/reference.IANA.$iana.xml
# http://xml2rfc.ietf.org/public/rfc/bibxml-iana/reference.IANA.$iana.kramdown

use strict vars;
use CGI qw(taint);
use LWP::Simple;

$CGI::DISABLE_UPLOADS = 1;          # Disable uploads
$CGI::POST_MAX        = 512 * 1024; # limit posts to 512K max

my $cgi = CGI->new();

# for testing
# $cgi->param("anchor", "test");  
my $ignoreCache = 1;

my $replacementAnchor = mungeAnchor($cgi->param("anchor"));

my @refs = ();
my $nph = $0 =~ m(/nph-reanchor.cgi);

if ($#ARGV >= 0) {
    # look at $ARGV for testing purposes to determine format (xml vs kramdown) and IANA numbers
    @refs = @ARGV;
    # print "ARGV=" . join("|", @ARGV) . "\n";
} else {
    # if no $ARGV, look at $PATH_INFO to determine format (xml vs kramdown) and IANA number
    @refs = $ENV{PATH_INFO};
}

my $TOPDIR = "/home/www/tools.ietf.org/tools/xml2rfc/web/public/rfc/";

# for each reference:
for my $ref (@refs) {
    #    if file exists and doesn't include /../ in its path:
    #        reanchor the given file and print it
    my $printed = undef;
    if ($ref !~ m(/[.][.]/)) {
	my $path = "$TOPDIR/$ref";
	if (!open(path, "<", $path)) {
	    print STDERR "Cannot read $path: $!\n";
	} else {
	    print "HTTP/1.0 200 OK\n" if $nph;
	    print "Content-Type: text/xml\n\n";
	    local $/ = undef;
	    my $ref = <path>;
	    close path;
	    $ref = replaceAnchor($ref, $replacementAnchor);
	    print $ref;
	    $printed = 1
	}
    }

    if (!$printed) {
	printNotFound();
    }
}

sub printNotFound {
    print "HTTP/1.0 404 NOT FOUND\n" if $nph;
    print "Content-type: text/plain\n\n";
    print "invalid reference name\n";
}

sub mungeAnchor {
    my $anchor = shift;
    $anchor =~ tr/a-z/A-Z/;
    $anchor =~ s/[^A-Z0-9_-]//g;
    return $anchor;
}

sub replaceAnchor {
    my ($ref, $replacementAnchor) = @_;
    if ($replacementAnchor ne "") {
	$ref =~ s/anchor='[^']*'/anchor='$replacementAnchor'/m;
	$ref =~ s/anchor="[^"]*"/anchor='$replacementAnchor'/m;
    }
    return $ref;    
}
