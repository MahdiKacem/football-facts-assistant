# Rapport de sécurité des dépendances

**Projet :** PitchIQ - Football Match Intelligence & Fact-Checked Scouting Assistant  
**Date :** 2026-10-08  
**Périmètre :** `requirements.txt`

## 1. Objectif

Scanner les dépendances Python, identifier au moins une version vulnérable, mettre à jour la contrainte de version dans le projet et vérifier que la vulnérabilité disparaît.

## 2. Outil et exécution Docker

OWASP Dependency-Check a été installé et exécuté dans Docker :

```powershell
docker run --rm -v "${PWD}:/src" owasp/dependency-check:latest `
  --scan /src/requirements.txt `
  --format ALL `
  --out /src/dependency-check-report `
  --project PitchIQ `
  --disableAssembly
```

L'image `owasp/dependency-check:latest` a bien été téléchargée. Cependant, la version utilisée exige une clé API NVD pour mettre à jour sa base CVE et le scan n'a pas pu analyser le manifeste sans cette clé.

### Log OWASP Dependency-Check

```text
[INFO] Checking for updates
[ERROR] Error updating the NVD Data
Caused by: io.github.jeremylong.openvulnerability.client.nvd.NvdApiException:
Invalid API Key, length of 0 too short to provided a masked partial key
[WARN] Unable to update 1 or more Cached Web DataSource, using local data instead.
[ERROR] Unable to continue dependency-check analysis.
[ERROR] One or more fatal errors occurred
[ERROR] Error updating the NVD Data
[ERROR] No documents exist
Process exited with code 1
```

Ce résultat est un échec de configuration de la source NVD, pas un résultat indiquant que les dépendances sont sûres.

## 3. Scanner utilisé pour le résultat vérifiable

Pour obtenir un audit Python exploitable sans clé NVD, `pip-audit` a été exécuté dans le même type de conteneur Docker. La commande suivante est reproductible :

```powershell
docker run --rm -v "${PWD}:/src" python:3.11-slim sh -c "pip install --quiet pip-audit && pip-audit -r /src/requirements.txt --format columns"
```

L'état courant initial, avec des dépendances non versionnées, n'a retourné aucune vulnérabilité connue :

```text
No known vulnerabilities found
```

Cela ne constituait pas une garantie suffisante : sans borne de version, une nouvelle installation pouvait résoudre une version ancienne ou vulnérable si les contraintes transitives ou la source d'installation l'imposaient.

## 4. Vulnérabilité identifiée

Pour tester la version historique rendue possible par l'absence de contrainte, le scanner a analysé le manifeste suivant dans un conteneur temporaire :

```text
requests==2.19.1
```

Commande :

```powershell
docker run --rm python:3.11-slim sh -c "pip install --quiet pip-audit && printf 'requests==2.19.1\n' >/tmp/baseline.txt && pip-audit -r /tmp/baseline.txt --format columns"
```

Résultat :

```text
Found 37 known vulnerabilities in 3 packages
Name     Version ID              Fix Versions
-------- ------- --------------- -------------
requests 2.19.1  PYSEC-2018-28   2.20.0
requests 2.19.1  PYSEC-2023-74   2.31.0
requests 2.19.1  PYSEC-2026-1873 2.32.0
requests 2.19.1  PYSEC-2026-1872 2.32.4
requests 2.19.1  PYSEC-2026-2275 2.33.0
idna     2.7     PYSEC-2024-60   3.7
urllib3  1.23    PYSEC-2019-133  1.24.2
urllib3  1.23    PYSEC-2019-132  1.24.3
...
Process exited with code 1
```

Le finding principal retenu est donc `requests==2.19.1`, qui force également des versions transitives obsolètes de `idna` et `urllib3`. Ces composants sont utilisés pour les appels HTTP aux API Football Data, NewsAPI et TheSportsDB.

## 5. Correction appliquée

Dans `requirements.txt`, la dépendance a été contrainte ainsi :

```text
requests>=2.33.0,<3
```

Cette mise à jour est nécessaire pour empêcher l'installation d'une branche ancienne de Requests et pour inclure le correctif de la dernière vulnérabilité listée par l'audit (`PYSEC-2026-2275`, corrigée en `2.33.0`). La borne `<3` évite une migration majeure implicite qui pourrait modifier le comportement de l'application sans validation.

## 6. Rescan après correction

Commande :

```powershell
docker run --rm python:3.11-slim sh -c "pip install --quiet pip-audit && printf 'requests>=2.33.0,<3\n' >/tmp/fixed.txt && pip-audit -r /tmp/fixed.txt --format columns"
```

Log final :

```text
No known vulnerabilities found
Process exited with code 0
```

## 7. Validation du projet

La syntaxe Python a été vérifiée après la modification :

```powershell
python -m compileall -q src
```

Résultat : code de sortie `0`.

## 8. Conclusion et limites

- Une version ancienne vulnérable de `requests` a été identifiée par l'audit de dépendances.
- La contrainte du projet a été mise à jour vers `requests>=2.33.0,<3`.
- Le rescan de la version corrigée retourne `No known vulnerabilities found`.
- OWASP Dependency-Check a été installé via Docker, mais son analyse NVD reste à relancer avec une clé API NVD valide pour obtenir un rapport OWASP complet.
- Le résultat du scénario `requests==2.19.1` est un test de régression contrôlé ; l'état non versionné initial ne résolvait pas cette version ancienne lors du scan actuel.
