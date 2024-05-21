GITIGNORE = """
# Operating System Files
.DS_Store
Thumbs.db
desktop.ini

# IDE/Editor Files
.idea/
.vscode/
*.suo
*.ntvs*
*.njsproj
*.sln
*.swp
*~

# Build Output
node_modules/
dist/
build/
*.o
*.obj
*.class

# Dependency Directories
vendor/
jspm_packages/
typings/
*.jar
*.war

# Logs and Temporary Files
*.log
*.tmp
*.temp

# System Files
*.dll
*.exe
*.pdb
*.lib
*.so
*.dylib

# Configuration Files
.env
.DS_Store
.project
.classpath
.settings/

# IDE/Editor Specific
.idea/
.vscode/
*.sublime-project
*.sublime-workspace
*.idea/

# Miscellaneous
.dockerignore
.npmignore
.babelrc
.eslintrc
.gitattributes

# Custom Logs or Data Files
# Add any other file or directory specific to your project
"""

import os
import subprocess


def get_username():
    _result = subprocess.run(["gh", "auth", "status"], check=True, cwd=current_directory, capture_output=True,
                             text=True)
    first_index = _result.stdout.find("account") + len("account") + 1
    last_index = _result.stdout.find("(") - 1
    return _result.stdout[first_index:last_index]


# Get the current directory name
current_directory = os.getcwd()
directory_name = os.path.basename(current_directory)


def verify_directory_name(_directory_name):
    if " " in _directory_name:
        print("Invalid directory name.")
        print("Directory name should not contain any spaces.")
        print("Trying to fix it...")
        _directory_name = _directory_name.replace(" ", "-")
        print(f"Directory name: {_directory_name}")
        return _directory_name
    return _directory_name


repo_url = (f"https://github.com/{get_username()}/"
            f"{verify_directory_name(directory_name)}.git")

# Check if authorized user is logged in
try:
    _result = subprocess.run(["gh", "auth", "status"], check=True, cwd=current_directory, capture_output=True,
                             text=True)
    if not _result.stdout.find("Logged in to github.com account"):
        print("You are not logged in to GitHub.")
        print("Please log in and try again.")
        exit()
except subprocess.CalledProcessError:
    pass

# Check of existing .git
if not os.path.exists(".git"):
    subprocess.run(["git", "init"], cwd=current_directory)

# Check if .gitignore exists
if not os.path.exists("../.gitignore"):
    with open("../.gitignore", "w") as f:
        f.write(GITIGNORE)

# Create a repo on GitHub
try:
    subprocess.run(["gh", "repo", "create", directory_name, "--public"], cwd=current_directory)
except subprocess.CalledProcessError as e:
    try:
        subprocess.run(["gh", "repo", "create", f"{directory_name}_2", "--public"], cwd=current_directory)
    except:
        print(f"Failed to create repo on GitHub: {e}")
    # pass


def commit_and_push(_message):
    try:
        subprocess.run(["git", "add", "."], cwd=current_directory)
        subprocess.run(["git", "commit", "-m", _message], cwd=current_directory)
        subprocess.run(["git", "branch", "-M", "main"], cwd=current_directory)
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=current_directory)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=current_directory)
    except subprocess.CalledProcessError as e:
        print(f"Failed to commit and push: {e}")


# Commit and push
if __name__ == "__main__":
    print("Committing and pushing...")
    message = input("Enter commit message: {or go with the default message}")
    if message.strip() == "":
        message = "Initial commit"
    commit_and_push(message)
    print("[OK]")
    exit()
