from gitgud.handlers import definition

@definition('repository')
def define_repo(role):
    return """\
        A **repository** is a container storing all of your project files
        and their revision history, along with many more things.

        On your file system, it exists as the '.git' directory inside
        your working directory.
        """

@definition('object')
def define_object(role):
    return """\
        An **object** is the base component of everything that makes a repository up.

        Notable object kinds are commits, branches, or tags.
        """

@definition('commit')
def define_commit(role):
    return """\
        A **commit** is an object representing an individual change to a
        set of files, uniquely identified by a hexadecimal number named hash.

        Commits record information on the author, date, and nature of the
        changes, and acts as a node in the history tree.
        """

@definition('branch')
def define_branch(role):
    return """\
        A **branch** is an object representing a divergence in the history tree,
        and exist independently of other branches, making it an useful context
        to commit changes that are experimental, while keeping the `master`
        branch intact.

        ..
          A---B---C---D
               \\
                E---F
        """
