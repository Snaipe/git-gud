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
            if action not in MISC_HANDLERS:
                MISC_HANDLERS[action] = list()
            MISC_HANDLERS[action].append(func)
        return func
    return decorator

def _get_misc_handler_for_vb(vb):
    if vb.lemma_ in MISC_HANDLERS:
        return MISC_HANDLERS[vb.lemma_]

    from gitgud.nlp import nlp

    handlers = [(nlp(k)[0].similarity(vb), v) for k, v in MISC_HANDLERS.items()]
    handlers = sorted(handlers, reverse=True, key=lambda x: x[0])

    if not handlers:
        return [default_handler]

    sim, handler = handlers[0]
    return handler if sim > 0.65 else [default_handler]

def handle_misc(role):
    handlers = _get_misc_handler_for_vb(role.node)
    result = []
    for h in handlers:
        res = h(role)
        if res:
            result.append(res)
    return '\n\n'.join(result)

DEFINITIONS = dict()

def definition(*nouns):
    def decorator(func):
        for noun in nouns:
            if noun not in DEFINITIONS:
                DEFINITIONS[noun] = list()
            DEFINITIONS[noun].append(func)
        return func
    return decorator

def handle_define(role):
    defs = []
    for t in role.targets:
        for defn in DEFINITIONS[t.lemma_]:
            defs.append(defn(role))
    if not defs:
        return 'What do you want me to give you the meaning of?'
    return '\n\n'.join(defs)


