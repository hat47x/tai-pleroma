"""Place a projection artifact and its operator binding for SUI to read."""

import argparse
import json
import os
from pathlib import Path


def install(root, tenant_id, doc_id, artifact):
    root = Path(root)
    destination = root / "tenants" / tenant_id / doc_id / "documentv1-projection.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(Path(artifact).read_bytes())

    registry_path = root / "epistemic-bindings.json"
    registry = {"bindings": []}
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    bindings = [
        entry
        for entry in registry.get("bindings", [])
        if not (entry.get("tenantId") == tenant_id and entry.get("docId") == doc_id)
    ]
    bindings.append(
        {"tenantId": tenant_id, "docId": doc_id, "artifactKind": "documentv1-projection"}
    )
    registry["bindings"] = bindings
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination, registry_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--doc", required=True)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()

    destination, registry = install(args.root, args.tenant, args.doc, args.artifact)
    print(json.dumps({"artifact": os.path.relpath(destination), "registry": os.path.relpath(registry)}))


if __name__ == "__main__":
    main()
