"""
Instance Identity Service
Generates and persists a unique instance UUID on first boot.
Used in all communications with the vendor license server.
"""
import os
import uuid

_INSTANCE_ID_PATH = os.environ.get("INSTANCE_ID_PATH", "/data/instance_id")


def get_instance_id() -> str:
    """Return the persistent instance UUID, generating it on first call."""
    # Try reading existing
    if os.path.exists(_INSTANCE_ID_PATH):
        with open(_INSTANCE_ID_PATH, "r") as f:
            iid = f.read().strip()
            if iid:
                return iid

    # Generate new UUID
    iid = str(uuid.uuid4())
    os.makedirs(os.path.dirname(_INSTANCE_ID_PATH), exist_ok=True)
    with open(_INSTANCE_ID_PATH, "w") as f:
        f.write(iid)

    print(f"🆔 New instance ID generated: {iid}")
    return iid
