"""Local integrity seal. Not third-party attestation; a local administrator can access the key."""
from __future__ import annotations
import hmac, hashlib, os, secrets
from pathlib import Path
from eija_studio.domain.models import canonical

class ReceiptSigner:
    def __init__(self, directory: Path):
        path = Path(directory) / "receipt.key"
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "wb") as f:
                f.write(secrets.token_bytes(32))
        self._key = path.read_bytes()
        if len(self._key) != 32:
            raise ValueError("Invalid local integrity key; do not replace it without archiving old evidence")

    def seal(self, receipt: dict) -> dict:
        data = {k: v for k, v in receipt.items() if k != "local_signature"}
        signature = hmac.new(self._key, canonical(data).encode(), hashlib.sha256).hexdigest()
        return {**data, "local_signature": signature}

    def authentic(self, receipt: dict) -> bool:
        supplied = receipt.get("local_signature", "")
        return isinstance(supplied, str) and hmac.compare_digest(self.seal(receipt)["local_signature"], supplied)
