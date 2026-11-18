"""Éléments partagés par les scripts d'analyse : lecture du TSV, style, date."""
from __future__ import annotations

import warnings
from datetime import date
from pathlib import Path

import pandas as pd

TODAY = date.today().strftime('%d%m%Y')   # format DDMMAAAA

INK, INK_2, GRID, SERIES = '#0b0b0b', '#52514e', '#e4e3df', '#2a78d6'
POSITIVE_BG, NEGATIVE_BG = '#e8f0fb', '#fbece6'

DATA_FILE = Path('data') / 'attrakdiff_orosens.tsv'
if not DATA_FILE.exists() and Path(DATA_FILE.name).exists():   # avant rangement
    DATA_FILE = Path(DATA_FILE.name)
RESULTS_DIR = Path('resultats')

# Participants à écarter de toute l'analyse : index de ligne -> raison.
# Ex. {12: 'doublon probable du participant 2'}
EXCLUDED_PARTICIPANTS: dict[int, str] = {}


def load_forms(path: str | Path) -> pd.DataFrame:
    """Lit l'export du formulaire.
    Ligne 0 vide, ligne 1 = "Item 1/3", ligne 2 = libellés des questions.
    Les lignes entièrement vides (réponse abandonnée) sont retirées."""
    forms_df = pd.read_csv(path, sep='\t', header=2, dtype=str)
    forms_df = forms_df.dropna(how='all').reset_index(drop=True)
    # on garde les index d'origine (le codage thématique s'appuie dessus)
    return forms_df.drop(index=[i for i in EXCLUDED_PARTICIPANTS if i in forms_df.index])


def output_path(out_dir, name: str, n: int, ext: str = '.png') -> Path:
    """Nom de fichier normalisé : <nom>_n<n>_<DDMMAAAA><ext>."""
    return Path(out_dir) / f'{name}_n{n}_{TODAY}{ext}'


def results_dir(n: int) -> Path:
    """Dossier de sortie d'un lancement : resultats/<DDMMAAAA>_n<n>/."""
    out = RESULTS_DIR / f'{TODAY}_n{n}'
    out.mkdir(parents=True, exist_ok=True)
    return out


def require_columns(forms_df: pd.DataFrame, labels, context: str):
    """Erreur explicite si une question a été renommée dans le formulaire."""
    missing = [label for label in labels if label not in forms_df.columns]
    if missing:
        raise KeyError(f'[{context}] colonnes absentes du TSV : {missing}')


def warn(message: str):
    warnings.warn(message, stacklevel=2)


def style_axes(ax, grid_axis=None):
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(GRID)
    ax.tick_params(colors=INK_2, length=0)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
