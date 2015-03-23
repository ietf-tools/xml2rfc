#!/usr/bin/perl -T

use strict vars;
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
my $trace;
my $sharedsecret = 'zzxoiuakjwefya%^&@#*(*(&@dflaskiouioiuklasfq';
my $salt = time();
my @filesToRemove;
my @dirsToRemove;
my %fileValues;

####### ########################### #######
####### # Process an xml2rfc HTTP request
####### #
####### # invoking form has these fields:
####### #       file "input" - contains the XML file
####### #       radiobutton "mode" - either txt, unpg, html, htmlxslt, nr, or xml
####### #       radiobutton "type" - either ascii (output to window), toframe (separate warnings/output windows) 
####### #		or binary (output to file)
####### #       radiobutton "format" - either ascii, pdf, epub, rtf, ps
####### #
####### #	radiobutton "checking" - either "strict" or "fast"
####### #
####### ########################### #######

my @modes = ('txt', 'unpg', 'html', 'htmlxslt', 'nr', 'xml');
my @formats = ('ascii',  'pdf',  'epub',  'rtf',  'ps');

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
$type = 'towindow' if $type eq 'ascii';
$type = 'tofile' if $type eq 'binary';

my %expandedModes = (
    txt => "Text",
    html => "HTML",
    htmlxslt => "HTML via XSLT",
    nr => "Nroff",
    unpg => "Unpaginated Text",
    xml => "XML"
    );
my %expandedFormats = (
    ascii => "ASCII",
    pdf => "PDF",
    epub => "ePub",
    rtf => "Rich Text Format",
    ps => "PostScript"
    );
