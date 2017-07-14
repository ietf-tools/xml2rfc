#!/usr/bin/perl -T

use 5.014;
use strict;
use CGI;
use Cwd qw(chdir getcwd);
use HTML::Entities ();
use Net::SMTP;
use Digest::MD5 qw(md5 md5_hex);
use Crypt::RC4;
use HTTP::Request;
use LWP::UserAgent;

umask(02);
my $dir = untaint(getcwd());
my $q = CGI->new;
my $debug = $q->param('debug') ? 1 : undef;
my $frameDebug = $q->param('framedebug') ? 1 : 0;
my $trace = '';
my $sharedsecret = 'zzxoiuakjwefya%^&@#*(*(&@dflaskiouioiuklasfq';
my $salt = time();
my @filesToRemove;
my @dirsToRemove;
my %fileValues;

<<COMMENT;
########################### #######
 Process an id2xml conversion request

 invoking form has these fields:
	file "input" or "url"
	    contains the id2xml file
	radio button "type"
	    either ascii (output to window), toframe (separate warnings/output windows)
	    or binary (output to file)

########################## #######


invokes
    id2xml file.txt

COMMENT

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
my $type     = checkValue('type', 'ascii', 'binary', 'toframe', 'towindow', 'tofile');
if ($type eq 'ascii') {
    $type = 'towindow';
} elsif ($type eq 'binary') {
    $type = 'tofile';
}


printHeaders("text/plain") if $debug;
my $outputfn = getOutputName($input);
my $basename = $outputfn;
$basename =~ s/.[^.]*$//;
print "input='$input', inputfn='$inputfn', outputfn='$outputfn', basename='$basename'\n" if $debug;
print "type=$type\n" if $debug;
saveTracePass("Generating output", "h1");

####### ########################### #######
####### # pass 0 - environment
####### #	change directory
####### #	set environment variables
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

my $newinputfn = setSubTempFile("$basename.txt");
my $ret = rename($inputfn, $newinputfn);
print "rename($inputfn,$newinputfn) ret='$ret'\n" if $debug;
$ret = chmod 0666, $newinputfn;
# print "chmod 0666, $newinputfn: ret='$ret'\n" if $debug;
my $TMPERR = getTempFileWithSuffix("err");
my ($ret, $out, $err);


####### ########################### #######
####### # pass 1 - expand and check input
####### #	id2xml $inputfn
####### #		check for errors
####### ########################### #######
####### #
####### # Run id2xml to: expand internal references and includes.
####### #
####### ########################### #######

my $curfile = $newinputfn;

my $tmpout = callId2xml("xml");
$curfile = $tmpout;

print "at end of first pass, curfile=$curfile\n" if $debug;
# print "<!-- type=$type -->\n"; # if $debug;

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
    printHeaders(getContentType());
    catFile($curfile);
} elsif ($type eq 'toframe') {
    my $TMPTRACE = "$inputfn-5.html";
    # my $errorMessage = "<h2 style='color: red'>Errors exist</h2>";
    my $warningMessage = "<h2 style='color: orange'>Warnings exist</h2>";
    # my $errorsExist = ($trace =~ /error/i) ? $errorMessage : "";
    my $warningsExist = ($trace =~ /warning:/i) ? $warningMessage : "";
    createFile($TMPTRACE, $warningsExist, $trace, "<hr/>\n");

    # my $outputfn = getOutputName($input, $mode, $format);
    print "curfile=$curfile\n" if ($debug);
    my $KEEP = keepTempFile($curfile, "$inputfn-6." . getExtension($curfile), $debug);
    print "KEEP=$KEEP\n" if ($debug);
    printHeaders("text/html");
    print "<html><head><title>id2xml Processor with Warnings &amp; Errors</title></head>\n";
    my $rows = '25%,*'; # (($format eq 'ascii') && ($mode ne 'xml')) ? '25%,*' : '50%,*';
    print "<frameset rows='$rows'>\n";
    print "<frame src='cat.cgi?debug=$frameDebug&input=" . encryptFileName($TMPTRACE) . "'/>\n";
    print "<frame src='cat.cgi/$outputfn?debug=$frameDebug&input=" . encryptFileName($KEEP) . "'/>\n";
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

sub callId2xml {
    my $suffix = shift;
    my $tmpout = getTempFileWithSuffix($suffix);
    my ($ret, $out, $err) = runCommand("umask 0;/usr/local/bin/id2xml -o $tmpout $curfile", $curfile, $tmpout, "Running id2xml-rfc2629");
    $curfile = $tmpout;
    print "id2xml ret=$ret\n" if $debug;
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
    print " <span style='font-size: xx-small'>" . `uname -n` . "</span>";
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

####### return a proper content-type value
sub getContentType {
    return "application/xml";
}

####### create an output filename based on the mode
####### and format, based on the input filename
sub getOutputName {
    my ($outputfn, $mode, $format) = @_;
    $outputfn = basename($outputfn);
    $outputfn =~ s/\.txt$/.xml.txt/;
    $outputfn = untaint($outputfn, '([^<>\s;&]*)');
    return $outputfn;
}

####### mail an error message to the administrator
sub mail_error {
    my $inputF = shift;
    my $errorInfo = shift;
    try {
	my $smtp = Net::SMTP->new("localhost", Timeout => 60);
	$smtp->mail("webmaster\@tools.ietf.org");
	# $smtp->mail("tony\@att.com");
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
