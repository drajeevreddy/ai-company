---
name: x402-agentic-payments
description: 'Use when building x402 paid endpoints or agent payments.'
---

# x402 Agentic Payments (Algorand)

Build order that works: verify the live payment path BEFORE writing product code.
Most x402 build failures are config (wrong ASA, wrong CAIP-2 string, missing opt-in),
not protocol bugs.

## 1. Verify live first (read-only, no wallets needed)

- POST/GET the protected endpoint, expect HTTP 402 with a `payment-required`
  header. Base64-decode it: confirm `scheme: exact`, TestNet CAIP-2 id, USDC ASA
  id, amount in micro-USDC, and `payTo`.
- GET the facilitator `/supported` endpoint and confirm the
  `exact` + TestNet-network combination is listed.
- Only then write client code. See `references/algorand-testnet-constants.md`
  for the verified constant values.

## 2. x402-avm signer contract (where builds actually break)

- `sign_transactions(unsigned_txns, indexes)` receives RAW msgpack bytes, not
  base64. Do NOT pass them through `encoding.msgpack_decode` (it base64-decodes
  first and dies with `msgpack.exceptions.ExtraData`). Decode with
  `msgpack.unpackb(raw, raw=False)` + `Transaction.undictify`, sign, and return
  RAW signed bytes - the SDK base64-encodes them itself.
- The settlement txid arrives in the retry response's `payment-response` (or
  `x-payment-response`) header as base64 JSON (`{"transaction": ...}`), NOT in
  the response body. Parse the header first, fall back to body fields.
- x402 payments are single-use: build a FRESH signed payload per attempt.
  Reused payloads are rejected as replays.

## 3. Guard before sign

Evaluate spend policy (blockedServices, allowedServices, maxPerRequest,
dailyBudget, requireApprovalAbove - first match wins) AFTER decoding the 402
price and BEFORE signing anything. Test every reject branch, not just ALLOW:
blocked service, non-allowlisted service, over-cap, over-budget, approval path.
Demo the BLOCK on camera - judges trust a guard they watch fire.

## 4. Wallet funding handoff

TestNet dispensers change auth rules often; treat human funding as a planned
handoff, not a failure. Automate everything around it: generate wallets,
submit ASA opt-ins for any wallet holding ALGO, move fee ALGO between your own
wallets, then hand the user exact addresses + faucet URLs and resume on
confirmation. Never request mainnet funds; never paste real mnemonics anywhere
but a 0600 `.env`.

## 5. Algorand ASA prerequisites (the #1 failure)

Every account must opt into the USDC ASA (zero-amount self-transfer) BEFORE it
can hold or receive USDC - faucet sends to non-opted accounts silently fail.
Accounts also need their own ALGO minimum balance even when the facilitator
covers fees. Provision order: fund ALGO, opt in, then fund USDC.
