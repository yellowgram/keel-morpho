# Keel — Minimum-Ops Checklist (v3)

**Owner:** yellowgram (founder book)  
**Sleeve:** ETH Credit Conservative / Morpho V1 wstETH–WETH / Regime B / chain 1  
**Scope:** Design-only. What must be true so the strategy runs with **thin founder + agent attention** and a **safe DEMO → live** gate.  
**Product:** OSS self-run toolkit. **Still killed / not ops:** grants packaging-as-product, multi-user vault, kits/invoice sell, Soft-WTP, unattended outreach.  
**Income path:** P&L after exit DEMO — not observe vanity, not pack polish for buyers.  
**Standing truth today (2026-09-26 ET):** `DEMO_ONLY=true`, `VAULT_ADDRESS=null`, `ALLOW=[]`, Regime-B-eligible markets often **0**, recommendation **IDLE_ALL**. IDLE is success.

---

## (1) Final checklist v3

### A. Mandate lock & DEMO gate (no silent mandate drift)

1. **Single mandate hash pinned in three places** — `config.json.mandate_hash`, `mandate_hash.txt`, and every pack/log header must match. Mismatch → observe **aborts** (no pack overwrite that claims a different mandate). Hash change only via human-pasted B2+ amendment recorded in `AMENDMENTS[]`.
2. **DEMO_ONLY is a hard process gate, not a label** — while `DEMO_ONLY=true`: never sign, never load private keys into the observe process, never write a live ACTION line, never invent ALLOW rows, never set `VAULT_ADDRESS` from agent code. Pack must print `DEMO_ONLY: true` on every emit.
3. **Live-exit gate is an explicit human flip checklist (all required)** — before flipping `DEMO_ONLY→false`: (a) VAULT_ADDRESS set by human, (b) ≥1 ALLOW row pasted by human for an eligible market, (c) O1–O7 no longer systematically PARTIAL on the markets you will touch, (d) RPC health green for 3 consecutive weekday observes, (e) signed kill-switch drill completed once on paper then once dry-run against the vault with **zero size**, (f) size rules (§D) written into config and re-hashed. Missing any item → stay DEMO.
4. **Regime B filters are config-only** — LLTV ≤ 0.86 WAD, wstETH collateral only, `FORBIDDEN_COLLATERAL` + forbidden LLTV buckets enforced in observe. Agent may not loosen filters without a pasted amendment; risk-up blocked; risk-down (REDUCE/EXIT/IDLE) always allowed without ALLOW.

### B. Kill switch & human authority (who can stop money)

5. **Named kill switch with one-line semantics** — `KILL=true` (config or env) forces recommendation **IDLE_ALL**, freezes new ALLOCATE drafts, and (post-DEMO) requires human-signed EXIT/REDUCE path only. Agent may set KILL on EXIT-class O* trips; only human clears KILL.
6. **Human owns four levers; agent owns none of them** — ALLOW rows, ACTION line, any signature, B2+ amendments. Packs may draft REFERENCE_ONLY deallocate text; agent never auto-ALLOW, never auto-sign, never auto-raise size.
7. **P_WSTETH drill is mandatory ops, not folklore** — if O4 hits EXIT (wst deviation): freeze new; EXIT open allocations; IDLE until O4 PASS. Drill status must appear in every pack while any open allocation exists; while idle, pack still records `PASS_DRILL` / `SKIP_IDLE` so the path is exercised in logging.
8. **ACTION line is human-only and append-only** — live txs require a human-pasted ACTION with marketId, size, direction, and expected mandate_hash. Observe process refuses to invent or “complete” ACTION from recommendation alone.

### C. Observe cadence & attention budget (thin ops)

9. **Cadence: 1× weekday observe @ 08:00 America/New_York** — `keel_daily_observe_once.sh` only. No weekend auto unless KILL or open allocation WARN/EXIT. Quiet-if-IDLE: if recommendation + blockers + eligible set unchanged vs prior weekday, log one short line; do not treat re-observe as progress.
10. **Founder attention SLA (written)** — weekday: skim pack header + recommendation + blockers (≤5 min). Escalate only on: KILL set, any O*_EXIT, mandate mismatch, fetch hard-fail 2 days running, or DEMO-exit flip request. No daily deep-dive required while IDLE_ALL + DEMO.
11. **Agent attention SLA** — run observe, emit pack+log, flag PARTIAL checks, never chase income kits / targets.csv as Keel-ops work. Outreach/kit scripts are **out of the ops path** (killed commercial track).
12. **Missed-observe rule** — 1 miss: next run notes gap. 2 consecutive weekday misses with open allocation (post-DEMO): auto-set KILL warn in pack; human must ack. While DEMO+idle: miss is log-only, not pager.

