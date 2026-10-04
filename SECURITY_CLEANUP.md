# Applying the privacy fixes to an existing repository

The updated source loads credentials from the environment and no longer includes expense logs or generated Python cache files. These changes do not revoke an old password or erase previous Git commits.

## 1. Rotate the old database password locally

If the password previously committed to the repository was real, change it in your MySQL administrator tool. Change it anywhere else it was reused. Do not paste the old or new password into a chat, README, issue, or commit.

Configure the application with a separate local account and put its new password in the ignored `.env` file. The README includes the account setup.

## 2. Remove obsolete tracked files when applying the changes

The corrected snapshot excludes these paths:

- `backend/server.log`
- `backend/__pycache__/`
- `frontend/__pycache__/`
- `test/__pycache__/`
- `test/backend/__pycache__/`
- `.idea/`
- `.DS_Store`

Adding `.gitignore` alone does not remove files already tracked by Git. If copying the corrected files into an existing clone, delete the tracked copies of the paths above and commit those deletions together with the source changes.

## 3. Review earlier history

Old commits may still contain the credential, expense log entries, and cached copies of the old code. A normal cleanup commit does not erase that history. Rotate real credentials first. For removal from repository history, follow GitHub's documented sensitive-data cleanup process and coordinate with anyone using the repository before rewriting it:

https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

Do not assume that rewriting Git history deletes copies that other people already downloaded.
