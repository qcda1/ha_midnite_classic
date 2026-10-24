# Tableau de bord « Console » — MidNite Classic

Tableau de bord Home Assistant pour un ou deux contrôleurs **MidNite Solar
Classic** surveillés par l'intégration [`ha_midnite_classic`](../../README.md).

Il regroupe sur une seule page :

- la puissance, l'étage de charge et la récolte de chaque Classic (plus le total combiné en version deux Classic) ;
- la banque de batteries vue par le **WhizBang Jr** (état de charge, tension, courant, Ah, énergie entrée/sortie) ;
- la génératrice commandée par **AUX 1** (statut, seuils, temps de marche, démarrages, commandes et journal) ;
- les chaînes photovoltaïques (tension, courant, Voc, raison de mise au repos) ;
- les fanions d'état (registre 4130) de chaque contrôleur.

> L'interface du tableau de bord est en français.

---

## Contenu du répertoire

Deux variantes, chacune formée d'un package et d'un tableau de bord.
**Choisissez la vôtre et installez uniquement ses deux fichiers.**

| Variante | Package → `config/packages/` | Tableau de bord → éditeur YAML |
|---|---|---|
| **Deux Classic** | `classic_console.yaml` | `tableau_de_bord.yaml` |
| **Un seul Classic** | `classic_console_1classic.yaml` | `tableau_de_bord_1classic.yaml` |

Le **package** crée les entités dérivées : bilan de la banque, statut de la
génératrice, compteurs `history_stats`, et deux automatisations qui
inscrivent les changements de configuration AUX 1 au journal. La version
deux Classic ajoute la puissance, la récolte du jour et l'énergie cumulée
combinées.

Le package est nécessaire : le tableau de bord affiche plusieurs entités qui
n'existent que grâce à lui.

> N'installez jamais les deux packages en même temps : ils déclarent les
> mêmes entités et Home Assistant refusera les doublons.

---

## Prérequis

### 1. L'intégration `ha_midnite_classic`

