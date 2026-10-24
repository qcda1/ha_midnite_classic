# ha_midnite_classic — notes pour la v1.4.0

Contrôle de génératrice par la sortie relais AUX 1, exposition complète du
mot d'état `InfoFlagsBits`, et instrumentation des échecs de communication.

Base : v1.3.0 (dernière version publiée sur GitHub).

Toutes les définitions viennent de
`docs/classic_register_map_Rev-C5-December-8-2013.pdf` (tables 4130-1, 4165-1,
et le tableau des registres 4166–4172). **Les unités et les échelles ont été
validées au banc sur un Classic 150 réel** — console MNGP et cycles de
génératrice chronométrés. Là où le manuel et la mesure divergent, c'est la
mesure qui a été retenue, et l'écart est documenté dans le code.

---

## 1. Registres AUX 1 en lecture/écriture (4166, 4167, 4168, 4172)

### Lecture

Le bloc `4161` ne lisait que 4 registres (4162 → 4165). Il en lit maintenant
**11** (4162 → 4172) :

| Registre | Clé | Manuel |
|---|---|---|
| 4166 | `Aux1VoltsLoAbs` | Aux 1 Low Absolute Threshold Voltage |
| 4167 | `Aux1DelayT` | Aux 1 Delay time before Asserting |
| 4168 | `Aux1HoldT` | Aux 1 Hold time before De-asserting |
| 4169 | `Aux2PwmVwidth` | Voltage range over which PWM operates (lecture seule) |
| 4170-4171 | — | RESERVED, sautés |
| 4172 | `Aux1VoltsHiAbs` | Aux 1 High Absolute Threshold Voltage |

### Écriture

Les quatre registres sont ajoutés à `WRITABLE_REGISTERS` et à `PARAMETER_META`
avec `writable=True`. `number.py` crée automatiquement les entités « (Set) »
correspondantes — aucun code supplémentaire nécessaire.

Tous sont marqués **(EE)** dans le manuel : les valeurs s'appliquent
immédiatement mais sont perdues au redémarrage du Classic tant que le bouton
« Save Settings to EEPROM » n'a pas été pressé.

### Unités : deux écarts par rapport au manuel

**Seuils 4166 / 4172 — pourcentage, aucune division.**
Le manuel documente `([reg] / 10) Volts`. En mode SOC% HIGH/LOW
(`Aux1Function` 22/23), ces registres contiennent en réalité un pourcentage
d'état de charge. Confirmé sur la console MNGP : un registre à 94 s'affiche 94,
pas 9,4. Cette égalité est d'ailleurs la preuve du mode SOC% — en mode tension,
registre et affichage ne coïncideraient pas.

→ unité `%`, échelle 1, précision 0, plage 0–100.

**Délais 4167 / 4168 — dixièmes de seconde, pas millisecondes.**
Le manuel indique « Milliseconds ». C'est faux pour ce firmware. Trois
transitions de relais chronométrées :

| Transition | Condition remplie | Relais | Écart | Registre | Attendu à 0,1 s/unité |
|---|---|---|---|---|---|
| Démarrage | 12:58:12 (seuil bas 89 > SOC 88) | 12:59:12 | 60 s | `hold = 600` | 60 s |
| Arrêt | 15:33:34 (SOC 91 > seuil haut 90) | 15:34:04 | 30 s | `delay = 300` | 30 s |
| Démarrage | 16:03:57 (seuil bas 93 > SOC 92) | 16:13:57 | 600 s | `hold = 6000` | 600 s |

Trois correspondances exactes sur deux ordres de grandeur, cohérentes avec
l'affichage MNGP (registre 10 → 1,0 s).

→ unité `s`, échelle 10, précision 1, pas 0,1, plage 0–6553,5
(registre 16 bits : 65535 → 6553,5 s).

### Les deux délais sont croisés par rapport à leur nom

Le tableau ci-dessus montre autre chose : c'est **`Aux1HoldT` (4168) qui retarde
le démarrage** de la génératrice, et **`Aux1DelayT` (4167) qui retarde l'arrêt**.

