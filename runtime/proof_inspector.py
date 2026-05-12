from __future__ import annotations

import hashlib
from pathlib import Path


RECEIPTS = [
    Path("receipts/runtime_proof_snapshot.json"),
    Path("receipts/canonical_release_baseline.json"),
    Path("receipts/release_lineage.jsonl"),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


if __name__ == "__main__":
    print("=" * 72)
    print("DETERMA PROOF INSPECTOR")
    print("=" * 72)
    print()

    for receipt in RECEIPTS:
        if not receipt.exists():
            print(f"MISSING: {receipt}")
            continue

        digest = sha256_file(receipt)

        print(f"FILE: {receipt}")
        print(f"SHA256: {digest}")
        print()

    print("Runtime proof inspection complete.")