### D. Size rules & book shape (capital discipline before live)

13. **Book size caps in config (human-set before live)** — `BOOK_NOTIONAL_CAP_WETH`, `PER_MARKET_CAP_WETH` (= min of absolute and `MARKET_REL_CAP`×book), `MAX_MARKETS_OPEN`. Defaults for first live sleeve: start tiny (human picks); agent never raises caps.
14. **MARKET_REL_CAP 0.25 enforced on any ALLOCATE draft** — relative market share of book ≤ 25%. Violating draft → refuse emit as ALLOCATE; fall back IDLE/REDUCE.
15. **No ALLOCATE without ALLOW ∩ PASS ∩ VAULT ∩ !DEMO_ONLY ∩ !KILL** — five-way AND. Empty ALLOW ⇒ IDLE_ALL always. Regime-B-eligible=0 ⇒ IDLE_ALL even if someone pasted ALLOW for an ineligible market (ALLOW for ineligible is poison — reject row at paste-check).
16. **EXIT liquidity preflight before any live EXIT/REDUCE** — O5 must run with `EXIT_LIQ_PCT` / `EXIT_LIQ_FLOOR_WETH`; if liquidity insufficient, pack says HOLD_EXIT_BLOCKED + human options (wait / partial / venue), never silent full exit assumption.
17. **Modeled outflow stress (O7) required before live size > dust** — `MODELED_OUTFLOW_PCT` over `MODELED_OUTFLOW_DAYS` must PASS on target market; else size stays at dust or IDLE.

### E. Data plane health (RPC / GraphQL / Llama)

18. **Triple-fetch status on every pack** — `graphql_ok`, `llama_ok`, `rpc_ok` with error strings. Pack STATUS: GREEN only if all needed checks runnable; AMBER if PARTIAL; RED if GraphQL hard-fail or mandate mismatch.
19. **RPC is not optional for live; it is optional for DEMO idle** — today public RPC 403 is acceptable under DEMO+idle (O4 PARTIAL). **Live gate requires** a working RPC (or authenticated provider) that can read `stEthPerToken` + block for O3/O4. Document the provider name in pack; do not pretend Llama alone covers O4.
20. **Staleness gate `STALE_S=900`** — market state older than STALE_S → O6 FAIL → no PASS score → no ALLOCATE. WARN path still allows IDLE/HOLD.
21. **Secondary oracle / wst cross-check wired before live** — O3 (oracle bps/time) and O4 (wst vs Llama secondary) must be non-PARTIAL on markets with open size. PARTIAL on those checks with open size → treat as WARN at minimum; EXIT thresholds still fire when data exists.
22. **Fetch hard-fail behavior** — GraphQL down: emit last-known pack marked HOLD/STALE if file exists, append log error, do not invent markets. Never clear ALLOW or flip DEMO on fetch failure.

### F. Logging, pack integrity, audit trail

23. **Pack mandatory sections every run** — timestamp (UTC + America/New_York), mandate_hash, DEMO_ONLY, REGIME, vault/allow/amendments, prices, **full wstETH–WETH market table** (uniqueKey/lltv/eligible/ineligible_reason/util/APYs/oracle), O1–O7 scoreboard with PARTIAL flags, recommendation, blockers, next human actions, log append.
24. **Append-only `log.md`** — one entry per observe; no rewrite of history. Include fetch booleans, eligible set, recommendation, blockers, drill status.
25. **ALLOW paste-check** — format `ALLOW | date | uniqueKey | lltv_wad | collateral | oracle | cap_rel | why`. Reject if collateral ≠ wstETH, lltv above Regime B max, uniqueKey not in latest market table, or cap_rel > MARKET_REL_CAP.
26. **Config / brief drift check** — observe refuses to run if `BRIEF_v1.1.md` missing or `config.json` unreadable; STATUS must say brief present. Thresholds live only in config — no shadow constants in ops docs that disagree (script may keep forbidden-bucket set but must match brief narrative).

