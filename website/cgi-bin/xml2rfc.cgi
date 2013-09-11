#!/usr/bin/perl -T

use 5.014;
use strict;
use CGI;
use Cwd qw(chdir getcwd);
use HTML::Entities ();
use Net::SMTP;
use Digest::MD5 qw(md5 md5_hex);
use Crypt::RC4;
use XML::Parser;
use HTTP::Request;
use LWP::UserAgent;

umask(02);
my $dir = untaint(getcwd());
my $q = CGI->new;
my $debug = $q->param('debug') ? 1 : undef;
my $trace = '';
my $sharedsecret = 'zzxoiuakjwefya%^&@#*(*(&@dflaskiouioiuklasfq';
my $salt = time();
my @filesToRemove;
my @dirsToRemove;
my %fileValues;

<<COMMENT;
########################### #######
 Process an xml2rfc HTTP request

 invoking form has these fields:
	file "input" or "url"
	    contains the XML file
	radio button "mode"
	    one of txt, unpg, html, htmlxslt, htmlrfcmarkup, nr, or xml
	radio button "format"
	    one of ascii, pdf, epub, mobi, rtf, ps
            epub and mobi requires an html* mode to be used
	    rtp does not allow an html* mode to be used
	radio button "type"
	    either ascii (output to window), toframe (separate warnings/output windows)
	    or binary (output to file)

	radiobutton "checking" - either "strict" or "fast"

########################## #######


mode:
txt		xml2rfc --text > text
unpg		xml2rfc --raw > unpg
nroff		xml2rfc --nroff > nroff
xml		xml2rfc --exp > xml
html		xml2rfc --html > html
htmlxslt	xml2rfc --exp > xml, xslt process > html
htmlrfcmarkup	xml2rfc --text > text, rfcmarkup > html

format:
*/ascii		done

html*/pdf	wkhtmltopdf < html* > pdf
*/pdf		enscript < * > ps; ps2pdf < ps > pdf

html*/ps	wkhtmltopdf < html* > pdf; pdf2ps < pdf > ps
*/ps		enscript < * > ps

html*/rtf	not allowed
*/rtf		enscript < * > rtf

htmlxslt/epub	xml2rfc-html2epub-viaxslt < xml > epub
html*/epub	ebook-convert < html* > epub
*/epub		rename to *.txt; ebook-convert < txt > epub

html*/mobi	ebook-convert < html* > mobi
*/mobi		rename to *.txt; ebook-convert < txt > mobi

COMMENT

my @modes = ('txt', 'unpg', 'html', 'htmlxslt', 'htmlrfcmarkup', 'nr', 'xml');
my @formats = ('ascii',  'pdf',  'epub', 'mobi',  'rtf',  'ps');

umask(0);
my $input    = $q->param('input');
my $inputfn  = untaint($q->tmpFileName($input));
my $url = $q->param('url');
if (($input eq '') || ($inputfn eq '')) {
    userError("No input file") if ($url eq '');
    my ($content, $err) = wget($url);
    userError($err) if ($err ne '');
    $inputfn = "/tmp/CGItemp$$.txt";
    createFile($inputfn, $content);
}

my $inputfndir = "$inputfn.dir";
my $modeAsFormat = $q->param('modeAsFormat');
if ($modeAsFormat =~ m((.*)/(.*))) {
   $q->param('mode', $1);
   $q->param('format', $2);
}
my $mode = checkValue('mode', @modes);
my $format = checkValue('format', @formats);
my $type     = checkValue('type', 'ascii', 'binary', 'toframe', 'towindow', 'tofile');
my $checking = checkValue('checking', 'strict', 'fast');
$checking = 'fast';
if ($type eq 'ascii') {
    $type = 'towindow';
} elsif ($type eq 'binary') {
    $type = 'tofile';
}
userError("Error: epub requires an html mode") if (($format eq "epub") && ($mode !~ /^html/));
userError("Error: mobi requires html mode") if (($format eq "mobi") && ($mode !~ /^html$/));
userError("Error: rtf does not allow an html mode") if (($format eq "rtf") && ($mode =~ /^html/));

