# StudioNet proofs

Network: **StudioNet**, chain **61999**, gasless development network.

Contract: **`0x0d44C6b7f4f6DcCA84691930caA0b03ac85dD52B`**.

Deployed source matches [recall_ribbon.py](../contracts/recall_ribbon.py) byte-for-byte. SHA-256: `5491e88a3a72f65a56223f40a92d01847881307b1959471b598ec136e924cf70`. Fixture commit: `0638ec3ffd4538269beda9f1a028b2b6bbd6f6f9`. Source URLs, hashes and all transaction hashes are in [deployment.json](deployment.json).

| Case | Verified state | Transaction |
| --- | --- | --- |
| Deployment | Constructor succeeded; source bytes verified | [Deploy](https://explorer-studio.genlayer.com/tx/0x5aebedf83f0d45062f43d5d8ef8bf56649657b128d82623185673652af2ba541) |
| Explicit exemption | 100–199 except 140–149: 90 known affected units | [Exemption](https://explorer-studio.genlayer.com/tx/0x80f60fb2e3e12a3d876883436ae13884f6b2425958272cf780725ccb62fe491f) |
| Independent overlapping notice | Adds 180–219; 110 known affected units in 100–219; overlap records both notice IDs | [Overlap](https://explorer-studio.genlayer.com/tx/0x40210193334cd4fd8107c114d3ffe984a02d16b3979bbbb874f95af5fd3e02f8) |
| Different product model | IGNORE; range index unchanged | [Different model](https://explorer-studio.genlayer.com/tx/0x3a114e4f0174f07020feabd67e31e1ff3db587be523b11c8b370d6693cbf6731) |
| Illegible upper serial bound | UNKNOWN; all lot summaries REVIEW; known ranges preserved | [Unresolved](https://explorer-studio.genlayer.com/tx/0x5c7e200f1dd6b96ba3ba708334d8e3855b48b72263c4d79bef58c22908271616) |

All five receipts are FINALIZED with MAJORITY_AGREE and successful execution. Each scenario JSON contains freshly read state and six `inspect_lot` results; each `*-receipt.json` preserves execution outputs and votes. Exemption and different-model receipts each record one dissenting vote. IDLE votes also occur when validator work is cancelled after quorum. Majority agreement is not unanimity.

[Successful CLI workflow](https://github.com/mohammadisina1988-jpg/recall-ribbon/actions/runs/38045966903). Run `node scripts/verify-proofs.cjs` to independently check source/fixture commitments, receipt success, strict majority votes, exact extracted scopes, state prefixes, per-serial provenance and all 24 lot queries. The oracle expands individual serials rather than reusing the contract's endpoint sweep.

The fictional notices demonstrate documentary scope interpretation. GitHub source pinning does not authenticate a manufacturer or prove document truth/completeness. NO_LISTED_MATCH is not safety clearance. Earlier accepted scope cannot be removed or expired in this conservative append-only index.
