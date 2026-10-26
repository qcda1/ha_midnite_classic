#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
from pymodbus.client import ModbusTcpClient as ModbusClient
from classic_registers import CLASSIC_REGISTERS as REGS
import time
import argparse
import logging
import sys
import os

"""
Variante de PrintRegisters.py qui permet d'EXCLURE certains registres de
l'affichage, via un fichier texte listant les numéros à ignorer.

Utilité: en cherchant un registre "caché" (ex: état du relais Aux1), on
élimine progressivement les registres déjà identifiés/non pertinents pour
ne garder que la liste des candidats restants.

Format du fichier d'exclusion (un par ligne):
    4101            -> exclut le registre 4101
    4160-4170       -> exclut la plage 4160 à 4170 inclusivement
    # commentaire   -> ligne ignorée
    (ligne vide)    -> ignorée

Si le fichier n'existe pas, il est simplement ignoré (aucune exclusion).

ATTENTION: À l'intérieur du Midnite Classic, la plage mémoire des registre ModBus
commence à zéro (0) mais la numérotation des registres commence à 4101. Il faut donc
soustraire 1 au numéro de registre qu'on passe à pymodbus pour lire et écrire dans
la bonne case mémoire.

ATTENTION: Écrire dans certains registres qui sont réservés ou qui sont en lecture
seulement ("R") peut mener à endommager l'appareil...

Document de référence: https://www.midnitesolar.com/pdfs/classic_register_map_Rev-C5-December-8-2013.pdf
"""

REG_MIN = 4101   # Premier registre du Classic
REG_MAX = 4384   # Dernier registre du Classic
CHUNK = 100      # Nombre max de registres lus par requête Modbus (limite protocole ~125)


def parse_range(texte):
    """Valide et convertit l'argument -r au format XXXX-YYYY.
    La même valeur des deux côtés (ex: 4115-4115) imprime un seul registre."""
    try:
        debut, fin = texte.split("-")
        debut = int(debut)
        fin = int(fin)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Format invalide '{texte}'. Format attendu: XXXX-YYYY (ex: 4115-4130)")
    if debut > fin:
        raise argparse.ArgumentTypeError(
            f"Le début de la plage ({debut}) doit être <= à la fin ({fin})")
    if debut < REG_MIN or fin > REG_MAX:
        raise argparse.ArgumentTypeError(
            f"La plage doit être entre {REG_MIN} et {REG_MAX}")
    return (debut, fin)


def charger_exclusions(chemin, log):
    """Charge la liste des registres à exclure depuis un fichier texte.
    Accepte des numéros seuls ou des plages 'NNNN-MMMM'. Lignes vides et
    lignes débutant par '#' sont ignorées. Si le fichier n'existe pas,
    retourne un ensemble vide silencieusement (comportement demandé)."""
    exclusions = set()
    if not chemin or not os.path.isfile(chemin):
        return exclusions
    with open(chemin, "r") as f:
        for ligne_brute in f:
            ligne = ligne_brute.strip()
            if not ligne or ligne.startswith("#"):
                continue
            if "-" in ligne:
                try:
                    a, b = ligne.split("-")
                    a, b = int(a), int(b)
                    if a > b:
                        a, b = b, a
                    exclusions.update(range(a, b + 1))
                except ValueError:
                    log.warning(f"Ligne d'exclusion invalide ignorée: '{ligne_brute.rstrip()}'")
            else:
                try:
                    exclusions.add(int(ligne))
                except ValueError:
                    log.warning(f"Ligne d'exclusion invalide ignorée: '{ligne_brute.rstrip()}'")
    return exclusions


parser = argparse.ArgumentParser(prog="PrintRegisters.py",
        description="Fetch and print Midnite Solar Classic registers, excluding "
                     "registers listed in an exclusion file. Useful for narrowing "
                     "down which register holds an undocumented value.",
        epilog="Output uses '-' as separator for easy csv import in Excel.")
parser.add_argument("-i", "--ip", default="192.168.20.10", type=str,
                    help="IP address of the Midnite Classic (default: %(default)s)")
parser.add_argument("-d", "--detail", default=2, type=int,
                    help="Level of detail (0 to 4) (default: %(default)s)")
# Groupe mutuellement exclusif pour -x, -b et -a
group = parser.add_mutually_exclusive_group()
group.add_argument("-x", "--hexa", action='store_true',
        help="Print values in hexadecimal 16 bits (default: %(default)s)")
group.add_argument("-b", "--bin", action='store_true',
        help="Print values in binary 16 bits, zero padded (default: %(default)s)")
group.add_argument("-a", "--all", action='store_true',
        help="Print values in decimal, hexadecimal and binary (default: %(default)s)")
parser.add_argument("-r", "--range", type=parse_range, default=(REG_MIN, REG_MAX),
        metavar="XXXX-YYYY",
        help="Range of registers to print, e.g. 4115-4130. "
             "Use the same value twice for a single register, e.g. 4115-4115 "
             "(default: %(default)s)")
parser.add_argument("-e", "--exclude", default="exclude.txt", type=str,
        help="Text file listing registers to exclude (one per line, or ranges "
             "'NNNN-MMMM'). Ignored silently if the file doesn't exist. "
             "(default: %(default)s)")
parser.add_argument("-l", "--loglvl", default="INFO", type=str,
                    help="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: %(default)s)")
parser.add_argument("-s", "--silence", action='store_true',
        help="Mode silencieux: seules les lignes de registres sont imprimées sur "
             "stdout (aucun bandeau, aucun message de log). Les logs vont sur "
             "stderr. Utile avec crontab + redirection vers un fichier "
             "(default: %(default)s)")