Ce n'est pas une erreur du manuel. `Aux1Function = 23` (« SOC% LOW ») est une
fonction **Active Low** : la sortie est asservie à l'inverse de la condition
logique. Les noms du manuel se lisent donc du côté de la condition, pas du relais :

| Registre | Nom manuel | Événement logique | Effet réel |
|---|---|---|---|
| 4167 `Aux1DelayT` | Delay before **Asserting** | SOC repasse au-dessus du seuil haut | délai avant **arrêt** |
| 4168 `Aux1HoldT` | Hold before **De-asserting** | SOC descend sous le seuil bas | délai avant **démarrage** |

En mode Active High (fonction 22), la correspondance s'inverse. Les noms des
entités restent ceux du manufacturier pour préserver la traçabilité avec les
registres ; le comportement réel est documenté dans `const.py` et le décodeur.

---

## 2. AUX 1 Off / Auto / On — nouvelle plateforme `select`

Table 4165-1 : le champ vit dans les **bits 6-7 du registre 4165**
(`Aux12Function`).

`select.aux_1_mode`, trois options :

| Valeur | Option | Description (manuel) |
|---|---|---|
| 0 | Aux 1 Off | Aux 1 output is forced OFF (0 Volts) |
| 1 | Aux 1 Auto | Aux 1 operates automatically as defined in Aux1Function |
| 2 | Aux 1 On | Aux 1 output is forced ON (~14 Volts) |

La valeur 3 (« Aux 1 Unimplemented ») n'est pas sélectionnable mais est
journalisée si l'appareil la rapporte.

### Le point critique : lecture-modification-écriture

Le registre 4165 empile quatre champs indépendants :

```
bits 0-5    Aux1Function       (ex. 23 = SOC% LOW)
bits 6,7    Aux1OffAutoOn      <-- seul champ modifié
bits 8-13   Aux2Function       (ex. 18 = Whizbang Junior)
bits 14,15  Aux2OffAutoOn
```

Écrire la valeur du mode seule effacerait l'affectation du WhizBang Jr et la
fonction SOC% de l'AUX 1. `write_aux1_off_auto_on()` fait donc
`(Aux12Function & ~0x00C0) | (mode << 6)`.

Vérifié : à partir de `Aux12Function = 0x5257`, les trois modes donnent
0x5217 / 0x5257 / 0x5297, avec `Aux1Function`, `Aux2Function` et
`Aux2OffAutoOn` intacts dans les trois cas.

En cas d'échec d'écriture : notification persistante et retour à l'état lu sur
l'appareil, comme pour l'interrupteur MPPT existant.

---

## 3. Registre 4130 (`InfoFlagsBits`) éclaté — nouvelle plateforme `binary_sensor`

### Dans le décodeur

La structure de `doDecode()` est **inchangée** : `("InfoFlagsBits",
decoder.decode_32bit_uint())` reste tel quel et le capteur existant continue de
fonctionner. L'éclatement se fait dans le post-traitement, comme les autres clés
dérivées (`ChargeStateText`, `Aux1FunctionText`, etc.).

Nouvelle table `INFO_FLAG_BITS` : `clé -> (masque, nom du manufacturier,
description du manufacturier)`. **25 fanions** ; les bits RESERVED (0x10, 0x20,
0x40, 0x800, 0x1000, 0x100000, 0x80000000) sont omis.

Les noms respectent la table 4130-1 telle quelle, y compris les graphies
d'origine : `StackumperF`, `XtraInfo2DsplayF`, `UN-LockJumperF`,
`OCP (Over Current Protect)`. Les clés sont préfixées `InfoFlag_` pour éviter
toute collision avec les clés de registres.

### Dans Home Assistant

Une entité par fanion, avec la description du manufacturier en attribut d'état
(`flag_name`, `description`, `mask`, `source_register`).

- **Entités normales** : `Aux 1 State On`, `Aux 2 State On`,
  `Equalize In Progress`.
