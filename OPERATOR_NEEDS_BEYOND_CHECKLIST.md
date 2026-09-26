# Keel — Operator Needs Beyond Minimum-Ops Checklist

**Audience:** Keel OPERATOR = founder + Keel agent (same book; not stranger OSS buyer, not multi-user vault)  
**Baseline treated as covered:** `/workspace/keel/MINIMUM_OPS_CHECKLIST.md` (v3)  
**Method:** three sequential adversarial expert iterations; each adds concrete needs, kills fluff.  
**Date:** 2026-09-26 ET — design-only; no live capital; no Soft-WTP; no multi-user vault invent.

---

## (1) Final Operator Needs inventory

Treat checklist items (mandate triple-pin, DEMO process gate, live-exit gate, KILL, human levers, P_WSTETH drill, cadence/SLAs, size caps, five-way AND, O5/O7, triple-fetch, pack/log integrity, paper→dust runbook, kill list) as **already required of the ops system**. Below is what the **operator pair** must still bring, decide, own, or do that the checklist does not fully specify.

### Before live / DEMO gate

1. **Correct product mental model** — Keel is a Regime-B observe → score → recommend → REFERENCE_ONLY draft loop for a **founder Morpho V1 wstETH–WETH sleeve**. It is **not** a custodian, signer, yield optimizer, curator dashboard, multi-user vault, or “safe autonomous allocator.” IDLE_ALL with eligible=0 is success, not a bug. Founder must accept: agent never signs; capital risk is protocol + human paste + attention.
2. **Mandate acceptance as capital policy** — Founder explicitly accepts Regime B (LLTV ≤ 0.86 WAD, wstETH-only, forbidden collateral list) knowing today’s observed markets are often **all ineligible**. Choosing to stay IDLE forever vs pasting a B2 amendment that loosens filters is a **capital policy decision**, not an observe defect.
3. **Custody / signer stack separate from observe** — Hardware wallet, Safe, or other human-controlled signer path that will eventually execute ACTION lines. Private keys never enter the observe host, agent env, `config.json`, pack, or chat. Checklist forbids agent keys; **founder still designs where keys live**.
4. **Vault identity plan (human-owned)** — Which address will become `VAULT_ADDRESS` (EOA, Safe, Morpho vault / MetaMorpho host, or other). Checklist requires human-set vault before live; **operator must pick and verify ownership/control** of that address (and any host vault / allocator role) before the flip.
5. **Authenticated RPC / provider plan for live** — Named provider (or self-hosted) that can read `stEthPerToken`, block, and any oracle views needed for O3/O4. Budget, API key custody (not in git), and failover. Checklist says DEMO+idle may tolerate `rpc_ok=false` (today’s 403); **live gate needs a real plan the founder buys and wires**.
6. **Secondary price / oracle cross-check ownership** — Which Llama path + optional RPC secondary the book trusts for O3/O4; what happens if Llama disagrees with Morpho market oracle. Checklist demands non-PARTIAL before size; **operator names the sources and escalation when they diverge**.
7. **Book size philosophy written once** — First `BOOK_NOTIONAL_CAP_WETH`, `PER_MARKET_CAP_WETH`, `MAX_MARKETS_OPEN`, `DUST_CAP_WETH` chosen by founder with a one-line rationale (e.g. “dust = learn exit path; not income”). Checklist requires caps in config; **numbers and risk appetite are operator-owned**.
8. **Kill-switch reachability** — How founder will notice `KILL=true` / O*_EXIT within the attention SLA (pack path on disk, notify channel, calendar block at 08:00 ET skim). Checklist defines KILL semantics; **operator must actually see it when AFK-adjacent**.
9. **Paper drill schedule before any DEMO flip** — Calendar: P_WSTETH paper drill once; zero-size dry-run against intended vault once (§A.3e). Checklist mandates them; **founder books the time and records pass/fail**.
10. **Named RACI inside the operator pair** — Who pastes ALLOW / ACTION / amendments (founder only); who runs observe (agent); who clears KILL (founder only); who pays RPC (founder). Checklist splits levers; **operator writes the names so the agent does not “helpfully” paste**.
11. **Out-of-band secrets hygiene** — RPC keys, any future explorer API keys, signer PINs: password manager / separate machine. Never in `/workspace/keel` packs or income dirs.
12. **Accept kill-list for attention** — Kits, targets.csv, Soft-WTP, OSS packaging are not ops. Operator does not schedule them against the 08:00 observe skim.

