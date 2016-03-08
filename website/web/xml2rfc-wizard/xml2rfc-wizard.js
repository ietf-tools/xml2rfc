var RFCcount = 4;
var IDcount = 4;
var KEYWORDcount = 4;

var IntroPage = 1;
var TitlePage = 2;
var AuthorPage = 3;
var KeywordsAbstractPage = 4;
var RfcPage = 5;
var OptionPage = 6;
var FinalPage = 7;

function val(id)
{
    id = $(id);
    if (id != undefined) {
        return id.value.replace(/^[ \t]*/,'').replace(/[ \t]*$/,'');
    }
    return "";
}

function escapeHTML(v)
{
    if (v)
	return v.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g, "<br/>");
    return "";
}

function v(id, def)
{
    var ret = escapeHTML(val(id));
    if ((ret == '') && (def != undefined)) return def;
    return ret;
}

function av(id)
{
    alert("av(" + id + ")");
    id = $(id);
    if (id != undefined) {
        alert("found " + id + ", value='" + id.value + "'");
        return id.value.replace(/^[ \t]*/,'').replace(/[ \t]*$/,'');
    }
    return "";
}

function showAuthor(a)
{
    for (var i = 1; i <= 5; i++) {
        Element.hide("author" + i);
    }
    Element.show("author" + a);
}

function closeInstruction(str)
{
    Element.hide("info");
}

function showInstruction(str)
{
    $('innerinfo').innerHTML = str.replace(/__/g, "'");
    Element.show('info');
}

var curPage = 1;
var maxPage = 1;
function prevPage()
{
    updateXml();
    Element.hide("page" + curPage--);
    Element.show("page" + curPage);
}

function nextPage()
{
    closeInstruction();
    if (checkRequired()) {
	Element.hide("page" + curPage++);
	Element.show("page" + curPage);
	if (curPage > maxPage) maxPage = curPage;
    }
    updateXml();
}

function setPage(num)
{
    closeInstruction();
    for (var pageCnt = 1; pageCnt <= FinalPage; pageCnt++) {
	Element.hide("page" + pageCnt);
    }
    Element.show("page" + num);
    updateXml();
}

function checkRequiredValue(obj)
{
    obj = $(obj);
    if (v(obj) == '') {
	alert(obj.id + " is missing a required value");
	$(obj).focus();
	return 0;
    }
    return 1;
}

function checkRequiredValues(objs, fn)
{
    for (var i = 0; i < objs.length; i++) {
	var obj = objs[i];				  
	if (Element.hasClassName(obj, "required")) {
	    if (!checkRequiredValue(obj)) {
		if (fn != undefined) fn(obj);
		return 0;
	    }
	}
    }
    return 1;
}

function checkRequired()
{
    if (curPage == TitlePage) {
	if ((v('idtitle').length > 35) && !checkRequiredValue('idshorttitle'))
	    return 0;
	return checkRequiredValues($$(".page" + curPage));
    } else if (curPage == AuthorPage) {
	if (!checkRequiredValue('author1_fullname')) return 0;
	for (var authorCnt = 1; authorCnt <= 5; authorCnt++) {
	    if ((v('author' + authorCnt + '_fullname') != '') && 
		!checkRequiredValues($$(".author" + authorCnt + "_page3"), function(obj) {
			showAuthor(authorCnt);
			$(obj).focus();
		    })) {
		return 0;
	    }
	}
	return 1;
    } else {
	return checkRequiredValues($$(".page" + curPage));
    }
}

function prepRfcNum(str)
{
    if (str != undefined)
	return str.replace(/^rfc/i, '');
    return '';
}

function prepIdName(str)
{
    if (str != undefined)
	return str.replace(/^draft-/, '').replace(/\.txt$/, '');
    return '';
}

function fixDocName(str)
{
    if (str == '') return '';
    if (!str.match(/^draft-/)) str = "draft-" + str;
    str = str.replace(/[.]txt$/, '').replace(/[^a-z0-9.-]/i, '');
    if (!str.match(/-[0-9][0-9]$/)) str += "-00";
    return str;
}

function prepDocName(str)
{
    if (str == '') return 'unknown';
    return fixDocName(str);
}

function checkTitle()
{
    var title = v('idtitle');
    if (title.length > 35) Element.addClassName('required');
    else Element.removeClassName('required');
}

function checkDocName()
{
    var fn = $('filename');
    fn.value = fixDocName(fn.value);
}

// var alerted = 0;
function provisional(valname, tag, useEmpty)
{
    var tmp = v(valname);
    // if (alerted++ < 5) alert("provisional(" + valname + "," + tag + ")='" + tmp + "'");
    if ((tmp != '') || useEmpty) {
	return '      <' + tag + '>' + tmp + '</' + tag + '>\n';
    } else {
	return "<!-- <" + tag + "/> -->\n";
    }
}