- **Entités diagnostic** : les 22 autres.
- **`device_class: problem`** sur les fanions de défaut (EEPROM, GroundFault,
  ArcFault, OCP, NegBatCurrent, LowBatteryV, TempCompShorted, InputShorted,
  HyperVoc) et **`heat`** sur la surchauffe → affichage Problème/OK.

`InfoFlag_Aux1StateOn` (masque `0x00004000`, bit 14) est le fanion identifié
pour l'état du relais AUX 1. L'entité s'appelle
`binary_sensor.<nom_appareil>_aux_1_state_on` — aucun conflit avec un
`binary_sensor.aux1_relay_state` existant.

---

## 4. Diagnostic de communication

Chantier mené séparément des trois précédents, en septembre 2026, et intégré à
la v1.4.0 au moment du commit.

### Le problème d'origine

`async_read_classic()` ne rapportait que `getRegisters returned empty data`.
Ce message ne distingue pas « le réseau a disparu » de « le Classic a refusé
la connexion », ce qui rendait impossible de savoir où chercher. Les erreurs
survenaient plusieurs fois par jour sur l'instance du chalet et laissaient des
trous dans les graphiques.

### Sonde TCP et `errno` réel

Chaque lecture ouvre d'abord une connexion TCP nue (`_probe_tcp()`) avant
d'appeler le décodeur. L'`errno` est conservé et nommé via `errno.errorcode` :

- `ENETUNREACH` / `EHOSTUNREACH` → la route ou l'adresse source a disparu ;
- `ECONNREFUSED` / `ECONNRESET` → le Classic a refusé ou coupé la session ;
- `errno=None` avec une durée proche du timeout → timeout de connexion.

La durée de la sonde est mesurée et journalisée. C'est elle qui a résolu le
cas : des `ENETUNREACH` en **0–1 ms** prouvaient que le noyau rejetait
`connect()` sans émettre un paquet, donc une perte de porteuse côté hôte. La
cause s'est révélée être le verrou d'insertion brisé du connecteur RJ45 du
RPi4, le câble légèrement sorti — lien replié à 100 Mbps et porteuse perdue
~15 fois par jour.

### Reprises avec attente croissante

`async_read_classic_ex()` réessaie en attendant `backoff × n` entre les essais.
Défauts : 3 essais, timeout de connexion 3 s, backoff 2 s — soit environ 15 s
de panne couverts, sous l'intervalle de scrutation de 60 s.

Une coupure plus courte que cette fenêtre devient invisible : la lecture
réussit au 2e ou 3e essai et aucun trou n'apparaît dans le recorder. Les
paramètres sont exposés en keyword-only sur le coordinator
(`read_attempts`, `connect_timeout`, `retry_backoff`).

### Compatibilité ascendante

`async_read_classic()` conserve sa signature et son contrat (`dict | None`).
La nouvelle `async_read_classic_ex()` retourne `(data, ReadDiagnostics)` et
n'est appelée que par le coordinator.

`config_flow.py` passe `attempts=1` : à la configuration, un hôte injoignable
doit échouer en 3 s plutôt que de faire patienter l'utilisateur 15 s devant un
formulaire. Les reprises ne servent qu'au polling continu.

### Compteurs de santé

Le coordinator tient `consecutive_errors`, `total_reads`, `total_errors`,
`last_success`, `last_error`, `last_read_ms`, et un `deque` des 20 dernières
défaillances. `diagnostic_snapshot()` les expose en bloc.

### Téléchargement de diagnostics

`diagnostics.py` (nouveau) implémente
`async_get_config_entry_diagnostics()`. Le bouton apparaît sous Paramètres →
Appareils et services → Midnite Solar Classic → ⋮ → Télécharger les
diagnostics.

`_collect_coordinators()` parcourt `hass.data[DOMAIN][entry.entry_id]` de
manière tolérante (coordinator direct, dict, liste, ou objet porteur), pour ne
pas dépendre de la forme exacte du stockage.

Le rapport contient `entry.data` et `entry.options` — donc l'hôte et le port,
qui sont le sujet même du rapport. Aucune donnée d'authentification n'est
stockée par l'intégration.

