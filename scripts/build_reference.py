"""Hand-curated reference tables (sources, claims register, NGO profiles, announced pledges, eligibility).
Every entry carries source ids that resolve in sources.csv. Edit here, then run:  python scripts/build_reference.py
"""
import pathlib
import pandas as pd

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "reference"
OUT.mkdir(parents=True, exist_ok=True)

U = "https://"
sources = [
 # id, title, publisher, date, url, type, reliability
 ("S01","Communiqué d'Africa CDC sur le financement de la riposte à l'épidémie d'Ebola en RDC","Africa CDC","2026-10-15",U+"africacdc.org/news-item/communique-dafrica-cdc-sur-le-financement-de-la-riposte-a-lepidemie-debola-en-rdc/","Primaire","Haute (déclaration officielle, chiffres non audités)"),
 ("S02","Communiqué d'Africa CDC (reprise)","Actualite.cd","2026-10-15",U+"actualite.cd/2026/10/15/communique-dafrica-cdc-sur-le-financement-de-la-riposte-lepidemie-debola-en-rdc","Presse","Moyenne"),
 ("S03","Ebola en RDC : gestion opaque des fonds… au moins 700 millions USD introuvables","Actualite.cd","2026-10-15",U+"actualite.cd/2026/10/15/ebola-en-rdc-gestion-opaque-des-fonds-alloues-la-riposte-au-moins-700-millions-usd","Presse","Moyenne (cite 926,66 M$)"),
 ("S04","RDC : le CDC Afrique exige des comptes sur plus de 700 millions USD","Radio Okapi","2026-10-15",U+"www.radiookapi.net/2026/10/15/actualite/sante/rdc-le-cdc-afrique-exige-des-comptes-sur-plus-de-700-millions-usd","Presse","Moyenne (cite 962 M$)"),
 ("S05","RDC : 72 structures n'ayant pas justifié l'utilisation de fonds Ebola interdites d'opérer","Radio Okapi","2026-10-16",U+"www.radiookapi.net/2026/10/16/actualite/sante/rdc-72-structures-nayant-pas-justifie-lutilisation-de-fonds-ebola","Presse","Moyenne"),
 ("S06","RDC : accréditation obligatoire pour les acteurs de la riposte Ebola","Congo Quotidien","2026-10-16",U+"www.congoquotidien.com/2026/10/16/accreditation-obligatoire-riposte-ebola/","Presse","Moyenne (25 organisations sur 97)"),
 ("S07","Ebola en RDC : 700 millions de dollars non retracés dans la riposte","Congo Quotidien","2026-10-15",U+"www.congoquotidien.com/2026/10/15/fonds-riposte-ebola-non-retraces/","Presse","Moyenne (cite 926,66 M$)"),
 ("S08","DR Congo Ebola Funds: US$700 Million Still Untraced","Rio Times","2026-10-15",U+"www.riotimesonline.com/dr-congo-ebola-funds-700-million-2026/","Presse","Moyenne"),
 ("S09","RDC : plus de 700 millions de dollars de la riposte contre Ebola restent sans traçabilité","Afrik.com","2026-10-16",U+"www.afrik.com/rdc-plus-de-700-millions-de-dollars-de-la-riposte-contre-ebola-restent-sans-tracabilite","Presse","Moyenne (chiffres INSP du 2 oct.)"),
 ("S10","United States pledges additional life-saving health assistance (Ebola)","U.S. Department of State","2026-09-23",U+"www.state.gov/releases/office-of-the-spokesman/2026/09/united-states-pledges-additional-life-saving-health-assistance-in-response-to-ebola-outbreak/","Primaire","Haute (annonce, pas un décaissement)"),
 ("S11","G20 Chair's statement: Ebola ministerial","U.S. Department of State","2026-09-30",U+"www.state.gov/releases/office-of-the-spokesman/2026/09/g20-chairs-statement-ebola-ministerial-on-accelerating-collective-action-to-defeat-ebola/","Primaire","Haute (annonces)"),
 ("S12","2026 Ebola Outbreak: Frequently Asked Questions (R49484)","Congressional Research Service","2026-10",U+"www.congress.gov/crs-product/R49484","Primaire","Haute"),
 ("S13","Almost $3 Billion Raised For DRC's Ebola Outbreak","Health Policy Watch","2026-09-24",U+"healthpolicy-watch.news/almost-3-billion-raised-for-drcs-ebola-outbreak-as-focus-shifts-to-nord-kivu/","Presse spécialisée","Moyenne (additionne 887 + 267 M$, contredit S10)"),
 ("S14","Ebola watch: Almost $3 billion mobilised so far","The Standard","2026-09",U+"www.standardmedia.co.ke/africa/article/2001558679/ebola-watch-almost-3-billion-mobilised-so-far-leaders-want-every-dollar-tracked","Presse","Moyenne (2,997 Md$ selon Kaseya)"),
 ("S15","Global Leaders Pledge $470 Million to End Ebola Outbreak in the DRC","TopAfricaNews","2026-10-01",U+"www.topafricanews.com/2026/10/01/global-leaders-pledge-470-million-to-end-ebola-outbreak-in-the-drc/","Presse","Moyenne (reprend le communiqué du G20)"),
 ("S16","Ebola outbreak 2026","OCHA","2026-10",U+"www.unocha.org/ebola-outbreak-2026","Primaire","Haute"),
 ("S17","Énoncé du Coordonnateur humanitaire – FH RDC – Allocation Réserve 2 (2026)","OCHA RDC","2026-03-26",U+"www.unocha.org/publications/report/democratic-republic-congo/enonce-du-coordonnateur-humanitaire-en-rdc-fonds-humanitaire-en-rdc-allocation-reserve-2-2026","Primaire","Haute (PDF fourni par l'utilisateur)"),
 ("S18","FH RDC : liste des partenaires éligibles, août 2025","OCHA RDC","2025-08","","Primaire","Haute (PDF fourni par l'utilisateur ; pas d'URL directe obtenue)"),
 ("S19","FH RDC : liste des partenaires éligibles, avril 2025 (page)","OCHA RDC","2025-04",U+"www.unocha.org/publications/report/democratic-republic-congo/rd-congo-fonds-humanitaire-liste-des-partenaires-eligibles-avril-2025","Primaire","Haute"),
 ("S20","OCHA FTS – exports RDC 2026 (flows, full view, recipients)","OCHA FTS","2026-10-16",U+"fts.unocha.org/countries/52/flows/2026","Jeu de données","Haute (déclarations volontaires, retards)"),
 ("S21","IMC – Ebola Outbreak, Ituri – Situation Report #1","International Medical Corps","2026-05-15",U+"cdn1.internationalmedicalcorps.org/wp-content/uploads/2026/05/IntlMedCorps-DRC_Ebola_Ituri_SitRep01.pdf","Primaire (ONG)","Moyenne (auto-déclaration)"),
 ("S22","DR Congo: New centre opens at heart of record Ebola outbreak","ONU Info","2026-08",U+"news.un.org/en/story/2026/08/1168064","Presse institutionnelle","Haute"),
 ("S23","Ebola Response Update – June 12, 2026","U.S. Department of State (miroir GlobalSecurity)","2026-06-12",U+"www.globalsecurity.org/security/library/news/2026/06/sec-260612-state01.htm","Primaire (miroir)","Moyenne à haute"),
 ("S24","Ebola Response Update – May 29, 2026","U.S. Department of State (miroir GlobalSecurity)","2026-05-29",U+"www.globalsecurity.org/security/library/news/2026/05/sec-260529-state01.htm","Primaire (miroir)","Moyenne à haute"),
 ("S25","International Medical Corps – évaluation","CharityWatch","2025",U+"www.charitywatch.org/charities/international-medical-corps","Évaluateur indépendant","Moyenne à haute"),
 ("S26","IMC Worldwide (société de conseil) acquise par DT Global","Infrastructure Global","2022",U+"infra.global/international-development-consultancy-imc-worldwide-acquired-by-dt-global/","Presse spécialisée","Moyenne"),
 ("S27","DRC: Ebola epidemic, an emergency declared","Solidarités International","2026",U+"www.solidarites.org/en/press/drc-ebola-epidemic-an-emergency-declared/","Primaire (ONG)","Moyenne (auto-déclaration)"),
 ("S28","DRC: Over 180 children dead in Ebola outbreak","Save the Children","2026-07-22",U+"www.savethechildren.org/us/about-us/media-and-news/2026-press-releases/drc-over-180-children-dead-ebola-outbreak-thousands","Primaire (ONG)","Moyenne (auto-déclaration)"),
 ("S29","DR Congo: Ebola outbreak, a crisis within a neglected crisis","Norwegian Refugee Council","2026-07",U+"nrc.no/news/2026/dr-congo-ebola-outbreak-a-crisis-within-a-neglected-crisis","Primaire (ONG)","Moyenne (auto-déclaration)"),
 ("S30","Ebola in Ituri: ALIMA's integrated approach","MedAngel / ALIMA","2026-09",U+"www.medangel.org/ebola-alima-innovative-approach/","Primaire (ONG, relais)","Moyenne"),
 ("S31","Ituri : renforcement des prestataires de soins pour prévenir Ebola","ACP","2026-07",U+"acp.cd/science-sante-environnement/ituri-renforcement-des-prestataires-de-soins-de-sante-pour-prevenir-le-virus-ebola/","Presse (agence nationale)","Moyenne"),
 ("S32","Ituri : remise de médicaments par l'UNICEF pour la gratuité des soins à Bambu","ACP","2026-08",U+"acp.cd/science-sante-environnement/ituri-remise-de-medicaments-par-lunicef-pour-la-gratuite-de-soins-a-bambu/","Presse (agence nationale)","Moyenne"),
 ("S33","Ebola in DR Congo: a crisis within a crisis","Norad","2026",U+"www.norad.no/en/news/news/2026/ebola-in-dr-congo-the-infection-is-spreading-rapidly/","Primaire","Haute"),
 ("S34","Save the Children – Democratic Congo","Save the Children International","2026",U+"dev.savethechildren.net/democratic-congo","Primaire (ONG)","Moyenne"),
 ("S35","Solidarités international (article)","Wikipédia","2026",U+"en.wikipedia.org/wiki/Solidarit%C3%A9s_international","Encyclopédie","Moyenne (date de création)"),
 ("S36","Save the Children (article)","Wikipédia","2026",U+"en.wikipedia.org/wiki/Save_the_Children","Encyclopédie","Moyenne (date de création)"),
 ("S37","Tracker « DRC Ebola response 2026: funding tracker by recipient » (captures du 15 oct.)","Auteur anonyme","2026-10-15","","Secondaire anonyme","Faible à moyenne : recoupé partiellement avec S20"),
 ("S38","Post @TJMufuta relayant Kaseya","X","2026-10",U+"x.com/TJMufuta/status/2110845648731881982","Réseau social","Non lu (accès bloqué pour l'outil)"),
 ("S39","Ebola en RDC : 700 M$… (INSP, 2 oct. : 25 partenaires sur ~94)","Actualite.cd / Rio Times","2026-10-02","","Presse","Voir S03, S08, S09"),
]

