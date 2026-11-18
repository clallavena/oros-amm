from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from common import (TODAY, INK, INK_2, GRID, SERIES, DATA_FILE, load_forms, output_path,
                    results_dir, require_columns, warn, style_axes)

# ---------------------------------------------------------------------------
# 1. Mapping des questions du TSV (même principe que attrakdiffReader.py)
# ---------------------------------------------------------------------------

# Questions à choix unique : code -> {libellé TSV: modalités ordonnées}
categorical = {'CONNAIT_AUTEUR': {"Connaissez-vous personnellement l'auteur du site ?": ['Oui', 'Non']},
               'SAIT_RESERVER' : {"A l'avenir, je saurais comment réserver une sortie": ['Oui', 'Non']},
               'INTERFACE'     : {'Interface utilisée ': ['Ordinateur', 'Smartphone', 'Tablette']},
               'NAVIGATEUR'    : {'Précisez le navigateur utilisé': ['Chrome', 'Firefox', 'Safari', 'Opera']},
               'AGE'           : {"Tranche d'âge": ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75']},
               'SORTIES_12M'   : {'Combien de sorties en montagne avez-vous faites ces 12 derniers mois ?':
                                      ['0', '1-2', '3-5', '6-10', 'plus de 10']},
               'RECOURS_PRO'   : {'Avez vous déjà fait appel à un professionel de la montagne':
                                      ['Jamais', 'Une fois', 'Plusieurs fois']},
               'HABITAT'       : {'Où habitez vous ?': ['Urbain', 'Rural', 'Zone montagne']},
               'INTENTION_12M' : {'Envisagez-vous une sortie accompagnée dans les 12 prochains mois ':
                                      ['Oui', 'Peut-être', 'Non']}}

# Échelles de 1 à 5 : code -> {libellé TSV: intitulé de la question}
likert = {'PLACE_MONTAGNE'  : {'Peu fort / Très forte': 'Place de la montagne dans la vie'},
          'CONNAISSANCE_AMM': {'Pas du tout / Absolument': "Je sais ce qu'un AMM peut me proposer"}}

# Cases à cocher : code -> libellé TSV
autonomie = {'AUTO1': 'Je ne pars jamais seul·e',
             'AUTO2': 'Je pars sur sentier balisés',
             'AUTO3': 'Je prépare mes itinéraires seul·e, y compris hors sentier',
             'AUTO4': "Je sais m'orienter en montagne",
             'AUTO5': 'Je sais identifier les risques',
             'AUTO6': 'Je connais le milieu naturel montagnard (faune, flore, geologie, paysage',
             'AUTO7': 'Rien de tout cela'}

sorties = {'SORT1': 'Randonnée à la journée',
           'SORT2': 'Randonnée à la demie journée',
           'SORT3': 'Itinérance de plusieurs jours',
           'SORT4': 'Randonnée raquettes'}

# Quiz : code -> {libellé TSV: True si l'activité est encadrable par un AMM}
quiz = {'AMM1': {'Randonnée estivale à la journée/demi journée': True},
        'AMM2' : {'Randonnée raquette dans la neige': True},
        'AMM3' : {'Randonnée dans la neige sans raquette': True},
        'AMM4' : {"Une course d'alpinisme côté F": False},
        'AMM5' : {"Une course d'orientation": True},
        'AMM6' : {'Itinérance en randonnée en autonomie en milieu isolé': True},
        'AMM7' : {'Du trail': True},
        'AMM8' : {'Une randonnée glaciaire': False},
        'AMM9' : {'Une sortie observation ornitho': True}}

def _labels():
    """Tous les libellés de colonnes attendus dans le TSV."""
    return ([next(iter(q)) for q in categorical.values()]
            + [next(iter(q)) for q in likert.values()]
            + list(autonomie.values()) + list(sorties.values())
            + [next(iter(q)) for q in quiz.values()])


def build_profile_df(forms_df: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par participant, une colonne par code, types nettoyés.
    Une modalité inconnue (ex. un nouveau navigateur) déclenche un avertissement
    au lieu de disparaître en silence : il suffit de l'ajouter au dict."""
    require_columns(forms_df, _labels(), 'Questionnaire')
    columns = {}
    for code, question in categorical.items():
        (label, levels), = question.items()
        raw = forms_df[label].astype('string').str.strip()
        # harmonise la casse ('chrome' -> 'Chrome') sur les modalités connues
        lookup = {level.lower(): level for level in levels}
        mapped = raw.str.lower().map(lookup)
        unknown = sorted(set(raw[mapped.isna() & raw.notna()]))
        if unknown:
            warn(f'[{code}] modalités non prévues dans le dict `categorical` : {unknown}')
        columns[code] = pd.Categorical(mapped, categories=levels, ordered=True)
    for code, question in likert.items():
        (label, _), = question.items()
        columns[code] = pd.to_numeric(forms_df[label], errors='coerce')
    for code, label in {**autonomie, **sorties}.items():
        columns[code] = forms_df[label].eq('X')
    for code, item in quiz.items():
        (label, _), = item.items()
        columns[code] = forms_df[label].eq('X')
    return pd.DataFrame(columns)



# ---------------------------------------------------------------------------
# 2. Description de l'échantillon
# ---------------------------------------------------------------------------

def frequencies(profile_df: pd.DataFrame) -> dict:
    """Tableau effectif / % pour chaque question à choix unique ou échelle."""
    tables = {}
    for code in [*categorical, *likert]:
        counts = profile_df[code].value_counts(sort=False).sort_index()
        tables[code] = pd.DataFrame({'n': counts,
                                     '%': (100 * counts / len(profile_df)).round(0)})
    return tables


def checkbox_rates(profile_df: pd.DataFrame, group: dict) -> pd.Series:
    """% de participants ayant coché chaque case."""
    return (100 * profile_df[list(group)].mean()).rename(group).round(0)


# ---------------------------------------------------------------------------
# 3. Quiz « activités encadrables par un AMM »
# ---------------------------------------------------------------------------

def score_quiz(profile_df: pd.DataFrame, quiz: dict) -> pd.DataFrame:
    """Par participant : bonnes réponses, oublis, faux positifs et score sur 9.
    Une bonne réponse = cocher une activité encadrable OU ne pas cocher une
    activité non encadrable."""
    key = pd.Series({code: next(iter(item.values())) for code, item in quiz.items()})
    answers = profile_df[key.index]
    correct = answers.eq(key, axis=1)
    return pd.DataFrame({'bonnes_reponses': correct.sum(axis=1),
                         'oublis': (~answers & key).sum(axis=1),          # encadrable non coché
                         'faux_positifs': (answers & ~key).sum(axis=1),   # non encadrable coché
                         'score_%': (100 * correct.mean(axis=1)).round(0)})


def quiz_by_activity(profile_df: pd.DataFrame, quiz: dict) -> pd.DataFrame:
    """Par activité : % de participants ayant donné la bonne réponse."""
    rows = []
    for code, item in quiz.items():
        (label, allowed), = item.items()
        rows.append({'code': code, 'activite': label, 'encadrable': allowed,
                     'reussite_%': round(100 * profile_df[code].eq(allowed).mean())})
    df = pd.DataFrame(rows).set_index('code')
    df.attrs['n'] = len(profile_df)
    return df


def knowledge_correlation(profile_df, quiz_scores):
    """Spearman entre connaissance perçue (1 à 5) et score réel au quiz."""
    data = pd.concat([profile_df['CONNAISSANCE_AMM'], quiz_scores['score_%']], axis=1).dropna()
    return stats.spearmanr(data.iloc[:, 0], data.iloc[:, 1])


# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------

TITLES = {'CONNAIT_AUTEUR': "Connaît l'auteur", 'SAIT_RESERVER': 'Saurait réserver',
          'INTERFACE': 'Interface', 'NAVIGATEUR': 'Navigateur', 'AGE': "Tranche d'âge",
          'SORTIES_12M': 'Sorties sur 12 mois', 'RECOURS_PRO': 'Recours à un pro',
          'HABITAT': 'Habitat', 'INTENTION_12M': 'Sortie accompagnée\ndans les 12 mois',
          'PLACE_MONTAGNE': 'Place de la montagne\n(1 = peu, 5 = très forte)',
          'CONNAISSANCE_AMM': "Sait ce qu'un AMM propose\n(1 = pas du tout, 5 = absolument)"}


def _style(ax, grid_axis='y'):
    style_axes(ax, grid_axis)


def plot_sample(profile_df: pd.DataFrame, path='questionnaire_echantillon.png'):
    """Petits multiples : une question par panneau, effectifs en barres."""
    N = len(profile_df)
    codes = [*categorical, *likert]
    fig, axes = plt.subplots(4, 3, figsize=(12, 13))
    for ax, code in zip(axes.flat, codes):
        counts = profile_df[code].value_counts(sort=False).sort_index()
        if code in likert:                                   # toutes les valeurs 1 à 5
            counts = counts.reindex(range(1, 6), fill_value=0)
        bars = ax.bar(counts.index.astype(str), counts.values, color=SERIES, width=0.6)
        ax.bar_label(bars, padding=2, color=INK, fontsize=8)
        ax.set_ylim(0, N + 1.5)
        ax.set_title(TITLES[code], loc='left', color=INK, fontsize=10)
        ax.tick_params(axis='x', labelsize=8, rotation=0)
        _style(ax)
    for ax in axes.flat[len(codes):]:
        ax.set_visible(False)
    fig.suptitle(f"Description de l'échantillon (n = {N}) – {TODAY}",
                 x=0.01, ha='left', color=INK, fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return fig


def plot_checkboxes(profile_df: pd.DataFrame, path='questionnaire_pratiques.png'):
    """Profil d'autonomie et types de sorties : % de participants par case."""
    N = len(profile_df)
    groups = [('Profil d\'autonomie en montagne', autonomie),
              ('Types de sorties pratiquées', sorties)]
    fig, axes = plt.subplots(2, 1, figsize=(9, 7),
                             gridspec_kw={'height_ratios': [len(autonomie), len(sorties)]})
    for ax, (title, group) in zip(axes, groups):
        rates = checkbox_rates(profile_df, group)
        bars = ax.barh(rates.index, rates.values, color=SERIES, height=0.6)
        ax.bar_label(bars, labels=[f'{v:.0f} %' for v in rates.values],
                     padding=3, color=INK, fontsize=8)
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
        ax.set_title(title, loc='left', color=INK, fontsize=10)
        ax.tick_params(axis='y', labelsize=8)
        _style(ax, grid_axis='x')
    fig.suptitle(f'Pratiques déclarées (% de participants, n = {N}) – {TODAY}',
                 x=0.01, ha='left', color=INK, fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return fig


def plot_quiz(quiz_items: pd.DataFrame, path='questionnaire_quiz_amm.png'):
    """Taux de bonnes réponses par activité, corrigé indiqué à droite."""
    N = quiz_items.attrs['n']
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(quiz_items['activite'], quiz_items['reussite_%'], color=SERIES, height=0.6)
    ax.bar_label(bars, labels=[f'{v} %' for v in quiz_items['reussite_%']],
                 padding=3, color=INK, fontsize=8)
    for y, allowed in enumerate(quiz_items['encadrable']):
        ax.text(1.02, y, 'encadrable' if allowed else 'non encadrable',
                transform=ax.get_yaxis_transform(), ha='left', va='center',
                color=INK_2, fontsize=8, fontweight='normal' if allowed else 'bold')
    ax.set_xlim(0, 112)
    ax.set_xticks(range(0, 101, 20))
    ax.invert_yaxis()
    ax.tick_params(axis='y', labelsize=8)
    _style(ax, grid_axis='x')
    ax.set_title(f'Quiz AMM : % de bonnes réponses par activité (n = {N}) – {TODAY}',
                 loc='left', color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return fig


def plot_knowledge_gap(profile_df, quiz_scores, path='questionnaire_connaissance_amm.png'):
    """Connaissance perçue (1 à 5) vs score réel au quiz."""
    N = len(profile_df)
    rho, _ = knowledge_correlation(profile_df, quiz_scores)
    data = pd.DataFrame({'percue': profile_df['CONNAISSANCE_AMM'],
                         'score': quiz_scores['score_%']})
    counts = data.groupby(['percue', 'score']).size().reset_index(name='n')
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(counts['percue'], counts['score'], s=60 + 90 * (counts['n'] - 1),
               color=SERIES, edgecolor='white', lw=2, zorder=3)
    for _, r in counts[counts['n'] > 1].iterrows():
        ax.annotate(f"×{int(r['n'])}", (r['percue'], r['score']), xytext=(10, 0),
                    textcoords='offset points', va='center', color=INK, fontsize=8)
    ax.set_xlim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_ylim(0, 105)
    ax.set_xlabel("« Je sais ce qu'un AMM peut me proposer » (1 à 5)", color=INK)
    ax.set_ylabel('Score au quiz (%)', color=INK)
    _style(ax)
    ax.set_title(f'Connaissance perçue vs réelle (n = {N}, ρ = {rho:.2f}) – {TODAY}',
                 loc='left', color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return fig


def run(forms_df: pd.DataFrame, out_dir='.'):
    """Profil, quiz et graphiques ; tableaux CSV enregistrés dans out_dir."""
    profile_df = build_profile_df(forms_df)
    n = len(profile_df)
    path = lambda name, ext='.png': output_path(out_dir, name, n, ext)
    quiz_scores = score_quiz(profile_df, quiz)
    quiz_items = quiz_by_activity(profile_df, quiz)

    freq = pd.concat({code: t for code, t in frequencies(profile_df).items()},
                     names=['question', 'modalite'])
    freq.to_csv(path('questionnaire_frequences', '.csv'))
    pd.concat([checkbox_rates(profile_df, autonomie), checkbox_rates(profile_df, sorties)]
              ).to_csv(path('questionnaire_cases_cochees', '.csv'), header=['%'])
    quiz_scores.to_csv(path('quiz_scores_participants', '.csv'))
    quiz_items.to_csv(path('quiz_reussite_activites', '.csv'))

    plot_sample(profile_df, path('questionnaire_echantillon'))
    plot_checkboxes(profile_df, path('questionnaire_pratiques'))
    plot_quiz(quiz_items, path('questionnaire_quiz_amm'))
    plot_knowledge_gap(profile_df, quiz_scores, path('questionnaire_connaissance_amm'))
    return profile_df, quiz_scores, quiz_items


if __name__ == '__main__':
    forms_df = load_forms(DATA_FILE)
    profile_df, quiz_scores, quiz_items = run(forms_df, results_dir(len(forms_df)))
    for code, table in frequencies(profile_df).items():
        print(f'\n{code}\n{table}')
    print('\n', quiz_scores, '\n\n', quiz_items, sep='')
    rho, p_value = knowledge_correlation(profile_df, quiz_scores)
    print(f'\nSpearman connaissance perçue / score : rho = {rho:.2f}, p = {p_value:.3f}')
