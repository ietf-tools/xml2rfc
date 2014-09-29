#!/usr/bin/perl -T

use 5.014;
use strict;
use CGI;
use Cwd qw(chdir getcwd);
use HTML::Entities ();
use Net::SMTP;
use HTTP::Request;
use LWP::UserAgent;

umask(02);
my $dir = untaint(getcwd());
my $q = CGI->new;
my $trace = '';
my $debug = $q->param('debug') ? 1 : undef;
my $addComments = $q->param('addcomments') ? 1 : undef;
my $showRules = $q->param('showrules') ? 1 : undef;
my @filesToRemove;
my @dirsToRemove;

# set environment
$ENV{PATH} = "/usr/bin:/bin";
$ENV{DOCUMENT_ROOT} = 'web' if !defined($ENV{DOCUMENT_ROOT});
$ENV{SERVER_ADMIN} = 'tony@att.com';
# $ENV{HOME} = "/var/tmp";
# $ENV{HOME} = "/home/tonyh";
$ENV{LANG} = "en_US";

printHeaders("text/plain") if $debug;

my $input    = $q->param('input');
my $inputfn  = untaint($q->tmpFileName($input));
my $url = $q->param('url');
print "input='$input', inputfn='$inputfn'\n" if $debug;
print "addComments='$addComments'\n" if $debug;
print "showRules='$showRules'\n" if $debug;

if (($input eq '') || ($inputfn eq '')) {
    userError("No input file") if ($url eq '');
    my ($content, $err) = wget($url);
    userError($err) if ($err ne '');
    $inputfn = "/tmp/CGItemp$$.txt";
    createFile($inputfn, $content);
}
print `ls -l $inputfn` if $debug;
my $inputfndir = "$inputfn.dir";

my $outputfn = getOutputName($input);
my $basename = $outputfn;
$basename =~ s/.[^.]*$//;
print "input='$input', inputfn='$inputfn', outputfn='$outputfn', basename='$basename'\n" if $debug;

my $TMPERR = getTempFileWithSuffix("err");
my ($ret, $out, $err);

my $TMP2 = getTempFileWithSuffix("txt");
my $noCommentsFlag = $addComments ? "" : "-C";
my $showRulesFlag = $showRules ? "-#" : "";
my ($ret, $out, $err) = runCommand("./convertv2v3 $noCommentsFlag $showRulesFlag < $inputfn", $inputfn, $TMP2, "Calling convertv2v3");

printHeaders("text/plain");
print $out;
print "================\n$err" if ($err ne '');

####### ########################### #######
####### # all done
####### ########################### #######

cleanup();
exit;

####### ########################### #######
####### #### utility functions
####### ########################### #######

####### create an output filename based on the mode
####### and format, based on the input filename
sub getOutputName {
    my $outputfn = shift;
    $outputfn = basename($outputfn);
    $outputfn =~ s/\.xml$//;	# remove trailing .xml
    $outputfn = untaint($outputfn, '([^<>\s;&]*)');
    $outputfn .= ".xml";		# add in a new extension
    return $outputfn;
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

####### use a given pattern to untaint a value
####### default to the entire value
sub untaint {
    my $str = shift;
    my $pat = shift;
    $pat = "(.*)" if !defined($pat);
    return $1 if ($str =~ /$pat/);
    return undef;
}

####### create a new temp file with a given suffix
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

####### save an external command's standard output,
####### standard error, error code for later printing
sub saveTrace {
    # return if $type ne 'toframe';
    my ($ret, $out, $err) = @_;
    $out =~ s(/var/tmp/|/tmp/)()gm;
    $err =~ s(/var/tmp/|/tmp/)()gm;
    $trace .= "<hr/><pre>\n" .  HTML::Entities::encode($out) . "</pre>\n" if ($out ne '');
    $trace .= "<hr/><pre>\n" .  HTML::Entities::encode($err) . "</pre>\n" if ($err ne '');
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

####### return all but the final path segment of a filename
sub dirname {
    my $fn = shift;
    $fn =~ s/\\/\//g;
    return "." if ($fn !~ /\//);
    $fn =~ s/\/[^\/]*$//;
    return $fn;
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

####### save an external command's pass name in the trace
####### for later printing
sub saveTracePass {
    my $pass = shift;
    my $h = shift;
    $h = 'h2' if $h eq '';
    # return if $type ne 'toframe';
    $trace .= "<$h>$pass</$h>\n";
}

####### retrieve the contents of a document at a given URI
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