### Messages en anglais

Tous les messages de journal et le texte remonté dans `UpdateFailed` sont en
anglais. `diag.summary` s'affiche dans l'interface Home Assistant de
l'utilisateur, et le dépôt est public.

---

## 5. Fichiers touchés

| Fichier | Nature |
|---|---|
| `classic_modbusdecoder.py` | bloc 4161 étendu à 11 registres, 6 clés décodées, `/10` sur les deux délais, table `INFO_FLAG_BITS`, éclatement des 25 fanions |
| `classic_writer.py` | nouvelle fonction `write_aux1_off_auto_on()` |
| `classic_reader.py` | sonde TCP, `errno` nommé, `ReadDiagnostics`, reprises avec attente croissante, `async_read_classic_ex()` |
| `coordinator.py` | compteurs de santé, historique des défaillances, `diagnostic_snapshot()`, paramètres de reprise |
| `config_flow.py` | `attempts=1` sur les lectures de validation |
| `diagnostics.py` | **nouveau** — téléchargement de diagnostics de l'entrée de configuration |
| `select.py` | **nouveau** — entité AUX 1 Off/Auto/On |
| `binary_sensor.py` | **nouveau** — 25 entités Info Flag |
| `sensor.py` | ajout de `"duration": SensorDeviceClass.DURATION` à `_DEVICE_CLASS_MAP` |
| `const.py` | 5 entrées `PARAMETER_META`, 4 entrées `WRITABLE_REGISTERS`, constantes AUX 1, table `INFO_FLAG_META` |
| `__init__.py` | `Platform.SELECT` et `Platform.BINARY_SENSOR` enregistrées |
| `translations/en.json`, `fr.json` | libellés des nouveaux paramètres, entités number, select et 25 binary sensors |
| `manifest.json` | 1.3.0 → 1.4.0 |

**Correctif au passage** : `const.py` était resté à `VERSION = "1.2.0"` alors que
`manifest.json` annonçait `1.3.0`. Les deux sont maintenant à `1.4.0`.

Fichiers **non modifiés** : `number.py`, `button.py`, `switch.py`, `classic_registers.py`.
Les nouvelles entités number apparaissent automatiquement parce que `number.py`
itère sur `WRITABLE_REGISTERS`, et `config_flow.py` force déjà l'inclusion des
clés écrivables.

---

## 6. Limites connues

### Seuils figés en pourcentage

Un utilisateur dont l'AUX 1 est en mode tension (fonctions 1 à 4, 7, 8, 17 à
20) verrait « 292 % » là où le Classic affiche 29,2 V, et la plage 0–100
l'empêcherait d'écrire au-delà de 10,0 V.

Rendre ça adaptatif suppose de dériver l'unité **et** l'échelle d'écriture de
`Aux1Function` à la création des entités, ce qui touche `sensor.py`, `number.py`
et `classic_writer.py`. HA gérant mal un changement d'unité en cours de route
(avertissements, statistiques invalidées), le plus propre serait de résoudre
l'unité une fois au démarrage et d'exiger un rechargement de l'intégration après
un changement de `Aux1Function`. À faire seulement si le cas est rapporté.

### `entry.data` conserve des valeurs périmées

Relevé dans les diagnostics du 2026-10-23 : `entry.options` porte
`scan_interval: 60` et une liste `monitored_parameters` plus longue, tandis que
`entry.data` garde `scan_interval: 30` et une liste plus courte, héritée de la
configuration initiale.

Le comportement est correct — les options ont la priorité et c'est bien 60 s
qui s'applique. Mais tout code qui lirait `entry.data` plutôt que
`entry.options` obtiendrait la valeur périmée. À assainir lors d'une prochaine
révision du config flow.

---

## 7. Effet de bord à connaître : la carte journal

Les entités `sensor` porteuses d'une unité sont automatiquement exclues du
journal (« Activity ») de Home Assistant — protection documentée contre
l'inondation par les capteurs à variation rapide. Les quatre registres AUX 1
n'y apparaîtront donc pas.

