from gitgud.handlers import misc
from gitgud.nlp import WORDS

@misc('gitting')
def am_i_gitting_gud(role):
    if role.targets and role.actors:
        who = role.actors[0]
        target = role.targets[0]

        if target.similarity(WORDS['good']) > 0.65:
            if who.lemma_ == 'i':
                return 'I am positive you are.'
            elif who.lemma_ == 'you':
                return 'I am the embodiment of gud.'
            else:
                return "I don't know -- are they using git gud?"
        elif target.similarity(WORDS['bad']) > 0.65:
            if who.lemma_ == 'i':
                return 'Probably not -- you are using git gud after all.'
            elif who.lemma_ == 'you':
                return 'I am the embodiment of gud.'
            else:
                return 'How about focusing on *you* gitting gud?'

    return 'Uhm... maybe?'