sources += [
 ("S40","Ebola Response Update – August 5, 2026 (extrait du communiqué du Département d'État)","U.S. Department of State (via Primary News Source)","2026-08-05",U+"primarynewssource.org/sourcedocument/ebola-response-update-august-5-2026/","Primaire (extrait)","Moyenne à haute"),
 ("S41","U.S. commits additional $242m for Ebola fight","Agence de presse du Ghana (GNA)","2026-08-05",U+"gna.org.gh/2026/08/u-s-commits-additional-242m-for-ebola-fight/","Presse","Moyenne (cite le communiqué)"),
 ("S42","US Offers $242million Additional Funding for Ebola Fight","Sanyu FM","2026-08",U+"sanyufm.com/us-offers-242million-additional-funding-for-ebola-fight-maintains-travel-ban-on-uganda/","Presse","Moyenne (cite : 350 M$ OCHA en plus, 1,8 Md$ annoncés le 14 mai)"),
 ("S43","Is The U.S. Stepping Up In The Fight Against Ebola?","KFF","2026-05",U+"www.kff.org/global-health-policy/is-the-u-s-stepping-up-in-the-fight-against-ebola/","Analyse indépendante","Haute (23 M$ annoncés mi-mai)"),
]
pd.DataFrame(sources, columns=["id","title","publisher","date","url","type","reliability"]).to_csv(OUT/"sources.csv", index=False)

