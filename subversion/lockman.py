import subprocess
import xml.etree.cElementTree as ET

repo = ""

def get_locks(repo_path):
    output = subprocess.check_output(["svn", "status", "--xml", "--show-updates", repo_path])
    tree = ET.fromstring(output)

    locks = {}
    for entry in tree.findall('target/entry'):
        lock = entry.find('repos-status/lock')
        if lock is not None:
            lock_owner = lock.find('owner').text
            path = entry.get('path')

            locks.setdefault(lock_owner, []).append(path)

    return locks

def print_locks(repo_path):
    users = get_locks(repo_path)
    for user in users.keys():
        print(f"User '{user}' has {len(users[user])} files locked:")

        for file in users[user]:
            print(f"    {file}")


print_locks("/home/yammyshep/repos/FA23-LandOfLights")