L'historique n'est pas perdu pour autant : recorder, page Historique, cartes
`history-graph`, ApexCharts et statistiques continuent de tout voir. Pour
conserver une trace datée dans le journal, deux options :

- les entités jumelles `number.*_(Set)` ne sont pas dans le domaine `sensor` et
  restent donc visibles au journal ;
- une automatisation sur changement d'état appelant `logbook.log`, avec
  `entity_id` pointé sur `binary_sensor.*_aux_1_state_on` pour que les
  changements de configuration et les cycles de génératrice se retrouvent dans
  le même journal.

---

## 8. Vérifications faites

### AUX 1, select, binary sensors

- `ast.parse()` OK sur les fichiers Python modifiés ou créés ; JSON valide pour
  les deux fichiers de traduction.
- Décodage simulé du bloc 4161 sur 11 registres : `89 / 300 / 600 / 25 / 92`
  → `89 % / 30,0 s / 60,0 s / 25 / 92 %`, RESERVED sautés, alignement exact.
- Aller-retour écriture (`raw = round(valeur_HA × scale)`) sur les valeurs
  réelles des essais : 1,0 s → 10, 30,0 s → 300, 60,0 s → 600, 600,0 s → 6000,
  94 % → 94.
- Éclatement de `InfoFlagsBits` testé sur `0x00006008` → `Equalize In Progress`,
  `Battery Temp Sensor Installed`, `Aux1 State On`.
- Les 25 masques sont uniques ; `INFO_FLAG_BITS` et `INFO_FLAG_META` ont
  exactement les mêmes clés.
- Read-modify-write AUX 1 testé sur les trois modes, champs voisins préservés.
- Corrélation des trois transitions de relais recalculée depuis l'historique HA :
  écarts de 60 s, 30 s et 600 s, tous exacts à la seconde.

### Diagnostic de communication

- Validé en conditions réelles sur l'instance du chalet pendant un mois, avec
  des coupures réseau quotidiennes.
- Reprise observée en direct le 2026-09-24 à 09:46:54 : deux `ENETUNREACH` puis
  réussite au 3e essai en 6025 ms, sans trou dans le recorder.
- Échec complet observé à 09:49:03 : trois essais sur 9011 ms, `errno=101`
  journalisé, rétablissement au cycle suivant.
- Téléchargement de diagnostics vérifié le 2026-10-23 : le rapport sort avec le
  coordinator, ses compteurs et son historique. 2851 lectures, 0 erreur,
  `success_rate = 1.0` depuis la réparation du câble.

---

## 9. Note pour l'instance de test

L'instance Debian et HA font déjà tourner une v1.4.0 intermédiaire où les délais
étaient exposés bruts et sans unité. Après application de la version finale :

1. L'historique des deux délais change d'échelle — ce qui affichait 600
   affichera 60. Les points antérieurs restent à l'ancienne échelle dans le
   recorder.
2. `state_class` étant nouvellement défini, les statistiques long terme
   commencent à s'accumuler maintenant, sans rétroactivité. Aucun conflit
   d'unité n'est à craindre puisqu'aucune statistique n'existait avant.
3. Les quatre registres disparaissent de la carte journal (voir section 7).

Les trois fichiers de diagnostic tournent déjà sur l'instance ; ils y ont été
copiés à la main et le `diff` du 2026-10-23 confirme qu'ils sont identiques à
ceux du dépôt.

---

## 10. À revalider avant le push

1. Rechargement de l'intégration, entités présentes et numériques.
2. `select.aux_1_mode` : Auto → Off → Auto, puis relire `Aux1FunctionText` et
   `Aux2FunctionText` — doivent rester « SOC% LOW » et « Whizbang Junior (WB Jr.) ».
3. Écriture d'un délai depuis HA (ex. 45,0 s) et relecture sur le MNGP.
4. « Save Settings to EEPROM », redémarrage du Classic, valeurs conservées.
5. Téléchargement de diagnostics : le rapport contient bien le coordinator.
6. Config flow avec une adresse injoignable : échec en ~3 s, pas en ~15 s.