my %expandedModes = (
    txt => "Text",
    html => "HTML",
    htmlxslt => "HTML via XSLT",
    htmlrfcmarkup => "HTML via RfcMarkup",
    nr => "Nroff",
    unpg => "Unpaginated Text",
    xml => "XML"
    );
my %expandedFormats = (
    ascii => "ASCII",
    pdf => "PDF",
    epub => "ePub",
    mobi => "MOBI",
    rtf => "Rich Text Format",
    ps => "PostScript"
    );
my %extensions = (
    txt => 'txt',
    html => 'html',
    htmlxslt => 'html',
    htmlrfcmarkup => 'html',
    nr => 'nr',
    unpg => 'unpg',
    xml => 'xml',
    pdf => 'pdf',
    epub => 'epub',
    mobi => 'mobi',
    rtf => 'rtf',
    ps => 'ps'
    );
my %xml2rfc2modes = (
    html => 'html',
    htmlxslt => 'exp',
    htmlrfcmarkup => 'text',
    nr => 'nroff',
    pdf => 'text',
    ps => 'text',
    txt => 'text',
    unpg => 'raw',
    xml => 'exp',
    );

printHeaders("text/plain") if $debug;
my $outputfn = getOutputName($input, $mode, $format);
my $basename = $outputfn;
$basename =~ s/.[^.]*$//;
print "input='$input', inputfn='$inputfn', outputfn='$outputfn', basename='$basename'\n" if $debug;
print "mode=$mode, format=$format, checking=$checking, type=$type\n" if $debug;
saveTracePass("Generating $expandedModes{$mode} output in $expandedFormats{$format} format", "h1");

####### ########################### #######
####### # pass 0 - environment
####### #	change directory
####### #	set environment variables
####### #	if mode == xml
####### #		type = tofile
####### ########################### #######


# if in cgi-bin, cd one level up
if ($dir =~ /\/cgi-bin$/) {
    print "in '$dir', cd ..\n" if $debug;
    chdir("..");
    $dir = dirname($dir);
} else {
    print "in '$dir'\n" if $debug;
}
my $tmpdir = dirname($inputfn);

# set environment
$ENV{PATH} = "/usr/bin:/bin";
$ENV{DOCUMENT_ROOT} = 'web' if !defined($ENV{DOCUMENT_ROOT});
$ENV{SERVER_ADMIN} = 'tony@att.com';
# $ENV{HOME} = "/var/tmp";
# $ENV{HOME} = "/home/tonyh";
$ENV{LANG} = "en_US";

$ENV{XML_LIBRARY} = "$dir/web/public/rfc/bibxml";
foreach my $bibxml (<$dir/web/public/rfc/bibxml?>) {
    $ENV{XML_LIBRARY} .= ":$bibxml";
}

# link/copy files needed in order to convert files
foreach my $dtdFile ('rfc2629-other.ent', 'rfc2629-xhtml.ent', 'rfc2629.dtd', 'rfc2629.xslt') {
    my $tmpDtdFile = "$dir/etc/xslt/$dtdFile";
    my $nfile = "$tmpdir/$dtdFile";
    if (!-l $nfile && !-f $nfile) {
	my $ret = symlink($tmpDtdFile, $nfile);
	print "symlink($tmpDtdFile, $nfile) => $ret\n" if $debug;
    }
}

# force xml to go to a file instead of the window
$type = 'tofile' if (($type eq 'towindow') && ($mode eq 'xml'));

my $newinputfn = setSubTempFile("$basename.xml");
my $ret = rename($inputfn, $newinputfn);
print "rename($inputfn,$newinputfn) ret='$ret'\n" if $debug;
$ret = chmod 0666, $newinputfn;
# print "chmod 0666, $newinputfn: ret='$ret'\n" if $debug;
my $TMPERR = getTempFileWithSuffix("err");
my ($ret, $out, $err);


