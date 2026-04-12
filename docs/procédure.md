# 📦 Procédure complète : Gestion des mises à jour HACS pour Midnite Solar Classic

Ce guide vous explique comment gérer le cycle de vie des versions de votre intégration Home Assistant avec HACS, de la modification du code jusqu'à la publication des notes de version.

## 📋 Table des matières

- Structure des versions
- Procédure standard (indépendante de l'IDE)
- Exemple concret avec release notes
- Vérifications pré-release
- Dépannage HACS

## 🏗️ Structure des versions

### Versionnement sémantique (SemVer)

```yaml
vMAJOR.MINOR.PATCH
Exemples:
  v1.0.0  # Version initiale
  v1.0.1  # Correction de bug
  v1.1.0  # Nouvelle fonctionnalité
  v2.0.0  # Changement incompatible
```

## Fichiers à maintenir synchronisés

| Fichier	       | Élément à mettre à jour       |
| -------------- | ----------------------------- |
| manifest.json	 | "version": "1.0.1"            |  
| const.py	     | VERSION = "1.0.1" (optionnel) |  
| GitHub Release | Tag + Release Notes           |



## 🔧 Procédure standard (indépendante de l'IDE)

Cette procédure fonctionne avec n'importe quel IDE (Cursor, VS Code, PyCharm, etc.)

### Phase 1 : Développement (pas de mise à jour HACS)

```bash
# 1. Modifiez votre code normalement
# 2. Testez localement dans Home Assistant
# 3. Committez sans changer la version

git add .
git commit -m "WIP: Amélioration des logs Modbus"
git push origin main
```


⚠️ Résultat : Aucune mise à jour proposée aux utilisateurs

### Phase 2 : Préparation d'une release officielle

```bash
# 1. Mettez à jour la version dans manifest.json
# Ouvrez le fichier et changez "version": "1.0.0" → "1.0.1"
# 2. (Optionnel) Mettez à jour const.py
# VERSION = "1.0.0" → VERSION = "1.0.1"
# 3. Committez les changements de version

git add manifest.json const.py
git commit -m "🔖 Release v1.0.1"

# 4. Poussez vers GitHub
git push origin main
```


### Phase 3 : Création du tag et de la release sur GitHub

Méthode A : Via ligne de commande

```bash
# Créer un tag annoté
git tag -a v1.0.1 -m "Version 1.0.1 - Amélioration des logs Modbus"
# Pousser le tag vers GitHub
git push origin v1.0.1
```


Méthode B : Via l'interface web GitHub (recommandée pour les release notes)

1. Allez sur [https://github.com/qcda1/ha_midnite_classic/releases](https://github.com/qcda1/ha_midnite_classic/releases)
2. Cliquez sur "Create a new release"
3. Sélectionnez le tag existant ou créez-en un nouveau
4. Remplissez le formulaire (voir section suivante)

### 📝 Exemple concret avec release notes

Formulaire de création de release GitHub

```yaml
Tag version: v1.0.1
Release title: Version 1.0.1 - Amélioration des logs Modbus
Previous tag: v1.0.0  # Optionnel, pour générer automatiquement les changements
```

Exemple de Release Notes (à copier dans la zone de texte)

```markdown

## 🚀 Nouvelles fonctionnalités

- Ajout du support pour le Classic 200
- Nouvelle entité de mise à jour automatique
- Logs Modbus plus détaillés en mode debug

## 🐛 Corrections

- Correction du bug de reconnexion après perte réseau
- Résolution du problème d'intervalle minimum à 30 secondes
- Correction des unités pour BatTemperature (°C)

## 🔧 Améliorations techniques

- Réduction de la charge CPU de 20%
- Mise à jour de pymodbus vers 3.6.2
- Refactorisation du config_flow pour meilleure stabilité

## ⚠️ Breaking changes (si applicable)

- Aucun breaking change dans cette version

## 📦 Installation

La mise à jour sera proposée automatiquement dans HACS.
Redémarrez Home Assistant après l'installation.

## 🙏 Remerciements

Merci à @utilisateur pour le signalement du bug #42
```


Ce que vos utilisateurs verront dans HACS

Lorsqu'ils cliqueront sur l'icône de mise à jour, ils verront exactement ce texte formaté en Markdown !

## ✅ Vérifications pré-release

Avant de publier une version, vérifiez ces points :

### Checklist de qualité

* L'intégration fonctionne avec la dernière version stable de HA
* Les entités se créent correctement
* Le flux d'options (⚙️) fonctionne sans erreur
* La version dans manifest.json correspond au tag GitHub
* Les release notes sont rédigées et compréhensibles

Vérification du manifest.json complet

```json
{
  "domain": "ha_midnite_classic",
  "name": "Midnite Solar Classic",
  "version": "1.0.1",
  "requirements": ["pymodbus>=3.6.0"],
  "dependencies": [],
  "codeowners": ["@qcda1"],
  "config_flow": true,
  "iot_class": "local_polling",
  "documentation": "[https://github.com/qcda1/ha_midnite_classic](https://github.com/qcda1/ha_midnite_classic)",
  "issue_tracker": "[https://github.com/qcda1/ha_midnite_classic/issues](https://github.com/qcda1/ha_midnite_classic/issues)"
}
```

## 🔍 Dépannage HACS

### Problème : La mise à jour n'apparaît pas dans HACS

Solutions :

1. Attendez jusqu'à 24h (HACS ne vérifie pas en temps réel)
2. Forcez la vérification : HACS → ⋮ → "Redémarrer HACS"
3. Vérifiez que le tag existe sur GitHub : git ls-remote --tags origin
4. Assurez-vous que le tag correspond EXACTEMENT à la version dans manifest.json

### Problème : La release notes n'apparaît pas

Solutions :

1. Vérifiez que vous avez bien rempli la description de la release
2. La release doit être "publiée" (pas en "draft" ou "pre-release")
3. Attendez quelques minutes après publication

Commande de diagnostic rapide

```bash

# Vérifier les tags locaux
git tag -l

# Vérifier les tags distants
git ls-remote --tags origin

# Vérifier la dernière version dans manifest.json
cat manifest.json | grep version
```


## 🤖 Note sur Cursor IDE

Cursor n'affecte PAS cette procédure car :

* Cursor utilise les mêmes commandes Git standards
* Les opérations GitHub sont indépendantes de l'éditeur
* La configuration HACS ne dépend que du dépôt GitHub

Avantages de Cursor pour ce workflow :

✅ Auto-complétion pour les release notes (Markdown)
✅ Intégration Git visuelle (onglet Source Control)
✅ Commits et push en un clic
✅ Visualisation des tags

Commandes équivalentes dans Cursor :

| Terminal	           | Interface Cursor                   |
| -------------------- | ---------------------------------- |
| git add .	           | Bouton + sur les fichiers modifiés |
| git commit -m "msg"	 | Champ de message + ✓               |
| git push	| ⋮ → Push                                      |
| git tag -a v1.0.1	   | Panel Git → Create Tag             |

📊 Résumé visuel du cycle

```text
Développement (version inchangée)
    ↓
git push origin main → Pas de mise à jour HACS ❌
    ↓
Incrémenter version dans manifest.json
    ↓
git commit -m "🔖 Release v1.0.1"
git push origin main
    ↓
Créer tag v1.0.1
    ↓
Créer release sur GitHub avec notes
    ↓
HACS propose la mise à jour ✅
    ↓
Les utilisateurs voient vos release notes
```
## 🎯 Bonnes pratiques finales

1. Testez toujours localement avant de créer une release
2. Rédigez des release notes claires même pour les petites mises à jour
3. Utilisez des préfixes dans vos commits (🐛 Fix:, ✨ Feat:, 📝 Docs:)
4. Gardez un CHANGELOG.md dans votre dépôt pour l'historique
5. Communiquez les breaking changes en MAJUSCULES dans les release notes

Procédure validée pour : Home Assistant 2026.3+, HACS 1.34+, Git 2.x+