### DEMO observe (daily while `DEMO_ONLY=true`)

13. **Reproduce one full pack locally and archive a baseline** — Keep a weekday pack + matching log entry + `mandate_hash` as the team’s “known-good DEMO” artifact. Checklist defines pack sections; **operator stores proof** for “is observe broken or is Morpho empty?”
14. **Founder 5-minute skim actually happens** — Header + recommendation + blockers + fetch booleans. Escalate only on checklist triggers. Skipping skim for a week while claiming “thin ops” is an operator failure mode.
15. **Interpret IDLE_ALL + eligible=0 correctly** — Do not loosen Regime B, invent ALLOW, or “fix” markets. Next human actions stay: wait for eligible market, or deliberate B2 paste. Checklist forces IDLE; **operator must not fight it with busywork observes**.
16. **Quiet-if-IDLE discipline** — If recommendation + blockers + eligible set unchanged, treat as log-only; do not regenerate kits or re-run observe-as-progress. Agent must not propose “more GraphQL polish” as ops progress.
17. **PARTIAL taxonomy ownership** — When pack flags O1/O3/O4 PARTIAL (current reality), founder records which PARTIALs are **accepted under DEMO+idle** vs **blockers for live**. Checklist allows DEMO PARTIAL; **operator tracks the graduation criteria per check**.
18. **Fetch-failure triage first line** — graphql_ok / llama_ok / rpc_ok: which failures are vendor weather vs config vs ban (403). Checklist defines STATUS colors; **operator keeps a short private note of provider contacts / status pages**.
19. **Mandate drift watch** — Spot-check that pack header hash == `config.json` == `mandate_hash.txt` after any human edit. Checklist aborts on mismatch if coded; **until/unless enforced in code, founder is the last line**.
20. **No shadow books** — Do not run a second unofficial observe, spreadsheet ALLOCATE, or “mental ALLOW” outside pack/log. One book, one pack path.

### Configure (config, ALLOW, vault, amendments)

21. **Human-edited `config.json` as the only threshold source** — Thresholds (ORACLE_*, WST_*, UTIL_*, BORROWER_*, STALE_S, EXIT_LIQ_*, MODELED_OUTFLOW_*, FORBIDDEN_*) changed only by founder with dated note in `AMENDMENTS[]` or adjacent changelog. Agent does not “tune” to make PASS appear.
22. **ALLOW paste discipline** — Founder pastes rows only in the documented format; verifies uniqueKey against **latest** full market table; verifies lltv ≤ Regime B max and collateral=wstETH; sets `cap_rel` ≤ MARKET_REL_CAP with a written why. Checklist paste-check rejects poison; **operator must not paste from memory or Discord snippets**.
23. **B2+ amendment ritual** — Any Regime loosen, IDLE default change, or size-up is a **pasted amendment text** recorded in config, with date and intent. No chat-only “we should allow 94.5%” that never lands in `AMENDMENTS[]`.
24. **VAULT_ADDRESS set only when control is proven** — Founder confirms they can sign for that address (and any allocator roles) before writing it into config. Setting vault “to unblock the pack” without control is forbidden.
25. **ALLOW ∩ eligibility preflight before DEMO flip** — At least one ALLOW row must refer to a market that is Regime-B-eligible **in the current pack**, not a wish. Checklist five-way AND; **operator verifies the intersection by hand once**.
26. **Size caps written before flip** — Caps and dust limit in config and included in mandate re-hash / amendment trail (§A.3f). Do not flip DEMO with “caps TBA.”
27. **Kill / DEMO flag consistency rules internalized** — Operator knows: re-enabling DEMO_ONLY with open live size ⇒ INCONSISTENT EXIT PRIORITY; clearing KILL is human-only; agent may set KILL on EXIT trips.
28. **Reference book continuity** — Keep `REFERENCE_BOOK_ID` / `REFERENCE_UNITS` meaningful through paper sleeve week so DEMO packs stay comparable; do not reset reference IDs casually.

