# Subversion lock manager tool
#
# Lists locks currently held by users in an easy-to-read way

import os.path
import subprocess
import xml.etree.cElementTree as ET

def main():
    repo_path = get_repository()
    if not repo_path:
        print(f"Failed to get repository path! Exiting!")
        exit(1)

    running = True
    while running:
        running = prompt_user(repo_path)

    print("Goodbye!")

def get_locks(repo_path):
    print("Fetching locks from repository...")
    output = subprocess.check_output(["svn", "status", "--xml", "--show-updates", repo_path])
    tree = ET.fromstring(output)

    locks = {}
    for entry in tree.findall('target/entry'):
        lock = entry.find('repos-status/lock')
        if lock is not None:
            lock_owner = lock.find('owner').text
            path = entry.get('path')

            locks.setdefault(lock_owner, []).append(os.path.relpath(path, repo_path))

    return locks

def print_locks(repo_path):
    users = get_locks(repo_path)
    for user in users.keys():
        print(f"User '{user}' has {len(users[user])} files locked:")

        for file in users[user]:
            print(f"    {file}")
        
        print()

def input_repository():
    trynum = 0
    while trynum < 3:
        trynum += 1

        path = input("Enter repository path: ")
        if os.path.exists(path):
            proc = subprocess.run(['svn', 'info', '--xml', path], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if proc.returncode == 0:
                return path
            else:
                print(f"Failed to find subversion repository at {path}. Try using an absolute path.")
        else:
            print(f"{path} is not a valid path.")
    
    print(f"Failed to get repository path after {trynum} attempts. Aborting!")
    return None

def get_repository():
    #TODO: Check a config file before asking for input, and cache input
    return input_repository()

def unlock_by_user(repo_path):
    locks = get_locks(repo_path)

    print("Users:")
    users = []
    for i, user in enumerate(locks.keys()):
        print(f"{i}) {user}")
        users.insert(i, user)
    
    index = input("Enter number for user: ")
    username = users[int(index)]
    
    for lock in locks[username]:
        print(f"Unlocking {lock}...")
        if not unlock_file(os.path.join(repo_path, lock)):
            print(f"Failed to unlock {lock}")

def unlock_file(file_path):
    proc = subprocess.run(['svn', 'unlock', '--force', file_path])
    return proc.returncode == 0

def print_help():
    print("Lockman help:")
    print("    L) List locks")
    print("    U) Unlock by user")
    print("    Q) Quit")

def prompt_user(repo_path):
    print()

    action = input(f"Lockman action ({repo_path})> ").upper()[0]
    print()

    if action == 'H':
        print_help()
    elif action == 'L':
        print_locks(repo_path)
    elif action == 'U':
        unlock_by_user(repo_path)
    elif action == 'Q':
        return False
    elif action == "E":
        return False
    else:
        print(f"Action not recognized: {action}")

    return True


if __name__ == "__main__":
    main()
