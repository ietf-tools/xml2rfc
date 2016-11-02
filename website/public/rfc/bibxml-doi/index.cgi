#!/usr/bin/perl 

# http://xml2rfc.ietf.org/public/rfc/bibxml-doi/reference.DOI.$doi.xml
# http://xml2rfc.ietf.org/public/rfc/bibxml-doi/reference.DOI.$doi.kramdown

# http://xml2rfc.ietf.org/public/rfc/bibxml-doi/reference.DOI.10.1145/1355734.1355746.xml

my @DOIrefs = ();
my $nph = undef;

print STDERR "0=$0\n";
if ($#ARGV >= 0) {
    # look at $ARGV for testing purposes to determine format (xml vs kramdown) and DOI numbers
    @DOIrefs = @ARGV;
    # print "ARGV=" . join("|", @ARGV) . "\n";
} else {
    # if no $ARGV, look at $PATH_INFO to determine format (xml vs kramdown) and DOI number
    @DOIrefs = $ENV{PATH_INFO};
}


# for each DOI:
for my $DOIref (@DOIrefs) {
    #    if cache has file already and < 24 hours old
    #        cat cached copy
    #    else
    #        grab dx.doi.org/$DOI
    #        convert to appropriate format
    #        save in cache
    # print STDERR "DOIref=$DOIref\n";
    if ($DOIref =~ m(^/?reference.DOI[.](\d+[.]\d+)[/._](\d+[.]\d+)[.](xml|kramdown)$)) {
	my $DOIpt1 = $1;
	my $DOIpt2 = $2;
	my $type = $3;
	# print STDERR "DOIpt1=$DOIpt1 DOIpt2=$DOIpt2 type=$3\n";
	my $opt = $type eq 'xml' ? "x" : "h";
	print "HTTP/1.0 200 OK\n" if $nph;
	print "Content-Type: text/$type\n\n";
	my $CACHEDIR = "/var/tmp/doi-cache";
	my $TMP = "$CACHEDIR/reference.DOI_${DOIpt1}_${DOIpt2}.${type}";
	# print STDERR "-s $TMP=" . (-s $TMP) . ", -M $TMP=" . (-M _);
	if (-s $TMP && -M _ < 1) {
	    print STDERR "Using cached file $TMP";
	    print `cat $TMP`;
	} else {
	    print STDERR "Running: doilit -$opt=DOI_${DOIpt1}_${DOIpt2} ${DOIpt1}/${DOIpt2}";
	    print `mkdir -p $CACHEDIR;doilit -$opt=DOI_${DOIpt1}_${DOIpt2} ${DOIpt1}/${DOIpt2} | tee "$TMP.tmp";mv "$TMP.tmp" "$TMP"`;
	}
    } else {
	print "HTTP/1.0 404 NOT FOUND\n" if $nph;
	print "Content-type: text/plain\n\n";
	print "invalid DOI or type\n";
    }
}
