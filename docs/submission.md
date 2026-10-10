Category: **Builder → Intelligent Contracts**

Title: **RecallRibbon: Consensus serial-range provenance index**

Notes / Description:

> RecallRibbon turns prose recall notices into a disjoint serial-range index for a fixed product. Leader and validators independently fetch commit-pinned full documents, check SHA-256, and interpret exact applicability, operative status, included serial ranges and exemptions. Exact agreement drives per-notice subtraction and an endpoint sweep retaining all overlapping notice IDs. Inventory queries count affected units once, preserve provenance, and return REVIEW for unresolved notices. The bounded append-only design prevents silent removal of accepted scope. Four finalized StudioNet MAJORITY_AGREE proofs cover exemptions, overlapping scope, a different model and an unknown upper bound; 24 onchain lot reads match an independent oracle. Includes 33 direct tests covering 1,764 interval configurations. Synthetic fixtures demonstrate documentary interpretation, not product-safety truth; publisher authenticity and completeness remain trust assumptions.

Evidence:

- [Repository](https://github.com/mohammadisina1988-jpg/recall-ribbon)
- [GenLayer contract source](https://github.com/mohammadisina1988-jpg/recall-ribbon/blob/main/contracts/recall_ribbon.py)
- [Full onchain proofs](https://github.com/mohammadisina1988-jpg/recall-ribbon/blob/main/proofs/README.md)
- [Deployment transaction](https://explorer-studio.genlayer.com/tx/0x5aebedf83f0d45062f43d5d8ef8bf56649657b128d82623185673652af2ba541)

StudioNet contract: `0x0d44C6b7f4f6DcCA84691930caA0b03ac85dD52B` (chain 61999; gasless development network).
