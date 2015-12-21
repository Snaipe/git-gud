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

import sys
import os
import spacy.en
import traceback
import pprint

from enum import Enum
from . import handlers

nlp = None

WORDS = dict()

def init():
    global nlp
    if nlp is None:
        nlp = spacy.en.English()

    WORDS['want'] = nlp('want')[0]
    WORDS['good'] = nlp('good')[0]
    WORDS['bad']  = nlp('bad')[0]

    return nlp

def get_children(node, f):
    return filter(f, node.children)

def get_child(node, f):
    return next(filter(f, node.children))

def get_child_by_arc(node, arc):
    return get_child(node, lambda c: c.dep_ == arc)

def get_child_by_tag(node, tag):
    return get_child(node, lambda c: c.tag_ == tag)

## SRL

def classify_judgement(self, node):
    pass

def classify_define(self, node):
    def get_targets(node):
        tgs = [node]
        for c in node.children:
            if c.dep_ in {'dobj', 'conj', 'attr', 'acomp'}:
                tgs += get_targets(c)
        return tgs
    self.targets = get_targets(node)[1:]

def detect_define(node):
    if node.lemma_ == 'be':
        return get_child(node, lambda c: c.lower_ in {'what', 'who'}) is not None
    return node.lemma_ in {'define'}

def detect_locate(node):
    if node.lemma_ == 'be':
        return get_child(node, lambda c: c.lower_ in {'where'}) is not None

class SemanticFrame(Enum):
    JUDGEMENT = {
        'detect': lambda node: node.lemma_ in {'judge', 'blame', 'praise', 'appreciate', 'admire', 'like', 'dislike', 'love', 'hate'},
        'classify': classify_judgement,
        'handler': lambda x: None,
    }
    STATEMENT = {
        'detect': lambda node: node.lemma_ in {'say', 'tell'},
        'classify': lambda x, y: None,
        'handler': lambda x: None,
    }
    ACTION = {
        'detect': lambda node: node.lemma_ in {'do', 'undo', 'move', 'fix', 'delete', 'add', 'remove', 'change', 'modify', 'append', 'prepend', 'specify'},
        'classify': lambda x, y: None,
        'handler': lambda x: None,
    }
    DEFINE = {
        'detect': detect_define,
        'classify': classify_define,
        'handler': handlers.handle_define,
    }
    LOCATE = {
        'detect': detect_locate,
        'classify': lambda x, y: None,
        'handler': lambda x: None,
    }
    MISC = {
        'detect': lambda x: True,
        'classify': lambda x, y: None,
        'handler': handlers.handle_misc,
    }

_PINDENT = 0
def pretty_repr(self):
    global _PINDENT
    _PINDENT += 2
    out = pprint.pformat(vars(self), width=1, indent=_PINDENT)
    _PINDENT -= 2
    return out

class SemanticRole(object):
    def __init__(self, frame, node=None):
        self.frame = frame
        self.node = node
        self.subroles = dict()

    __repr__ = pretty_repr

def mean_similarity(w, wset):
    sim = 0
    for e in wset:
        sim += w.similarity(e)
    sim /= len(wset)
    return sim

def classify_verb(vb):
    for frame in SemanticFrame:
        if frame.value['detect'](vb):
            return frame
    return SemanticFrame.MISC

def classify_sentence(root):
    frame = classify_verb(root)
    role = SemanticRole(frame, root)
    frame.value['classify'](role, root)
    cld = get_children(root, lambda x: x.pos_ == 'VERB')
    for c in cld:
        role.subroles[c.lemma_] = classify_sentence(c)
    return role

def extract_action_and_target(node):
    if node.lower_ == 'help' or node.similarity(WORDS['want']) > 0.65:
        for c in node.children:
            if c.dep_ == 'ccomp':
                node = c
                break

    action = node
    target = None

    if node.lemma_ == 'be':
        a, t = None, None
        for c in node.children:
            if c.dep_ == 'nsubj' and c.lower_ == 'what':
                a = nlp('define')[0]
            if c.dep_ == 'attr':
                t = c
        if t is not None and a is not None:
            action, target = a, t

    if target is None:
        for c in node.children:
            if c.dep_ == 'dobj' or c.dep_ == 'advmod' or c.dep_ == 'acomp':
                target = c
                break

    return action, target

def default_handler(a, t):
    return "I'm sorry, I couldn't find anything to match what you asked me.\nMaybe try asking me something simpler?"

def get_handler_for_action(action):
    if action.lemma_ in HANDLERS:
        return HANDLERS[action.lemma_]

    handlers = [(nlp(k)[0].similarity(action), v) for k, v in HANDLERS.items()]

    sim, handler = sorted(handlers, reverse=True, key=lambda x: x[0])[0]
    return handler if sim > 0.65 else [default_handler]

ABBREVS = [
        ('repo', 'repository'),
        ('dir', 'directory'),
        ('gud', 'good'),
    ]

def query(q):
    if len(q.strip()) == 0:
        return ''

    try:
        words = map(lambda x: x.lower_, nlp.tokenizer(q))

        new_words = list()
        for n in words:
            for a, w in ABBREVS:
                if n == a:
                    n = w
            new_words.append(n)
        q = ' '.join(new_words)
        s = nlp(q)

        role = classify_sentence(s[:].root)
        pprint.pprint(role)

        response = role.frame.value['handler'](role)
        if response is None:
            return default_handler(None, None)
        return response
    except:
        traceback.print_exc(file=sys.stderr)

    return 'An error occured while processing your last query.'