### G. DEMO → live runbook (minimum path, no theater)

27. **Paper sleeve first** — REFERENCE_BOOK_ID + REFERENCE_UNITS continue through ≥5 consecutive weekday GREEN/AMBER observes with stable IDLE or (if eligible appears) scored PASS without allocating.
28. **Dust live sleeve** — human sets VAULT, pastes one ALLOW for a true Regime-B-eligible market, flips DEMO only after §A.3, size ≤ `DUST_CAP_WETH` (human-set). One allocate + one full exit cycle before any size-up amendment.
29. **Size-up only by amendment** — each increase is a dated amendment with new caps; no agent “scale into yield.”
30. **Rollback** — human can re-set `DEMO_ONLY=true` anytime; open live size must still follow EXIT path (DEMO flag does not abandon positions). Pack must show both flags if that state occurs (`DEMO_ONLY=true` with non-zero live) as **INCONSISTENT — EXIT PRIORITY**.

### H. What is explicitly NOT ops work (kill list)

31. **Killed tracks stay killed** — client kits, invoice/pilot outreach, targets.csv send math, grant/OSS packaging are not Keel minimum-ops. Do not schedule them on the observe cadence.
32. **No multi-user / vault-product surface** — no share class, no depositor UX, no public status page. Founder book only.
33. **No BMNR/BMNU/CoinDCX pricing or allocation** — out of sleeve; pack must never include them as positions.

---

## (2) Delta log (v0 → v1 → v2 → v3)

### v0 — thin seed (pre-adversarial)

Observe cadence · mandate hash · kill switch · size rules · RPC health · logging · DEMO gate · exit criteria.

### Iteration 1 — Adversarial expert A (security / ops) → v1

**Attack thesis:** DEMO_ONLY as a sticker + agent-writable vault/ALLOW + unsigned “recommendations that feel like orders” is how a thin book loses funds. Public RPC 403 already proves O4 is hollow; going live on Llama-only is false safety. Kill switch that only humans can set (but agents can’t trip) fails under EXIT events when founder is AFK.

| Change | Rationale |
| --- | --- |
| DEMO_ONLY as **process gate** (no keys, no ACTION invent, no auto-ALLOW) | Label-only DEMO is theater |
| Mandate hash **triple-pin + abort on mismatch** | Silent brief/config drift is a classic ops footgun |
| Agent may **set** KILL on EXIT-class trips; only human clears | Founder AFK during O4 EXIT |
| ALLOW paste-check (collateral/lltv/uniqueKey/cap) | Poison ALLOW rows become “authorized” loss |
| RPC required for live; DEMO+idle may tolerate rpc_ok=false | Matches today’s 403 reality without lying about O4 |
| ACTION line human-only, append-only | Stops observe→sign confusion |
| P_WSTETH drill required in pack path | Brief already defines it; ops must exercise it |
| Live-exit gate as multi-item human checklist | Single boolean flip is too weak |

### Iteration 2 — Adversarial expert B (systems / reliability) → v2

**Attack thesis:** v1 is authority-correct but still pages the founder on noise and fails closed/open the wrong way when GraphQL dies, observes are missed, or PARTIAL checks become permanent. Thin attention needs quiet-IDLE, miss rules, and hard-fail behavior that doesn’t corrupt state.

| Change | Rationale |
| --- | --- |
| Quiet-if-IDLE + 5-min founder skim SLA | Prevents observe-as-busywork (income lock already said this) |
| Missed-observe rule differentiated DEMO-idle vs live-open | Don’t pager on idle DEMO; do escalate if live size unwatched |
| Triple-fetch + GREEN/AMBER/RED STATUS | One glance health for thin attention |
| GraphQL hard-fail → HOLD/STALE last pack, no state wipe | Avoid “empty markets ⇒ clear book” disasters |
| STALE_S blocks PASS/ALLOCATE | Stale PASS is worse than honest IDLE |
| O3/O4 must be non-PARTIAL with open size | Permanent PARTIAL today is fine only while idle |
| Config/brief presence check; append-only log | Integrity without a heavy platform |
| Weekend auto only if KILL or open WARN/EXIT | Cuts unnecessary fetch load and false alerts |

