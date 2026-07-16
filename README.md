# Projet final — Inférence causale sur les achats en ligne

Ce projet étudie l'effet moyen d'une session tenue le **week-end** plutôt qu'en semaine sur la probabilité qu'elle se termine par un achat (`Revenue`). L'analyse repose sur le jeu **Online Shoppers Purchasing Intention** et demeure observationnelle : les estimations ont une interprétation causale seulement sous les hypothèses explicitées dans le rapport et le notebook.

## Livrables à consulter

- Rapport final : `04_outputs/rapport/rapport_final_inference_causale_online_shoppers.pdf`
- Version modifiable du rapport : `04_outputs/rapport/rapport_final_inference_causale_online_shoppers.docx`
- Présentation : `04_outputs/presentation/presentation_finale_inference_causale_online_shoppers.pptx`
- Notebook exécuté : `01_notebooks/livrable/projet_final_inference_causale_online_shoppers.ipynb`
- Export HTML du notebook : `04_outputs/notebook_html/projet_final_inference_causale_online_shoppers.html`
- Fiche de préparation à l'oral : `03_notes/fiche_orale_questions_pieges.md`

Le rapport présente la question causale, les données, les connaissances préalables, le DAG de travail, l'exploration FCI, l'identification, les estimateurs, les diagnostics, les analyses de robustesse et les limites d'interprétation.

## Contenu de la remise

L'archive `rendu_final_inference_causale_online_shoppers.zip` s'extrait dans un seul dossier racine nommé `projet_inference_causale_online_shoppers/`. Ce dossier contient exactement les 21 fichiers suivants :

```text
projet_inference_causale_online_shoppers/
├── README.md
├── requirements.txt
├── 01_notebooks/
│   └── livrable/
│       └── projet_final_inference_causale_online_shoppers.ipynb
├── 02_data/
│   └── raw/
│       └── online_shoppers_intention.csv
├── 03_notes/
│   └── fiche_orale_questions_pieges.md
├── 04_outputs/
│   ├── figures/
│   │   ├── 01_description_et_recouvrement.png
│   │   ├── 02_dag_de_travail.png
│   │   ├── 03_pag_fci.png
│   │   ├── 04_recouvrement_propension.png
│   │   ├── 05_equilibre_covariables.png
│   │   ├── 06_estimations_principales.png
│   │   └── 07_robustesse_aipw.png
│   ├── notebook_html/
│   │   └── projet_final_inference_causale_online_shoppers.html
│   ├── presentation/
│   │   └── presentation_finale_inference_causale_online_shoppers.pptx
│   ├── rapport/
│   │   ├── rapport_final_inference_causale_online_shoppers.docx
│   │   └── rapport_final_inference_causale_online_shoppers.pdf
│   └── tableaux/
│       ├── 01_aretes_pag_fci.csv
│       ├── 02_estimations_principales.csv
│       ├── 03_equilibre_covariables.csv
│       └── 04_analyses_robustesse.csv
└── src/
    └── _construire_notebook_livrable.py
```

## Données et résultat principal

- Source : UCI Machine Learning Repository, jeu n° 468.
- DOI : [10.24432/C5F88Q](https://doi.org/10.24432/C5F88Q)
- Fichier : `02_data/raw/online_shoppers_intention.csv`
- Dimensions : 12 330 sessions et 18 variables.
- SHA-256 : `b3055ee355f59134d851d32641183cb4a8b45def7124d2f50442a042f358e0d9`

L'analyse principale porte sur les 11 079 sessions pour lesquelles `SpecialDay = 0`, afin d'éviter le défaut structurel de recouvrement observé ailleurs. L'association brute est de **+2,03 points de pourcentage**. L'estimation AIPW principale est de **+1,51 point**, avec un intervalle de confiance à 95 % de **[-0,18 ; 3,19] points**. Cet intervalle contient zéro : les données restent compatibles avec un faible effet positif comme avec l'absence d'effet moyen.

## Installation

Les versions validées sont fixées dans `requirements.txt`. Depuis la racine extraite `projet_inference_causale_online_shoppers/`, créer puis activer un environnement virtuel.

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

Sous Linux ou macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

L'environnement de remise a été validé sous Python 3.14.3. Une exécution complète prend généralement d'une à trois minutes, selon le processeur.

## Reproduction de l'analyse

Le notebook fourni est déjà exécuté. Pour le relancer de façon non interactive depuis la racine du projet :

```powershell
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 01_notebooks/livrable/projet_final_inference_causale_online_shoppers.ipynb
```

Cette commande recalcule l'analyse et régénère les figures ainsi que les tableaux. Pour reconstruire ensuite l'export HTML :

```powershell
python -m jupyter nbconvert --to html --output-dir 04_outputs/notebook_html 01_notebooks/livrable/projet_final_inference_causale_online_shoppers.ipynb
```

Pour une exécution interactive :

```powershell
python -m jupyter lab
```

Ouvrir ensuite le notebook final et choisir **Run All**.

## Paramètres de reproductibilité

- Graine globale : `20260715`
- Validation croisée stratifiée : cinq plis
- Score de propension borné numériquement dans `[0,01 ; 0,99]`
- Bootstrap de la standardisation : 500 réplications
- Versions logicielles : fixées dans `requirements.txt`

Le notebook vérifie l'empreinte SHA-256 du fichier de données avant l'analyse et interrompt volontairement l'exécution si le contenu ne correspond pas à la copie validée.