function genXml()
{
    var o = "";
	
    if (maxPage > 1) {
	o += '<?xml version="1.0" encoding="US-ASCII"?>\n' +
	    '<!DOCTYPE rfc SYSTEM "rfc2629.dtd" [\n';
	if (maxPage >= RfcPage) {
	    for (var rfcCnt = 0; rfcCnt <= RFCcount; rfcCnt++) {
		var rfcnum = v('rfc' + rfcCnt);
		if (rfcnum != '') {
		    rfcnum = prepRfcNum(rfcnum);
		    o += '<!ENTITY RFC' + rfcnum + ' SYSTEM "http://xml.resource.org/public/rfc/bibxml/reference.RFC.' + rfcnum + '.xml">\n';
		}    
	    }
	    for (var idCnt = 1; idCnt <= IDcount; idCnt++) {
		var r = v('id' + idCnt);
		if (r != '') {
		    r = prepIdName(r);
		    o += '<!ENTITY I-D.' + r + ' SYSTEM "http://xml.resource.org/public/rfc/bibxml3/reference.I-D.' + r + '.xml">\n';
		}
	    }
	}
	o += "]>\n";
	o += '<?xml-stylesheet type="text/xsl" href="rfc2629.xslt" ?> <!-- used by XSLT processors -->\n';
	o += '<!-- OPTIONS, known as processing instructions (PIs) go here. -->\n';
	if (maxPage >= OptionPage) {
	    o += '<!-- For a complete list and description of PIs,\n';
	    o += '     please see http://xml.resource.org/authoring/README.html. -->\n';
	    o += '<!-- Below are generally applicable PIs that most I-Ds might want to use. -->\n';
	    o += '<?rfc strict="yes" ?> ';
	    o += '<!-- give errors regarding ID-nits and DTD validation -->\n';
	    o += '<!-- control the table of contents (ToC): -->\n';
	    o += '<?rfc toc="' + v('toc') + '"?> ';
	    o += '<!-- generate a ToC -->\n';
	    o += '<?rfc tocdepth="' + v('tocdepth') + '"?> ';
	    o += '<!-- the number of levels of subsections in ToC. default: 3 -->\n';
	    o += '<!-- control references: -->\n';
	    o += '<?rfc symrefs="' + v('symrefs') + '"?> ';
	    o += '<!-- use symbolic references tags, i.e, [RFC2119] instead of [1] -->\n';
	    o += '<?rfc sortrefs="' + v('sortrefs') + '" ?> ';
	    o += '<!-- sort the reference entries alphabetically -->\n';
	    o += '<!-- control vertical white space: \n';
	    o += '     (using these PIs as follows is recommended by the RFC Editor) -->\n';
	    o += '<?rfc compact="' + v('compact') + '" ?> ';
	    o += '<!-- do not start each main section on a new page -->\n';
	    o += '<?rfc subcompact="' + v('subcompact') + '" ?> ';
	    o += '<!-- keep one blank line between list items -->\n';
	    o += '<!-- end of popular PIs -->\n';
	}
	if (maxPage < TitlePage) {
	    o += '<!-- rfc will be defined here -->\n';
	} else {
	    o += '<rfc ' + 
		' category="' + v('category', 'unknown') + '"' +
		' docName="' + prepDocName(v('filename')) + '"' + 
		' ipr="' + v('ipr', 'unknown') + '"';
	    if (v('updates') != '') o += ' updates="' + v('updates') + '"';
	    if (v('obsoletes') != '') o += ' obsoletes="' + v('obsoletes') + '"';
	    o += '>\n';
	    o += '  <front>\n';
	    o += '    <title';
	    if (v('idshorttitle') != '')
		o += ' abbrev="' + v('idshorttitle') + '"';
	    o += '>' + v('idtitle') + '</title>\n';
	    if (maxPage < AuthorPage) {
		o += "<!-- author information will go here -->\n";
	    } else {
		for (var authorCnt = 1; authorCnt <= 5; authorCnt++) {
		    if (v('author' + authorCnt + '_fullname') != '') {
			o += '    <author' + 
			    ' fullname="' + v('author' + authorCnt + '_fullname', 'unknown') + '"' +
			    ' initials="' + v('author' + authorCnt + '_initials', 'unknown') + '"' +
			    ' surname="' + v('author' + authorCnt + '_surname', 'unknown') + '"';
			if (v('author' + authorCnt + '_editor') == 'yes') {
			    o += ' role="editor"';
			}
			o += '>\n';
			o += provisional('author' + authorCnt + '_organization', "organization");
			o += '      <address>\n';
			var postal = [ "street", "city", "region", "code", "country" ];
			var needPostal = 0;
			for (var postalCnt = 0; postalCnt < postal.length; postalCnt++) {
			    if (v('author' + authorCnt + '_' + postal[postalCnt]) != '') {
				needPostal = 1;
				break;
			    }
			}

			if (needPostal) {
			    o += '        <postal>\n';
			    o += provisional('author' + authorCnt + '_' + postal[0], postal[0], 1);
			    for (var postalCnt = 1; postalCnt < postal.length; postalCnt++) {
				o += provisional('author' + authorCnt + '_' + postal[postalCnt], postal[postalCnt]);
			    }
			    o += '        </postal>\n';
			} else {
			    o += '        <!-- postal><street/><city/><region/><code/><country/></postal -->\n';
			}
			o += provisional('author' + authorCnt + '_phone', 'phone');
			o += provisional('author' + authorCnt + '_facsimile', 'facsimile');
			o += provisional('author' + authorCnt + '_email', 'email');
			o += provisional('author' + authorCnt + '_uri', 'uri');
			o += '      </address>\n';
			o += '    </author>\n';
		    }
		}
	    }
	    
	    o += '    <date year="' + (new Date()).getFullYear() + '" />\n';
	    o += provisional('area', 'area');
	    o += provisional('workgroup', 'workgroup');
	    if (maxPage < KeywordsAbstractPage) {
		o += "<!-- abstract will go here -->\n";
	    } else {
		for (var keywordCnt = 1; keywordCnt <= KEYWORDcount; keywordCnt++) {
		    o += provisional('keyword' + keywordCnt, 'keyword');
		}

		o += '    <abstract>\n';
		o += '      <t>\n';
		o += v('abstract', 'not yet specified');
		o += '      </t>\n';
		o += '    </abstract>\n';
	    }
	    
	    o += '  </front>\n';
	    o += '  <middle>\n';
	    o += '    <section title="Introduction">\n';
	    o += '      <t>\n';
	    o += '        The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",\n';
	    o += '        "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in\n';
	    o += '        this document are to be interpreted as described in\n';
	    o += '        <xref target="RFC2119"/>.\n';
	    o += '      </t>\n';
	    o += '      <t>\n';
	    o += '        This document is being discussed on the xyz@example.org mailing list.\n';
	    o += '      </t>\n';
	    o += '      <t>\n';
	    o += '        Add some text here. You will need to use these references somewhere within the text:\n';
	    if (maxPage >= RfcPage) {
		for (var rfcCnt = 1; rfcCnt <= RFCcount; rfcCnt++) {
		    var r = v('rfc' + rfcCnt);
		    if (r != '') {
			o += '        <xref target="RFC' + prepRfcNum(r) + '"/>\n';
		    }    
		}
		for (var idCnt = 1; idCnt <= IDcount; idCnt++) {
		    var r = v('id' + idCnt);
		    if (r != '') {
			o += '        <xref target="I-D.' + prepIdName(r) + '"/>\n';
		    }
		}
	    }
	    o += '      </t>\n';
	    o += '    </section>\n';
	    o += '    <section anchor="Acknowledgements" title="Acknowledgements">\n';
	    o += '    </section>\n';
	    o += '    <section anchor="IANA" title="IANA Considerations">\n';
	    o += '    </section>\n';
	    o += '    <section anchor="Security" title="Security Considerations">\n';
	    o += '    </section>\n';
	    o += '  </middle>\n';
	    if (maxPage < RfcPage) {
		o += "<!-- references will go here -->\n";
	    } else {
		o += '  <back>\n';
		o += '    <references title="Normative References">\n';
		for (var rfcCnt = 0; rfcCnt <= RFCcount; rfcCnt++) {
		    var r = v('rfc' + rfcCnt);
		    if (r != '') {
			o += '      &RFC' + prepRfcNum(r) + ';\n';
		    }    
		}
		o += '    </references>\n';
		var hasID = 0;
		for (var idCnt = 1; idCnt <= IDcount; idCnt++) {
		    var r = v('id' + idCnt);
		    if (r != '') {
			hasID = 1;
		    }
		}
		if (hasID) {
		    o += '    <references title="Informative References">\n';
		    for (var idCnt = 1; idCnt <= IDcount; idCnt++) {
			var r = v('id' + idCnt);
			if (r != '') {
			    o += '      &I-D.' + prepIdName(r) + ';\n';
			}
		    }
		    o += '    </references>\n';
		}
		o += '  </back>\n';
	    }
	    o += '</rfc>\n';
	}
    }
    return o;
}

function updateXml()
{
    if (curPage > 1) {
	Element.show('outputouter');
	var g = genXml();
	$('output').innerHTML = escapeHTML(g);
    } else {
	Element.hide('outputouter');
    }
}

function updateAction()
{
    $('xml').value = genXml();
    var fn = fixDocName($('filename').value);
    
    var f = $('form');
    f.method = 'POST';
    f.action = "../cgi-bin/echoXml.cgi/" + fn + ".xml";
    f.submit();
}

function fillForm()
{
    $('idtitle').value = 'This is My Great New Protocol';
    $('category').value = 'info';
    $('filename').value = 'draft-abc-00';
    $('ipr').value = 'trust200902';
    $('author1_fullname').value = 'Joe Nobody';
    $('author1_initials').value = 'J.';
    $('author1_surname').value = 'Nobody';
    $('author1_email').value = 'abc@example.com';
    $('abstract').value = 'abc';
    maxPage = FinalPage;
    updateXml();
}