### Execute live (dust → first cycle → size-up)

29. **Live-exit gate walkthrough (all §A.3 items)** — Founder ticks: vault set, ALLOW∩eligible, O1–O7 not systematically PARTIAL on touch markets, RPC green 3 weekday observes, paper + zero-size drill done, caps hashed. Missing any → stay DEMO. Checklist lists them; **operator performs and records the tick-sheet**.
30. **ACTION line craft (human)** — Every live tx preceded by pasted ACTION: marketId, size, direction (ALLOCATE/REDUCE/EXIT), expected `mandate_hash`, timestamp. Founder never signs from “recommendation vibes” alone.
31. **Pre-sign simulation / calldata check (operator-owned tooling)** — Before broadcast: verify target market, assets, size vs caps, and that calldata matches ACTION. Checklist notes Guard/Safe are out of band; **founder still needs *some* check** (explorer sim, Tenderly, Safe sim, or equivalent) — choose and stick to it.
32. **Dust allocate → full exit cycle before size-up** — One complete round-trip at ≤ `DUST_CAP_WETH` with packs showing ALLOCATE then EXIT/IDLE. Checklist requires it; **operator refuses size-up amendments until the cycle is in log.md**.
33. **O5 exit-liquidity respect** — If pack says HOLD_EXIT_BLOCKED, founder waits / partials / changes venue per pack options; does not force full exit assumption on thin books.
34. **O7 outflow PASS before >dust** — No “just a bit more” while O7 FAIL. Size-up amendment only after O7 PASS on target market.
35. **Post-tx reconciliation** — After each signed ACTION: compare onchain position vs pack recommendation vs ACTION intent; append outcome note to log (or a founder ledger). Checklist is pre-trade heavy; **operator owns post-trade truth**.
36. **MEV / execution quality acceptance** — Exits and allocates on mainnet may sandwich or slip. Operator accepts that observe does not protect execution; choose time/size/route accordingly (or stay dust).
37. **Size-up only via dated amendment** — New caps in config + amendment text; never agent “scale into APY.”

### Operate (ongoing live / open size)

38. **Weekday skim + weekend rule adherence** — 08:00 ET weekday observe; weekend auto only if KILL or open WARN/EXIT. Founder does not demand vanity weekend packs while quiet IDLE.
39. **Open-size PARTIAL = treat as WARN floor** — With capital deployed, O3/O4 PARTIAL is not “DEMO cozy”; escalate provider fix or REDUCE/EXIT per brief. Checklist states the rule; **operator enforces emotionally when yield looks good**.
40. **Missed-observe ack when live-open** — On 2 consecutive weekday misses with open size: pack KILL warn → founder must ack in log/amendment. Do not ignore.
41. **Provider money & key rotation** — Pay RPC invoices; rotate keys if leaked; keep fallback URL documented. Checklist cannot pay Alchemy/Infura for you.
42. **Correlated LST stress playbook (human)** — On stETH/wstETH depeg headlines or oracle chaos: expect KILL / P_WSTETH path; founder available to sign EXIT. Checklist cannot guarantee presence; **operator plans coverage** (backup signer with same vault powers, or accept halt risk).
43. **Utilization / borrower concentration response** — When O1/O2 WARN/EXIT fire on open markets: follow score → REDUCE/EXIT without waiting for a new ALLOW (risk-down always allowed). Do not “HOLD for APY.”
44. **Market table discipline persists live** — Every pack still tables **all** wstETH–WETH markets + ineligible_reason; operator does not shrink to “our one market” and miss regime drift.
45. **Amendment hygiene under time pressure** — Even in a hurry, size/regime changes go through AMENDMENTS[]; chat panic is not config.
46. **Income = P&L after DEMO exit — measured honestly** — Track PnL / drawdown vs observe count vanity. Checklist kill-list already bans kits-as-ops; **operator’s scoreboard must match**.
47. **Periodic residual-risk review** — Re-read checklist §(3) residual risks (protocol, empty eligible set, data plane, custody paste, attention) against current open size; decide stay / cut / amend mandate.

