#!/usr/bin/env python3

import sys
import os
import spacy.en
import traceback

from xmlrpc.server import SimpleXMLRPCServer

PORT = 4224

nlp = None

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

# Server & NLP

WORDS = dict()

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

        action, target = extract_action_and_target(nlp(q)[:].root)

        handlers = get_handler_for_action(action)

        for handler in handlers:
            response = handler(action, target)
            if response is not None:
                break

        if response is None:
            return default_handler(action, target)
        return response
    except:
        traceback.print_exc(file=sys.stderr)

    return 'An error occured while processing your last query.'

def ping():
    pass

def start_server():
    print('Intializing NLP engine... (this may take a while)')

    global nlp
    if nlp is None:
        nlp = spacy.en.English()

    WORDS['want'] = nlp('want')[0]
    WORDS['good'] = nlp('good')[0]
    WORDS['bad']  = nlp('bad')[0]

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
