# Algorand TestNet constants for x402 (verified live, Sep 2026)

Probed directly against the kit backend and GoPlausible facilitator.
Re-verify with a live 402 decode if a build behaves oddly - constants drift.

- Network (CAIP-2 TestNet): `algorand:SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=`
- Network (CAIP-2 Mainnet): `algorand:wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8=`
- USDC ASA (TestNet): `10458941`, 6 decimals ($0.01 = 10000 micro-USDC)
- USDC ASA (Mainnet): `31566704`
- Facilitator: `https://facilitator.goplausible.xyz` (`/supported` lists
  exact/TestNet and exact/Mainnet)
- Kit demo backend: `https://x402-builder-kit.vercel.app`
  - POST `/api/x402/summarize` -> $0.01 (10000)
  - GET `/api/x402/market-data` -> $0.005 (5000)
  - POST `/api/x402/news-summary` -> $0.01 (10000), body `{"topic": ...}`
  - POST `/api/x402/report-generate` -> $0.02 (20000),
    body `{"market_snippet": ..., "news_snippet": ...}`
- Faucets: ALGO `https://lora.algokit.io/testnet/fund`, USDC
  `https://faucet.circle.com` (select Algorand TestNet)
- Explorer: `https://lora.algokit.io/testnet/tx/<txid>`
- Python SDK: `x402-avm` (import from `x402.*`), plus `py-algorand-sdk`,
  `msgpack`, `python-dotenv`. TestNet algod: `https://testnet-api.algonode.cloud`.
