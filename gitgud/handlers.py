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

class HandlerBase(object):
    def __init__(self):
        self._handlers = dict()

    def _decorator(self, *nodes):
        def decorator(func):
            for node in nodes:
                if node not in self._handlers:
                    self._handlers[node] = list()
                self._handlers[node].append(func)
            return func
        return decorator

    @property
    def decorator(self):
        return self._decorator

    def handler(self, role):
        pass

class VerbHandler(HandlerBase):

    def __get_handlers(self, vb):
        if vb.lemma_ in self._handlers:
            return self._handlers[vb.lemma_]

        from gitgud.nlp import nlp

        handlers = [(nlp(k)[0].similarity(vb), v) for k, v in self._handlers.items()]
        handlers = sorted(handlers, reverse=True, key=lambda x: x[0])

        if not handlers:
            return [default_handler]

        sim, handler = handlers[0]
        return handler if sim > 0.65 else [default_handler]

    def handler(self, role):
        handlers = self.__get_handlers(role.node)
        result = []
        for h in handlers:
            res = h(role)
            if res:
                result.append(res)
        return '\n\n'.join(result)

class VerbSubjectHandler(HandlerBase):

    def _decorator(self, actions, *targets):
        def decorator(func):
            for action in actions:
                for target in targets:
                    if (action, target) not in self._handlers:
                        self._handlers[(action, target)] = list()
                    self._handlers[(action, target)].append(func)
            return func
        return decorator

    def __get_handlers(self, vb, target):
        if (vb.lemma_, target.lemma_) in self._handlers:
            return self._handlers[(vb.lemma_, target.lemma_)]

        from gitgud.nlp import nlp

        handlers = [(nlp(k[0])[0].similarity(vb), nlp(k[1])[0].similarity(target), v) for k, v in self._handlers.items()]
        handlers = sorted(handlers, reverse=True, key=lambda x: x[0] * 10 + x[1])

        if not handlers:
            return [default_handler]

        sim_vb, sim_tgt, handler = handlers[0]
        return handler if sim_vb > 0.65 and sim_tgt > 0.65 else [default_handler]

    def handler(self, role):
        if not role.targets:
            return None

        handlers = self.__get_handlers(role.node, role.targets[0])
        result = []
        for h in handlers:
            res = h(role)
            if res:
                result.append(res)
        return '\n\n'.join(result)

class DefinitionHandler(HandlerBase):

    def handler(self, role):
        defs = []
        for t in role.targets:
            if t.lemma_ not in self._handlers:
                defs.append('A `%s` does not seem to have anything to do with git.' % t.lemma_)
                continue
            for defn in self._handlers[t.lemma_]:
                defs.append(defn(role))
        if not defs:
            return 'What do you want me to give you the meaning of?'
        return '\n\n'.join(defs)

DEFINE  = DefinitionHandler()
ACTION  = VerbSubjectHandler()
MISC    = VerbHandler()

definition  = DEFINE.decorator
action      = ACTION.decorator
misc        = MISC.decorator