claims = [
 ("C01","Les bailleurs auraient décaissé 962 M$ vers les partenaires de mise en œuvre.","Déclaré","Déclaration officielle d'Africa CDC. Montant fourni par les bailleurs, non audité.","S01,S04","Obtenir la ventilation par bailleur."),
 ("C02","Le montant de départ est 962 M$ ou 926,66 M$.","Contradictoire","Le communiqué dit 962 M$ ; plusieurs médias citent 926,66 M$ et Kaseya dit « 900 − 200 = 700 », ce qui s'accorde mieux avec 926,66. Avec 962, l'écart est de 742 M$.","S01,S03,S07","Demander la source exacte à Africa CDC."),
 ("C03","25 partenaires sur ~94 ont déclaré 226,344 M$ reçus et 127,374 M$ dépensés (INSP, 2 oct.).","Déclaré","Chiffres de l'INSP relayés par la presse. Le ministre de la Santé parle de 25 organisations sur 97.","S03,S08,S09,S06","Obtenir la liste nominative des 25."),
 ("C04","Le solde disponible est de 89,326 M$ (INSP).","Contradictoire","226,344 − 127,374 = 98,970 M$, soit 9,644 M$ de plus que le solde annoncé. Africa CDC arrondit à 100 M$.","S03,S01","Demander à l'INSP l'explication de l'écart de 9,6 M$."),
 ("C05","Les ~700 M$ sont détournés.","Non établi","Kaseya précise qu'il ne s'agit pas encore de détournement mais d'un défaut de transparence ; les fonds seraient chez les partenaires. Aucune preuve publique de détournement.","S01,S03,S08","Audits indépendants par partenaire."),
 ("C06","Les fonds n'ont pas transité par le Trésor public.","Déclaré","Déclaré par le ministre de la Communication et par Kaseya.","S05,S06","—"),
 ("C07","Les États-Unis ont fourni/annoncé 887 M$ au total (267 M$ inclus), dont plus de 780 M$ du Département d'État.","Établi (annonce)","Communiqué du 23 sept. et G20 du 30 sept. Arithmétique : 512 + 267 ≈ 779 M$. Le montant est annoncé, non vérifié comme versé.","S10,S11,S12","Comparer aux awards USAspending (obligations, paiements)."),
 ("C08","Les États-Unis ont fourni 887 M$ plus 267 M$ (1,15 Md$).","Réfuté","Health Policy Watch et d'autres additionnent ; les sources primaires indiquent 887 M$ cumulés.","S13,S10,S11","—"),
 ("C09","« iMC Worldwide » dans FTS = International Medical Corps.","Probable","28,01 M$ du Département d'État, ventilés par secteur comme une ONG multisectorielle ; aucune autre ligne « International Medical Corps » dans FTS RDC 2026. Une société de conseil homonyme existe (IMC Worldwide Ltd). Pas de source primaire qui l'affirme.","S20,S23,S26","Fiche FTS du flux 396634 ; fiche USAspending des awards."),
 ("C10","Le total Ebola du tracker pour iMC (28,09 M$) est exact.","Établi","23,000 M$ + 5,011 M$ (flux 396618 RDC–Ouganda, colonne « Amount shared on boundary ») + ~0,075 M$ en nature = 28,086 M$.","S20,S37","—"),
 ("C11","142,1 M$ des 148,9 M$ d'allocations FH citant Ebola portent l'étiquette « US ».","Établi","Étiquettes [US]/[non-US] dans les descriptions FTS des allocations RA 3 à RA 5.","S20","—"),
 ("C12","Seuls 39,1 M$ des 148,9 M$ concernent des projets purement Ebola.","Établi","Les autres projets citent Ebola avec des conflits ou des déplacements parmi leurs types d'urgence.","S20","Ne pas présenter ces ONG comme bénéficiaires de « fonds Ebola »."),
 ("C13","L'allocation RA 2 (145,9 M$, 26 mars 2026) est distincte des allocations Ebola.","Établi","Énoncé du Coordonnateur humanitaire daté d'avant l'épidémie ; FTS : 83 flux pour 145,9 M$.","S17,S20","—"),
 ("C14","25 des 26 bénéficiaires du FH figurent sur la liste des partenaires éligibles d'août 2025 ; Danish Refugee Council n'y figure pas.","Établi (nom à nom)","Rapprochement sur les noms. FCD correspond à « FECONDE » (même intitulé). La liste a 14 mois.","S18,S20","Vérifier la liste à jour pour DRC (Danemark)."),
 ("C15","72 structures sont interdites d'opérer faute d'accréditation (97 − 25).","Déclaré","Relayé par l'ACP/Radio Okapi ; arithmétique cohérente avec 25 sur 97.","S05,S06","—"),
 ("C16","Perimeter Knightworks, LLC a reçu 40 M$ « probablement Ebola » (24 sept.).","Non vérifié","Donnée du tracker seul. Aucune information publique trouvée sur la société lors des recherches web.","S37","Fiche USAspending, SAM.gov, société mère."),
 ("C17","Le total FTS Ebola du tracker est de 398,6 M$.","Non reproduit","Le filtre sur les descriptions donne 320,0 M$ (flux multi-pays inclus). Le mot-clé FTS EBOLA2026 n'est pas dans l'export.","S20,S37","Réexporter avec le filtre mot-clé."),
 ("C18","Les États-Unis représentent 92 % des 962 M$ si leur 887 M$ est inclus.","Hypothèse","Calcul 887 / 962. Hypothèse de lecture : le chiffre d'Africa CDC pourrait refléter surtout l'annonce américaine.","S01,S10","Ventilation par bailleur d'Africa CDC."),
]