####### ########################### #######
####### # pass 1 - expand and check input
####### #	xml2rfc $inputfn > $TMP1
####### #		check for errors
####### #	sax < $TMP1
####### #		check for errors
####### ########################### #######
####### #
####### # Run xml2rfc to: expand internal references and includes.
####### #
####### ########################### #######

my $curfile = $newinputfn;

given ($mode) {
    when("txt") {
	my $tmpout = callXml2rfc("txt", "text");
	$curfile = $tmpout;
    }
    when("unpg") {
	my $tmpout = callXml2rfc("txt", "raw");
	$curfile = $tmpout;
    }
    when("nr") {
	my $tmpout = callXml2rfc("nr", "nroff");
	$curfile = $tmpout;
    }
    when("xml") {
	my $tmpout = callXml2rfc("xml", "exp");
	$curfile = $tmpout;
    }
    when("html") {
	my $tmpout = callXml2rfc("html", "html");
	$curfile = $tmpout;
    }
    when("htmlxslt") {
	my $TMP1 = callXml2rfc("xml", "exp");
	if (($format eq "epub") || ($format eq "mobi")) {
	    $curfile = $TMP1;
	} else {
	    my $TMP2 = getTempFileWithSuffix("html");
	    ($ret, $out, $err) = runCommand("xsltproc $dir/etc/xslt/rfc2629.xslt $TMP1 > $TMP2", $TMP1, $TMP2, "Generating $expandedModes{$mode}");
	    userError("Unable to Validate File", $err) if ($err =~ /Error/);
	    $curfile = $TMP2;
	}
    }
    when("htmlrfcmarkup") {
	my $TMP1 = callXml2rfc("txt", "text");
	my $TMP2 = getTempFileWithSuffix("html");
	($ret, $out, $err) = runCommand("env - /home/www/tools.ietf.org/tools/rfcmarkup/rfcmarkup url=file://$TMP1 > $TMP2", $TMP1, $TMP2, "Generating $expandedModes{$mode}");
	userError("Unable to Validate File", $err) if ($err =~ /Error/);
	open(TMP2, "<", $TMP2) or userError("Unable to open temp file", $!);
	my $firstLine = <TMP2>;
	if ($firstLine =~ /^content-type:/i) {
	    print "Skipping '$firstLine'\n" if $debug;
	    while (<TMP2>) {
	        print "Skipping '$_'\n" if $debug;
		last if $_ =~ /^$/;
	    }
	    my $TMP3 = getTempFileWithSuffix("html");
	    open(TMP3, ">", $TMP3) or userError("Unable to create temp file", $!);
	    while (<TMP2>) {
		print TMP3 $_;
	    }
	    close(TMP2);
	    close(TMP3);
	    $curfile = $TMP3;
	} else {
	    $curfile = $TMP2;
	}
    }
    default {
	userError("unknown mode $mode");
    }
}

print "at end of first pass, curfile=$curfile\n" if $debug;

####### ########################### #######
####### # pass 2 - convert to output format
####### #	if format == ascii
####### #		done
####### #	else
####### #		convert $TMP2.$mode $TMP3.$format
####### ########################### #######

