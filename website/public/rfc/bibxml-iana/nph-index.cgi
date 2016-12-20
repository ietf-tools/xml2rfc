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

my @IANArefs = ();
my $nph = $0 =~ m(/nph-index.cgi);

if ($#ARGV >= 0) {
    # look at $ARGV for testing purposes to determine format (xml vs kramdown) and IANA numbers
    @IANArefs = @ARGV;
    # print "ARGV=" . join("|", @ARGV) . "\n";
} else {
    # if no $ARGV, look at $PATH_INFO to determine format (xml vs kramdown) and IANA number
    @IANArefs = $ENV{PATH_INFO};
}

# for each IANA:
for my $IANAref (@IANArefs) {
    #    if cache has file already and < 24 hours old
    #        cat cached copy
    #    else
    #        grab dx.doi.org/$IANA
    #        convert to appropriate format
    #        save in cache
    if ($IANAref =~ m(^/?reference.IANA[.]([^/]+)[.](xml|kramdown)$)) {
	my $IANAref = $1;
	my $type = $2;
	# print STDERR "IANAref=$IANAref type=$3\n";
	my $opt = $type eq 'xml' ? "x" : "h";
	print "HTTP/1.0 200 OK\n" if $nph;
	print "Content-Type: text/$type\n\n";
	my $CACHEDIR = "/var/tmp/iana-cache";
	my $TMP = "$CACHEDIR/reference.IANA.${IANAref}.${type}";
	# print STDERR "-s $TMP=" . (-s $TMP) . ", -M $TMP=" . (-M _);
	my $printed = undef;
	if ((-s $TMP) && (-M _ < 1) && !$ignoreCache) {
	    print STDERR "Using cached file $TMP\n";
	    if (!open(TMP, "<", $TMP)) {
		print STDERR "Cannot read $TMP: $!\n";
	    } else {
		local $/ = undef;
		my $ref = <TMP>;
		close TMP;
		$ref = replaceAnchor($ref, $type, $replacementAnchor);
		print $ref;
		$printed = 1
	    }
	}

	if (!$printed) {
	    umask(0);
	    mkdir($CACHEDIR);

	    my $a = get("http://www.iana.org/assignments/$IANAref/");

	    # print STDERR "a=====\n$a\n====\n";
	    # print STDERR "====\n";
	    $a =~ m(<title>([^<]*)</title>)m;
	    my $title = $1;

	    # print STDERR "title=$title\n";
	    if ($title =~ /page not found/i) {
		printNotFound();
	    } else {
		my $anchor = mungeAnchor($IANAref);

		my $ref = "<reference anchor='$anchor' target='http://www.iana.org/assignments/$IANAref'>\n" .
		    "<front>\n" .
		    "<title>$title</title>\n" .
		    "<author><organization>IANA</organization></author>\n" .
		    "</front>\n" .
		    "</reference>\n";
		
		if (!open(TMP, ">", $TMP)) {
		    print STDERR "Cannot create $TMP: $!\n";
		} else {
		    print TMP $ref;
		}

		$ref = replaceAnchor($ref, $type, $replacementAnchor);
		print $ref;
	    }
	}
    } else {
	printNotFound();
    }
}

sub printNotFound {
    print "HTTP/1.0 404 NOT FOUND\n" if $nph;
    print "Content-type: text/plain\n\n";
    print "invalid IANA name or type\n";
}

sub mungeAnchor {
    my $anchor = shift;
    $anchor =~ tr/a-z/A-Z/;
    $anchor =~ s/[^A-Z0-9_-]//g;
    return $anchor;
}

sub replaceAnchor {
    my ($ref, $type, $replacementAnchor) = @_;
    if ($replacementAnchor ne "") {
	if ($type eq 'xml') {
	    $ref =~ s/anchor='[^']*'/anchor='$replacementAnchor'/;
	    $ref =~ s/anchor="[^"]*"/anchor='$replacementAnchor'/;
	} else {
	    $ref =~ s/^  [^:]*:/  $replacementAnchor:/;
	}
    }
    return $ref;    
}
