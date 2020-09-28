# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-

import magic

def get_file_mime_type(name):
    m = magic.Magic()
    m.cookie = magic.magic_open(magic.MAGIC_NONE | magic.MAGIC_MIME | magic.MAGIC_MIME_ENCODING)
    magic.magic_load(m.cookie, None)
    filetype = m.from_file(name)
    return filetype