my $enscriptPsArguments = "--font=Courier12 --language=PostScript --no-header --quiet";
given($format) {
    when("ascii") { # all done
    }
    when("pdf") {
        if ($mode =~ /^html/) {
	    my $TMP2 = getTempFileWithSuffix("pdf");
	    ($ret, $out, $err) = runCommand("etc/wkhtmltopdf-i386 --quiet $curfile $TMP2", $curfile, $TMP2, "Converting to PDF");
	    userError("Unable to Convert File", $err) if ($err ne '');
	    $curfile = $TMP2;
	} else {
	    my $TMP2 = getTempFileWithSuffix("ps");
	    ($ret, $out, $err) = runCommand("enscript $enscriptPsArguments --output=$TMP2 < $curfile", $curfile, $TMP2, "Converting to intermediate PS");
	    userError("Conversion error to intermediate postscript", $err) if ($err ne '');
	    my $TMP3 = getTempFileWithSuffix("pdf");
	    ($ret, $out, $err) = runCommand("ps2pdf $TMP2 $TMP3", $TMP2, $TMP3);
	    userError("Conversion error to final PDF", $err) if ($err ne '');
	    $curfile = $TMP3;
	}
    }
    when("ps") {
        if ($mode =~ /^html/) {
	    my $TMP2 = getTempFileWithSuffix("pdf");
	    ($ret, $out, $err) = runCommand("etc/wkhtmltopdf-i386 --quiet $curfile $TMP2", $curfile, $TMP2, "Converting to intermediate PDF");
	    userError("Unable to Convert File", $err) if ($err ne '');
	    my $TMP3 = getTempFileWithSuffix("ps");
	    ($ret, $out, $err) = runCommand("pdf2ps $TMP2 $TMP3", $TMP2, $TMP3, "Converting to final PS");
	    userError("Conversion error to final PS", $err) if ($err ne '');
	    $curfile = $TMP3;
	} else {
	    my $TMP2 = getTempFileWithSuffix("ps");
	    ($ret, $out, $err) = runCommand("enscript $enscriptPsArguments --output=$TMP2 < $curfile", $curfile, $TMP2, "Converting to PS");
	    userError("Conversion error to final postscript", $err) if ($err ne '');
	    $curfile = $TMP2;
	}
    }
    when("rtf") {
	if ($mode =~ /^html/) {
	    userError("RTF is not supported for HTML modes");
	} else {
	    my $TMP2 = getTempFileWithSuffix("rtf");
	    ($ret, $out, $err) = runCommand("enscript --language=rtf --no-header --quiet --output=$TMP2 < $curfile", $curfile, $TMP2, "Converting to RTF");
	    userError("Conversion error to intermediate postscript", $err) if ($err ne '');
	    $curfile = $TMP2;
	}
    }
    when("epub") {
	my $TMP2 = getTempFileWithSuffix("epub");
	if ($mode eq "htmlxslt") {
	    ($ret, $out, $err) = runCommand("etc/xml2rfc-html2epub-viaxslt $curfile $TMP2", $curfile, $TMP2, "Converting to epub");
	    userError("Conversion error to epub", $err) if ($err =~ /error/i);
	} else {
	    if ($mode !~ /^html/) {
		my $TMP3 = getTempFileWithSuffix("txt");
		rename($curfile, $TMP3);
		$curfile = $TMP3;
	    }
	    getFileValues($newinputfn);
	    $fileValues{"rfc/front/title"} =~ s/'/_/g;
	    $fileValues{"rfc/front/keyword"} =~ s/'/_/g;
	    $fileValues{authors} =~ s/'/_/g;
	    my $TMP4 = getTempFileWithSuffix("html");
	    ($ret, $out, $err) = runCommand("sed -e '/\@page {/,/]]>/d' -e '/<\\/style/s/^/\\/*]]>*\\//' < $curfile > $TMP4; ebook-convert $TMP4 $TMP2 " .
	    # ($ret, $out, $err) = runCommand("ebook-convert $curfile $TMP2 " .
		# "--no-svg-cover " .
		"--no-default-epub-cover " .
		"--authors='" . untaint($fileValues{authors}) . "' " .
		"--title='" .  untaint($fileValues{"rfc/front/title"}) . "' " .
		"--tags='" .  untaint($fileValues{"rfc/front/keyword"}) . "' ",
		$curfile, $TMP2, "Converting to $format");
	}
	$curfile = $TMP2;
    }
    when("mobi") {
	my $TMP2 = getTempFileWithSuffix("mobi");
        if ($mode !~ /^html/) {
	    my $TMP3 = getTempFileWithSuffix("txt");
	    rename($curfile, $TMP3);
	    $curfile = $TMP3;
	}
	getFileValues($newinputfn);
	$fileValues{"rfc/front/title"} =~ s/'/_/g;
	$fileValues{"rfc/front/keyword"} =~ s/'/_/g;
	$fileValues{authors} =~ s/'/_/g;
	my $TMP4 = getTempFileWithSuffix("html");
	($ret, $out, $err) = runCommand("sed -e '/\@page {/,/]]>/d' -e '/<\\/style/s/^/\\/*]]>*\\//' < $curfile > $TMP4; ebook-convert $TMP4 $TMP2 " .
	# ($ret, $out, $err) = runCommand("ebook-convert $curfile $TMP2 " .
		# "--no-svg-cover " .
		# "--no-default-epub-cover " .
		"--authors='" . untaint($fileValues{authors}) . "' " .
		"--title='" .  untaint($fileValues{"rfc/front/title"}) . "' " .
		"--tags='" .  untaint($fileValues{"rfc/front/keyword"}) . "' ",
		$curfile, $TMP2, "Converting to $format");
	$curfile = $TMP2;
    }
    default {
	userError("unknown format $format");
    }
}

