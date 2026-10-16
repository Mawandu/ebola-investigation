# Suivi des fonds de la riposte Ebola en RDC (2026)

Application Streamlit d'analyse indépendante, fondée uniquement sur des **sources publiques**.
Elle confronte les montants annoncés par les bailleurs, les déclarations d'Africa CDC et de l'INSP,
et les flux enregistrés par **OCHA FTS**, et documente chaque affirmation avec son niveau de preuve.

> Un écart de traçabilité n'est pas une preuve de détournement. Aucune source consultée n'établit de détournement.
> L'outil organise des écarts à faire expliquer ; il n'accuse personne.

## Pages
Synthèse · Chiffres officiels (réconciliation) · Donateurs (annoncé contre FTS, calendrier) · Bénéficiaires (FTS) ·
Fonds humanitaire RDC (tours, étiquettes US, éligibilité) · Fiches ONG · Registre des vérifications · **Contribuer (réponses, documents)** · Méthodologie et sources.

## Lancer en local
```bash
python -m venv .venv && source .venv/bin/activate     # Windows : .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
python tests/test_data.py                              # contrôles de cohérence
```

## Déployer sur Streamlit Community Cloud
1. Pousser ce dossier dans un dépôt GitHub (public ou privé).
2. Sur https://share.streamlit.io : *Create app* → choisir le dépôt, la branche, fichier principal `app.py`.
3. Déployer. Aucun secret n'est nécessaire (aucune API externe).

## Structure
```
app.py                       application (9 pages)
inbox.py                     boîte de dépôt (réponses, fichiers, export zip)
data/raw/                    exports OCHA FTS bruts (RDC 2026, 16 oct. 2026)
data/inbox/                  dépôts reçus (ignorés par git, voir ci-dessous)
data/processed/              tables calculées par scripts/build_data.py
data/reference/              tables documentées (sources, registre des vérifications, fiches, annonces, calendrier)
scripts/build_data.py        FTS bruts -> tables traitées (filtre Ebola, flux multi-pays, métadonnées du Fonds humanitaire)
scripts/build_reference.py   tables documentées ; chaque ligne porte des identifiants de source (S01…)
tests/test_data.py           totaux, arithmétique, résolution des sources, exécution de toutes les pages
```

## Page « Contribuer »
Permet de déposer une réponse (Africa CDC, INSP, OCHA, ONG…), un document ou des données (export FTS, USAspending), relié à un constat du registre.
- Chaque dépôt est enregistré **« Non vérifié »** (message, lien, date, position, empreinte SHA-256 des fichiers).
- Types acceptés : pdf, csv, xlsx/xls, docx, txt, md, json, png, jpg ; 15 Mo et 5 fichiers max ; les CSV/XLSX sont prévisualisés et les exports FTS détectés.
- Onglet **Exporter pour la recherche** : zip (`contributions.csv`, `responses.jsonl`, fichiers) à redéposer dans la conversation d'analyse pour relecture et intégration au registre.
- **Protection** : définir `CONTRIB_PASSWORD` dans *Settings → Secrets* de Streamlit Cloud (`CONTRIB_PASSWORD = "…"`). Sans cela, la page est ouverte à toute personne ayant le lien.
- **Persistance** : le disque de Streamlit Community Cloud est éphémère (redémarrage = perte). Exporter régulièrement ; pour un stockage durable, brancher un service externe (non inclus).

## Mettre à jour
- **Nouveaux flux FTS** : remplacer les fichiers de `data/raw/` (export « full view »), puis `python scripts/build_data.py`.
- **Nouvelles sources ou constats** : éditer `scripts/build_reference.py`, puis `python scripts/build_reference.py`.
  Tout identifiant de source cité doit exister dans `sources`, sinon `tests/test_data.py` échoue.

## Limites connues
- Le filtre « Ebola » repose sur les **descriptions** FTS ; le mot-clé FTS `EBOLA2026` n'est pas dans l'export, donc les totaux sont un plancher.
- Les exports FTS n'ont **pas de date de flux** ; les dates de projet viennent des descriptions du Fonds humanitaire.
- Les flux multi-pays (RDC + Ouganda…) sont comptés en entier mais la part destinée à la RDC est inconnue.
- FTS ne contient ni prêts, ni fonds de développement, ni contrats : un faible taux de visibilité n'est pas une anomalie en soi.
- « iMC Worldwide » (nom FTS) = International Medical Corps : **probable, non prouvé**.
- Le post X d'origine et le tracker anonyme (captures du 15 oct.) ne sont pas des sources officielles.
- Fiches ONG : dates de création marquées « non sourcé » à confirmer ; « Aucun trouvé » ne vaut pas certificat.