claims += [
 ("C19","Les allocations « US » du Fonds humanitaire (142,1 M$) relèvent d'une enveloppe distincte des 887 M$ annoncés.","Établi (déclaration)","Le Département d'État indique que 350 M$ d'aide humanitaire via OCHA (sur 1,8 Md$ annoncés le 14 mai) s'ajoutent à ses annonces directes (512 M$ au 5 août). Ne pas additionner les deux séries.","S40,S42,S11","Confirmer le périmètre avec OCHA."),
]
pd.DataFrame(claims, columns=["id","claim","status","evidence","source_ids","next_step"]).to_csv(OUT/"claims.csv", index=False)

pledges = [
 # donor, announced_musd, basis, source_ids, fts_source_orgs (';' separated, matched to donors.csv)
 ("États-Unis",887,"Total annoncé au 23 sept. (dont 267 M$ le 23 sept.)","S10,S11","United States Department of State;United States of America, Government of"),
 ("Union européenne",568,"Citée par le CRS (inclut aide humanitaire d'urgence)","S12","European Commission's Humanitarian Aid and Civil Protection Department"),
 ("Banque mondiale",433,"Citée par le CRS (RDC et région) ; 90 M$ annoncés au G20","S12,S15",""),
 ("Royaume-Uni",105.6,"Total après 67,5 M$ annoncés le 30 sept.","S15","United Kingdom, Government of"),
 ("France",34,"Cumul après 16 M$ le 30 sept.","S15","France, Government of"),
 ("Allemagne",30.7,"Cumul après 24,8 M$ le 30 sept.","S15",""),
 ("Corée du Sud",18,"G20, 30 sept.","S11",""),
 ("Japon",12.4,"Cumul (G20)","S11","Japan, Government of"),
 ("Émirats arabes unis",10,"G20, 30 sept.","S11","Mohamed Bin Zayed Foundation For Humanity"),
 ("CERF (OCHA)",60,"« Jusqu'à 60 M$ » (mai) ; d'autres montants cités ensuite","S16","Central Emergency Response Fund"),
]
pd.DataFrame(pledges, columns=["donor","announced_musd","basis","source_ids","fts_source_orgs"]).to_csv(OUT/"pledges.csv", index=False)

