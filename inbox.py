"""Boîte de dépôt : enregistre les réponses et documents déposés dans l'application.

Chaque contribution est écrite dans data/inbox/responses.jsonl et ses fichiers dans data/inbox/files/<id>/.
Tout est marqué « Non vérifié » : une contribution n'entre dans le registre qu'après relecture.
NB : sur Streamlit Community Cloud le disque est éphémère ; exporter régulièrement (export_zip).
"""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import re
import uuid
import zipfile
from datetime import datetime, timezone

import pandas as pd

ROOT = pathlib.Path(__file__).parent
INBOX = ROOT / "data" / "inbox"
ALLOWED = {"pdf", "csv", "xlsx", "xls", "txt", "md", "json", "png", "jpg", "jpeg", "docx"}
MAX_BYTES = 15 * 1024 * 1024
MAX_FILES = 5
KINDS = [
    "Réponse officielle (Africa CDC, INSP, OCHA, ministère…)",
    "Réponse d'une ONG ou d'un partenaire",
    "Document (rapport, audit, liste de partenaires…)",
    "Données (export FTS, USAspending, tableur…)",
    "Correction ou contradiction d'un constat",
    "Autre",
]
POSITIONS = ["Confirme", "Infirme", "Précise ou nuance", "Nouvel élément"]


def safe_name(name: str) -> str:
    name = pathlib.Path(name).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "fichier"
    return name[:120]


def _validate(files: list[tuple[str, bytes]]) -> None:
    if len(files) > MAX_FILES:
        raise ValueError(f"Maximum {MAX_FILES} fichiers par contribution.")
    for name, data in files:
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in ALLOWED:
            raise ValueError(f"Type de fichier non accepté : {name} (acceptés : {', '.join(sorted(ALLOWED))}).")
        if len(data) > MAX_BYTES:
            raise ValueError(f"{name} dépasse {MAX_BYTES // 1024 // 1024} Mo.")
        if not data:
            raise ValueError(f"{name} est vide.")


def save_contribution(meta: dict, files: list[tuple[str, bytes]], base: pathlib.Path = INBOX) -> dict:
    """Validate and persist one contribution; return the stored record."""
    message = (meta.get("message") or "").strip()
    url = (meta.get("source_url") or "").strip()
    if not message and not files and not url:
        raise ValueError("Ajoutez au moins un message, un lien ou un fichier.")
    if url and not url.lower().startswith(("http://", "https://")):
        raise ValueError("Le lien doit commencer par http:// ou https://.")
    _validate(files)
    cid = uuid.uuid4().hex[:10]
    stored = []
    if files:
        folder = base / "files" / cid
        folder.mkdir(parents=True, exist_ok=True)
        for name, data in files:
            fn = safe_name(name)
            (folder / fn).write_bytes(data)
            stored.append({"name": fn, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    rec = {
        "id": cid,
        "received_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "contributor": (meta.get("contributor") or "").strip()[:120],
        "organisation": (meta.get("organisation") or "").strip()[:120],
        "kind": meta.get("kind", "Autre"),
        "claim_id": meta.get("claim_id") or "",
        "position": meta.get("position", ""),
        "message": message[:5000],
        "source_url": url[:500],
        "source_date": str(meta.get("source_date") or ""),
        "files": stored,
        "status": "Non vérifié",
    }
    base.mkdir(parents=True, exist_ok=True)
    with (base / "responses.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def load_contributions(base: pathlib.Path = INBOX) -> pd.DataFrame:
    cols = ["id", "received_utc", "contributor", "organisation", "kind", "claim_id", "position",
            "message", "source_url", "source_date", "files", "status"]
    path = base / "responses.jsonl"
    if not path.exists():
        return pd.DataFrame(columns=cols)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    df = pd.DataFrame(rows)
    for c in cols:
        if c not in df:
            df[c] = ""
    return df[cols].sort_values("received_utc", ascending=False).reset_index(drop=True)


def export_zip(base: pathlib.Path = INBOX) -> bytes:
    """Zip of responses.jsonl, a CSV view and every stored file (to bring back into the research chat)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        df = load_contributions(base)
        z.writestr("contributions.csv", df.assign(files=df.files.apply(lambda f: "; ".join(x["name"] for x in f))).to_csv(index=False))
        path = base / "responses.jsonl"
        if path.exists():
            z.write(path, "responses.jsonl")
        for p in sorted((base / "files").glob("*/*")) if (base / "files").exists() else []:
            z.write(p, f"files/{p.parent.name}/{p.name}")
    return buf.getvalue()


def sniff_table(name: str, data: bytes) -> dict | None:
    """Preview CSV/XLSX uploads and flag OCHA FTS exports (they contain a 'Flow ID' header)."""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(data), nrows=8, sep=None, engine="python")
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(data), header=None, nrows=8)
        else:
            return None
    except Exception:  # noqa: BLE001 - preview is best effort
        return None
    flat = " ".join(map(str, df.astype(str).values.ravel().tolist() + list(map(str, df.columns))))
    return {"kind": "fts" if "Flow ID" in flat else "table", "preview": df, "name": name}