### When breaks

48. **First-line triage tree (operator-owned)** — (1) mandate hash match? (2) DEMO/KILL/INCONSISTENT flags? (3) graphql/llama/rpc booleans? (4) STALE_S / O6? (5) ALLOW poison vs eligible=0? (6) PARTIAL vs true EXIT? (7) human paste error on ACTION/ALLOW? Checklist defines behaviors; **operator needs this as a sticky runbook**.
49. **Classify loss / near-miss correctly** — Protocol bug / oracle / LST depeg / paste error / unsigned-from-recommendation / RPC lie / attention miss / regime-too-tight (zero P&L) are different labels. Prevents “Keel failed” postmortems when the failure was human or Morpho.
50. **Rollback & halt** — Known-good config + last GREEN/AMBER pack; ability to set KILL; ability to stop signing independently of observe. Re-DEMO with open size ⇒ EXIT priority, not “ignore positions.”
51. **Fetch hard-fail behavior trust** — On GraphQL down: do not invent markets or clear ALLOW; use last-known HOLD/STALE pack. If agent ever wipes state, treat as severity-1 ops bug.
52. **Drill failure = capital halt** — If P_WSTETH or zero-size dry-run fails, do not proceed to size-up; fix path first.
53. **Escalation is founder-only for money moves** — Agent surfaces; founder signs or IDLE. No “agent emergency ALLOCATE.”

### Explicitly NOT Keel (operator must obtain elsewhere or accept absence)

