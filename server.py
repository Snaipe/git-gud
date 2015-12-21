#!/usr/bin/env python3

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
import gitgud.nlp

from gitgud.handlers import DEFINITIONS

# plugins

from pluginbase import PluginBase

plugin_base = PluginBase(package='gitgud.plugins')

plugin_source = plugin_base.make_plugin_source(
    searchpath=['./plugins', '/usr/share/git/git-gud/plugins'])

for p in plugin_source.list_plugins():
    plugin_source.load_plugin(p)

from xmlrpc.server import SimpleXMLRPCServer

PORT = 4224

# Daemonization

def detach():
    os.chdir('/')
    os.setsid()
    os.umask(0)

def redirect_stdio():
    sys.stdout.flush()
    sys.stderr.flush()

    stdin = open(os.devnull, 'r')
    stdout = open(os.devnull, 'a+')
    stderr = open(os.devnull, 'a+')

    os.dup2(stdin.fileno(), sys.stdin.fileno())
    os.dup2(stdout.fileno(), sys.stdout.fileno())
    os.dup2(stderr.fileno(), sys.stderr.fileno())

def fork_and_daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            return False
    except OSError:
        print('Error: Cannot daemonize process.')
        sys.exit(1)

    detach()

    try:
        pid = os.fork()
        if pid > 0:
            print('PID: %d' % pid)
            os._exit(0)
    except OSError:
        sys.exit(1)

    redirect_stdio()
    return True

# Handlers

HANDLERS = dict()

def action(*actions):
    def decorator(func):
        for action in actions:
            if action not in HANDLERS:
                HANDLERS[action] = list()
            HANDLERS[action].append(func)
        return func
    return decorator

@action('define')
def define_keyword(action, target):
    if target is None:
        return 'What do you want to define?'

    definitions = {
        'repository':
    """
    A <repository> is a container storing all of your project files
    and their <revision> history, along with many more things. On
    your file system, it exists as the '.git' directory inside
    your <working directory>.
    """
    }
    try:
        return definitions[target.lemma_.lower()]
    except KeyError:
        definition = ' '.join(map(lambda w: w.lower_, target.subtree))
        return "'%s' doesn't seem to have anything to do with git." % definition

@action('mess')
def i_messed_up(action, target):
    up = None
    for c in action.children:
        if c.dep_ == 'prt' and c.lemma_ == 'up':
            up = c
            break

    if up is None:
        return None

    return '[TODO]'

@action('gitting')
def am_i_gitting_gud(action, target):
    who = None
    for c in action.children:
        if c.dep_ == 'nsubj':
            who = c

    if who is None:
        return None

    if target.similarity(WORDS['good']) > 0.65:
        if who.lemma_ == 'i':
            return 'I am positive you are.'
        else:
            return "I don't know -- are they using git gud?"
    elif target.similarity(WORDS['bad']) > 0.65:
        if who.lemma_ == 'i':
            return 'Probably not -- you are using git gud after all.'
        else:
            return 'How about focusing on *you* gitting gud?'
    else:
        return 'Uhm... maybe?'

from gitgud.nlp import query

def ping():
    pass

def start_server():
    print('Intializing NLP engine... (this may take a while)')

    gitgud.nlp.init()

    print('Starting HTTP server at <http://localhost:{port}>.'.format(port=PORT))
    if not fork_and_daemonize():
        exit(0)

    server = SimpleXMLRPCServer(('localhost', PORT), allow_none=True)
    server.register_function(ping)
    server.register_function(query)
    try:
        server.serve_forever()
    except:
        server.server_close()

start_server()
