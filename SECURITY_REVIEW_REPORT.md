# Security Review Report: Library Login Demo

**Intern:** Roopa S
**Date:** 20/12/2026
**Scope:** `insecure_demo.py`, a fictional local library-login sample. The review used source-code inspection only. No real system, account, website, or production data was accessed.

## Executive summary

The reviewed sample contains several high-risk patterns that would expose an application to unauthorized access and data disclosure if deployed. The accompanying `secure_app.py` demonstrates the recommended direction: parameterized queries, strong password hashing, generic authentication failures, input validation, and safe logging.

## Method

1. Read each function and traced how external input reaches the database and console output.
2. Checked authentication, database access, error handling, validation, and logging.
3. Rated findings by likely impact in a real deployment.
4. Implemented a safer local reference version and tested normal and unsafe-input cases.

## Findings

| ID | Severity | Issue | Evidence | Risk | Recommended remediation |
|---|---|---|---|---|---|
| F-01 | High | SQL injection | `login()` and `find_book()` build SQL with f-strings. | An attacker could alter a query or retrieve data they should not access. | Use parameterized statements with `?` placeholders. Allow-list input where practical. |
| F-02 | High | Plaintext password handling | The query compares a user-supplied password directly with a database column. | A database leak would expose reusable passwords. | Store a unique salt and a slow password hash such as PBKDF2, bcrypt, scrypt, or Argon2. Compare hashes using a constant-time function. |
| F-03 | Medium | Sensitive information in error output | Failed logins print the account name and password. | Screen logs, terminals, or monitoring records may expose credentials. | Return a generic login result. Never print or log passwords, tokens, or secrets. |
| F-04 | Medium | No input validation | The sample accepts any length or characters. | Oversized or malformed inputs add attack surface and make monitoring harder. | Validate type, length, and allowed characters before processing input. |
| F-05 | Medium | Missing authentication defenses | The sample has no rate limiting, lockout policy, or audit trail. | Automated password guessing could proceed without meaningful detection. | Add rate limits and monitored audit events in the real web or API layer. Avoid storing sensitive values in those events. |

## Safer implementation overview

`secure_app.py` addresses the review findings as follows:

- Uses SQLite parameter binding rather than string-built SQL.
- Stores PBKDF2-HMAC-SHA256 hashes with unique random salts.
- Uses `hmac.compare_digest` for password-hash comparison.
- Checks username format, password length, and book-search input.
- Uses generic authentication results and redacts sensitive values from logs.
- Uses context managers so database connections close correctly.

## Verification performed

| Check | Expected result | Result |
|---|---|---|
| Correct local demo credentials | Authentication succeeds. | Pass |
| Invalid credentials | Authentication fails without disclosing the password or account details. | Pass |
| Normal book search | Matching titles return. | Pass |
| SQL-like search text | Validation rejects the input before it reaches the query. | Pass |

## Residual considerations

This short local example intentionally omits a web interface, user registration, HTTPS configuration, session management, rate-limiting infrastructure, secret management, backups, and monitoring. A production application should add those controls and receive testing appropriate to its environment.

## Conclusion

The insecure sample should remain a review-only teaching artifact. The safer rewrite demonstrates the core coding controls required to reduce the identified risks.