profiles = [
 # fts_name, display, type, founded, drc_presence, role_2026, accounts, incidents, eligible_hf, source_ids, caveat
 ("iMC Worldwide","International Medical Corps (identité probable)","ONG internationale (États-Unis)","1984 (non sourcé)","En RDC depuis 1999 ; Ebola depuis 2018 (SitRep, mai 2026)","Centre de traitement de 100 lits et centre de transit près de Bunia ; dépistage dans 24 établissements","États financiers audités, Form 990 ; CharityWatch : critères de gouvernance et de transparence remplis","Aucun trouvé","Oui (IMC)","S21,S22,S23,S25,S26","Le nom FTS « iMC Worldwide » n'est pas confirmé comme IMC ; une société de conseil homonyme existe."),
 ("MEDAIR","Medair","ONG internationale (Suisse)","1989 (non sourcé)","À documenter","Partenaire du Département d'État avec IMC : appui à 100 établissements de santé, dont six structures Ebola","Comptes audités 2025 selon le tracker (non vérifié)","Aucun trouvé","Oui","S23","—"),
 ("Solidarités International","Solidarités International","ONG internationale (France)","1980 (Wikipédia)","Depuis 2000 ; riposte Ebola 2018-2020 (site de l'ONG)","Sensibilisation, eau-hygiène, protection en Ituri avec des partenaires locaux","Rapport du commissaire aux comptes 2024 selon le tracker (non vérifié)","Aucun trouvé","Oui","S27,S35","19,1 M$ reçus via le Fonds humanitaire uniquement."),
 ("Save the Children","Save the Children","ONG internationale","1919 (Wikipédia)","Depuis 1994 (site de l'ONG)","Soutien psychosocial à plus de 4 000 enfants en Ituri (22 juillet)","Rapport des trustees (charity 1076822) selon le tracker (non vérifié)","Aucun trouvé","Oui","S28,S34,S36","—"),
 ("World Food Programme","Programme alimentaire mondial","Agence ONU","1961 (non sourcé)","À documenter","Fournitures déchargées à l'aéroport de Bunia le 30 mai","Comptes audités (tracker)","Aucun trouvé","Oui","S33","46 M$ via le Fonds humanitaire, aucun purement Ebola."),
 ("Norwegian Refugee Council","Norwegian Refugee Council","ONG internationale (Norvège)","1946 (non sourcé)","Depuis 2001 (offre d'emploi NRC, source faible)","Eau, hygiène et engagement communautaire en Ituri","Comptes annuels 2025 (tracker)","Aucun trouvé","Oui","S29","11 M$ via le Fonds humanitaire."),
 ("Alliance for International Medical Action","ALIMA","ONG internationale (France)","2009 (non sourcé)","À documenter","Quatre centres de traitement Ebola (Rwampara, CME-Bunia, Nizi, Lita) ouverts en deux mois","Comptes annuels 2025 (tracker)","Aucun trouvé","Oui","S30","7,45 M$ via le Fonds humanitaire."),
 ("Danish Refugee Council","Danish Refugee Council","ONG internationale (Danemark)","1956 (non sourcé)","À documenter","Rôle Ebola 2026 non documenté dans les recherches","Site non chargé lors du contrôle du tracker","Non cherché","Absent de la liste d'août 2025","S18","6,65 M$ via le Fonds humanitaire ; vérifier la liste à jour."),
 ("Programme de Promotion des Soins de santé primaires","PPSSP","ONG nationale (RDC)","À documenter","Cité dans des notes d'information OCHA Ituri (2021-2022) ; partenaire de l'UNICEF à Bambu (2026)","A formé 40 soignants à Bunia et Bambu (juillet 2026)","Aucun compte publié trouvé (tracker)","Aucun trouvé","Oui","S31,S32,S18","Projet FTS : réponse en santé aux déplacés avec Ebola parmi trois types d'urgence."),
 ("FEMME CONGOLAISE POUR LE DEVELOPPEMENT","Femme Congolaise pour le Développement (FCD / FECONDE)","ONG nationale (RDC)","À documenter","À documenter","À documenter","Aucune présence en ligne trouvée (tracker)","Non cherché","Oui (sous « FECONDE »)","S18","Rapprochement sur le nom complet."),
 ("Caritas Bunia","Caritas Bunia","ONG nationale (confessionnelle)","À documenter","À documenter","À documenter","Aucun compte trouvé (tracker)","Non cherché","Oui","S18","—"),
 ("Caritas Congo","Caritas Congo asbl","ONG nationale (confessionnelle)","À documenter","À documenter","À documenter","Chiffres d'activité seulement (tracker)","Non cherché","Oui","S18","Projet débutant le 25 oct., financement non-US."),
 ("Réseau des associations congolaises des jeunes du Nord-Kivu","RACOJ Nord-Kivu","ONG nationale (RDC)","À documenter","À documenter","Secteur FTS : aide en espèces multi-usage","Aucun compte trouvé (tracker)","Non cherché","Oui","S18","—"),
 ("RESEAU DES MEDIAS POUR LE DEVELOPPEMENT","Réseau des Médias pour le Développement (REMED)","ONG nationale (RDC)","À documenter","À documenter","Secteur FTS : sécurité alimentaire","Aucun compte trouvé (tracker)","Non cherché","Oui","S18","Identité exacte non confirmée (tracker)."),
 ("YMES Grand Lac","YMES Grand Lac","ONG nationale (RDC)","À documenter","À documenter","Secteur FTS : eau-hygiène","Organisation non identifiée en ligne (tracker)","Non cherché","Oui","S18","Projet débutant le 12 oct."),
]
pd.DataFrame(profiles, columns=["fts_name","display_name","type","founded","drc_presence","role_2026","accounts_public","incidents_found","eligible_hf_aug2025","source_ids","caveat"]).to_csv(OUT/"ngo_profiles.csv", index=False)

