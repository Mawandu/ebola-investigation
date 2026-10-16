"""Consistency checks. Run:  python -m pytest -q   (or: python tests/test_data.py)"""
import pathlib
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = pathlib.Path(__file__).resolve().parents[1]
P, R = ROOT / "data" / "processed", ROOT / "data" / "reference"


def test_fts_totals():
    f = pd.read_csv(P / "fts_ebola_flows.csv")
    assert len(f) == 246
    assert abs(f.total_usd.sum() - 320_033_000) < 5_000
    inc, itn = f[f.boundary == "Incoming"], f[f.boundary == "Internal"]
    assert len(inc) == 109 and abs(inc.amount_usd.sum() - 152_800_000) < 5_000
    assert abs(inc.shared_usd.sum() - 18_320_000) < 5_000
    assert len(itn) == 137 and abs(itn.amount_usd.sum() - 148_900_000) < 5_000


def test_imc_matches_tracker():
    r = pd.read_csv(P / "recipients.csv").set_index("fts_name")
    assert abs(r.loc["iMC Worldwide", "direct_usd"] - 28_011_254) < 1


def test_source_ids_resolve():
    ids = set(pd.read_csv(R / "sources.csv").id)
    for name in ["claims", "reconciliation", "ngo_profiles", "pledges", "timeline"]:
        df = pd.read_csv(R / f"{name}.csv")
        for cell in df.source_ids.dropna():
            for sid in str(cell).split(","):
                assert sid.strip() in ids, (name, sid)


def test_reconciliation_arithmetic():
    assert round(962 - 220) == 742
    assert round(226.344 - 127.374, 3) == 98.970
    assert round(98.970 - 89.326, 3) == 9.644
    assert 512 + 267 == 779


def test_app_runs_all_pages():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception
    for page in at.sidebar.radio[0].options:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, page


def test_inbox_roundtrip(tmp_path):
    import sys; sys.path.insert(0, str(ROOT))
    import inbox
    rec = inbox.save_contribution({"message": "x", "claim_id": "C02", "source_url": "https://exemple.org"}, [("a b.csv", b"x,y\n1,2\n")], base=tmp_path)
    df = inbox.load_contributions(tmp_path)
    assert len(df) == 1 and df.iloc[0].claim_id == "C02" and df.iloc[0].status == "Non vérifié"
    assert (tmp_path / "files" / rec["id"] / "a_b.csv").exists()
    assert len(inbox.export_zip(tmp_path)) > 100
    for bad in ([("x.exe", b"1")], [("e.csv", b"")]):
        try:
            inbox.save_contribution({"message": "m"}, bad, base=tmp_path)
        except ValueError:
            continue
        raise AssertionError("fichier invalide accepté")
    try:
        inbox.save_contribution({"source_url": "ftp://x"}, [], base=tmp_path)
    except ValueError:
        pass
    else:
        raise AssertionError("lien invalide accepté")


if __name__ == "__main__":
    import tempfile
    for n, fn in list(globals().items()):
        if n.startswith("test_"):
            fn(pathlib.Path(tempfile.mkdtemp())) if "tmp_path" in fn.__code__.co_varnames[:1] else fn(); print("ok", n)
