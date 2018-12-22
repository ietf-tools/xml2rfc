# Copyright The IETF Trust 2017, All Rights Reserved
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

# The following text entries, derived from RFC 7841, were taken from
# https://www.rfc-editor.org/materials/status-memos.txt on 01 Feb 2018

boilerplate_rfc_status_of_memo = {
    'IETF': {
        'std': {
            'true' : ["""
            This is an Internet Standards Track document.
            """,

            """
            This document is a product of the Internet Engineering Task Force
            (IETF).  It represents the consensus of the IETF community.  It has
            received public review and has been approved for publication by
            the Internet Engineering Steering Group (IESG).  Further
            information on Internet Standards is available in Section 2 of 
            RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
        'bcp': {
            'true' : [ """
            This memo documents an Internet Best Current Practice.
            """,

            """
            This document is a product of the Internet Engineering Task Force
            (IETF).  It represents the consensus of the IETF community.  It has
            received public review and has been approved for publication by
            the Internet Engineering Steering Group (IESG).  Further information
            on BCPs is available in Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
        'exp': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for examination, experimental implementation, and
            evaluation.
            """,

            """
            This document defines an Experimental Protocol for the Internet
            community.  This document is a product of the Internet Engineering
            Task Force (IETF).  It represents the consensus of the IETF community.
            It has received public review and has been approved for publication
            by the Internet Engineering Steering Group (IESG).  Not all documents
            approved by the IESG are candidates for any level of Internet
            Standard; see Section 2 of RFC 7841. 
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for examination, experimental implementation, and
            evaluation.
            """,

            """
            This document defines an Experimental Protocol for the Internet
            community.  This document is a product of the Internet Engineering
            Task Force (IETF).  It has been approved for publication by the
            Internet Engineering Steering Group (IESG).  Not all documents
            approved by the IESG are candidates for any level of Internet
            Standard; see Section 2 of RFC 7841. 
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
        'historic': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet
            community.  This document is a product of the Internet Engineering
            Task Force (IETF).  It represents the consensus of the IETF community.
            It has received public review and has been approved for publication by
            the Internet Engineering Steering Group (IESG).  Not all documents
            approved by the IESG are candidates for any level of Internet
            Standard; see Section 2 of RFC 7841. 
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet
            community.  This document is a product of the Internet Engineering Task Force
            (IETF).  It has been approved for publication by the Internet
            Engineering Steering Group (IESG).  Not all documents approved by the
            IESG are candidates for any level of Internet Standard; see Section 2
            of RFC 7841. 
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
        'info': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.  
            """,

            """
            This document is a product of the Internet Engineering Task Force
            (IETF).  It represents the consensus of the IETF community.  It has
            received public review and has been approved for publication by the
            Internet Engineering Steering Group (IESG).  Not all documents
            approved by the IESG are candidates for any level of Internet
            Standard; see Section 2 of RFC 7841. 
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.  
            """,

            """
            This document is a product of the Internet Engineering Task Force
            (IETF).  It has been approved for publication by the Internet
            Engineering Steering Group (IESG).  Not all documents approved by the
            IESG are candidates for any level of Internet Standard; see Section 2
            of RFC 7841.   
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
    },
    'IAB': {
        'historic': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet
            community.  This document is a product of the Internet Architecture
            Board (IAB) and represents information that the IAB has deemed
            valuable to provide for permanent record.  It represents the consensus of the
            Internet Architecture Board (IAB).  Documents approved for
            publication by the IAB are not candidates for any level of Internet
            Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet
            community.  This document is a product of the Internet Architecture
            Board (IAB) and represents information that the IAB has deemed
            valuable to provide for permanent record.  Documents approved for
            publication by the IAB are not candidates for any level of Internet
            Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
        'info': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.  
            """,

            """
            This document is a product of the Internet Architecture Board
            (IAB) and represents information that the IAB has deemed valuable
            to provide for permanent record.  It represents the consensus of the Internet
            Architecture Board (IAB).  Documents approved for publication
            by the IAB are not candidates for any level of Internet Standard; see
            Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.
            """,

            """
            This document is a product of the Internet Architecture Board
            (IAB) and represents information that the IAB has deemed valuable
            to provide for permanent record.  Documents approved for publication
            by the IAB are not candidates for any level of Internet Standard; see
            Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
    },
    'IRTF': {
        'exp': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for examination, experimental implementation, and
            evaluation. 
            """,

            """
            This document defines an Experimental Protocol for the Internet
            community.  This document is a product of the Internet Research
            Task Force (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  This RFC represents the consensus of the
            {group_name} Research Group of the Internet Research Task Force
            (IRTF).  Documents approved for publication by the IRSG are not a
            candidate for any level of Internet Standard; see Section 2 of RFC
            7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for examination, experimental implementation, and
            evaluation.
            """,

            """
            This document defines an Experimental Protocol for the Internet
            community.  This document is a product of the Internet Research Task
            Force (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  This RFC represents the individual
            opinion(s) of one or more members of the {group_name} Research Group
            of the Internet Research Task Force (IRTF).  Documents approved for
            publication by the IRSG are not candidates for any level of Internet
            Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'n/a': [ """
            This document is not an Internet Standards Track specification; it is
            published for examination, experimental implementation, and
            evaluation.
            """,

            """
            This document defines an Experimental Protocol for the Internet
            community.  This document is a product of the Internet Research
            Task Force (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  Documents approved for publication by the
            IRSG are not candidates for any level of Internet Standard; see
            Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
        'historic': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet
            community.  This document is a product of the Internet Research Task Force
            (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  This RFC represents the consensus of
            the {group_name} Research Group of the Internet Research Task Force (IRTF).
            Documents approved for publication by the IRSG are not a candidate for
            any level of Internet Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet community.
            This document is a product of the Internet Research Task Force
            (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  This RFC represents the individual opinion(s) of one or more
            members of the {group_name} Research Group of the Internet
            Research Task Force (IRTF).  Documents approved for
            publication by the IRSG are not a candidate for
            any level of Internet Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'n/a': [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet
            community.  This document is a product of the Internet Research
            Task Force (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  Documents approved for publication by the
            IRSG are not candidates for any level of Internet Standard; see
            Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
        'info': {
            'true' : [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.  
            """,

            """
            This document is a product of the Internet Research Task Force
            (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  This RFC represents the consensus of the {group_name}
            Research Group of the Internet Research Task Force (IRTF).
            Documents approved for publication by the IRSG are not a
            candidate for any level of Internet Standard; see Section 2 of RFC
            7841.   
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.  
            """,

            """
            This document is a product of the Internet Research Task Force
            (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  This RFC represents the individual opinion(s) of one or more
            members of the {group_name} Research Group of the Internet
            Research Task Force (IRTF).  Documents approved for publication by the IRSG are not a
            candidate for any level of Internet Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'n/a': [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.
            """,

            """
            This document is a product of the Internet Research Task Force
            (IRTF).  The IRTF publishes the results of Internet-related
            research and development activities.  These results might not be
            suitable for deployment.  Documents approved for publication by the
            IRSG are not candidates for any level of Internet Standard; see
            Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
    },
    'independent': {
        'exp': {
            'n/a' : [ """
            This document is not an Internet Standards Track specification; it is
            published for examination, experimental implementation, and
            evaluation.
            """,

            """
            This document defines an Experimental Protocol for the Internet
            community.  This is a contribution to the RFC Series,
            independently of any other RFC stream.  The RFC Editor has chosen to publish this
            document at its discretion and makes no statement about its value
            for implementation or deployment.  Documents approved for publication
            by the RFC Editor are not candidates for any level of Internet
            Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            """
            ,
            ],
        },
        'historic': {
            'n/a' : [ """
            This document is not an Internet Standards Track specification; it is
            published for the historical record.
            """,

            """
            This document defines a Historic Document for the Internet
            community.  This is a contribution to the RFC Series, independently of any
            other RFC stream.  The RFC Editor has chosen to publish this
            document at its discretion and makes no statement about its value
            for implementation or deployment.  Documents approved for
            publication by the RFC Editor are not candidates for any level of
            Internet Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
            'false': [ """
            """
            ,
            ],
        },
        'info': {
            'n/a' : [ """
            This document is not an Internet Standards Track specification; it is
            published for informational purposes.
            """,

            """
            This is a contribution to the RFC Series, independently of any
            other RFC stream.  The RFC Editor has chosen to publish this
            document at its discretion and makes no statement about its value
            for implementation or deployment.  Documents approved for
            publication by the RFC Editor are not candidates for any level of
            Internet Standard; see Section 2 of RFC 7841.
            """,

            """
            Information about the current status of this document, any
            errata, and how to provide feedback on it may be obtained at
            {scheme}://www.rfc-editor.org/info/rfc{rfc_number}.
            """
            ,
            ],
        },
    },
}