my %extensions = (
    txt => 'txt',
    html => 'html',
    htmlxslt => 'html',
    nr => 'nr',
    unpg => 'unpg',
    xml => 'xml',
    pdf => 'pdf',
    epub => 'epub',
    rtf => 'rtf',
    ps => 'ps'
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
# userError("Unable to rename temp file", $!) if $ret;


####### ########################### #######
####### # pass 1 - expand and check input
####### #	xml2rfc $inputfn > $TMP1
####### #		check for errors
####### #	sax < $TMP1
####### #		check for errors
####### ########################### #######


# Run xml2rfc to: expand internal references and includes.
# If not doing strict checking, this will generate the final version as well.
my $needExpansionToXml =
	($checking eq 'strict') ||
	($format eq 'epub') ||
	($mode eq 'htmlxslt')
	;
my $finalTclPassHere;
if ($mode eq 'xml') {
    $finalTclPassHere = 1;
} else {
    if ($mode eq 'htmlxslt') {
	if ($format eq 'epub') {
	    $finalTclPassHere = 1;
	}
    } elsif (!$needExpansionToXml) {
	$finalTclPassHere = 1;
    }
}

my $TMP1 = $finalTclPassHere ?
    ($needExpansionToXml ?  setSubTempFile("$basename-2.xml") : setSubTempFile("$basename-2." . $extensions{$mode})) :
    ($needExpansionToXml ?  setTempFile("$inputfn-1.xml") : setTempFile("$inputfn-1." . $extensions{$mode}));

my %xml2rfc2modes = (
    epub => 'text',
    html => 'html',
    htmlxslt => 'exp',
    nr => 'nroff',
    pdf => 'text',
    ps => 'text',
    rtf => 'text',
    txt => 'text',
    unpg => 'raw',
    xml => 'exp',
    );
# for my $key (keys %xml2rfc2modes) {
#     print "key=$key, mode='$xml2rfc2modes{$key}'\n";
# }
my $xml2rfc2mode = $xml2rfc2modes{$mode};

print "mode='$mode', xml2rfc2mode='$xml2rfc2mode'\n" if $debug;
print "TMP1=$TMP1\n" if $debug;
my $TMPERR = setTempFile("$inputfn.err");

my ($ret, $out, $err) = runCommand("etc/xml2rfc2 --$xml2rfc2mode --out=$TMP1 $newinputfn", $newinputfn, $TMP1, 
    $needExpansionToXml ?  "Expanding internal references" : "Expanding internal references and generating $mode"
    );
print "xml2rfc ret=$ret\n" if $debug;
print "out='$out'\n" if $debug;
print "err='$err'\n" if $debug;
userError("Unable to Validate File", $err) if ($err ne '');

# Do the strict DTD checking.
if ($checking eq 'strict') {
    ($ret, $out, $err) = runCommand("java -cp etc/xercesImpl.jar:etc/xercesSamples.jar sax.Counter -v $TMP1", $TMP1, $TMP1, "Strict DTD check");
    print "xerces ret=$ret\n" if $debug;
    print "out='$out'\n" if $debug;
    print "err='$err'\n" if $debug;

    if ($err =~ /no grammar found/) {
       $out .= "\nAre you missing the statement <!DOCTYPE rfc SYSTEM \"rfc2629.dtd\"> in your source file?\n\n";
       $out .= $err;
    } else {
       $out .= $err;
    }
    $out .= "\n\nTo proceed, you should fix your input file.\n" .
      "You may also try doing the conversion with Strict Checking turned off.\n";
    userError("Unable to Validate File", $out) if (($out =~ /\[Error\]/) || ($out =~ /\[Fatal Error\]/));
}


####### ########################### #######
####### # pass 2 - expand xml2rfc
####### #	if mode == xml
####### #		TMP2.xml = TMP1
####### #	else
####### #		xml2rfc TMP1 TMP2.$mode
####### ########################### #######


my $TMP2;
if ($mode eq 'xml') {
    $TMP2 = $TMP1;
    print "TMP2=$TMP2\n" if $debug;
} else {
    # $TMP2 = setTempFile("$inputfn-2." . $extensions{$mode});
    if ($mode eq 'htmlxslt') {
	if ($format eq 'epub') {
	    $TMP2 = $TMP1;
	    print "TMP2=$TMP2\n" if $debug;
	} else {
	    $TMP2 = setTempFile("$inputfn-2." . $extensions{$mode});
	    print "TMP2=$TMP2\n" if $debug;
	    my ($ret, $out, $err) = runCommand("xsltproc $dir/etc/xslt/rfc2629.xslt $TMP1 > $TMP2", $TMP1, $TMP2, "Generating $mode");
	    print "xsltproc ret=$ret\n" if $debug;
	    print "out='$out'\n" if $debug;
	    print "err='$err'\n" if $debug;
	    userError("Unable to Validate File", $err) if ($err =~ /Error/);
	}
    } elsif (!$needExpansionToXml) {
	$TMP2 = $TMP1;
	print "TMP2=$TMP2\n" if $debug;
    } else {
	$TMP2 = setSubTempFile("$basename." . $extensions{$mode});
	print "TMP2=$TMP2\n" if $debug;
	my ($ret, $out, $err) = runCommand("tclsh etc/xml2rfc-dev.tcl xml2rfc $TMP1 $TMP2", $TMP1, $TMP2, "Generating $mode");
	print "xml2rfc ret=$ret\n" if $debug;
	print "out='$out'\n" if $debug;
	print "err='$err'\n" if $debug;
	userError("Unable to Validate File", $err) if ($err ne '');
    }
}


####### ########################### #######
####### # pass 3 - convert to output format
####### #	if format == ascii
####### #		TMP3.$mode = TMP2.$mode
####### #	else
####### #		convert $TMP2.$mode $TMP3.$mode.$format
####### ########################### #######


my $TMP3;
if ($format eq 'ascii') {
    $TMP3 = $TMP2;
} else {
    $TMP3 = setTempFile("$inputfn-3." . $extensions{$format});
    if ($mode eq 'txt') {
	my $filesize = -s $TMP2;
	my $ret = truncate($TMP2, $filesize - 2);
	print "truncate ret=$ret\n" if $debug;
    }
    my ($ret, $out, $err);
    my $enscriptPsArguments = "--font=Courier12 --language=PostScript --no-header --quiet";
    if ($format eq 'pdf') {
	if (($mode eq 'html') || ($mode eq 'htmlxslt')) {
	    ($ret, $out, $err) = runCommand("etc/wkhtmltopdf-i386 --quiet $TMP2 $TMP3", $TMP2, $TMP3, "Converting to $format");
	    print "wkhtmltopdf ret=$ret\n" if $debug;
	    print "out='$out'\n" if $debug;
	    print "err='$err'\n" if $debug;
	    userError("Conversion error to pdf", $err) if ($err ne '');
	} else {
	    my $TMP4 = setTempFile("$inputfn-4.ps");
	    print "TMP3=$TMP3\n" if $debug;
	    print "TMP4=$TMP4\n" if $debug;
	    ($ret, $out, $err) = runCommand("enscript $enscriptPsArguments --output=$TMP4 < $TMP2", $TMP2, $TMP4, "Converting to $format");
	    print "enscript ret=$ret\n" if $debug;
	    print "out='$out'\n" if $debug;
	    print "err='$err'\n" if $debug;
	    userError("Conversion error to intermediate postscript", $err) if ($err ne '');
	    ($ret, $out, $err) = runCommand("ps2pdf $TMP4 $TMP3", $TMP4, $TMP3);
	}
    } elsif ($format eq 'rtf') {
	if (($mode eq 'html') || ($mode eq 'htmlxslt')) {
	    $err = "HTML => RTF is not supported";
	} else {
	    ($ret, $out, $err) = runCommand("enscript --language=rtf --no-header --quiet --output=$TMP3 < $TMP2", $TMP2, $TMP3, "Converting to $format");
	}
    } elsif ($format eq 'ps') {
	if (($mode eq 'html') || ($mode eq 'htmlxslt')) {
	    my $TMP4 = setTempFile("$inputfn-4.pdf");
	    print "TMP3=$TMP3, TMP4=$TMP4\n" if $debug;
	    ($ret, $out, $err) = runCommand("etc/wkhtmltopdf-i386 --quiet $TMP2 $TMP4", $TMP2, $TMP4, "Converting to intermediate PDF");
	    print "wkhtmltopdf ret=$ret\n" if $debug;
	    print "out='$out'\n" if $debug;
	    print "err='$err'\n" if $debug;
	    userError("Conversion error to intermediate pdf", $err) if ($err ne '');
	    ($ret, $out, $err) = runCommand("pdf2ps $TMP4 $TMP3", $TMP4, $TMP3, "Converting to $format");
	} else {
	    ($ret, $out, $err) = runCommand("enscript $enscriptPsArguments --output=$TMP3 < $TMP2", $TMP2, $TMP3, "Converting to $format");
	}
    } elsif ($format eq 'epub') {
	if ($mode eq 'htmlxslt') {
	    print "TMP2=$TMP2, TMP3=$TMP3\n" if $debug;
	    ($ret, $out, $err) = runCommand("etc/xml2rfc-html2epub-viaxslt $TMP2 $TMP3", $TMP2, $TMP3, "Converting to $format");
	    if ($err !~ /error/i) {
		$out .= $err;
		$err = '';
	    }
	} else {
	    my $TMP4;
	    if ($mode eq 'html') {
		$TMP4 = $TMP2;
	    } else {
		$TMP4 = setTempFile("$TMP2.txt");
		print "TMP3=$TMP3, TMP4=$TMP4\n" if $debug;
		rename($TMP2, $TMP4);
	    }
	    getFileValues($TMP1);
	    $fileValues{"rfc/front/title"} =~ s/'/_/g;
	    $fileValues{"rfc/front/keyword"} =~ s/'/_/g;
	    $fileValues{authors} =~ s/'/_/g;
	    ($ret, $out, $err) = runCommand("ebook-convert $TMP4 $TMP3 " .
		# "--no-svg-cover " .
		"--no-default-epub-cover " .
		"--authors='" . untaint($fileValues{authors}) . "' " .
		"--title='" .  untaint($fileValues{"rfc/front/title"}) . "'" . 
		"--tags='" .  untaint($fileValues{"rfc/front/keyword"}) . "'", 
		$TMP4, $TMP3, "Converting to $format");
	}
    }

    print "conversion ret=$ret\n" if $debug;
    print "out='$out'\n" if $debug;
    print "err='$err'\n" if $debug;
    userError("Conversion error to $format", $err) if ($err ne '');
}


####### ########################### #######
####### # pass 4 - send back to browser
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
    catFile($TMP3);
} elsif ($type eq 'toframe') {
    my $TMPTRACE = "$inputfn-5.html";
    createFile($TMPTRACE, $trace, "<hr/>\n");

    # my $outputfn = getOutputName($input, $mode, $format);
    my $KEEP = keepTempFile($TMP3, "$inputfn-6." . getExtension($TMP3), $debug);
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
    catFile($TMP3);
}


####### ########################### #######
####### # all done
####### ########################### #######


cleanup();


####### ########################### #######
####### #### utility functions
####### ########################### #######


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
    print "runCommand($cmd)\n" if $debug;
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

    print "<h1>$event</h1>\n";
    print "<pre>$info</pre>\n";
    print "<hr/>\n";
    print $ENV{SERVER_SIGNATURE};
    print "</body></html>\n";
    cleanup();
    exit();
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
	if ($mode eq 'html') { return "text/html"; }
	if ($mode eq 'htmlxslt') { return "text/html"; }
	if ($mode eq 'xml') { return "text/xml"; }
	return "text/plain";	# nr, unpg
    } elsif ($format eq 'pdf') {
	return "application/pdf";
    } elsif ($format eq 'epub') {
	return "application/epub+zip";
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
        $smtp->datasend($q->param(input));
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
