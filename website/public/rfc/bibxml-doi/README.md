# bibxml7
Index.cgi in this directory will auto-generate DOI references in bibxml format.

http://xml2rfc.ietf.org/public/rfc/bibxml-doi/reference.DOI.10.1145/1355734.1355746.xml

The suffix determines whether xml or kramdown is generated.

The magic is performed by the doilit tool from kramdown.

# Some possible resources for DOI info:

# https://trac.tools.ietf.org/tools/xml2rfc/trac/ticket/326

# curl http://api.crossref.org/works/10.1145/1355734.1355746/transform/application/vnd.crossref.unixref+xml
#    <?xml version="1.0" encoding="UTF-8"?>
#    <doi_records>
#      <doi_record owner="10.1145" timestamp="2011-08-23 04:35:26">
#        <crossref>
#          <journal>
#            <journal_metadata language="en">
#              <full_title>ACM SIGCOMM Computer Communication Review</full_title>
#              <abbrev_title>SIGCOMM Comput. Commun. Rev.</abbrev_title>
#              <issn media_type="print">01464833</issn>
#            </journal_metadata>
#            <journal_issue>
#              <publication_date media_type="print">
#                <month>03</month>
#                <day>31</day>
#                <year>2008</year>
#              </publication_date>
#              <journal_volume>
#                <volume>38</volume>
#              </journal_volume>
#              <issue>2</issue>
#              <doi_data>
#                <doi>10.1145/1355734</doi>
#                <timestamp>20080401112845</timestamp>
#                <resource>http://portal.acm.org/citation.cfm?doid=1355734</resource>
#              </doi_data>
#            </journal_issue>
#            <journal_article publication_type="full_text">
#              <titles>
#                <title>OpenFlow</title>
#                <subtitle>enabling innovation in campus networks</subtitle>
#              </titles>
#              <contributors>
#                <person_name sequence="first" contributor_role="author">
#                  <given_name>Nick</given_name>
#                  <surname>McKeown</surname>
#                </person_name>
#                <person_name sequence="additional" contributor_role="author">
#                  <given_name>Tom</given_name>
#                  <surname>Anderson</surname>
#                </person_name>
#                <person_name sequence="additional" contributor_role="author">
#                  <given_name>Hari</given_name>
#                  <surname>Balakrishnan</surname>
#                </person_name>
#                <person_name sequence="additional" contributor_role="author">
#                  <given_name>Guru</given_name>
#                  <surname>Parulkar</surname>
#                </person_name>
#                <person_name sequence="additional" contributor_role="author">
#                  <given_name>Larry</given_name>
#                  <surname>Peterson</surname>
#                </person_name>
#                <person_name sequence="additional" contributor_role="author">
#                  <given_name>Jennifer</given_name>
#                  <surname>Rexford</surname>
#                </person_name>
#                <person_name sequence="additional" contributor_role="author">
#                  <given_name>Scott</given_name>
#                  <surname>Shenker</surname>
#                </person_name>
#                <person_name sequence="additional" contributor_role="author">
#                  <given_name>Jonathan</given_name>
#                  <surname>Turner</surname>
#                </person_name>
#              </contributors>
#              <publication_date media_type="print">
#                <month>03</month>
#                <day>31</day>
#                <year>2008</year>
#              </publication_date>
#              <pages>
#                <first_page>69</first_page>
#              </pages>
#              <doi_data>
#                <doi>10.1145/1355734.1355746</doi>
#                <timestamp>20080401112845</timestamp>
#                <resource>http://portal.acm.org/citation.cfm?doid=1355734.1355746</resource>
#              </doi_data>
#            </journal_article>
#          </journal>
#        </crossref>
#      </doi_record>
#    </doi_records>


# ACCEPT_CITE_JSON = {"Accept" => "application/citeproc+json"}
#  cite = JSON.parse(open("http://dx.doi.org/#{doi}", ACCEPT_CITE_JSON).read)
# curl -L -H "Accept: application/citeproc+json" http://dx.doi.org/10.1145/1355734.1355746
#    {
#        "indexed": {
#            "date-parts": [ [2015,12,26] ],
#            "date-time":"2015-12-26T12:01:12Z",
#            "timestamp":1451131272323
#        },
#        "reference-count":0,
#        "publisher":"Association for Computing Machinery (ACM)",
#        "issue":"2",
#        "published-print": {
#            "date-parts":[[2008,3,31]]
#        },
#        "DOI":"10.1145\/1355734.1355746",
#        "type":"journal-article",
#        "created":{
#            "date-parts":[[2008,4,1]],
#            "date-time":"2008-04-01T16:08:32Z",
#            "timestamp":1207066112000
#        },
#        "page":"69",
#        "source":"CrossRef",
#        "title":"OpenFlow",
#        "prefix":"http:\/\/id.crossref.org\/prefix\/10.1145",
#        "volume":"38",
#        "author":[ {
#                "affiliation":[],
#                "family":"McKeown",
#                "given":"Nick"
#            },{
#                "affiliation":[],
#                "family":"Anderson",
#                "given":"Tom"
#            },{
#                "affiliation":[],
#                "family":"Balakrishnan",
#                "given":"Hari"
#            },{
#                "affiliation":[],
#                "family":"Parulkar",
#                "given":"Guru"
#            },{
#                "affiliation":[],
#                "family":"Peterson",
#                "given":"Larry"
#            },{
#                "affiliation":[],
#                "family":"Rexford",
#                "given":"Jennifer"
#            },{
#                "affiliation":[],
#                "family":"Shenker",
#                "given":"Scott"
#            },{
#                "affiliation":[],
#                "family":"Turner",
#                "given":"Jonathan"
#            }],
#        "member":"http:\/\/id.crossref.org\/member\/320",
#        "container-title":"ACM SIGCOMM Computer Communication Review",
#        "deposited":{
#            "date-parts":[[2011,8,23]],
#            "date-time":"2011-08-23T08:35:26Z",
#            "timestamp":1314088526000
#        },
#        "score":1.0,
#        "subtitle":[
#            "enabling innovation in campus networks"
#        ],
#        "issued":{
#            "date-parts":[[2008,3,31]]
#        },
#        "URL":"http:\/\/dx.doi.org\/10.1145\/1355734.1355746",
#        "ISSN":["0146-4833"],
#        "subject":[
#            "Computer Networks and Communications",
#            "Software"
#        ]
#    }
