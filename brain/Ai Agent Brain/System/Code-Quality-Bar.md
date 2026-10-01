# Code Quality Bar

Distilled from `clean-code` (Uncle Bob framework), `refactoring-patterns`, `test-driven-development`. Full references: `skill_view('clean-code')` + linked files under it. Goal: every change scores 10/10 below; leave code cleaner than found.

## Scoring
- 9–10: intent-revealing names, small focused functions, consistent errors, clean comprehensive tests.
- 7–8: mostly clean, minor ambiguities, a long function or two, thin edge cases.
- 5–6: good patterns beside duplication, unclear names, inconsistent handling.
- 3–4: multi-purpose long functions, misleading names, poor tests. 1–2: unreadable.

## The six disciplines
- Names reveal intent (`elapsedTimeInDays`, `isActive`, `calculateMonthlyRevenue`); no encodings, no Hungarian, one word per concept; rename freely.
- Functions: 4–6 lines ideal, ≤2 args, one abstraction level, step-down reading order. Flag args → split the function. Command-query separation: change state or return a value, never both. Guard clauses up top.
- Comments: a comment is a failure to express in code. Keep only the why (RFC, legal, genuine trap). Delete commented-out code — version control remembers. Newspaper layout: high-level first, details below.
- Errors: exceptions over return codes; never return or pass null (empty collection, Optional, Null Object); include operation + state in every message; wrap third-party APIs.
- Tests (F.I.R.S.T.: fast, independent, repeatable, self-validating, timely): one concept per test, `shouldRejectExpiredToken` names, builder helpers, mock time/network/fs. TDD three laws: failing test first, only enough to fail, only enough code to pass. No tests for reversible low-impact changes; never scaffold testing into a testless repo.
- Smells → targeted moves: duplication → extract; feature envy → move method to the data; magic numbers → named constants; dead code → delete; shotgun surgery → consolidate. Never refactor and add features in one diff.

## Quick diagnostic (any "no" = the action)
- Understandable without reading bodies? If no → rename.
- All functions under ~20 lines? If no → extract helpers.
- Zero commented-out blocks? If no → delete.
- Errors separate from happy path? If no → extract handlers.
- One responsibility per class? If no → split.
- Test per public method, descriptive names, duplication under 3 occurrences, constants named, suite under 10s?

## Traps
- Clever one-liners, abbreviated names, generic catch blocks, untested error paths, premature optimization, god classes, refactoring without a safety net, style drift (decide once, enforce with formatter/linter).
