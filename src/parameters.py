from pathlib import Path

PARENT_DIR = Path(__file__).parent.resolve().parent
DATA_DIR = PARENT_DIR / "data"


COLUMNS_FILTERS = [
    'Domaine professionnel', 
    'Grand domaine',
    'Métier',
    'Type de structure',
    'Numéro de département',
    'région',
    ]