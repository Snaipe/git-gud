"""
Copyright (C) 2015 Franklin "Snaipe" Mathieu <https://snai.pe>

This file is part of 'git gud'.

'git gud' is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

'git gud' is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with 'git gud'.  If not, see <http://www.gnu.org/licenses/>.
"""

ABBREVS = [
        ('repo', 'repository'),
        ('dir', 'directory'),
        ('gud', 'good'),
    ]

def substitute_abbreviations(sent):
    from gitgud.nlp import nlp

    words = map(lambda x: x.lower_, nlp.tokenizer(sent))

    new_words = list()
    for n in words:
        for a, w in ABBREVS:
            if n == a:
                n = w
        new_words.append(n)
    return ' '.join(new_words)