# Humanitarian-fund recipients (Ebola-described) -> entry in the Aug 2025 eligible list
elig = [
 ("World Food Programme","World Food Programme (WFP)","Exact"),("Solidarités International","Solidarités Internationale (Solidarités)","Exact"),
 ("Save the Children","Save the Children (SCI)","Exact"),("Norwegian Refugee Council","Norwegian Refugee Council (NRC)","Exact"),
 ("Alliance for International Medical Action","Alliance for Internationale Medical Action (ALIMA)","Exact"),
 ("Danish Refugee Council","(aucune entrée)","Absent"),("Mercy Corps Europe","Mercy Corps (Mercy Corps)","Probable"),
 ("Agency for Technical Cooperation and Development","Agency for Technical Cooperation and Development (ACTED)","Exact"),
 ("International Organization for Migration","International Organization for Migration (IOM)","Exact"),
 ("Programme de Promotion des Soins de santé primaires","Programme de Promotion des Soins de santé primaires (PPSSP)","Exact"),
 ("United Nations Children's Fund","United Nations Children's Fund (UNICEF)","Exact"),
 ("Food and Agriculture Organization of the United Nations","Food and Agriculture Organization of the United Nations (FAO)","Exact"),
 ("Cooperazione Internazionale - COOPI","Cooperazione Internazionale - COOPI (COOPI)","Exact"),
 ("United Nations High Commissioner for Refugees","United Nations High Commissioner for Refugees (UNHCR)","Exact"),
 ("ActionAid Democratic Republic of the Congo","Action Aid Internationale RD Congo (AAI)","Probable"),
 ("World Vision International","World Vision Internationale (WVI)","Exact"),
 ("FEMME CONGOLAISE POUR LE DEVELOPPEMENT","Femme Congolaise pour le Développement (FECONDE)","Probable (même intitulé, sigle différent)"),
 ("Caritas Bunia","Caritas Bunia (CARBUNIA)","Exact"),("Première Urgence Internationale","Première Urgence Internationale (PUI)","Exact"),
 ("Concern Worldwide","Concern","Probable"),("Caritas Congo","Caritas Congo asbl (CARCO)","Exact"),
 ("ACT Alliance / Norwegian Church Aid","Norwegian Church Aid (NCA)","Probable"),
 ("Réseau des associations congolaises des jeunes du Nord-Kivu","Réseau des associations congolaises des jeunes du Nord-Kivu (RACOJ Nord-Kivu)","Exact"),
 ("RESEAU DES MEDIAS POUR LE DEVELOPPEMENT","Réseau des Médias pour le Développement (REMED)","Exact"),
 ("Red Cross of the Democratic Republic of the Congo","Croix-Rouge de la République Démocratique du Congo (CRRDC)","Exact"),
 ("YMES Grand Lac","YMES Grand Lac (YMES)","Exact"),
]
pd.DataFrame(elig, columns=["fts_name","eligible_list_entry","match"]).to_csv(OUT/"hf_eligibility_check.csv", index=False)

