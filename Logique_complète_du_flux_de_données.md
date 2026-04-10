# Logique complète du flux de données

---

## Flux de données : Classic → HA

```
classic_modbusdecoder.py          const.py              sensor.py / config_flow.py
─────────────────────────         ─────────────────────  ──────────────────────────
getRegisters()                    PARAMETER_META         Entités HA
  └─ retourne TOUT le dict  ──►   (sous-ensemble)  ──►   (ce que l'utilisateur
     ex: 60+ clés                 (métadonnées)           a coché)
```

---

## Rôle de chaque fichier

**`classic_modbusdecoder.py`** — Source de vérité. Retourne **toutes** les valeurs lues depuis les registres Modbus, sans filtre. Aucune notion de HA ici.

**`const.py / PARAMETER_META`** — Dictionnaire de **métadonnées** pour les paramètres qu'on veut pouvoir exposer. Il ne contient pas forcément *tous* les paramètres retournés par le Classic — seulement ceux pour lesquels on veut définir une unité, une classe d'appareil, et une icône. Les paramètres absents de `PARAMETER_META` fonctionnent quand même, mais s'affichent sans unité ni icône.

**`config_flow.py`** — Lors de la configuration, lit les clés du dict retourné par `getRegisters()` et les propose toutes comme cases à cocher — qu'elles soient dans `PARAMETER_META` ou non.

**`sensor.py`** — Crée une entité pour chaque paramètre coché. Si le paramètre est dans `PARAMETER_META`, il hérite des métadonnées (unité, icône, etc.). Sinon, l'entité est créée quand même mais sans ces informations.

---

## Pour ajouter vos nouvelles valeurs

Vous avez donc **deux niveaux** selon ce que vous voulez :

**Niveau minimal** — la valeur apparaît dans la liste des cases à cocher lors de la configuration, sans unité ni icône :

Rien à faire dans `const.py` — si la clé est retournée par `getRegisters()`, elle apparaît automatiquement dans le config flow.

**Niveau complet** — avec unité, icône, classe d'appareil :

Ajoutez une entrée dans `PARAMETER_META` dans `const.py` :

```python
"MaNouvelleValeur": ("Nom affiché", "unité", "device_class", "state_class", "mdi:icon"),
```

Par exemple pour une tension :
```python
"AbsorbVoltage": ("Tension d'absorption", "V", "voltage", "measurement", "mdi:battery-arrow-up"),
```

Et si vous voulez qu'elle soit cochée par défaut à l'installation, ajoutez la clé dans `DEFAULT_PARAMETERS` également dans `const.py`.

---

## Pourquoi `PARAMETER_META` ne contient pas tout ?

C'est un choix délibéré fait au départ — on n'a défini les métadonnées que pour les paramètres les plus utiles. Les autres (comme `reserved1`, `StatusRoll`, les octets MAC individuels, etc.) sont retournés par le Classic mais n'ont pas de sens pratique pour la plupart des utilisateurs, donc on ne leur a pas attribué de métadonnées. Ils restent disponibles dans le config flow si quelqu'un veut les cocher quand même.