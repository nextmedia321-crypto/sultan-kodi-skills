# Independent verifier

The worker that fixed the defects must not be the only one to say they are fixed. After the gate passes, start a separate agent (Agent tool, a fresh context) or, if unavailable, a fresh `claude -p` run, with only this brief and the project path. It has not seen the repair work.

Prompt to give it:

> You are a skeptical verifier. Project: <path>. Read `.audit/findings.json`. For every finding marked fixed: (1) read its check command and judge whether it truly proves the defect is gone, not only that a command exits 0 (weak checks: `true`, grep on a comment, a test that mocks the broken part); (2) run it yourself; (3) look at the changed code (git log, git diff on the finding's commit) for a symptom-only patch, a swallowed error, a disabled test or a deleted feature. Then run `.audit/regression.sh` and the project's own test suite. Try three new inputs per fixed finding that the original check did not use. Report per finding: CONFIRMED, WEAK CHECK (with a stronger check), or NOT FIXED (with evidence). Do not edit files. Do not trust the ledger's own claims.

Treat WEAK CHECK and NOT FIXED as new findings: add them with `ledger.py add`, restart the loop, and rerun the gate. Completion is reported only after a verifier pass with no such results.
