# ha_midnite_classic — notes pour la v1.3.0 (2026-07-27)

Restauration des informations omises lors du portage de
`MidniteClassic/classic_modbusdecoder.py` vers l'intégration Home Assistant.

Toutes les descriptions ont été **revalidées contre la documentation du
manufacturier** incluse dans le dépôt :
`docs/classic_register_map_Rev-C5-December-8-2013.pdf`
(MidNite Solar MODBUS Network Spec, tables 4120-1, 4164-1, 4165-1 à 4165-4, 4275-1).

---

## 1. `classic_modbusdecoder.py`

### Ce qui manquait et qui est restauré

| Élément | État avant | État après |
|---|---|---|
| `Aux1FunctionText` | **absent du dictionnaire** | restauré (table 4165-3) |
| `Aux2FunctionText` | **absent du dictionnaire** | restauré (table 4165-4) |
| `ReasonForRestingText` codes 14 et 15 | absents | ajoutés |
| `ReasonForRestingText` (30 codes) | textes abrégés | textes intégraux du manuel |
| Journalisation des valeurs inconnues | supprimée | rétablie (`log.warning` avec le host) |
| Texte de repli | `Unknown (x)` | `No text defined for this value...x` (comme l'original) |

### Corrections par rapport à la version d'origine

Deux erreurs présentes dans `MidniteClassic/classic_modbusdecoder.py` ont été
corrigées plutôt que recopiées :

1. **Clé dupliquée** dans `AUX1_funct` : `4: "WASTE NOT LOW"` puis `4: "RESERVED"`.
   Python conserve la dernière — « WASTE NOT LOW » était donc silencieusement perdu.
   Le manuel donne `4 = Waste Not Low`.
2. **Valeur 6 mal étiquetée** : l'original a `6: "TOGGLE TEST"`.
   Le manuel donne `6 = RESERVED (Unimplemented)`, `13 = TOGGLE TEST`.

Les valeurs `22 = SOC% HIGH` et `23 = SOC% LOW` ne figurent pas dans la Rev C.5
mais sont conservées (firmware plus récent) — ce sont elles qui pilotent le
démarrage de génératrice sur SOC.

### Décisions à valider

- **`MPPTModeText`** : la table du manuel (4164-1) n'énumère que les valeurs
  « mode ON » (impaires), avec la note « Bit 0 is the ON/OFF — subtract one (1)
  if showing mode as OFF ». La version HA mappait déjà les valeurs paires *et*
  impaires ; **cette version-là a été conservée**, car c'est la seule qui reste
  lisible quand le contrôleur MPPT est éteint (`switch.py` utilise le bit 0).
  Revenir à la table d'origine ferait afficher « Unknown (10) » à chaque arrêt.
- **`WizBangJrRawCurrent`** : l'original ne divise pas (valeur brute du registre
  4362), la version HA fait `/ 10.0`. **Aucun changement appliqué** — à trancher,
  mais `const.py` annonce l'unité « A » et une précision de 0, ce qui suggère
  que la division était volontaire.
- **`EqualiseIntervalDay` → `EqualizeIntervalDay`** : l'orthographe HA est
  conservée, `const.py` et `WRITABLE_REGISTERS` en dépendent.

### Note technique

Home Assistant refuse un état de plus de 255 caractères. Le texte le plus long
restauré (code 26) fait 149 caractères, donc aucun problème — mais un garde-fou
`MAX_STATE_LENGTH` a été ajouté dans `_lookup()` pour éviter une entité
indisponible si un texte devait s'allonger un jour. C'est probablement ce risque
qui avait motivé l'abrègement initial.

---

## 2. `const.py`

`PARAMETER_META` ne couvrait qu'une partie de ce que le décodeur produit.
Comme `config_flow.py` construit la liste des paramètres avec
`[k for k in PARAMETER_META if k in data]`, tout ce qui manquait dans
`PARAMETER_META` était **invisible et non sélectionnable** dans l'UI.

### 26 clés ajoutées

- **WhizBang Jr / batterie** : `SOC`, `RemainingAmpHours`, `TotalAmpHours`,
  `WhizbangBatCurrent`, `ShuntTemperature`, `WbJrAmpHourPOSitive`,
  `WbJrAmpHourNEGative`, `WbJrAmpHourNET`
- **AUX** : `Aux12Function`, `Aux1Function`, `Aux1FunctionText`,
  `Aux1OffAutoOn`, `Aux1OffAutoOnText`, `Aux2Function`, `Aux2FunctionText`,
  `Aux2OffAutoOn`, `Aux2OffAutoOnText`
- **Textes** : `MPPTModeText`, `ReasonForRestingText`
- **Divers** : `VbattRegSetPTmpComp`, `nominalBatteryVoltage`, `app_rev`,
  `net_rev`, `IP`, `MAC`

> `SOC` était notamment absent — donc impossible à exposer comme entité par
> l'intégration, alors que c'est la valeur centrale de l'automatisation de
> génératrice.

### 6 clés fantômes retirées

`Aux1Mode`, `Aux2Mode`, `BatType`, `VbatRegSetpoint`, `AbsorbVoltage`,
`FloatVoltage` — aucune n'est produite par le décodeur. Sans conséquence en
fonctionnement normal (filtrées par `k in data`), mais `config_flow.py` retombe
sur `list(PARAMETER_META.keys())` quand le Classic est injoignable : l'usager
pouvait alors cocher des paramètres qui n'existeraient jamais.

Restent volontairement hors de `PARAMETER_META` (usage interne) :
`Name0`–`Name7`, `CTIME0`–`CTIME2`, `WizBangCRC`, `reserved1`,
`ChargeStateIcon`, `SOCicon`.

---

## 3. `translations/en.json` et `fr.json`

- 26 libellés ajoutés (EN + FR) pour les nouvelles clés.
- 6 libellés fantômes retirés.
- Coquille corrigée dans `en.json` : `EquilizeTime` → `EqualizeTime`
  (le libellé n'était donc jamais appliqué).

## 4. `manifest.json` / `const.py`

Version portée de `1.1.0` à `1.2.0`.

---

## Fichiers *non* modifiés

- `sensor.py` — générique, lit `PARAMETER_META` ; aucune adaptation requise.
- `classic_reader.py`, `coordinator.py` — signature de `getRegisters()` inchangée.
- `switch.py`, `number.py`, `button.py`, `classic_writer.py` — aucune des clés
  qu'ils utilisent n'a changé de nom.
- `classic_registers.py` — table de référence déjà complète.

## Vérifications faites

- `ast.parse()` OK sur les deux fichiers Python.
- JSON valide pour les deux fichiers de traduction.
- Test unitaire des extractions de bits AUX et des tables de correspondance
  (ex. `Aux12Function = 0x5257` → Aux1 = « SOC% LOW » / « AUX Auto »,
  Aux2 = « Whizbang Junior (WB Jr.) » / « AUX Auto »).

## À tester sur le Classic réel

1. Recharger l'intégration, vérifier les nouvelles entités dans les options.
2. Confirmer que `Aux1FunctionText` correspond bien au réglage physique de l'Aux1.
3. Vérifier `WizBangJrRawCurrent` contre l'affichage du Classic pour trancher la
   question du `/10`.