# Midnite Solar Classic — Home Assistant Integration

*[Français](#français) | [English](#english)*

---

<a name="français"></a>
# 🇫🇷 Français

Intégration personnalisée pour les contrôleurs de charge solaire **Midnite Solar Classic 150** (et modèles compatibles).  
Communique avec l'appareil via **Modbus TCP**.

## Fonctionnalités

- Lecture périodique de tous les registres du Classic via Modbus TCP
- Intervalle de lecture configurable de **30 à 3 600 secondes**
- Sélection des paramètres à exposer comme entités HA via l'interface graphique
- Validation de la connexion et récupération automatique du nom de l'appareil lors de la configuration
- Support multi-appareils (plusieurs Classic avec des adresses IP différentes)
- Flux d'options (icône ⚙️) pour modifier l'intervalle et les paramètres sans reconfigurer

## Pré-requis

| Composant | Version |
|---|---|
| Home Assistant OS | 2026.3+ |
| pymodbus | ≥ 3.6.0 (installé automatiquement) |

Le Classic doit être connecté au réseau local et accessible depuis Home Assistant.

## Installation

### 1 — Cloner le dépôt dans Home Assistant

Via SSH sur votre instance HA :

```bash
cd /config/custom_components/
git clone https://github.com/qcda1/ha_midnite_classic.git ha_midnite_classic_repo
```

Ou pour une installation liée à Git (mises à jour via `git pull`) :

```bash
cd /config/custom_components/ha_midnite_classic
git init
git remote add origin https://github.com/qcda1/ha_midnite_classic.git
git pull origin main
```

### 2 — Structure du dossier installé
La structure suivante du répertoire est le résultat de l'étape 1:
```
custom_components/ha_midnite_classic/
├── __init__.py
├── classic_modbusdecoder.py
├── classic_reader.py
├── config_flow.py
├── const.py
├── coordinator.py
├── manifest.json
├── Payload.py
├── sensor.py
├── translations/
│   ├── en.json
│   └── fr.json
└── brand/
    ├── icon.png
    └── icon@2x.png
```

> Tous les fichiers nécessaires sont inclus dans ce dépôt — aucun téléchargement supplémentaire requis.

### 3 — Redémarrer Home Assistant

Paramètres → Système → Redémarrer.

### 4 — Ajouter l'intégration

Paramètres → Appareils et services → **+ Ajouter une intégration** → chercher **Midnite Solar Classic**.

## Configuration

### Étape 1 — Connexion

| Champ | Description | Défaut |
|---|---|---|
| Adresse IP | IP du Classic sur le réseau local | — |
| Port Modbus TCP | Port du serveur Modbus du Classic | **502** |
| Intervalle (s) | Fréquence de lecture en secondes (30–3600) | **60** |

L'intégration se connecte immédiatement pour valider la connexion et lire le nom de l'appareil (registre `Name`).

### Étape 2 — Paramètres surveillés

Une liste de cases à cocher affiche tous les paramètres retournés par votre Classic.  
Cochés par défaut :

`BatVoltage`, `PVVoltage`, `BatCurrent`, `EnergyToday`, `Power`, `ChargeStage`, `State`, `PVCurrent`, `TotalEnergy`, `Name`, `ChargeStateText`

## Entités créées

Chaque paramètre sélectionné devient un capteur (`sensor`) avec unité, classe d'appareil et classe d'état attribuées automatiquement.

| Paramètre | Unité | Classe |
|---|---|---|
| BatVoltage | V | voltage / measurement |
| PVVoltage | V | voltage / measurement |
| BatCurrent | A | current / measurement |
| Power | W | power / measurement |
| EnergyToday | kWh | energy / total_increasing |
| TotalEnergy | kWh | energy / total_increasing |
| BatTemperature | °C | temperature / measurement |
| ChargeStateText | — | — |

## Options

Cliquez sur ⚙️ pour modifier l'intervalle de lecture ou la liste des paramètres.  
Les changements prennent effet immédiatement.

## Ajouter plusieurs Classic

Répétez « Ajouter une intégration » avec une adresse IP différente pour chaque appareil.

## Dépannage

| Symptôme | Solution |
|---|---|
| « Impossible de se connecter » | Vérifier IP, port, et que le Classic est sous tension et accessible depuis HA |
| Entités indisponibles | Consulter les logs HA : Paramètres → Système → Journaux |
| Erreur pymodbus | Redémarrer HA — pymodbus ≥ 3.6.0 est installé automatiquement |

## Licence

MIT.  
Basé sur les travaux de [ClassicDIY/ClassicMQTT](https://github.com/ClassicDIY/ClassicMQTT) et [qcda1/MidniteClassic](https://github.com/qcda1/MidniteClassic).

---

<a name="english"></a>
# 🇨🇦 English

Custom integration for **Midnite Solar Classic 150** solar charge controllers (and compatible models).  
Communicates with the device over **Modbus TCP**.

## Features

- Periodic polling of all Classic registers via Modbus TCP
- Configurable polling interval from **30 to 3,600 seconds**
- Select which parameters to expose as HA entities via the UI
- Connection validation and automatic device name retrieval during setup
- Multi-device support (multiple Classic controllers with different IP addresses)
- Options flow (⚙️ icon) to change interval and parameters without reconfiguring (To be fixed)

## Requirements

| Component | Version |
|---|---|
| Home Assistant OS | 2026.3+ |
| pymodbus | ≥ 3.6.0 (installed automatically) |

The Classic must be connected to the local network and reachable from Home Assistant.

## Installation

### 1 — Clone the repository into Home Assistant

Via SSH on your HA instance:

```bash
cd /config/custom_components/
git clone https://github.com/qcda1/ha_midnite_classic.git ha_midnite_classic
```

Or for a Git-linked install (updates via `git pull`):

```bash
cd /config/custom_components/ha_midnite_classic
git init
git remote add origin https://github.com/qcda1/ha_midnite_classic.git
git pull origin main
```

### 2 — Installed folder structure

Step 1 creates the custom component folder structure as follwo:
```
custom_components/ha_midnite_classic/
├── __init__.py
├── classic_modbusdecoder.py
├── classic_reader.py
├── config_flow.py
├── const.py
├── coordinator.py
├── manifest.json
├── Payload.py
├── sensor.py
├── translations/
│   ├── en.json
│   └── fr.json
└── brand/
    ├── icon.png
    └── icon@2x.png
```

> All required files are included in this repository — no additional downloads needed.

### 3 — Restart Home Assistant

Settings → System → Restart.

### 4 — Add the integration

Settings → Devices & services → **+ Add integration** → search for **Midnite Solar Classic**.

## Configuration

### Step 1 — Connection

| Field | Description | Default |
|---|---|---|
| IP Address | Classic's IP on the local network | — |
| Modbus TCP Port | Classic's Modbus server port | **502** |
| Interval (s) | Polling frequency in seconds (30–3600) | **60** |

The integration connects immediately to validate the connection and read the device name (`Name` register).

### Step 2 — Monitored parameters

A checklist displays all parameters returned by your Classic.  
Checked by default:

`BatVoltage`, `PVVoltage`, `BatCurrent`, `EnergyToday`, `Power`, `ChargeStage`, `State`, `PVCurrent`, `TotalEnergy`, `Name`, `ChargeStateText`

## Created entities

Each selected parameter becomes a `sensor` entity with unit, device class and state class assigned automatically.

| Parameter | Unit | Class |
|---|---|---|
| BatVoltage | V | voltage / measurement |
| PVVoltage | V | voltage / measurement |
| BatCurrent | A | current / measurement |
| Power | W | power / measurement |
| EnergyToday | kWh | energy / total_increasing |
| TotalEnergy | kWh | energy / total_increasing |
| BatTemperature | °C | temperature / measurement |
| ChargeStateText | — | — |

## Options

Click ⚙️ to change the polling interval or the monitored parameter list.  
Changes take effect immediately.

## Multiple Classic controllers

Repeat "Add integration" with a different IP address for each device.

## Troubleshooting

| Symptom | Solution |
|---|---|
| "Cannot connect" | Check IP, port, and that the Classic is powered on and reachable from HA |
| Unavailable entities | Check HA logs: Settings → System → Logs |
| pymodbus error | Restart HA — pymodbus ≥ 3.6.0 is installed automatically |

## License

MIT.  
Based on the work of [ClassicDIY/ClassicMQTT](https://github.com/ClassicDIY/ClassicMQTT) and [qcda1/MidniteClassic](https://github.com/qcda1/MidniteClassic).
