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

from enum import Enum

def default_handler(role):
    return "I'm sorry, I couldn't find anything to match what you asked me.\nMaybe try asking me something simpler?"

MISC_HANDLERS = dict()

def misc(*actions):
    def decorator(func):
        for action in actions:
            if action not in HANDLERS:
                MISC_HANDLERS[action] = list()
            MISC_HANDLERS[action].append(func)
        return func
    return decorator

def _get_misc_handler_for_vb(vb):
    if vb.lemma_ in HANDLERS:
        return HANDLERS[vb.lemma_]

    handlers = [(nlp(k)[0].similarity(vb), v) for k, v in HANDLERS.items()]

    sim, handler = sorted(handlers, reverse=True, key=lambda x: x[0])[0]
    return handler if sim > 0.65 else [default_handler]

def handle_misc(role):
    handler = _get_misc_handler_for_vb(role.node)
    return handler(role)

DEFINITIONS = dict()

def definition(*nouns):
    def decorator(func):
        for noun in nouns:
            if noun not in HANDLERS:
                DEFINITIONS[noun] = list()
            DEFINITIONS[noun].append(func)
        return func
    return decorator

def handle_define(role):
    defs = []
    for t in role.targets:
        defs.append(DEFINITIONS[t.lemma_](role))
    if not defs:
        return 'What do you want me to give you the meaning of?'
    return '\n\n'.join(defs)
