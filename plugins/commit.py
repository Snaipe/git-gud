from gitgud.handlers import action

@action(['fix', 'edit'], 'commit')
def fix_commit(role):
    return """\
        .. tip::
            Generally, it's best not to edit an existing commit if it
            has already been published, as it involves rewriting history.

        To *edit the last commit*, make use of ``git commit --amend``.

        To *edit an arbitrary commit*, commit your changes with ``git commit
        --fixup <hash>``, then squash them the original commit with ``git
        rebase -i --autosquash``.
        """

@action(['fix', 'edit'], 'message')
def fix_message(role):
    return ""