print "at end of second pass, curfile=$curfile\n" if $debug;

####### ########################### #######
####### # pass 3 - send back to browser
####### #	if type = towindow
####### #		output to window
####### #	else if type = toframe
####### #		create a frameset
####### #		let cgi.pl output the files and cleanup
####### #	else
####### #		output to file
####### ########################### #######


if ($type eq 'towindow') {
    printHeaders(getContentType($mode, $format));
    catFile($curfile);
} elsif ($type eq 'toframe') {
    my $TMPTRACE = "$inputfn-5.html";
    # my $errorMessage = "<h2 style='color: red'>Errors exist</h2>";
    my $warningMessage = "<h2 style='color: orange'>Warnings exist</h2>";
    # my $errorsExist = ($trace =~ /error/i) ? $errorMessage : "";
    my $warningsExist = ($trace =~ /warning/i) ? $warningMessage : "";
    createFile($TMPTRACE, $warningsExist, $trace, "<hr/>\n");

    # my $outputfn = getOutputName($input, $mode, $format);
    my $KEEP = keepTempFile($curfile, "$inputfn-6." . getExtension($curfile), $debug);
    printHeaders("text/html");
    print "<html><head><title>XML2RFC Processor with Warnings &amp; Errors</title></head>\n";
    my $rows = (($format eq 'ascii') && ($mode ne 'xml')) ? '25%,*' : '50%,*';
    print "<frameset rows='$rows'>\n";
    print "<frame src='cat.cgi?input=" . encryptFileName($TMPTRACE) . "'/>\n";
    print "<frame src='cat.cgi/$outputfn?input=" . encryptFileName($KEEP) . "'/>\n";
    print "</frameset>";
    print "</html>";
    if ($debug) {
	print "\n================================================================\n";
	catFile($TMPTRACE);
	print "================================================================\n";
	catFile($KEEP);
    }

} elsif ($type eq 'tofile') {
    # my $outputfn = getOutputName($input, $mode, $format);
    # cgi_content_type "unknown/exe"
    printHeaders("application/octet-stream", "Content-Disposition: attachment; filename=\"$outputfn\"");
    catFile($curfile);
} else {
    userError("unknown output type $type");
}

####### ########################### #######
####### # all done
####### ########################### #######

cleanup();
exit;

####### ########################### #######
####### #### utility functions
####### ########################### #######

sub callXml2rfc {
    my $suffix = shift;
    my $xml2rfcMode = shift;
    my $tmpout = getTempFileWithSuffix($suffix);
    my ($ret, $out, $err) = runCommand("etc/xml2rfc2 --$xml2rfcMode --file=$tmpout $curfile", $curfile, $tmpout, "Expanding internal references and generating $expandedModes{$mode}");
    $curfile = $tmpout;
    print "xml2rfc ret=$ret\n" if $debug;
    print "out='$out'\n" if $debug;
    print "err='$err'\n" if $debug;
    if ($err =~ /ERROR/) {
	userError("Unable to Validate File", $err, $out);
    } else {
	$out .= $err;
    }
    return $tmpout;
}

