import re
import subprocess
import xml.etree.cElementTree as ET
import os.path
from urllib.parse import urlparse


def get_repo_path():
    script_path = os.path.abspath(__file__)
    output = subprocess.check_output(["svn", "info", "--xml", script_path])
    entry = ET.fromstring(output).find('entry')
    return entry.find('wc-info/wcroot-abspath').text


def get_svn_user():
    script_path = os.path.abspath(__file__)
    output = subprocess.check_output(["svn", "info", "--xml", script_path])
    entry = ET.fromstring(output).find('entry')
    repo_url = entry.find('repository/root').text
    parsed = urlparse(repo_url)
    repo_server = f"{parsed.scheme}://{parsed.netloc}"

    output = str(subprocess.check_output(["svn", "auth"]))
    credentials = re.split("[\t\n\r]*-{10,}", output)
    for cred in credentials:
        if cred.find(f"Authentication realm: <{repo_server}") != -1:
            username = re.findall("(?<=Username: )[^\\\\s]*", cred)
            return username[0]

    return None


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


def unlock_files(repo_path=get_repo_path(), user=get_svn_user()):
    locks = get_locks(repo_path)

    if user not in locks:
        print(f"No files are locked in the repository by {user}.")
        return

    for lock in locks[user]:
        file_path = os.path.join(repo_path, lock)
        proc = subprocess.run(['svn', 'unlock', '--force', file_path])
        if proc.returncode != 0:
            print(f"Failed to unlock file: {lock}")


if __name__ == "__main__":
    unlock_files()