recon = [
 ("Écart « 962 − 220 »","962 − 220","742 M$","Communiqué : « plus de 700 M$ »","S01"),
 ("Écart « 926,66 − 226,3 »","926,66 − 226,344","700,3 M$","S'accorde avec le « 900 − 200 = 700 » de Kaseya","S03"),
 ("Solde INSP","226,344 − 127,374","98,970 M$","INSP annonce 89,326 M$ : écart de 9,644 M$","S03,S09"),
 ("Participation","25 / 94 et 25 / 97","26,6 % et 25,8 %","Africa CDC : « moins de 30 % »","S01,S09,S06"),
 ("Structures sans accréditation","97 − 25","72","Cohérent avec « 72 structures » (ACP)","S05,S06"),
 ("Part américaine du 962 M$","887 / 962","92,2 %","Hypothèse : le chiffre d'Africa CDC reflète surtout l'annonce américaine","S01,S10"),
 ("Cumul américain","512 + 267","779 M$","« Plus de 780 M$ » du Département d'État ; le solde (≈ 107 M$) vient d'autres agences","S10"),
 ("iMC Worldwide (FTS)","23,000 + 5,011 + 0,075","28,086 M$","Tracker : 28,087 M$ → concordance à 1 k$ près","S20,S37"),
 ("Allocation RA 2","145,9 M$ (énoncé du 26 mars)","83 flux = 145,9 M$ dans FTS","Allocation distincte, antérieure à l'épidémie","S17,S20"),
]
pd.DataFrame(recon, columns=["check","computation","result","reading","source_ids"]).to_csv(OUT/"reconciliation.csv", index=False)