####### execute an external command, capturing
####### its standard output, standard error, error code
sub runCommand {
    my $cmd = shift;
    my $infn = shift;
    my $outfn = shift;
    my $pass = shift;
    saveTracePass($pass);
    print "\n--- $pass ---\n" if $debug;
    $cmd .= " 2>$TMPERR";
    print "\n!!!!!!!!!!!!!!!! runCommand($cmd)\n\n" if $debug;
    my $out = `$cmd`;
    my $ret = $?;
    my $err = getFile($TMPERR);
    my $binfn = basename($infn);
    my $boutfn = basename($outfn);
    $out =~ s($infn|$binfn)(INPUT)gm;
    $out =~ s($outfn|$boutfn)(OUTPUT)gm;
    $err =~ s($infn|$binfn)(INPUT)gm;
    $err =~ s($outfn|$boutfn)(OUTPUT)gm;
    saveTrace($ret, $out, $err);
    if ($debug) {
	print "command ret=$ret\n";
	print "out='$out'\n";
	print "err='$err'\n";
    }
    return ($ret, $out, $err);
}

####### save an external command's standard output,
####### standard error, error code for later printing
sub saveTrace {
    return if $type ne 'toframe';
    my ($ret, $out, $err) = @_;
    $out =~ s(/var/tmp/|/tmp/)()gm;
    $err =~ s(/var/tmp/|/tmp/)()gm;
    $trace .= "<hr/><pre>\n" .  HTML::Entities::encode($out) . "</pre>\n" if ($out ne '');
    $trace .= "<hr/><pre>\n" .  HTML::Entities::encode($err) . "</pre>\n" if ($err ne '');
}

####### save an external command's pass name in the trace
####### for later printing
sub saveTracePass {
    my $pass = shift;
    my $h = shift;
    $h = 'h2' if $h eq '';
    return if $type ne 'toframe';
    $trace .= "<$h>$pass</$h>\n";
}

####### remove any temporary files we created
sub cleanup {
    for my $file (@filesToRemove) {
	unlink($file) unless $debug;
    }
    for my $dir (@dirsToRemove) {
	rmdir($dir) if -d $dir;
    }
}

####### get a CGI parameter and make certain it
####### has one of our known values
sub checkValue {
    my ($name, @args) = @_;
    my $val = $q->param($name);
    # print "val='$val', name='$name', arg0='$args[0]'\n";
    return $args[0] if !defined($val);
    foreach my $cval (@args) {
	return $cval if ($cval eq $val);
    }
    userError("Error: $name must be set to one of", join(' ', @args) . "\n(found $val)");
}

####### print out an HTML page with a given error message
sub userError {
    printHeaders("text/html");
    print "<html><head><title>You lose</title></head><body>";

    my $event = HTML::Entities::encode(shift);
    my $info = HTML::Entities::encode(shift);
    my $text = HTML::Entities::encode(shift);

    print "<style>.error { color: red; }</style>\n";
    print "<h1 class='error'>$event</h1>\n";
    print "<pre class='error'>$info</pre>\n";
    print "<pre>$text</pre>\n";
    print "<hr/>\n";
    print $ENV{SERVER_SIGNATURE};
    print "</body></html>\n";
    cleanup();
    exit();
}

my $suffixCount = 0;
sub getTempFileWithSuffix {
    my $suffix = shift;
    $suffixCount++;
    my $tmp = setSubTempFile("$basename-$suffixCount.$suffix");
    print "getTempFileWithSuffix() => '$tmp'\n" if $debug;
    return $tmp;
}

####### add a temporary file to the removal list
sub setTempFile {
    my $ret = shift;
    push @filesToRemove, $ret;
    return $ret;
}

####### add a temporary file in a temporary subdirectory to the removal list
sub setSubTempFile {
    my $ret = shift;
    $ret =~ s(^.*/)();
    $ret = "$inputfndir/$ret";
    if (! -d "$inputfndir") {
	mkdir($inputfndir);
	push @dirsToRemove, $inputfndir;
    }
    push @filesToRemove, $ret;
    return $ret;
}

