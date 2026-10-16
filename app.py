"""Suivi des fonds de la riposte Ebola en RDC (2026) – application Streamlit.

Tous les chiffres proviennent de data/processed (exports OCHA FTS) et data/reference (tables
documentées, chaque ligne renvoyant à un identifiant de source). Voir la page « Méthodologie ».
"""
from __future__ import annotations

import pathlib

import altair as alt
import pandas as pd
import streamlit as st

import inbox

ROOT = pathlib.Path(__file__).parent
PROC, REF = ROOT / "data" / "processed", ROOT / "data" / "reference"
DATA_DATE = "16 octobre 2026"

st.set_page_config(page_title="Fonds Ebola RDC 2026 – suivi", page_icon="🔎", layout="wide")

st.markdown(
    """
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
h1, h2, h3 {letter-spacing: -0.01em;}
.tag {display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.8rem; font-weight:600;}
.ok {background:#DCEFE3; color:#14532D;} .warn {background:#FBEBCB; color:#7A4A06;}
.bad {background:#F7D9DA; color:#7F1D1D;} .gray {background:#E5E7EB; color:#374151;}
.note {border-left:4px solid #B7791F; padding:0.5rem 0.9rem; background:rgba(183,121,31,0.08); margin:0.8rem 0;}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- data access
@st.cache_data
def load(name: str, folder: str = "ref") -> pd.DataFrame:
    return pd.read_csv((REF if folder == "ref" else PROC) / f"{name}.csv")


def mfmt(x: float, d: int = 1) -> str:
    """12345678 -> '12,3 M$' (French decimal comma)."""
    return f"{x / 1e6:,.{d}f}".replace(",", " ").replace(".", ",") + " M$"


def nfmt(x: float, d: int = 1) -> str:
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


SOURCES = load("sources").set_index("id")


def links(ids: str) -> str:
    """'S01,S10' -> markdown links (fall back to plain id when a source has no URL)."""
    out = []
    for sid in [i.strip() for i in str(ids).split(",") if i.strip()]:
        if sid in SOURCES.index and isinstance(SOURCES.loc[sid, "url"], str) and SOURCES.loc[sid, "url"]:
            out.append(f"[{sid}]({SOURCES.loc[sid, 'url']})")
        else:
            out.append(sid)
    return " · ".join(out)


def md_table(df: pd.DataFrame, link_cols: tuple[str, ...] = ("source_ids",)) -> str:
    """Render a DataFrame as a markdown table, turning source-id columns into links."""
    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    rows = []
    for _, r in df.iterrows():
        cells = [links(r[c]) if c in link_cols else str(r[c]).replace("|", "/") for c in df.columns]
        rows.append("| " + " | ".join(cells) + " |")
    return head + "\n".join(rows)


def status_tag(s: str) -> str:
    s0 = s.lower()
    cls = ("ok" if s0.startswith("établi") else "bad" if s0.startswith(("réfut", "contrad")) else
           "warn" if s0.startswith(("probable", "hypoth", "non reproduit", "non vérifi", "non établi")) else "gray")
    return f'<span class="tag {cls}">{s}</span>'


FLOWS = load("fts_ebola_flows", "proc")
RECIP = load("recipients", "proc")
DONORS = load("donors", "proc")
HF = load("hf_rounds", "proc")

inc = FLOWS[FLOWS.boundary == "Incoming"]
itn = FLOWS[FLOWS.boundary == "Internal"]
INC_TOTAL, INC_SHARED = inc.total_usd.sum(), inc.shared_usd.sum()
HF_TOTAL = itn.amount_usd.sum()
HF_EBOLA_ONLY = itn.loc[itn.ebola_only, "amount_usd"].sum()
HF_US = itn.loc[itn.hf_label == "US", "amount_usd"].sum()


# ---------------------------------------------------------------- pages
def page_synthese() -> None:
    st.title("Fonds de la riposte Ebola en RDC (2026)")
    st.caption(f"Tableau de suivi indépendant · données OCHA FTS du {DATA_DATE} · sources publiques uniquement")
    st.markdown(
        '<div class="note"><b>Lecture prudente.</b> Un écart de traçabilité n\'est pas une preuve de détournement. '
        "Aucune source publique consultée n'établit de détournement. Chaque chiffre renvoie à sa source "
        "et à un niveau de preuve (page « Registre des vérifications »).</div>",
        unsafe_allow_html=True,
    )
    c = st.columns(5)
    c[0].metric("Annoncé comme décaissé (Africa CDC)", "962 M$", help="926,66 M$ selon d'autres citations de Kaseya")
    c[1].metric("Déclaré reçu par 25 partenaires", "226,3 M$", help="INSP, 2 octobre 2026")
    c[2].metric("Écart à retracer", "≈ 700–742 M$", help="962 − 220 = 742 ; 926,66 − 226,3 = 700")
    c[3].metric("Visible dans FTS (flux entrants)", mfmt(INC_TOTAL), help="Flux multi-pays inclus")
    c[4].metric("Annoncé par les États-Unis", "887 M$", help="Cumul au 23 septembre 2026")

    left, right = st.columns([3, 2])
    with left:
        st.subheader("De l'annonce à la dépense déclarée")
        df = pd.DataFrame(
            {"étape": ["Annoncé décaissé (Africa CDC)", "Déclaré reçu (25 partenaires)", "Déclaré dépensé",
                       "Solde par soustraction", "Visible dans FTS (entrant)"],
             "M$": [962, 226.344, 127.374, 98.97, INC_TOTAL / 1e6]})
        chart = (alt.Chart(df).mark_bar(color="#0E5A66").encode(
            y=alt.Y("étape:N", sort=None, title=None), x=alt.X("M$:Q", title="millions de dollars"),
            tooltip=["étape", alt.Tooltip("M$:Q", format=",.1f")])
            + alt.Chart(df).mark_text(align="left", dx=4).encode(
                y=alt.Y("étape:N", sort=None), x="M$:Q", text=alt.Text("M$:Q", format=",.1f")))
        st.altair_chart(chart.properties(height=240), width="stretch")
        st.caption("Le solde de 98,97 M$ est calculé (226,344 − 127,374). L'INSP annonce 89,326 M$ : voir « Chiffres officiels ».")
    with right:
        st.subheader("Ce qu'il faut retenir")
        st.markdown(
            "- **Le défaut de reporting est documenté** : 25 partenaires sur 94 à 97 ont répondu à l'INSP ; "
            "72 structures sont soumises à accréditation.\n"
            "- **Le chiffre de départ est incertain** : 962 ou 926,66 M$.\n"
            f"- **Les États-Unis pèsent 92 % du 962 M$** s'ils y sont inclus ; seuls ~7 % de leur annonce apparaissent "
            f"comme flux Ebola directs dans FTS ({mfmt(inc[inc.source_org.str.contains('United States')].total_usd.sum())}).\n"
            f"- **Le Fonds humanitaire a alloué {mfmt(HF_TOTAL)}** citant Ebola, dont seulement {mfmt(HF_EBOLA_ONLY)} "
            "pour des projets purement Ebola.\n"
            "- **Aucun détournement n'est établi** ; les fonds seraient chez les partenaires, pas au Trésor."
        )

    st.subheader("Niveau de preuve des constats")
    claims = load("claims")
    counts = claims.status.str.split(" ").str[0].value_counts()
    cols = st.columns(len(counts))
    for col, (k, v) in zip(cols, counts.items()):
        col.markdown(f"{status_tag(k)}<br><b style='font-size:1.6rem'>{v}</b>", unsafe_allow_html=True)
    st.caption("Détail et sources : page « Registre des vérifications ».")


def page_chiffres() -> None:
    st.header("Chiffres officiels et réconciliation")
    st.markdown("Chaque contrôle arithmétique ci-dessous est reproductible à partir des sources citées.")
    rec = load("reconciliation")
    rec.columns = ["Contrôle", "Calcul", "Résultat", "Lecture", "source_ids"]
    st.markdown(md_table(rec), unsafe_allow_html=True)
    st.subheader("Déclarations de référence")
    stm = pd.DataFrame([
        ("Africa CDC, 15 oct.", "962 M$ décaissés par les donateurs ; plus de 700 M$ inconnus des autorités ; moins de 30 % des partenaires ont participé", "S01"),
        ("Kaseya, cité par la presse", "Les fonds « existent » chez les partenaires, pas au gouvernement ; pas (encore) de détournement évoqué", "S03,S08"),
        ("INSP (Mwamba), 2 oct.", "25 partenaires sur ~94 ; engagements ~260 M$ ; 226,344 M$ perçus ; 127,374 M$ dépensés ; solde 89,326 M$", "S03,S09"),
        ("Ministre de la Santé (Kamba)", "25 organisations autorisées sur 97 ; accréditation obligatoire", "S06"),
        ("Ministre de la Communication (Muyaya)", "Les fonds ne transitent pas par le Trésor : ils vont directement aux partenaires de mise en œuvre", "S05"),
    ], columns=["Qui, quand", "Contenu (reformulé)", "source_ids"])
    st.markdown(md_table(stm), unsafe_allow_html=True)
    st.markdown(
        '<div class="note"><b>Deux incohérences à faire expliquer</b> : (1) 962 contre 926,66 M$ au départ ; '
        "(2) un solde de 89,326 M$ alors que 226,344 − 127,374 = 98,970 M$ (écart de 9,644 M$).</div>",
        unsafe_allow_html=True,
    )


def page_donateurs() -> None:
    st.header("Donateurs : annoncé contre visible dans FTS")
    st.caption("« Annoncé » = promesse ou montant déclaré par le bailleur. FTS exclut prêts, fonds de développement et contrats.")
    pl = load("pledges")
    fts = []
    for orgs in pl.fts_source_orgs.fillna(""):
        names = [o for o in orgs.split(";") if o]
        fts.append(DONORS[DONORS.source_org.isin(names)].total_usd.sum() / 1e6 if names else 0.0)
    pl["FTS Ebola (M$)"] = [round(x, 1) for x in fts]
    pl["Part visible"] = [f"{v / a * 100:.0f} %" for v, a in zip(fts, pl.announced_musd)]
    chart_df = pl.melt(id_vars="donor", value_vars=["announced_musd", "FTS Ebola (M$)"], var_name="série", value_name="M$")
    chart_df["série"] = chart_df["série"].map({"announced_musd": "Annoncé", "FTS Ebola (M$)": "Visible dans FTS"})
    ch = alt.Chart(chart_df).mark_bar().encode(
        y=alt.Y("donor:N", sort=list(pl.donor), title=None), x=alt.X("M$:Q", scale=alt.Scale(type="symlog")),
        color=alt.Color("série:N", scale=alt.Scale(range=["#0E5A66", "#E0A04A"])), yOffset="série:N",
        tooltip=["donor", "série", alt.Tooltip("M$:Q", format=",.1f")])
    st.altair_chart(ch.properties(height=380), width="stretch")
    st.caption("Échelle logarithmique symétrique pour rendre lisibles les petits bailleurs.")
    show = pl[["donor", "announced_musd", "FTS Ebola (M$)", "Part visible", "basis", "source_ids"]]
    show.columns = ["Bailleur", "Annoncé (M$)", "FTS Ebola (M$)", "Part visible", "Base de l'annonce", "source_ids"]
    st.markdown(md_table(show), unsafe_allow_html=True)
    st.markdown(
        '<div class="note"><b>Attention aux additions.</b> Selon le Département d\'État (communiqué du 5 août), les 350 M$ '
        "d'aide humanitaire passant par OCHA s'<i>ajoutent</i> à ses annonces directes (512 M$ à cette date, 887 M$ au 23 sept.). "
        "Les allocations « US » du Fonds humanitaire ne doivent donc pas être additionnées aux 887 M$.</div>",
        unsafe_allow_html=True,
    )
    st.subheader("Calendrier des annonces et événements")
    tl = load("timeline")
    tl.columns = ["Date", "Acteur", "Événement", "Montant (M$)", "Cumul (M$)", "source_ids"]
    st.markdown(md_table(tl.fillna("")), unsafe_allow_html=True)
    st.subheader("Tous les donateurs visibles dans FTS (flux Ebola entrants)")
    d = DONORS.copy()
    d["total_musd"] = (d.total_usd / 1e6).round(2)
    d["dont multi-pays (M$)"] = (d.shared_multi_country_usd / 1e6).round(2)
    st.dataframe(d[["source_org", "source_country", "total_musd", "dont multi-pays (M$)", "flows"]].rename(
        columns={"source_org": "Donateur", "source_country": "Pays", "total_musd": "Total (M$)", "flows": "Flux"}),
        width="stretch", hide_index=True)
    st.download_button("Télécharger (CSV)", d.to_csv(index=False).encode(), "donateurs_fts_ebola.csv", "text/csv")


def page_beneficiaires() -> None:
    st.header("Bénéficiaires dans FTS")
    st.caption(f"Flux dont la description cite Ebola ou Bundibugyo · export du {DATA_DATE} · "
               "« Direct » = reçu d'un bailleur ou du CERF ; « Via Fonds humanitaire » = allocation du fonds poolé.")
    r = RECIP.copy()
    r["Direct (M$)"] = (r.direct_usd / 1e6).round(2)
    r["Via Fonds humanitaire (M$)"] = (r.via_hf_usd / 1e6).round(2)
    r["Total (M$)"] = (r.total_usd / 1e6).round(2)
    c1, c2 = st.columns([2, 1])
    q = c1.text_input("Filtrer par nom")
    canal = c2.selectbox("Canal", ["Tous", "Direct seulement", "Via Fonds humanitaire seulement"])
    if q:
        r = r[r.fts_name.str.contains(q, case=False)]
    if canal == "Direct seulement":
        r = r[r.direct_usd > 0]
    elif canal.startswith("Via"):
        r = r[r.via_hf_usd > 0]
    top = r.sort_values("total_usd", ascending=False).head(20)
    long = top.melt(id_vars="fts_name", value_vars=["Direct (M$)", "Via Fonds humanitaire (M$)"], var_name="canal", value_name="M$")
    ch = alt.Chart(long).mark_bar().encode(
        y=alt.Y("fts_name:N", sort=list(top.fts_name), title=None), x=alt.X("M$:Q", title="M$"),
        color=alt.Color("canal:N", scale=alt.Scale(range=["#0E5A66", "#E0A04A"])), tooltip=["fts_name", "canal", "M$"])
    st.altair_chart(ch.properties(height=max(260, 24 * len(top))), width="stretch")
    st.dataframe(r[["fts_name", "Direct (M$)", "Via Fonds humanitaire (M$)", "Total (M$)", "direct_flows", "hf_flows"]].rename(
        columns={"fts_name": "Bénéficiaire (nom FTS)", "direct_flows": "Flux directs", "hf_flows": "Flux Fonds"}),
        width="stretch", hide_index=True)
    st.markdown(
        '<div class="note"><b>Deux précautions.</b> (1) Les flux « multi-pays » (RDC et Ouganda) affichent 0 $ dans la colonne '
        f"principale de FTS ; je les ai ajoutés ({mfmt(INC_SHARED)}) mais la part destinée à la RDC est inconnue. "
        "(2) « iMC Worldwide » est le nom FTS ; son identité avec International Medical Corps est probable, non prouvée.</div>",
        unsafe_allow_html=True,
    )
    st.download_button("Télécharger (CSV)", RECIP.to_csv(index=False).encode(), "beneficiaires_fts_ebola.csv", "text/csv")


def page_fonds() -> None:
    st.header("Fonds humanitaire RDC (fonds poolé)")
    st.markdown(
        f"Les descriptions FTS des allocations contiennent le **tour d'allocation**, une étiquette **US / non-US**, les **dates de projet** "
        f"et les **types d'urgence**. Total cité Ebola : **{mfmt(HF_TOTAL)}**, dont **{mfmt(HF_US)}** étiquetés « US » "
        f"et seulement **{mfmt(HF_EBOLA_ONLY)}** sur des projets purement Ebola."
    )
    h = HF.copy()
    h["M$"] = (h.total_usd / 1e6).round(2)
    h["dont purement Ebola (M$)"] = (h.ebola_only_usd / 1e6).round(2)
    ch = alt.Chart(h).mark_bar().encode(
        x=alt.X("round:N", title=None, sort=None), y=alt.Y("M$:Q"), color=alt.Color("label:N", title="Étiquette"),
        tooltip=["round", "label", "M$", "flows"])
    st.altair_chart(ch.properties(height=280), width="stretch")
    st.markdown(md_table(h[["round", "label", "M$", "dont purement Ebola (M$)", "flows"]].rename(
        columns={"round": "Tour", "label": "Étiquette", "flows": "Flux"}), link_cols=()))
    st.markdown(
        '<div class="note">Projets « mixtes » : le type d\'urgence cite Ebola <b>avec</b> des conflits ou des déplacements. '
        "Les présenter comme « fonds Ebola » serait trompeur. L'allocation RA 2 du 26 mars 2026 (145,9 M$, avant l'épidémie, "
        f"{links('S17')}) est distincte.</div>",
        unsafe_allow_html=True,
    )
    contrib = load("hf_contributions_all_topics", "proc")
    st.subheader("Contributions reçues par le Fonds en 2026 (tous sujets)")
    contrib["M$"] = (contrib.amount_usd / 1e6).round(1)
    st.dataframe(contrib[["source_org", "M$"]].rename(columns={"source_org": "Source"}), hide_index=True, width="stretch")
    st.subheader("Contrôle d'éligibilité des bénéficiaires (liste d'août 2025)")
    el = load("hf_eligibility_check")
    st.markdown(
        f"{(el.match != 'Absent').sum()} des {len(el)} bénéficiaires figurent sur la liste ({links('S18')}) ; "
        "une absence peut venir d'un ajout postérieur à août 2025."
    )
    el.columns = ["Nom FTS", "Entrée de la liste", "Rapprochement"]
    st.dataframe(el, hide_index=True, width="stretch")
    st.subheader("Allocations et dates de début de projet")
    a = itn[["flow_id", "destination_org", "hf_round", "hf_label", "hf_start", "ebola_only", "amount_usd", "fts_url"]].copy()
    a["amount_usd"] = (a.amount_usd / 1e6).round(2)
    a.columns = ["Flux", "Bénéficiaire", "Tour", "Étiquette", "Début", "Purement Ebola", "M$", "Lien FTS"]
    st.dataframe(a.sort_values("Début"), hide_index=True, width="stretch",
                 column_config={"Lien FTS": st.column_config.LinkColumn("Lien FTS", display_text="ouvrir")})
    st.caption("Plusieurs projets débutent après le 12 octobre alors que FTS les marque « payés » : "
               "ces fonds ne peuvent pas encore avoir été dépensés.")


def page_fiches() -> None:
    st.header("Fiches des bénéficiaires")
    st.caption("Chaque case est sourcée ; « Aucun trouvé » signifie que mes recherches web n'ont rien remonté, pas qu'il n'existe rien.")
    p = load("ngo_profiles")
    choix = st.selectbox("Organisation", p.display_name)
    row = p[p.display_name == choix].iloc[0]
    st.subheader(row.display_name)
    c1, c2 = st.columns(2)
    c1.markdown(f"**Type** : {row.type}\n\n**Création** : {row.founded}\n\n**Présence en RDC** : {row.drc_presence}")
    c2.markdown(f"**Comptes publiés** : {row.accounts_public}\n\n**Incident documenté** : {row.incidents_found}\n\n"
                f"**Éligibilité FH (août 2025)** : {row.eligible_hf_aug2025}")
    st.markdown(f"**Rôle dans la riposte 2026** : {row.role_2026}")
    rec = RECIP[RECIP.fts_name == row.fts_name]
    if len(rec):
        r0 = rec.iloc[0]
        st.markdown(f"**Dans FTS (Ebola)** : {mfmt(r0.direct_usd)} directs · {mfmt(r0.via_hf_usd)} via le Fonds humanitaire")
    if row.caveat != "—":
        st.markdown(f'<div class="note">{row.caveat}</div>', unsafe_allow_html=True)
    st.markdown("**Sources** : " + links(row.source_ids), unsafe_allow_html=True)
    with st.expander("Tableau complet"):
        st.dataframe(p.drop(columns=["fts_name"]), hide_index=True, width="stretch")


def page_registre() -> None:
    st.header("Registre des vérifications")
    st.caption("Chaque affirmation du dossier avec son niveau de preuve, ses sources et la prochaine étape.")
    cl = load("claims")
    statuts = sorted(cl.status.unique())
    sel = st.multiselect("Filtrer par statut", statuts, default=statuts)
    cl = cl[cl.status.isin(sel)]
    contribs = inbox.load_contributions()
    n_by = contribs.claim_id.value_counts().to_dict() if len(contribs) else {}
    for _, r in cl.iterrows():
        with st.container(border=True):
            st.markdown(f"**{r.id}** {status_tag(r.status)}  \n{r.claim}", unsafe_allow_html=True)
            st.markdown(f"*Preuve* : {r.evidence}")
            st.markdown(f"*Sources* : {links(r.source_ids)} · *Prochaine étape* : {r.next_step}")
            if n_by.get(r.id):
                st.markdown(f"**{n_by[r.id]} contribution(s) reçue(s)** : voir la page « Contribuer ».")


def page_methode() -> None:
    st.header("Méthodologie, limites et sources")
    st.markdown(
        f"""
**Données.** Exports OCHA FTS « RDC 2026 » du {DATA_DATE} (flux, vue complète, bénéficiaires), fournis par l'utilisateur.
Un flux est dit « Ebola » si sa description cite *Ebola* ou *Bundibugyo*. Le mot-clé FTS `EBOLA2026` n'est pas dans l'export :
les totaux sont donc **un plancher**. Les exports n'ont **pas de date de flux** ; les dates de projet proviennent des descriptions
du Fonds humanitaire.

**Flux entrants et internes.** « Entrant » = argent venant d'un bailleur ou du CERF. « Interne » = allocation du Fonds humanitaire
à un partenaire. Les deux ne s'additionnent pas sans précaution : les contributions des bailleurs au Fonds ne sont pas décrites comme Ebola.

**Flux multi-pays.** FTS affiche 0 $ en « Montant » et la somme en « Amount shared on boundary » pour les flux couvrant plusieurs pays.
Ils sont inclus dans les totaux et signalés séparément ; la part destinée à la RDC est inconnue.

**Niveaux de preuve.** *Établi* (source primaire lue ou calcul reproductible) · *Déclaré* (déclaration officielle non auditée) ·
*Probable / Hypothèse* · *Contradictoire* · *Non vérifié / Non reproduit* · *Réfuté*.

**Limites.** FTS repose sur des déclarations volontaires, avec retard, et ne contient ni prêts, ni fonds de développement, ni contrats.
Le tracker anonyme du 15 octobre n'est pas une source officielle ; il est recoupé quand c'est possible. Le post X d'origine n'a pas pu être lu.
Les fiches ONG sont limitées aux informations publiques trouvées ; l'absence d'incident ne vaut pas certificat.
Cet outil n'accuse personne : il organise des écarts à faire expliquer.

**Mise à jour des données.** Placer de nouveaux exports FTS dans `data/raw/`, puis `python scripts/build_data.py`.
Les tables documentées se modifient dans `scripts/build_reference.py` (`python scripts/build_reference.py`).
"""
    )
    st.subheader("Toutes les sources")
    s = load("sources").copy()
    s["Lien"] = s.url.fillna("")
    st.dataframe(s[["id", "title", "publisher", "date", "type", "reliability", "Lien"]].rename(
        columns={"id": "ID", "title": "Titre", "publisher": "Éditeur", "date": "Date", "type": "Type", "reliability": "Fiabilité"}),
        hide_index=True, width="stretch",
        column_config={"Lien": st.column_config.LinkColumn("Lien", display_text="ouvrir")})


def get_secret(name: str):
    try:
        return st.secrets.get(name)
    except Exception:  # no secrets file configured
        return None


def page_contribuer() -> None:
    st.header("Contribuer : réponses et documents")
    st.markdown(
        "Déposez ici une **réponse** (Africa CDC, INSP, OCHA, une ONG…), un **document** (rapport, audit, liste de partenaires) "
        "ou des **données** (export FTS, USAspending). Chaque dépôt est enregistré comme **« Non vérifié »** et relié, si vous le "
        "souhaitez, à un constat du registre. Il est ensuite relu et recoupé avant d'entrer dans l'analyse."
    )
    pwd = get_secret("CONTRIB_PASSWORD")
    if pwd:
        if st.text_input("Mot de passe", type="password") != pwd:
            st.info("Saisissez le mot de passe pour accéder à cette page.")
            return
    else:
        st.warning("Page ouverte : toute personne ayant le lien peut déposer. Définissez `CONTRIB_PASSWORD` dans les secrets pour la protéger.")
    st.markdown(
        '<div class="note"><b>Avant de déposer.</b> Ne déposez pas de données personnelles non publiques ni de documents '
        "dont la diffusion vous exposerait. Sur Streamlit Community Cloud, le disque est <b>éphémère</b> : "
        "exportez régulièrement le dossier (onglet « Exporter »).</div>",
        unsafe_allow_html=True,
    )
    t1, t2, t3, t4 = st.tabs(["Déposer", "Journal", "Exporter pour la recherche", "Ce que nous cherchons"])
    claims = load("claims")
    n = st.session_state.setdefault("form_n", 0)

    with t1:
        if st.session_state.get("flash"):
            st.success(st.session_state.pop("flash"))
        c1, c2 = st.columns(2)
        who = c1.text_input("Nom (facultatif)", key=f"who{n}")
        org = c2.text_input("Organisation (facultatif)", key=f"org{n}")
        kind = c1.selectbox("Nature du dépôt", inbox.KINDS, key=f"kind{n}")
        pos = c2.selectbox("Position par rapport au constat", inbox.POSITIONS, key=f"pos{n}")
        options = ["(aucun / nouveau constat)"] + [f"{r.id} – {r.claim[:90]}" for r in claims.itertuples()]
        claim_sel = st.selectbox("Constat concerné", options, key=f"claim{n}")
        c3, c4 = st.columns(2)
        sdate = c3.date_input("Date du document ou de la réponse", value=None, key=f"date{n}")
        url = c4.text_input("Lien de la source (si public)", key=f"url{n}", placeholder="https://…")
        msg = st.text_area("Réponse ou précision", key=f"msg{n}", height=140,
                           placeholder="Ex. : l'INSP indique que le solde de 89,3 M$ inclut… (citez le passage et sa source)")
        files = st.file_uploader("Fichiers (PDF, CSV, XLSX, DOCX, TXT, JSON, images ; 15 Mo max, 5 fichiers)",
                                 type=sorted(inbox.ALLOWED), accept_multiple_files=True, key=f"files{n}")
        payload = [(f.name, f.getvalue()) for f in files or []]
        for name, data in payload:
            sn = inbox.sniff_table(name, data)
            if sn:
                label = "Export FTS détecté" if sn["kind"] == "fts" else "Tableau détecté"
                st.caption(f"**{name}** : {label}. Aperçu des premières lignes.")
                st.dataframe(sn["preview"], width="stretch")
        ok = st.checkbox("Je confirme que ce dépôt ne contient pas de données personnelles non publiques.", key=f"ok{n}")
        if st.button("Enregistrer", type="primary", disabled=not ok, key=f"save{n}"):
            meta = {"contributor": who, "organisation": org, "kind": kind, "position": pos,
                    "claim_id": "" if claim_sel.startswith("(") else claim_sel.split(" – ")[0],
                    "message": msg, "source_url": url, "source_date": sdate or ""}
            try:
                rec = inbox.save_contribution(meta, payload)
            except ValueError as e:
                st.error(str(e))
            else:
                st.session_state["flash"] = f"Enregistré (référence {rec['id']}, statut « Non vérifié »)."
                st.session_state["form_n"] = n + 1
                st.rerun()

    with t2:
        df = inbox.load_contributions()
        if df.empty:
            st.info("Aucune contribution pour l'instant.")
        else:
            st.metric("Contributions", len(df))
            show = df.assign(fichiers=df.files.apply(lambda f: ", ".join(x["name"] for x in f)))
            st.dataframe(show[["id", "received_utc", "kind", "claim_id", "position", "organisation", "fichiers", "status"]].rename(
                columns={"received_utc": "Reçu (UTC)", "kind": "Nature", "claim_id": "Constat", "position": "Position",
                         "organisation": "Organisation", "status": "Statut"}), hide_index=True, width="stretch")
            for r in df.head(30).itertuples():
                with st.expander(f"{r.id} · {r.received_utc} · {r.kind}"):
                    st.markdown(f"**Constat** : {r.claim_id or '—'} · **Position** : {r.position} · **Statut** : {r.status}")
                    if r.message:
                        st.write(r.message)
                    if r.source_url:
                        st.markdown(f"Source : {r.source_url}")
                    for f in r.files:
                        path = inbox.INBOX / "files" / r.id / f["name"]
                        if path.exists():
                            st.download_button(f"{f['name']} ({f['bytes'] // 1024} Ko)", path.read_bytes(), f["name"], key=f"dl{r.id}{f['name']}")
                            st.caption(f"SHA-256 : {f['sha256']}")

    with t3:
        st.markdown(
            "Le dossier exporté contient `contributions.csv`, `responses.jsonl` et tous les fichiers déposés.\n\n"
            "**Pour continuer la recherche** : téléchargez le zip, puis déposez-le dans la conversation d'analyse. "
            "Chaque élément sera relu, recoupé avec les sources existantes, puis intégré au registre avec un niveau de preuve "
            "(*Établi*, *Déclaré*, *Contradictoire*…)."
        )
        st.download_button("Télécharger le dossier (zip)", inbox.export_zip(), "contributions_ebola_rdc.zip", "application/zip")

    with t4:
        st.markdown(
            "**Documents les plus utiles**\n"
            "1. Ventilation par bailleur du montant de 962 M$ (Africa CDC) et source du chiffre de 926,66 M$.\n"
            "2. Liste nominative des 25 partenaires qui ont déclaré à l'INSP, et explication du solde de 89,3 M$ (INSP).\n"
            "3. Liste à jour des partenaires éligibles du Fonds humanitaire RDC (OCHA), notamment Danish Refugee Council.\n"
            "4. Fiches USAspending des awards (International Medical Corps, Perimeter Knightworks, FHI 360…).\n"
            "5. Rapports financiers audités des principaux bénéficiaires, et lettres de réponse aux demandes de l'INSP."
        )
        open_q = claims[~claims.status.str.startswith("Établi")]
        open_q = open_q[open_q.next_step != "—"][["id", "claim", "status", "next_step"]]
        open_q.columns = ["ID", "Constat", "Statut", "Ce qu'il faudrait obtenir"]
        st.dataframe(open_q, hide_index=True, width="stretch")


PAGES = {
    "Synthèse": page_synthese,
    "Chiffres officiels": page_chiffres,
    "Donateurs": page_donateurs,
    "Bénéficiaires (FTS)": page_beneficiaires,
    "Fonds humanitaire RDC": page_fonds,
    "Fiches ONG": page_fiches,
    "Registre des vérifications": page_registre,
    "Contribuer (réponses, documents)": page_contribuer,
    "Méthodologie et sources": page_methode,
}

with st.sidebar:
    st.markdown("### Fonds Ebola RDC 2026")
    page = st.radio("Navigation", list(PAGES), label_visibility="collapsed")
    st.caption(f"Données FTS : {DATA_DATE}\n\nOutil d'analyse indépendant, sources publiques. Aucune accusation.")

PAGES[page]()