timeline = [
 ("2026-05-14","États-Unis","1,8 Md$ d'assistance à OCHA annoncés (dont 350 M$ pour RDC, Soudan du Sud, Ouganda, précisés plus tard)",None,None,"S40,S42"),
 ("2026-05-15","RDC / OMS","Rapport de situation n°1 d'IMC : épidémie d'Ebola Bundibugyo en Ituri",None,None,"S21"),
 ("2026-05","États-Unis","23 M$ d'urgence mobilisés pour la RDC et l'Ouganda",23,23,"S43"),
 ("2026-06-16","États-Unis (G7)","Engagement de fournir jusqu'à 500 M$ supplémentaires",500,None,"S40"),
 ("2026-08-05","États-Unis","242 M$ supplémentaires : aide directe annoncée > 512 M$",242,512,"S40,S41"),
 ("2026-09-23","États-Unis","267 M$ supplémentaires : total direct 887 M$",267,887,"S10,S11"),
 ("2026-09-30","G20 (États-Unis)","Plus de 470 M$ d'engagements nouveaux ; promesses mondiales > 2 Md$",470,None,"S11,S15"),
 ("2026-10-02","INSP (RDC)","25 partenaires sur ~94 ont déclaré 226,3 M$ reçus et 127,4 M$ dépensés",None,None,"S03,S09"),
 ("2026-10-14","Africa CDC","Kaseya : plus de 700 M$ à retracer chez les partenaires",None,None,"S01,S04,S08"),
 ("2026-10-15","Gouvernement RDC","Accréditation obligatoire des acteurs de la riposte ; 72 structures interdites d'opérer sans accréditation",None,None,"S05,S06"),
]
pd.DataFrame(timeline, columns=["date","actor","event","amount_musd","cumulative_musd","source_ids"]).to_csv(OUT/"timeline.csv", index=False)
print("reference tables written:", [p.name for p in OUT.glob("*.csv")])
