This directory contains a set of python scripts:

gen-bibxml-ieee-all -		run from ../gen-bibxml-all to execute all of the
				following programs:

gen-bibxml-ieee-get-update -	uses ftplib.FTP_TLS to grab the updates and store
				them into the updates directories
				(This script can also be used to create a brand new
				cache directory, should the need ever arise again.
				See the make target get-cache-do-not-use below for the
				proper options.)
gen-bibxml-ieee-apply-update -	is run with an update directory name, and applies
				the updates to the cache directory. (Deleted files
				are stored elsewhere in the cache in case something
				went awry needed to be recovered.)
gen-bibxml-ieee-gen-bibxml -	grabs whatever is in the cache/IEEEstd directory and
				applies it to the destination bibxml directory.

The following program from ../bibxml_common is also used:

generate-tarball-zipfile - shell script that grabs whatever is in a bibxml
				directory and creates the tgz and zip copies

See the makefile and gen-bibxml-ieee-all for how the programs can be unit tested and executed.
