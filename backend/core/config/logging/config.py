import logging
import sys

# === 1. Créer un logger personnalisé === #
logger = logging.getLogger(__name__)

# === 2. Créer un ou plusieurs handler === #
# Diriger les logs vers "standard output"
stream_handler = logging.StreamHandler(sys.stdout)

# === 3. Ajouter les handlers au logger === #
logger.addHandler(stream_handler)


# === 4. Choisir un niveau de journalisation minimum === #
logger.setLevel(logging.DEBUG)

# === 5. Définir le format des logs === #
# Définir un format pour la console
stream_format = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] {%(module)s -> %(funcName)s} - %(message)s",
)

# Associer les formats au handlers
stream_handler.setFormatter(stream_format)
