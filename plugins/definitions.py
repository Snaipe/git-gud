from gitgud.handlers import definition

@definition('repository')
def define_repo(role):
    return (
        "A <repository> is a container storing all of your project files "
        "and their <revision> history, along with many more things. On "
        "your file system, it exists as the '.git' directory inside "
        "your <working directory>.\n"
    )
