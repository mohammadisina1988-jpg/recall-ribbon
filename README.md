# RecallRibbon

A standalone GenLayer notice-to-serial provenance index. It converts prose recall scope into an exact, disjoint interval overlay for a fixed manufacturer and model. It answers how many units in an inventory serial range match indexed notices and which notices support each affected segment.

## Mechanism

Anyone submits a commit-pinned notice URL and SHA-256. Leader and validators independently download the full document and interpret exact product applicability, operative status, inclusive serial ranges and explicit exemptions. Each supplies a source-anchored quote. The validator compares every canonical decision/range/exemption exactly, including IGNORE and UNKNOWN. Missing exception decisions cannot silently imply no exemption.

After consensus, the contract subtracts exemptions **within their own notice**, sweeps half-open endpoints, and stores maximally merged disjoint segments with sorted notice-ID provenance. Overlapping notices do not double-count units. An exemption in one notice cannot erase another notice's affected scope. An unresolved notice makes every lot query REVIEW while retaining known matches.

## Interface

Constructor: `(publisher_repository, manufacturer, model)`.

- `ingest_notice(url, sha256)`: append an independently evaluated notice and rebuild the interval overlay.
- `inspect_lot(start, end)`: inclusive numeric serial lot; exact known affected count, provenance segments, unresolved notices and status.
- `get_state()`: full retained source documents, classifications and index.

Statuses: KNOWN_FULL, KNOWN_PARTIAL, NO_LISTED_MATCH or REVIEW. NO_LISTED_MATCH means absent from the indexed documents; it is not a product-safety clearance.

## Boundaries

The publisher repository is fixed at deployment and trusted to publish truthful documents with stable IDs. Commit pinning and SHA-256 prove byte integrity, not manufacturer authentication. Numeric serials are restricted to 1–999999, at most four inclusion and four exception ranges per notice, and twelve notices per contract. Unknown/contradictory/unsupported scopes fail closed to REVIEW. No caller supplies authoritative range labels.

This index is deliberately append-only and conservative. No cancellation, expiry or revised document can remove an earlier accepted scope. A notice that is itself cancelled is IGNORE; it cannot revoke earlier notices. Deploy a fresh index for a revised authoritative snapshot. Query results are relative to indexed notices, which need not be complete or current. No physical inventory, service delivery, bank fact, quarantine operation or money transfer is proven. Fixtures use fictional products.

## Validation

Pinned GenVM runner and Python tooling. `genvm-lint check contracts/recall_ribbon.py --json`; `pytest tests/direct -q`.

33 direct tests include a pointwise oracle checking 1,764 interval/exemption configurations. Direct tests explicitly replay validator callbacks but do not simulate network consensus. The StudioNet workflow uses real independent validators, byte-checks deployed source, records finalized execution receipts, and reads six inventory queries after each of four notice ingestions. `node scripts/verify-proofs.cjs` verifies downloaded proofs using a separate per-serial oracle.

[Architecture](docs/architecture.md) · [Proofs](proofs/README.md) · [Submission draft](docs/submission.md).

## Repository design

Contract, interval algorithms, notice fixtures and oracle tests were written for this mechanism. CLI process hooks, receipt journaling, ephemeral-account workflow and Windows test compatibility reuse operational scaffolding from RemittanceKernel. This is not a renamed reconciliation contract: it has no invoice matching, allocation witnesses or document-consumption lifecycle. The computational primitive is an established interval sweep with provenance, not an invented algorithm.

GenLayer API references: [non-determinism](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism), [calling LLMs](https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms). The validator independently reinterprets evidence rather than merely validating response format.

## CLI deployment

`npm ci`; create a gasless StudioNet account; `genlayer network set studionet`; `genlayer deploy` uses the deploy module. For the complete proof workflow, run `.github/workflows/studionet-proof.yml`. Ephemeral signing credentials remain in `.secrets/` and never enter artifacts. Resume inputs accept the exact deployment hash and a JSON map of previously submitted scenario hashes; known transactions are polled rather than sent again. Accepted proof snapshots must match source, address and onchain state before reuse. Do not resume a different source version against an old deployment.
