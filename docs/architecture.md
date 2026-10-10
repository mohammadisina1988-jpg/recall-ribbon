# Consensus boundary and interval provenance

Flow: immutable publisher/product configuration → permissionless notice URL+hash → full contract-side acquisition → independent semantic interpretation → exact scope equivalence → deterministic range subtraction and overlay → persisted provenance → inventory-lot queries.

External publisher owns raw documentary assertions. The contract owns source commitments, accepted interpretations, range compilation and query semantics. A future frontend owns previews and indexing; this repository contains no app.

## Consensus target

Source JSON has exactly `id` and `text`. Duplicate JSON keys, invalid IDs, oversized bodies, wrong hash or unexpected URL scope revert. URLs require a full Git commit hash in the fixed public repository. The leader and each validator fetch bytes inside their own nondeterministic flow. Material source interpretation uses separate LLM calls and exact canonical agreement on ACTIVE/IGNORE/UNKNOWN, included ranges and exemptions. Leading-zero integer strings and range ordering/overlap normalize without changing membership. Booleans, fractional bounds and omitted material decisions are errors. Erroring leaders are rejected rather than approved solely because their output has the right shape.

ACTIVE must explicitly decide exception_mode NONE or RANGES. RANGES requires a nonempty exception list entirely inside included scope. IGNORE and UNKNOWN cannot introduce range fields. Source-anchored quotes need not be identical because they do not drive range membership; validators independently validate the leader's quote against their fetched document and independently determine all consequential fields. There is no confidence tolerance or majority-score threshold inside the contract.

## Overlay

Normalize each notice's inclusions and exclusions. Subtract exclusions first. For each remaining inclusive interval `[a,b]`, place an addition event at `a` and removal at `b+1`. Sweep endpoints with the active notice-ID set. Emit positive-length segments and merge only adjacent segments with identical provenance. The 999999 maximum makes endpoint arithmetic bounded without floating-point comparisons.

Exclusion applies only to its own notice. Overlap is an OR across active notices, with full notice provenance attached. Duplicate notice IDs and source hashes are rejected. Stored notice documents are append-only; the compact index is deterministically rebuilt from them. There are no owner proposals, graph versions, certificates, settlement claims or one-use allocation objects.

Each lot query clips the disjoint segments, counts inclusive units exactly once, and retains supporting notice IDs. Any UNKNOWN notice overrides the summary status to REVIEW, even if some or all queried units are already known to match. UNKNOWN does not invent a range, while IGNORE contributes neither intervals nor uncertainty.

## Trust and limitations

This is documentary index correctness under GenLayer consensus, not authenticated safety advice. The publisher remains trusted for truth, notice identity and completeness. Consensus can share a model bias. Hash pinning prevents document drift but does not prove provenance outside GitHub. Conservative append-only operation cannot clear historical recalls or expire notices. Real deployments need an authenticated authoritative snapshot and an explicit operational revision policy outside this primitive's current scope. No external side effect is claimed.

## Validation evidence

Direct tests cover malformed outputs, byte re-fetching, exact exemption boundaries, ignored/unknown disagreement, replay, unauthorized source domains, any-caller ingestion, serial limits and no double counting. A pointwise oracle checks 1,764 combinations independently of the endpoint sweep. Live scenario proofs exercise exemption removal, overlapping provenance, a different model and an unresolved upper bound. Receipt verification checks strict majority votes and successful execution rather than lifecycle status alone.