####### remove a temporary file from the removal list
sub keepTempFile {
    my $lookFor = shift;
    my $renameTo = shift;
    my $debug = shift;
    rename($lookFor, $renameTo);
    return $renameTo if $debug;
    print "'$lookFor' renamed to '$renameTo'\n" if $debug;
    my @tmp;
    for my $file (@filesToRemove) {
	push @tmp, $file if $file ne $lookFor;
    }
    @filesToRemove = @tmp;
    return $renameTo;
}

# for a given filename, return its extension
sub getExtension {
    my $fn = shift;
    $fn =~ s/^.*[.]//;
    return $fn;
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

####### copy the contents of a file to standard output
sub catFile {
    my $fn = shift;
    if ( open(RAW, "<", $fn) ) {
	my $r;
	my $block;
	while (($r = read(RAW, $block, 4096)) > 0) {
	    print $block;
	}
	close(RAW);
    }
}

####### copy the contents of a file to a local variable
sub getFile {
    my $fn = shift;
    if ( open(RAW, "<", $fn) ) {
	local $/;               # No line separator
	my $slurp = <RAW>;
	close(RAW);
	return $slurp;
    }
    return "";
}

# create a file and write the passed strings to it
sub createFile {
    my $fn = shift;
    open (TMPTRACE, ">", $fn) or userError("Error writing temp files", $!);
    for my $str (@_) {
	print TMPTRACE $str;
    }
    close TMPTRACE;
}

####### if not already generated, make sure there is a content
####### type header, along with any other headers we will need
my $printedHeader;
sub printHeaders {
    my $contentType = shift;
    if (!$printedHeader || $debug) {
	print "Content-Type: $contentType\n";
	foreach my $hdr (@_) {
	    print "$hdr\n";
	}
	print "\n";
    }
    $printedHeader = 1;
}

####### for the given mode and format, return
####### a proper content-type value
sub getContentType {
    my $mode = shift;
    my $format = shift;
    if ($format eq 'ascii') {
	if ($mode eq 'txt') { return "text/plain"; }
	if ($mode =~ /^html/) { return "text/html"; }
	if ($mode eq 'xml') { return "text/xml"; }
	return "text/plain";	# nr, unpg
    } elsif ($format eq 'pdf') {
	return "application/pdf";
    } elsif ($format eq 'epub') {
	return "application/epub+zip";
    } elsif ($format eq 'mobi') {
	return "application/x-mobipocket-ebook";
    } elsif ($format eq 'rtf') {
	return "application/rtf";
    } elsif ($format eq 'ps') {
	return "application/postscript";
    } else {
	return "application/octet-stream";
    }
}

####### create an output filename based on the mode
####### and format, based on the input filename
sub getOutputName {
    my ($outputfn, $mode, $format) = @_;
    $outputfn = basename($outputfn);
    $outputfn =~ s/\.xml$//;	# remove trailing .xml
    $outputfn = untaint($outputfn, '([^<>\s;&]*)');
    $outputfn .= ".";		# add in a new extension
    if ($format eq 'ascii') {
	$outputfn .= $extensions{$mode};
    } else {
	$outputfn .= "$extensions{$mode}.$extensions{$format}";
    }
    return $outputfn;
}

####### mail an error message to the administrator
sub mail_error {
    my $inputF = shift;
    my $errorInfo = shift;
    try {
	my $smtp = Net::SMTP->new("localhost", Timeout => 60);
	$smtp->mail("webmaster\@tools.ietf.org");
	$smtp->recipient($ENV{SERVER_ADMIN});
	$smtp->data;
        $smtp->datasend("From: webmaster\@tools.ietf.org");
        $smtp->datasend("Subject: [cgi_name] CGI problem");
        $smtp->datasend("\n");
        $smtp->datasend("CGI environment:");
        $smtp->datasend("REQUEST_METHOD: $ENV{REQUEST_METHOD}");
        $smtp->datasend("SCRIPT_NAME: $ENV{SCRIPT_NAME}");
	$smtp->datasend("INPUT_FILE: $inputF");
        $smtp->datasend("HTTP_USER_AGENT: $ENV{HTTP_USER_AGENT}");
        $smtp->datasend("HTTP_REFERER: $ENV{HTTP_REFERER}");
        $smtp->datasend("HTTP_HOST: $ENV{HTTP_HOST}");
        $smtp->datasend("REMOTE_HOST: $ENV{REMOTE_HOST}");
        $smtp->datasend("REMOTE_ADDR: $ENV{REMOTE_ADDR}");
        $smtp->datasend("cgi.tcl version: 1.4.3");
        $smtp->datasend("input:");
        $smtp->datasend($q->param("input"));
        $smtp->datasend("cookie: $ENV{HTTP_COOKIE}");
        $smtp->datasend("errorInfo: $errorInfo");
	$smtp->dataend();
	$smtp->quit();
    }
}


####### encrypt a filename so its path cannot be guessed
sub encryptFileName {
    my $fn = shift;
    $salt++;
    my $passphrase = $sharedsecret . "-" . length($fn) . "-$salt";
    my $rc4 = Crypt::RC4->new( md5($passphrase) );
    return unpack("H*", $rc4->RC4($fn)) . "-$salt";
}


####### return the final path segment of a filename
sub basename {
    my $fn = shift;
    $fn =~ s/\\/\//g;
    $fn =~ s/^.*\///;
    return $fn;
}

####### return all but the final path segment of a filename
sub dirname {
    my $fn = shift;
    $fn =~ s/\\/\//g;
    return "." if ($fn !~ /\//);
    $fn =~ s/\/[^\/]*$//;
    return $fn;
}


my @xmlPath;
my $xmlPath;
my $xmlCharVal;
my $firstElement = '';
my $lastElement = '';
my $responseType = '';

sub getFileValuesStart {
    my ($p, $txt, %attributes) = @_;
    push @xmlPath, $txt;
    $xmlPath = join('/', @xmlPath);
    $xmlCharVal = '';
    # print "start: p='$p', txt='$txt', path=$xmlPath\n" if $debug;
    $firstElement = $txt if $firstElement eq '';
    if ($xmlPath eq 'rfc/front/author') {
	print "author='" . $attributes{fullname} . "'\n" if $debug;
	$fileValues{authors} .= " & " if ($fileValues{authors} ne '');
	$fileValues{authors} .= $attributes{fullname};
    } elsif ($xmlPath eq 'rfc/middle') {
	die "--break--";
    }
}

sub getFileValuesEnd {
    my ($p, $txt) = @_;
    # print "end: p='$p', txt='$txt', path=$xmlPath\n" if $debug;
    $lastElement = $txt;

    if ($xmlPath =~ m(^rfc/front/)) {
	if ($xmlPath eq 'rfc/front/keyword') {
	    $fileValues{$xmlPath} .= ", " if ($fileValues{$xmlPath} ne '');
	}
	$fileValues{$xmlPath} .= $xmlCharVal;
	# print "PATH: '$xmlPath' => '$xmlCharVal'\n" if $debug;
    }

    pop @xmlPath;
    $xmlPath = join('/', @xmlPath);
}

sub getFileValuesChar {
    my ($p, $txt) = @_;
    $xmlCharVal .= $txt;
}

sub getFileValues {
    my $fn = shift;
    # initialize parser
    my $xp = new XML::Parser();

    # set callback functions
    $xp->setHandlers(Start => \&getFileValuesStart,
		     End => \&getFileValuesEnd,
		     Char => \&getFileValuesChar);

    eval {		# Enclose block for catching errors
	$xp->parsefile($fn); # parse XML
    };
    if ($@) {		# Check for parse error die
	if ($@ ne '--break--') {
	    my $error_str .= "XML PARSER TERMINATED: " . $@;
	    print $error_str, "\n" if $debug;
	    return $error_str;
	}
    }               # Die if errors
    return "";
}

sub wget {
    my $href = shift;
    my $ua = new LWP::UserAgent;
    $ua->timeout(60);
    my $req = new HTTP::Request(GET => $href);
    my $res = $ua->request($req);
    if ($res->is_error) {
	return (undef, "An error has occurred accessing $href: " . $res->status_line);
    }
    my $ret = $res->content;
    return ($ret, undef);
}
