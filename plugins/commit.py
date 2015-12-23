from gitgud.handlers import action

@action(['fix', 'edit'], 'commit')
def fix_commit(role):
    return "TIP: Generally, it's best to not edit an existing commit if it " \
        "has already been published, as it involves rewriting history.\n\n" \
        "To <edit the last commit>, make use of `git commit --amend`.\n\n" \
        "To <edit an arbitrary commit>, commit your changes with `git commit --fixup <hash>`, " \
        "then squash them the original commit with `git rebase -i --autosquash`."

