# Security Policy

This is a teaching repository. Its code runs locally on the Python standard library, makes no network calls, and handles only the synthetic fixture data bundled in `fixtures/` (fictional leads and companies; no real personal data).

If you find a security issue in the course code (for example an unsafe default in the stand-in engine's file checkpointer, or a pattern a lesson teaches that would be unsafe if copied into production), please report it privately through the contact channels on the TechAura GitHub profile rather than opening a public issue. We will acknowledge reports within a few working days and credit reporters who wish to be named.

One standing warning, repeated from Lesson 20: state editing, time travel, and approval interrupts are powerful primitives. In a real deployment they belong behind authentication and audit, exactly as the lessons describe their checkpoint trails.
