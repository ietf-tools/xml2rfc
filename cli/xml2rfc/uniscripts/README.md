Simple Python 3 module to query Unicode UCD script metadata (see UAX #24).

This module is useful for querying if a text is made of Latin characters,
Arabic, hiragana, kanji (han), and so on.  It works for all scripts supported
by the Unicode character database.

This module is dumb and slow.  If you need speed, you probably want to
implement your own functions.  See e.g. `man pcreunicode`, `man pcrepattern`
(`grep -P` supports `\p`).  As of this writing, the next-generation of Python
regexpes, available as the pypi library `regex`, also supports `\p`.

Sample usage:

    >>> import uniscripts
    >>> uniscripts.is_script('A', 'Latin')
    True

    # if you pass it a string, all characters must match
    >>> uniscripts.is_script('はるはあけぼの', 'Hiragana')
    True

    >>> uniscripts.is_script('はるはAkebono', 'Hiragana')
    False

    # ...but by default, it ignores 'Common' characters, such as punctuation.
    >>> uniscripts.is_script('はるは:あけぼの', 'Hiragana')
    True

    >>> uniscripts.is_script('中華人民共和国', 'Han') # 'Han' = kanji or hànzì
    True

    >>> uniscripts.which_scripts('z')
    ['Latin']

    >>> uniscripts.which_scripts('は')
    ['Hiragana']

    >>> uniscripts.which_scripts('ー') # U+30FC
    ['Common', 'Katakana', 'Hiragana', 'Hangul', 'Han', 'Bopomofo', 'Yi']

See docstrings for `is_script()`, `which_scripts()`.