args = parser.parse_args()

# Configuration du logging
niveau = getattr(logging, args.loglvl.upper(), None)
if niveau is None:
    print(f"Log level invalide: {args.loglvl}")
    print("Exiting...")
    sys.exit(1)
if args.silence and niveau < logging.WARNING:
    # En mode silencieux, on ne veut ni INFO ni DEBUG, même si -l en demandait.
    # Seuls WARNING/ERROR/CRITICAL restent (sur stderr), pour ne pas cacher une vraie panne.
    niveau = logging.WARNING
logging.basicConfig(
    level=niveau,
    stream=sys.stderr if args.silence else sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)

if not args.silence:
    print(time.ctime())

if args.detail not in range(0, 5):
    print(f"Details need to be between 0 and 4. Not {args.detail}")
    print("Exiting...")
    sys.exit(1)

reg_debut, reg_fin = args.range
log.debug(f"Plage de registres demandée: {reg_debut} à {reg_fin}")

exclusions = charger_exclusions(args.exclude, log)
if os.path.isfile(args.exclude):
    log.info(f"{len(exclusions)} registre(s) exclu(s) depuis '{args.exclude}'")
else:
    log.debug(f"Fichier d'exclusion '{args.exclude}' introuvable, aucune exclusion appliquée")


def formate_valeur(value):
    """Retourne la valeur formatée selon les options -x, -b, -a ou décimal par défaut.
    Le séparateur '-' est conservé pour l'import Excel/csv."""
    if args.hexa:
        return f"{value:04x}"
    if args.bin:
        return f"{value:016b}"          # Left fill with zeros, 16 positions
    if args.all:
        return f"{value:<6} - {value:04x} - {value:016b}"
    return f"{value:<6}"


# Start by fetching Midnite Solar Charge controller data via
# Ethernet adaptor.
Host = args.ip
if not args.silence:
    print(f"Host: {Host}")

try:
    Midnite = ModbusClient(host=Host, port=502)
    connection = Midnite.connect()
    if not args.silence:
        print("Connection = ", connection)
    if not connection:
        log.error(f"Impossible de se connecter à {Host}:502")
        sys.exit(1)
except Exception as bugg:
    log.exception("Bug de comm, ModbusClient: " + str(bugg))
    sys.exit(1)

if not args.silence:
    print("List of Midnite Solar Classic registers (registres exclus omis).")
    print("Based on the register table in document: classic_register_map_Rev-C5-December-8-2013.pdf")
    print("List can be cut/paste in Excel for csv conversion using '-' as the separator value.")
    if args.hexa:
        print("Printing registers in hexadecimal...")
    if args.bin:
        print("Printing registers in binary...")
    if args.all:
        print("Printing registers in decimal - hexadecimal - binary...")
    if exclusions:
        print(f"Exclusion file: {args.exclude} ({len(exclusions)} registre(s) exclu(s))")
    print("\n\n")

# ATTENTION: adresse mémoire Modbus = numéro de registre - 1
# On lit par blocs de CHUNK maximum.
n = reg_debut - 1            # Adresse mémoire de départ
adresse_fin = reg_fin - 1    # Adresse mémoire du dernier registre demandé

erreurs_lecture = 0
registres_imprimes = 0
while n <= adresse_fin:
    z = min(CHUNK, adresse_fin - n + 1)   # Nombre de registres à lire ce tour-ci
    log.debug(f"Lecture Modbus: adresse {n}, count {z} (registres {n+1} à {n+z})")
    try:
        request = Midnite.read_holding_registers(n, count=z)
    except Exception as bugg:
        log.exception(f"Exception Modbus en lisant l'adresse {n} (registre {n+1}): {bugg}")
        erreurs_lecture += 1
        n = n + z
        continue

    if request is None or request.isError():
        log.error(f"Erreur de lecture Modbus à l'adresse {n} (registre {n+1}): {request}")
        erreurs_lecture += 1
        n = n + z
        continue

    for value in request.registers:
        numero = n + 1
        if numero in exclusions:
            n = n + 1
            continue
        valeur = formate_valeur(value)
        try:
            if args.detail == 0:
                print(f"{numero} - {valeur}")
            elif args.detail == 1:
                print(f"{numero} - {valeur} - {REGS[numero][0]:<3}")
            elif args.detail == 2:
                print(f"{numero} - {valeur} - {REGS[numero][0]:<3} - {REGS[numero][1]}")
            elif args.detail == 3:
                print(f"{numero} - {valeur} - {REGS[numero][0]:<3} - {REGS[numero][1]:<25} - {REGS[numero][2]}")
            elif args.detail == 4:
                print(f"{numero} - {valeur} - {REGS[numero][0]:<3} - {REGS[numero][1]:<25} - {REGS[numero][2]:<30} - {REGS[numero][3]}")
        except KeyError:
            log.warning(f"Registre {numero} absent du dictionnaire CLASSIC_REGISTERS")
            print(f"{numero} - {valeur} - ???")
        registres_imprimes += 1
        n = n + 1

Midnite.close()
log.info(f"{registres_imprimes} registre(s) imprimé(s), {len(exclusions)} exclu(s) de la plage demandée.")
if erreurs_lecture:
    log.warning(f"Terminé avec {erreurs_lecture} erreur(s) de lecture Modbus.")
else:
    log.info("Lecture terminée sans erreur.")
sys.exit(0)