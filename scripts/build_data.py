"""Build processed datasets from the raw OCHA FTS exports (DRC 2026).

Usage:  python scripts/build_data.py
Inputs : data/raw/FTS_*full_view*.xlsx   (FTS export, 'Export data' sheet)
Outputs: data/processed/fts_ebola_flows.csv, recipients.csv, donors.csv, hf_rounds.csv
Filter : a flow is 'Ebola-described' if its description mentions Ebola or Bundibugyo.
         The FTS keyword tag (EBOLA2026) is NOT in the export, so totals are a floor.
"""
import glob, re, pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

f = glob.glob(str(RAW / "*full_view*.xlsx"))[0]
b = pd.read_excel(f, sheet_name="Export data", header=2)
b = b.rename(columns={
    "Flow ID": "flow_id", "Source org.": "source_org", "Source Country": "source_country",
    "Destination org.": "destination_org", "Destination Country": "destination_country",
    "Description": "description", "Sector": "sector", "Amount (US$)": "amount_usd",
    "Amount shared on boundary": "shared_usd", "Funding status": "status", "Boundary": "boundary"})
b["amount_usd"] = b["amount_usd"].fillna(0)
b["shared_usd"] = b["shared_usd"].fillna(0)
b["description"] = b["description"].astype(str)

e = b[b.description.str.contains("ebola|bundibugyo", case=False)].copy()
e["total_usd"] = e.amount_usd + e.shared_usd
d = e.description

# Humanitarian-fund (pooled) allocation metadata, parsed from the free-text description
e["hf_round"] = d.str.extract(r"\[(RA ?\d-[A-Za-z]+-2026)")[0]
e["hf_label"] = d.str.extract(r"\[RA ?\d-[A-Za-z]+-2026 ?(US|non-US)?\]")[0]
e["hf_start"] = d.str.extract(r"Project Start Date: (\d{4}-\d{2}-\d{2})")[0]
e["project_code"] = d.str.extract(r"Project Code: (\S+)")[0]
types = d.apply(lambda s: sorted(set(re.findall(r"Emergency Type: ([^\n]+)", s))))
e["emergency_types"] = types.apply(lambda l: " | ".join(l))
e["ebola_only"] = types.apply(lambda l: len(l) > 0 and all("Ebola" in x for x in l))
e["fts_url"] = "https://fts.unocha.org/flows/" + e.flow_id.astype(str)
e["description_short"] = d.str.replace(r"\s+", " ", regex=True).str.slice(0, 220)
cols = ["flow_id", "boundary", "source_org", "source_country", "destination_org", "destination_country",
        "sector", "status", "amount_usd", "shared_usd", "total_usd", "hf_round", "hf_label", "hf_start",
        "project_code", "emergency_types", "ebola_only", "description_short", "fts_url"]
e[cols].to_csv(OUT / "fts_ebola_flows.csv", index=False)

inc = e[e.boundary == "Incoming"]
itn = e[e.boundary == "Internal"]

# Recipients: direct (incoming) vs via pooled fund (internal)
r = pd.concat([
    inc.groupby("destination_org").agg(direct_usd=("total_usd", "sum"), direct_flows=("flow_id", "count"),
                                       shared_multi_country_usd=("shared_usd", "sum")),
    itn.groupby("destination_org").agg(via_hf_usd=("amount_usd", "sum"), hf_flows=("flow_id", "count"),
                                       hf_ebola_only_usd=("amount_usd", lambda s: s[itn.loc[s.index, "ebola_only"]].sum()),
                                       hf_us_label_usd=("amount_usd", lambda s: s[itn.loc[s.index, "hf_label"] == "US"].sum()),
                                       hf_first_start=("hf_start", "min")),
], axis=1).fillna({"direct_usd": 0, "direct_flows": 0, "shared_multi_country_usd": 0, "via_hf_usd": 0,
                   "hf_flows": 0, "hf_ebola_only_usd": 0, "hf_us_label_usd": 0})
r["total_usd"] = r.direct_usd + r.via_hf_usd
r.index.name = "fts_name"
r.reset_index().sort_values("total_usd", ascending=False).to_csv(OUT / "recipients.csv", index=False)

# Donors: incoming flows only (new money), grouped by source organisation
g = inc.groupby(["source_org", "source_country"], dropna=False).agg(
    total_usd=("total_usd", "sum"), flows=("flow_id", "count"), shared_multi_country_usd=("shared_usd", "sum")).reset_index()
g.sort_values("total_usd", ascending=False).to_csv(OUT / "donors.csv", index=False)

# Humanitarian fund rounds
h = itn.assign(round=itn.hf_round.fillna("(sans tour)"), label=itn.hf_label.fillna("n/a")).groupby(
    ["round", "label"]).agg(total_usd=("amount_usd", "sum"), flows=("flow_id", "count"),
                            ebola_only_usd=("amount_usd", lambda s: s[itn.loc[s.index, "ebola_only"]].sum())).reset_index()
h.to_csv(OUT / "hf_rounds.csv", index=False)

# Whole-file context (all topics) for the humanitarian fund
hf_in = b[(b.destination_org.astype(str).str.contains("Humanitarian Fund", case=False)) & (b.boundary == "Incoming")]
hf_in.groupby("source_org").amount_usd.sum().sort_values(ascending=False).reset_index().to_csv(
    OUT / "hf_contributions_all_topics.csv", index=False)

print("Ebola-described flows:", len(e), round(e.total_usd.sum() / 1e6, 2), "M$")
print("incoming:", len(inc), round(inc.amount_usd.sum() / 1e6, 2), "+ shared", round(inc.shared_usd.sum() / 1e6, 2))
print("internal (HF):", len(itn), round(itn.amount_usd.sum() / 1e6, 2))
print(h.to_string())
print(r.reset_index()[["fts_name", "direct_usd", "via_hf_usd"]].sort_values("direct_usd", ascending=False).to_string())