Installée et configurée pour vos Classic. Par défaut, les fichiers
supposent que les entités commencent par `classic1_` (et `classic2_` pour la
version deux Classic) — voir
[l'étape 5](#5-adapter-les-noms-dentités-si-vos-classic-ne-sappellent-pas-classic1--classic2)
si ce n'est pas votre cas.

### 2. Les paramètres exposés par l'intégration

À l'installation, l'intégration n'expose qu'un petit ensemble de paramètres.
Le tableau de bord en utilise davantage. Pour **chaque** Classic installé, ouvrez
**Paramètres → Appareils et services → MidNite Solar Classic → ⚙️ (Options)**
et cochez au minimum :

| Section | Paramètres à cocher |
|---|---|
| Production | `Power`, `EnergyToday`, `TotalEnergy`, `ChargeStateText`, `MPPTModeText`, `FETTemperature`, `Name` |
| Chaînes PV | `PVVoltage`, `PVCurrent`, `lastVOC`, `BatCurrent`, `ReasonForRestingText` |
| Banque / WhizBang Jr *(Classic 1)* | `BatVoltage`, `SOC`, `WhizbangBatCurrent`, `RemainingAmpHours`, `TotalAmpHours`, `WbJrAmpHourNET`, `WbJrAmpHourPOSitive`, `WbJrAmpHourNEGative`, `BatTemperature`, `nominalBatteryVoltage` |
| Génératrice AUX 1 *(Classic 1)* | `Aux1VoltsLoAbs`, `Aux1VoltsHiAbs`, `Aux1DelayT`, `Aux1HoldT`, `Aux1FunctionText`, `InfoFlag_Aux1StateOn` |
| Fanions d'état | `InfoFlag_ClassicOverTemperature`, `InfoFlag_GroundFaultF`, `InfoFlag_ArcFaultF`, `InfoFlag_OCP`, `InfoFlag_LowBatteryVF`, `InfoFlag_HyperVoc`, `InfoFlag_CurrentLimit`, `InfoFlag_PvPartialShadeF`, `InfoFlag_EqualizeInProgress`, `InfoFlag_BatteryTempSensorInstalled` |

Une entité manquante s'affiche comme `unknown` ou « Entité non disponible »
dans la carte correspondante — c'est presque toujours un paramètre non coché.

### 3. Le matériel supposé

- Un **WhizBang Jr** branché sur le Classic 1 — sans lui, la section
  *Banque de batteries* reste vide.
- **AUX 1 du Classic 1** configuré pour démarrer une génératrice selon
  l'état de charge (fonction *SOC% HIGH* ou *SOC% LOW*) — voir la section
  *Scope* du [README principal](../../README.md). Sans génératrice, la
  section *Génératrice* n'a pas de sens et peut être supprimée.

### 4. Deux cartes personnalisées (HACS)

Installez depuis **HACS → Frontend** :

| Carte | Utilisée pour |
|---|---|
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | Tout le style (couleurs, polices, bordures) |
| [apexcharts-card](https://github.com/RomRider/apexcharts-card) | Les trois graphiques historiques |

Rechargez ensuite le navigateur (vider le cache si les cartes ne s'affichent pas).

---

## Installation

### 1. Activer les packages

Si ce n'est pas déjà fait, ajoutez ceci dans `configuration.yaml` :

```yaml
homeassistant:
  packages: !include_dir_named packages
```

et créez le répertoire `config/packages/` s'il n'existe pas.

> Si votre `configuration.yaml` contient déjà une clé `homeassistant:`,
> ajoutez seulement la ligne `packages:` sous celle-ci — ne créez pas une
> deuxième clé `homeassistant:`.

### 2. Copier le package

Copiez le package de votre variante dans `config/packages/` (avec l'add-on
*File editor*, *Studio Code Server*, Samba ou SSH).

### 3. Vérifier puis redémarrer

**Outils de développement → YAML → Vérifier la configuration**, puis
**Redémarrer**. Un simple rechargement ne suffit pas la première fois : les
capteurs `history_stats` et la clé `packages` exigent un redémarrage complet.

Après le redémarrage, ces entités doivent exister
(**Outils de développement → États**) :

- `sensor.classic_puissance_combinee`, `sensor.classic_recolte_jour`, `sensor.classic_energie_cumulee` *(version deux Classic seulement)*
- `sensor.banque_puissance_nette`, `sensor.banque_sens_du_courant`, `sensor.banque_energie_accumulee`, `sensor.banque_energie_fournie`
- `sensor.generatrice_statut`, `sensor.generatrice_marge_avant_demarrage`
- `sensor.generatrice_marche_aujourd_hui`, `sensor.generatrice_marche_7_jours`, `sensor.generatrice_demarrages_aujourd_hui`
- `binary_sensor.generatrice_en_marche`

> **Attention aux suffixes `_2`.** Si vous aviez déjà créé des capteurs du
> même nom, Home Assistant ajoute `_2` au nouveau (ex.
> `sensor.banque_sens_du_courant_2`) et le tableau de bord ne le trouvera
> pas. Supprimez l'ancienne entité, puis renommez la nouvelle sans le `_2`.

### 4. Créer le tableau de bord

1. **Paramètres → Tableaux de bord → + Ajouter un tableau de bord →
   Nouveau tableau de bord à partir de zéro**. Nommez-le (ex. *Classic*) et
   choisissez une icône (ex. `mdi:solar-power-variant`).
2. Ouvrez-le, puis **⋮ → Modifier le tableau de bord**. Si on vous le
   propose, choisissez *Commencer avec un tableau de bord vide*.
3. **⋮ → Éditeur de configuration brute**.
4. Remplacez tout le contenu par celui du tableau de bord de votre variante, puis
   **Enregistrer** et fermez l'éditeur.

La vue *Console* est de type `panel` : elle occupe toute la largeur de
l'écran.

### 5. Adapter les noms d'entités si vos Classic ne s'appellent pas `CLASSIC1` / `CLASSIC2`

L'intégration construit les identifiants d'entités à partir du nom lu dans
le Classic. Un Classic nommé `GARAGE` produit donc `sensor.garage_power`,
`sensor.garage_state_of_charge`, etc.

Vérifiez vos préfixes dans **Paramètres → Entités** (cherchez `_power`).

Ensuite, faites un *chercher-remplacer* **dans les deux fichiers de votre
variante** (le package **et** le tableau de bord) **avant** de les
installer :

| Chercher | Remplacer par (exemple) |
|---|---|
| `classic1_` | `garage_` |
| `classic2_` | `toit_` *(version deux Classic seulement)* |

N'incluez **que** le préfixe avec le chiffre et le trait de soulignement
(`classic1_`). Les entités du package (`sensor.classic_puissance_combinee`,
etc.) commencent par `classic_` sans chiffre et ne doivent pas être
modifiées.

En ligne de commande :

```bash
# Deux Classic
sed -i 's/classic1_/garage_/g; s/classic2_/toit_/g' classic_console.yaml tableau_de_bord.yaml

# Un seul Classic
sed -i 's/classic1_/garage_/g' classic_console_1classic.yaml tableau_de_bord_1classic.yaml
```

> En version deux Classic, le Classic **1** doit être celui qui porte le WhizBang Jr et la
> génératrice sur AUX 1 : la banque de batteries et la génératrice sont lues
> uniquement sur lui.

Si vous avez déjà installé le package avec les mauvais noms, corrigez le
fichier, puis redémarrez Home Assistant.

### 6. Ajuster les échelles à votre installation (facultatif)

Les valeurs suivantes correspondent à l'installation d'origine (banque
48 V, environ 1,3 kW et 1,5 kW de panneaux). Adaptez-les dans le tableau de
bord de votre variante :

| Élément | Clé | Valeur d'origine |
|---|---|---|
| Jauge *Puissance* Classic 1 | `max`, `severity` | 1400 W (jaune 900, rouge 1200) |
| Jauge *Puissance* Classic 2 | `max`, `severity` | 1600 W (jaune 1200, rouge 1400) |
| Section *Combiné* (deux Classic) | `pmax`, `rmax` | 2600 W, 30 kWh |
| Carte de puissance (un Classic) | `pmax`, `rmax` | 1400 W, 15 kWh |
| Jauge *Tension batt* | `min`, `max`, `severity` | 44 à 62 V (banque 48 V) |
| Jauge *Courant batt* | `min`, `max` | −150 à 150 A |

Pour une banque 12 V ou 24 V, divisez les bornes de tension par 4 ou par 2.

---

## Dépannage

| Symptôme | Cause probable |
|---|---|
| « Custom element doesn't exist: apexcharts-card » | La carte n'est pas installée par HACS, ou le cache du navigateur doit être vidé. |
| Cartes sans style (fond blanc ou gris standard) | `card-mod` absent ou non chargé. |
| Valeurs `unknown` dans une carte | Paramètre non coché dans les options de l'intégration (prérequis 2). |
| « Entité non disponible : sensor.classic_… » | Package non chargé : vérifier `packages:` dans `configuration.yaml` et redémarrer. |
| Section *Combiné* indisponible (deux Classic) | L'un des deux Classic ne répond pas. Les totaux sont volontairement indisponibles tant qu'une source manque, pour ne pas fausser le tableau Énergie. |
| Le nombre de démarrages est à 0 malgré une génératrice en marche | Normal le premier jour : le compteur ne voit que les cycles survenus après la création de l'entité. |

---

## Différences de la version un seul Classic

- En haut, une seule rangée : jauge de puissance, puissance et récolte du
  jour en gros caractères, puis l'état du contrôleur (étage, MPPT, FET).
- *Chaînes photovoltaïques* : la carte du Classic est accompagnée d'un
  graphique de puissance sur 24 h.
- *Fanions d'état* : les dix fanions sont répartis en deux cartes,
  *Défauts* et *Conditions*.
- Les sections *Banque de batteries* et *Génératrice* sont identiques.