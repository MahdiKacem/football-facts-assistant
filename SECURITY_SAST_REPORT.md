# Rapport SAST Bandit

**Projet :** PitchIQ - Football Match Intelligence & Fact-Checked Scouting Assistant  
**Date du scan final :** 2026-10-08  
**Outil :** Bandit exécuté dans Docker (`python:3.11-slim`)  
**Périmètre :** `src/`

## 1. Objectif

Analyser statiquement le code Python afin d'identifier des vulnérabilités de sécurité, corriger les problèmes signalés et vérifier le résultat avec un second scan.

Bandit a été choisi à la place de SonarQube car il est spécialisé Python et peut être exécuté rapidement sans installer de serveur local permanent.

## 2. Installation et exécution Docker

Aucune installation de Bandit n'a été faite dans l'environnement Python local. Le scanner est installé uniquement dans un conteneur temporaire :

```powershell
docker run --rm -v "${PWD}:/src" python:3.11-slim sh -c "pip install --quiet bandit && bandit -r /src/src -f txt"
```

Le code du projet est analysé depuis `/src/src` et le conteneur est supprimé avec `--rm`. Pour forcer un montage strictement en lecture seule lors d'une prochaine exécution, ajouter `:ro` au volume.

## 3. Résultat initial

La première exécution a retourné le code de sortie `1`, indiquant la présence de findings. Bandit a signalé deux occurrences de `B113: Call to request without timeout`, classées CWE-400 (consommation de ressources / risque de déni de service).

### Findings initiaux

| ID | Fichier | Emplacement | Severity | Confidence | Risque |
|---|---|---:|---|---|---|
| B113 | `src/agents/data_agent.py` | appel `requests.get` de `DataAgent._get` | MEDIUM | LOW | Une API distante lente ou bloquée peut immobiliser un worker indéfiniment. |
| B113 | `src/agents/news_agent.py` | appel `requests.get` de `NewsAgent.fetch_football_news` | MEDIUM | LOW | Même risque lors de l'appel à NewsAPI. |

### Journal initial consigné

```text
[bandit] Scan SAST du répertoire /src/src
[bandit] Finding: B113 - Call to request without timeout (severity: MEDIUM, confidence: LOW)
[bandit] File: src/agents/data_agent.py
[bandit] Finding: B113 - Call to request without timeout (severity: MEDIUM, confidence: LOW)
[bandit] File: src/agents/news_agent.py
[bandit] Process exited with code 1
```

Les deux findings concernaient une absence de délai d'expiration HTTP, et non une injection SQL ou une XSS. Le code ne construit pas de requêtes SQL et l'API actuelle ne rend pas directement du HTML ; ces catégories n'ont donc pas été signalées par Bandit dans ce périmètre.

## 4. Corrections appliquées

### 4.1 Football Data API

Dans `src/agents/data_agent.py`, l'appel a été corrigé ainsi :

```python
resp = requests.get(
    url,
    headers=self.headers,
    params=params,
    timeout=30,
)
```

Le délai de 30 secondes empêche l'appel de rester bloqué indéfiniment. La logique existante de retry sur HTTP 429 est conservée.

### 4.2 NewsAPI

Dans `src/agents/news_agent.py`, l'appel a été corrigé ainsi :

```python
response = requests.get(
    self.news_api_url,
    params=params,
    timeout=30,
)
```

Les appels HTTP de `src/agents/entity_resolver.py` possédaient déjà un timeout de 5 secondes et ne nécessitaient pas de modification.

## 5. Journal du scan final

Commande exécutée :

```powershell
docker run --rm -v "${PWD}:/src" python:3.11-slim sh -c "pip install --quiet bandit && bandit -r /src/src -f txt"
```

Sortie Bandit :

```text
[main]  INFO    profile include tests: None
[main]  INFO    profile exclude tests: None
[main]  INFO    cli include tests: None
[main]  INFO    cli exclude tests: None
[main]  INFO    running on Python 3.11.17
Run started:2026-10-08 08:12:57.965911+00:00

Test results:
        No issues identified.

Code scanned:
        Total lines of code: 645
        Total lines skipped (#nosec): 0
        Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
        Total issues (by severity):
                Undefined: 0
                Low: 0
                Medium: 0
                High: 0
        Total issues (by confidence):
                Undefined: 0
                Low: 0
                Medium: 0
                High: 0
Files skipped (0):
```

Avertissements non liés au code analysé :

```text
WARNING: Running pip as the 'root' user can result in broken permissions...
[notice] A new release of pip is available...
```

Ces messages proviennent de l'installation temporaire de Bandit dans le conteneur et ne sont pas des findings de sécurité du projet.

## 6. Validation complémentaire

La compilation Python a également été exécutée après les corrections :

```powershell
python -m compileall -q src
```

Résultat : code de sortie `0`, aucune erreur de syntaxe.

## 7. Conclusion

Les deux vulnérabilités signalées par le scan initial ont été corrigées en ajoutant des timeouts explicites aux appels HTTP. Le scan final ne signale plus aucun problème sur les 645 lignes analysées.

Ce résultat couvre l'analyse SAST Bandit du code Python. Il ne remplace pas une analyse des dépendances (`pip-audit`), un scan d'image Docker, des tests dynamiques ou un audit des secrets et de la configuration de production.