### Iteration 3 — Adversarial expert C (capital / risk lead) → v3

**Attack thesis:** v2 can run the machine and still blow the book on size, relative market cap, exit liquidity fiction, and “eligible=0 so let’s loosen Regime B.” Income=P&L means the checklist must gate **capital shape**, not just process hygiene. Kits/invoice must stay off the ops path so attention returns to risk.

| Change | Rationale |
| --- | --- |
| Explicit book / per-market / max-markets caps before live | Thin books die from first-size hubris |
| Five-way AND for ALLOCATE (ALLOW∩PASS∩VAULT∩!DEMO∩!KILL) | Removes “almost live” allocate paths |
| Reject ALLOW for ineligible markets | Stops amendment-by-ALLOW-loophole |
| O5 exit-liq preflight + O7 outflow before >dust | Can’t exit = can’t responsibly enter |
| Paper → dust → one full exit cycle → size-up-by-amendment | Path dependence beats big-bang live |
| Rollback: DEMO re-on with open size = INCONSISTENT EXIT PRIORITY | Flag confusion must not strand capital |
| Kill list: kits/outreach/OSS/multi-user/BMN* | Protects attention budget; income=P&L only after live |
| Regime B loosen only via B2+ amendment (reaffirmed) | Eligible=0 is a market fact, not a bug to “fix” with higher LLTV |

**Killed / demoted from naive v0**

- “RPC health” as a single green light without DEMO vs live split — too crude; split in §E.
- “Exit criteria” as a vague sentence — replaced by §A.3 live gate + §G runbook + O5/O7.
- Any commercial kit / invoice checklist items — out of band (killed track).
- Multi-user vault / public status — not this product.

---

## (3) Top 5 residual risks the checklist cannot absorb

1. **Morpho / oracle / LST protocol risk** — Regime B and O3/O4 reduce *operational surprise*; they do not hedge smart-contract bugs, oracle manipulation, or stETH depeg tail events. Thin ops cannot substitute for protocol risk appetite.
2. **Regime-B-eligible set may stay empty** — Today all observed wstETH–WETH markets sit above 86% LLTV. Checklist correctly forces IDLE; it cannot create eligible markets. Live P&L may remain zero until markets or a human B2 amendment change the mandate — that is a capital outcome, not an ops failure.
3. **Data-plane fragility (GraphQL schema, Llama, RPC providers)** — PARTIAL O1 (borrower), O3 secondary, and rpc 403 are structural. Checklist demands non-PARTIAL before size, but vendors can regress after live; founder still needs a provider plan money can’t fully automate.
4. **Founder key / custody / execution quality** — Human signs. Wrong wallet, wrong calldata, MEV on exit, or paste error on ALLOW/ACTION are outside observe. Minimum-ops assumes a careful human signer; it does not provide a Safe, simulator gate, or Guard-style pre-broadcast proxy (separate product).
5. **Attention failure under correlated stress** — Kill switch + miss rules help, but a multi-day founder outage during a cascading LST event can still leave exits late. Checklist sets KILL and EXIT priority; it cannot guarantee a human is present to sign.

---

## Appendix — Map from v0 seed → v3 sections

| v0 seed | Fate in v3 |
| --- | --- |
| Observe cadence | §C.9–12 (cadence, SLAs, miss, quiet-IDLE) |
| Mandate hash | §A.1 (+ abort, amendments) |
| Kill switch | §B.5–7 (KILL, levers, P_WSTETH) |
| Size rules | §D.13–17 (caps, five-way AND, O5/O7) |
| RPC health | §E.18–22 (triple-fetch, DEMO vs live RPC, stale, hard-fail) |
| Logging | §F.23–26 (pack, log, ALLOW check, drift) |
| DEMO gate | §A.2–3 + §G.27–30 (process gate, live checklist, paper→dust) |
| Exit criteria | Folded into §A.3, §B.7, §D.16, §G.30 |
| — | **New:** kill list §H (kits/OSS/BMN*), attention SLAs §C |

*Last updated: 2026-09-26 ET — design-only; no live capital; no code changes in this pass.*
