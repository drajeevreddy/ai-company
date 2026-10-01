# Credential and authority design

Rules worth applying to any system where several interests meet: a service credential, a human UI, and machines acting on someone's behalf. Each came from a design decision that was wrong the first time.

## 1. One credential, one blast radius

If a browser session holds the credential that can rewrite every record, then losing a session loses the system. Give each surface its own credential with the minimum it needs: a console credential that can **read**, held by a person, separate from a service token that can **write**, held by a service.

Corollary: when the user-facing credential is not configured, **refuse** rather than falling back to the powerful one. Fail closed, and make the error say which variable to set. An insecure default that "just works" is the thing that ships.

## 2. "Not yours" and "doesn't exist" should look the same

For any resource scoped to a tenant, user or employee, return **404 for someone else's record, not 403**. A 403 confirms the record exists, and existence is often the sensitive fact. Implement it by scoping the query, not by checking after fetching — a `WHERE owner = $1` that finds nothing cannot leak, and an `if (row.owner !== user)` that throws a different error can.

## 3. Default sharing to the narrow case

When a feature lets data cross a boundary (one person's work becoming visible to another), the default is **same-owner only**. Widening it is a deliberate configuration change that is written to the audit trail — not a flag someone flips because they did not read the docs.

Refuse a denied send explicitly (`scope_denied`), never drop it silently: a message that disappears is indistinguishable from a bug.

## 4. Audit at the action, not at the delivery

Write the audit row where the action is performed, never conditionally on whether a transport happened to be connected. "Audited if delivered" means the trail has holes exactly when delivery fails, which is when you most need it. One action, one row, on every path.

## 5. Anything that can create work must not be able to approve work

Structural, not prompt-level. If a planner (human delegate, script, or LLM) can raise work, it must not hold the approval capability — otherwise it can approve its own output and the gate is decoration.

For an LLM specifically:
- **No approval tool exists.** Assert its absence in a test so a later refactor cannot quietly add one.
- Work it creates goes through the *same* scoring and gating as work a human raises. It never raises an autonomy level.
- Hard budgets (per-run calls, per-run tokens, per-period cap). Exceeding one refuses the action **and still writes the audit row**.
- Its output is data. Validate it, then hand it to a fixed tool host. Never `eval`, never a shell, never an argv built from model text.
- Refuse actions reserved to humans (here: `urgent` priority) with an audited refusal, not a silent downgrade.

## 6. Dispatch must not depend on the optional component

If an advisory component (a model, a recommender, a third-party service) is down or unconfigured, the core flow continues. It degrades and logs; it never blocks. Test the disabled path explicitly: with no API key, the component is a **no-op that writes nothing**, and the primary path is unaffected.

## 7. Every blocked state needs a release valve

A circuit breaker that parks something automatically, with no way for a human to unpark it, is a one-way door. Ship the release route in the same change as the breaker: clear the failure count, set the status to something truthful ("not parked" is not the same as "connected"), and audit who did it and what the previous state was.

## 8. Rate-limit before authenticating

Put the limiter in front of the credential check so guessing costs the attacker something, and so a leaked token has a ceiling. Exempt liveness endpoints — a limiter that hides health checks turns one incident into two.

See also: [[Skills/security|security]] · [[Skills/software-development|software-development]] · [[Skills/verify-by-running-it|verify-by-running-it]]