54. **Key custody, MPC, Safe modules, session keys** — Out of scope; founder supplies.
55. **Pre-broadcast Guard / calldata policy proxy** — Separate product; not assumed in minimum-ops (checklist residual #4).
56. **Hosted SaaS observe / managed Morpho allocator** — Self-run on founder book; no multi-tenant surface.
57. **Creating Regime-B-eligible Morpho markets** — Market structure is external; IDLE may persist.
58. **Yield optimization / TVL growth / curator competition** — Not the mandate; Regime B may refuse flagship 94.5/96.5 markets by design.
59. **BMNR / BMNU / CoinDCX pricing or hedging** — Explicitly out of sleeve.
60. **Client kits, invoice pilots, Soft-WTP, unattended outreach** — Killed commercial track; not ops; not revived here.
61. **Multi-user vault, share class, depositor UX, public status page** — Not this product.
62. **Legal / compliance sign-off that “IDLE or Regime B = safe”** — Do not claim; do not expect Keel to claim.
63. **Guaranteed founder availability during cascading LST events** — Process helps; presence is human.
64. **Insurance, audit of Morpho/wstETH, or oracle manipulation hedge** — Protocol risk appetite is operator’s.

---

## (2) Delta log per iteration

### Iteration 1 — Expert A (first-time founder-operator of the DEMO sleeve)

**Thesis:** Checklist makes the *system* thin-ops-ready; a founder still fails on mental model (IDLE≠broken), custody/RPC prerequisites, skim discipline, PARTIAL graduation criteria, and treating kits as “related work.”

| Added (concrete) | Why checklist alone is insufficient |
| --- | --- |
| Mental model: not custodian / not yield bot / IDLE success | Docs say it; operator must stop “fixing” eligible=0 |
| Mandate as capital policy (stay tight vs B2 loosen) | Eligible=0 residual is stated; decision still human |
| Separate signer/custody design | Agent never holds keys ≠ founder has a signer path |
| Vault identity + control proof before VAULT_ADDRESS | Human-set vault assumes an address plan |
| Paid/authenticated RPC plan for live | DEMO tolerates 403; live does not invent a provider |
| Book size philosophy + dust numbers | Caps fields exist; appetite does not |
| Kill reachability + paper drill calendar | Semantics ≠ calendar + notification path |
| RACI + secrets hygiene + kill-list attention | Levers named; humans still blur roles |
| Archive baseline pack; real 5-min skim | Cadence/SLA written; compliance is operator |
| PARTIAL taxonomy DEMO vs live blockers | PARTIAL allowed in DEMO; graduation is operator-tracked |
| Fetch triage note; mandate spot-check; no shadow books | STATUS/abort rules need a human first line |
| Config-only thresholds; ALLOW/B2 rituals | Paste-check helps; paste quality is human |
| Live tick-sheet; ACTION craft; dust cycle; reconcile | Runbook steps need operator performance |

**Killed as fluff:** “be careful,” “monitor the market,” “read Morpho docs,” Soft-WTP/income kit revival, multi-user vault brainstorming.

### Iteration 2 — Expert B (Morpho / LST risk + custody security) attacks/expands A

**Thesis:** A’s list is DEMO-complete for a careful solo founder but under-specifies blast radius: secondary oracle ownership, pre-sign sim, MEV/execution, INCONSISTENT DEMO+live, poison ALLOW from wrong table snapshot, and loss taxonomy that separates protocol from paste.

| Change | Rationale |
| --- | --- |
| **Add** secondary oracle / Llama-vs-Morpho divergence ownership | O3/O4 non-PARTIAL needs a *named* trust model |
| **Add** ALLOW against *latest* market table only | Stale uniqueKey paste = authorized wrong market |
| **Add** pre-sign simulation / calldata check (operator-chosen) | Human signer residual; checklist cannot absorb paste/calldata error |
| **Add** MEV / execution quality acceptance | Observe ≠ execution protection |
| **Add** post-tx reconciliation ledger | Pre-trade gates ≠ onchain truth |
| **Add** INCONSISTENT DEMO+open-size EXIT PRIORITY internalized | Flag confusion strands capital |
| **Add** open-size PARTIAL = WARN floor enforcement | Yield temptation overrides docs |
| **Add** correlated LST stress coverage (backup signer or accept halt) | Attention residual #5 |
| **Add** loss/near-miss taxonomy | Stops false “Keel failed” postmortems |
| **Add** drill failure = capital halt | Failed drill must block size-up emotionally |
| **Expand** NOT-provided: Guard/Safe, insurance/audit, “safe” compliance claim | Prevents security-theater shopping in this doc |
| **Kill** vague “secure the keys”; replace with no-keys-in-observe + separate signer + secrets hygiene | Actionable only |

### Iteration 3 — Expert C (thin-ops capital book runner) → final inventory

**Thesis:** B hardened risk/custody; running a live dust→sized book still needs provider money ops, weekend/miss rules under open size, util/borrower response without new ALLOW, full-table discipline live, honest P&L scoreboard, amendment hygiene under stress, and a sticky triage tree — or thin attention collapses into either neglect or busywork.

| Change | Rationale |
| --- | --- |
| **Add** provider pay/rotate/fallback as operate work | Live RPC is a bill, not a checkbox |
| **Add** missed-observe ack discipline when live-open | Miss rule is paper unless founder acks |
| **Add** O1/O2 WARN/EXIT → REDUCE/EXIT without waiting for ALLOW | Risk-down path must be practiced |
| **Add** full market table discipline under live tunnel vision | Regime drift hides if operator only watches “our” market |
| **Add** weekend rule adherence + no vanity packs | Protects attention budget |
| **Add** income=P&L honest scoreboard | Aligns with checklist kill-list / STRATEGY lock |
| **Add** periodic residual-risk review vs open size | Residual §(3) must be re-read, not framed |
| **Add** sticky first-line triage tree + rollback/halt | Outage is wrong time to re-read v3 |
| **Add** reference book continuity through paper week | Comparability for DEMO graduation |
| **Add** size-up-only-by-amendment under time pressure | Panic size-up is the classic thin-book death |
| **Harden** Execute section: tick-sheet + dust cycle gate before any size-up amendment | Path dependence |
| **Kill** Soft-WTP, kits, multi-user vault, public status as “operator needs” | Out of charter; attention poison |
| **Kill** “nice dashboards”; keep pack skim + fetch booleans + optional notify for KILL | Minimum that unblocks success |

---

## (3) Map — already in checklist vs new beyond-checklist

| Operator need (short) | In checklist v3? | Beyond (operator must…) |
| --- | --- | --- |
| Mandate triple-pin + abort | **Yes** §A.1 | Spot-check after human edits; treat mismatch as halt |
| DEMO_ONLY process gate | **Yes** §A.2 | Internalize: no keys/ACTION invent; IDLE≠broken |
| Live-exit multi-item gate | **Yes** §A.3 | Perform & record tick-sheet; calendar drills |
| Regime B config-only | **Yes** §A.4 | Accept eligible=0 or deliberate B2; no “fix markets” |
| KILL set-by-agent / clear-by-human | **Yes** §B.5 | Ensure founder can *see* KILL in SLA window |
| Human owns ALLOW/ACTION/sign/B2 | **Yes** §B.6 | Written RACI; no agent “helpful paste” |
| P_WSTETH drill in pack path | **Yes** §B.7 | Schedule paper + zero-size dry-run; halt on fail |
| ACTION human-only append-only | **Yes** §B.8 | Craft ACTION; never sign from vibes; reconcile after |
| Cadence / quiet-IDLE / SLAs / miss | **Yes** §C.9–12 | Actually skim; ack misses when live-open; no weekend vanity |
| Book / market / max-market caps | **Yes** §D.13–14 | Choose numbers + rationale; size-up by amendment only |
| Five-way AND + reject ineligible ALLOW | **Yes** §D.15 | Hand-verify ALLOW∩eligible on latest table before flip |
| O5 / O7 before exit / >dust | **Yes** §D.16–17 | Obey HOLD_EXIT_BLOCKED; no force exit / no ignore O7 |
| Triple-fetch STATUS | **Yes** §E.18 | First-line vendor triage note |
| RPC required for live | **Yes** §E.19 | Buy/wire/pay provider; rotate keys; fallback |
| STALE_S / O3–O4 non-PARTIAL w/ size | **Yes** §E.20–21 | Name secondary sources; escalate PARTIAL when live |
| GraphQL hard-fail HOLD/STALE | **Yes** §E.22 | Trust non-wipe; severity-1 if agent clears state |
| Pack sections + append-only log | **Yes** §F.23–24 | Archive baseline; post-tx outcome notes |
| ALLOW paste-check format | **Yes** §F.25 | Paste quality + latest-table discipline |
| Config/brief drift check | **Yes** §F.26 | Founder last line if code lag |
| Paper → dust → exit cycle → size-up | **Yes** §G.27–29 | Refuse size-up until cycle in log |
| DEMO re-on + open size INCONSISTENT | **Yes** §G.30 | EXIT priority behavior, not ignore |
| Kill list kits/OSS/BMN*/multi-user | **Yes** §H | Keep them off ops calendar / this doc |
| Product mental model & mandate-as-policy | Partial in brief | **New** — mandatory pre-live acceptance |
| Custody/signer stack design | Residual #4 | **New** — operator-owned |
| Vault control proof | “Human sets vault” | **New** — prove control before write |
| Secondary oracle trust model | O3/O4 required | **New** — name sources + divergence rule |
| Kill notify / skim reachability | SLA written | **New** — actual channel/calendar |
| PARTIAL graduation taxonomy | DEMO vs live split | **New** — operator tracking sheet |
| Pre-sign sim / calldata check | Out of band | **New** — choose tooling |
| Post-tx reconciliation | Absent | **New** |
| MEV/execution acceptance | Residual | **New** — explicit |
| LST stress coverage / backup signer | Residual #5 | **New** |
| Provider billing & key rotation | Mentioned | **New** — operate chore |
| Loss/near-miss taxonomy | Honesty | **New** — labels |
| Sticky triage + rollback/halt | Behaviors scattered | **New** — runbook form |
| Honest P&L scoreboard | Income=P&L | **New** — operator metric |
| Periodic residual-risk review | §(3) list | **New** — cadence vs open size |
| Compliance / “safe” claim | Non-goals | **New** — explicit NOT |
| Creating eligible markets | Residual #2 | **New** — accept external |

---

## (4) Top 10 beyond-checklist items

Ranked by **“operator cannot succeed without this”** (success = DEMO stays honest, live flip only when gate real, capital follows ALLOW∩PASS with human signatures, exits under stress without inventing risk-up, triage without pretending Keel is custody or a yield bot).

| Rank | Need | Why blocking |
| --- | --- | --- |
| 1 | **Correct mental model + mandate-as-policy** (IDLE/eligible=0 success; no silent Regime loosen) | Wrong model → poison ALLOW, B2-by-accident, or busywork that burns attention |
| 2 | **Human ACTION craft + never sign from recommendation alone** | Checklist blocks agent invent; founder can still self-bypass and lose funds |
| 3 | **Authenticated RPC / provider plan wired & paid before DEMO flip** | Live O3/O4 without RPC is false safety (today’s DEMO 403 proves the gap) |
| 4 | **Custody/signer stack separate from observe + pre-sign calldata check** | Keys-in-agent or blind broadcast are the highest-severity operator failures |
| 5 | **Live-exit tick-sheet performed** (vault control, ALLOW∩eligible, non-PARTIAL, RPC streak, drills, caps hashed) | Single boolean DEMO flip without the gate is how “almost ready” books die |
| 6 | **Dust allocate → full exit cycle in log before any size-up amendment** | Path dependence; first-size hubris is the thin-book killer |
| 7 | **Kill / EXIT reachability within attention SLA** (skim + notify; backup signer or accept halt) | KILL bits without a human who sees/signs do not move capital |
| 8 | **ALLOW/B2 paste discipline against latest full market table** | Stale or ineligible ALLOW becomes “authorized” loss |
| 9 | **Open-size PARTIAL / O1–O2 / O5–O7 obedience** (WARN floor, REDUCE/EXIT, no force-exit fiction) | Yield temptation and exit-liquidity denial are live-specific failure modes |
| 10 | **Sticky triage + loss taxonomy + post-tx reconciliation** | Without these, every incident becomes either panic size-up or “Keel failed” myth |

---

## Appendix — How to use this doc

- **Checklist owners:** Do not duplicate these as more product slogans; a few may inspire future pack fields (e.g. PARTIAL graduation column, drill pass/fail), but ownership stays with the operator pair.
- **Founder + agent:** Walk **Before live → DEMO observe → Configure → Execute live → Operate**; treat **NOT Keel** as hard stops.
- **Out of charter:** Soft-WTP, payee rails, client kits/invoice revival, multi-user vault invent, live capital moves in this pass — intentionally excluded.

*Last updated: 2026-09-26 ET — design-only; no live capital; no code/git/outreach in this pass.*
