# Security policy and repository hygiene

## Important: do not use this repository as-is with real accounts

The current repository history contains local SQLite database files under `data/`, including `users.db` and `data.db`, as well as a `data/current_user.txt` runtime file. These files should not be committed to a public source repository: database files may contain personal information, account records, or operational data.

The application code also contains a demo administrator credential (`admin` / `admin123`) and uses SHA-256 directly for password hashing. These are not suitable defaults for a production authentication system.

## Before deploying

1. Do not reuse any database or account data included in a repository checkout.
2. Remove local database and runtime files from version control after backing up any data that must be retained. Adding entries to `.gitignore` does not remove files that are already tracked.
3. If real credentials or personal information were ever committed, treat them as exposed: rotate affected credentials and assess whether the Git history also needs to be cleaned.
4. Replace demo credentials with a secure first-run administrator setup. Do not ship a known default password.
5. Replace plain SHA-256 password hashing with a password-hashing scheme designed for credentials, such as Argon2id, scrypt, or bcrypt, using a unique salt and appropriate work factor.
6. Keep API keys and other secrets in environment variables or a secrets manager; never commit them.

## Reporting a vulnerability

Please do not publish sensitive personal data, credentials, or exploit details in a public issue. Contact the repository owner privately with a concise description and reproduction steps.
