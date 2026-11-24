from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from common import (TODAY, INK, INK_2, GRID, DATA_FILE, load_forms, output_path, results_dir,
                    require_columns, warn, style_axes)

# ---------------------------------------------------------------------------
# 4. Analyse thématique des réponses ouvertes (Braun & Clarke, 2006)
#    Codage inductif : les codes viennent des réponses, puis sont regroupés
#    en thèmes. Chaque code porte une valence : '+' (point fort) / '-' (manque).
# ---------------------------------------------------------------------------

Q_RETENU = "Que retenez-vous du site ? de l'accompagnateur ? Des sorties proposées ?"
Q_QUESTIONS = "Aujourd'hui, quelles questions vous restent-il avant de réserver une sortie ?"

# Grille de codes : code -> {libellé: (thème, valence)}
codebook_retenu = {'ESTHETIQUE'  : {'Esthétique, design agréable': ('Interface', '+')},
                   'FACILITE'    : {"Facilité d'utilisation, fluidité": ('Interface', '+')},
                   'CLARTE'      : {'Clarté, organisation': ('Interface', '+')},
                   'PHOTOS'      : {'Photos, visuels': ('Interface', '+')},
                   'AFFICHAGE_PC': {'Images moins bien rendues sur PC (format fixe)': ('Interface', '-')},
                   'INFORMATIF'  : {'Contenu complet, précis, instructif': ('Contenu', '+')},
                   'DENSITE'     : {'Trop de contenu': ('Contenu', '-')},
                   'FILTRES'     : {'Filtres des sorties peu aidants': ('Contenu', '-')},
                   'DIVERSITE'   : {'Diversité des sorties et des niveaux': ('Offre de sorties', '+')},
                   'PROJECTION'  : {'Les sorties donnent envie, on se projette': ('Offre de sorties', '+')},
                   'TARIFS'      : {'Tarifs abordables': ('Offre de sorties', '+')},
                   'BIVOUAC'     : {'Pas de sortie en bivouac': ('Offre de sorties', '-')},
                   'PARCOURS'    : {"Parcours de l'accompagnateur": ('Accompagnateur', '+')},
                   'VISION'      : {'Vision du métier, supplément d\'âme': ('Accompagnateur', '+')},
                   'POSTURE_PRO' : {'Professionnalisme, transparence, prévention': ('Accompagnateur', '+')},
                   'CULTURE'     : {'Dimension ludique et culturelle': ('Accompagnateur', '+')},
                   'NOM_MARQUE'  : {'Sens du nom « Orosens » compris': ('Accompagnateur', '+')}}

codebook_questions = {'AUCUNE'        : {'Aucune question': ('Aucune', '+')},
                      'LOGISTIQUE'    : {'Déroulé : RDV, durée, programme, taille du groupe': ('Préparation', '-')},
                      'MATERIEL'      : {'Quoi apporter : eau, encas, matériel': ('Préparation', '-')},
                      'PRIX'          : {'Prix pas visible avant le formulaire': ('Conditions', '-')},
                      'ANNULATION'    : {"Conditions d'annulation": ('Conditions', '-')},
                      'CHIEN'         : {'Chien accepté ?': ('Conditions', '-')},
                      'PREUVE_SOCIALE': {'Avis des participants, sorties déjà faites': ('Confiance', '-')},
                      'ENVIRONNEMENT' : {"Gestion de l'environnement": ('Confiance', '-')},
                      'NOM_SORTIES'   : {'Nom des sorties': ('Contenu', '-')},
                      'CARTE'         : {'Localisation des sorties sur une carte (IGN)': ('Contenu', '-')},
                      'DATES'         : {'Dates des prochaines sorties': ('Conditions', '-')}}

# Codage : index du participant (ordre des lignes du TSV) -> codes attribués
coding_retenu = {0: ['ESTHETIQUE', 'DENSITE', 'PARCOURS', 'VISION'],
                 1: ['ESTHETIQUE', 'FACILITE', 'CLARTE'],
                 2: ['FACILITE', 'PROJECTION', 'PARCOURS'],
                 3: ['ESTHETIQUE', 'FACILITE', 'CLARTE', 'PARCOURS'],
                 4: ['POSTURE_PRO', 'CULTURE', 'FACILITE'],
                 5: ['FACILITE', 'INFORMATIF', 'ESTHETIQUE', 'DIVERSITE'],
                 6: ['DIVERSITE', 'FILTRES'],
                 7: ['ESTHETIQUE', 'DIVERSITE'],
                 8: ['PARCOURS', 'VISION'],
                 9: ['POSTURE_PRO', 'CLARTE', 'ESTHETIQUE', 'PROJECTION'],
                 10: ['INFORMATIF', 'TARIFS', 'DIVERSITE'],
                 11: ['ESTHETIQUE'],
                 12: ['PHOTOS', 'AFFICHAGE_PC'],   # doublon probable du participant 2
                 13: ['PHOTOS'],
                 14: ['ESTHETIQUE', 'PHOTOS', 'FACILITE'],
                 15: ['FACILITE', 'CLARTE', 'PARCOURS', 'INFORMATIF', 'TARIFS'],
                 16: ['NOM_MARQUE', 'DIVERSITE', 'PARCOURS', 'BIVOUAC'],
                 17: ['PROJECTION']}

coding_questions = {0: ['AUCUNE'],
                    1: ['LOGISTIQUE'],
                    2: ['PREUVE_SOCIALE'],
                    3: ['AUCUNE'],
                    4: ['CHIEN'],
                    5: ['ENVIRONNEMENT'],
                    6: ['PRIX'],
                    7: ['MATERIEL'],
                    8: ['AUCUNE'],
                    9: ['MATERIEL'],
                    10: ['ANNULATION', 'MATERIEL'],
                    11: ['NOM_SORTIES'],
                    12: ['PREUVE_SOCIALE'],        # doublon probable du participant 2
                    13: ['DATES'],
                    14: ['LOGISTIQUE'],
                    15: ['AUCUNE'],
                    16: ['AUCUNE'],
                    17: ['CARTE']}


def check_coding(forms_df: pd.DataFrame, question: str, coding: dict) -> pd.DataFrame:
    """Repère les nouvelles réponses pas encore codées (et les index de codage
    qui ne correspondent plus à une ligne du TSV). Renvoie les verbatims à coder."""
    require_columns(forms_df, [question], 'Analyse thématique')
    answers = forms_df[question].astype('string').str.strip()
    answered = answers[answers.notna() & answers.ne('')]
    orphans = sorted(set(coding) - set(forms_df.index))
    if orphans:
        warn(f'[{question[:30]}…] participants codés absents du TSV : {orphans}')
    todo = answered[~answered.index.isin(list(coding))]
    if len(todo):
        warn(f'[{question[:30]}…] {len(todo)} réponse(s) à coder : participants {list(todo.index)}')
    return pd.DataFrame({'participant': todo.index, 'question': question, 'verbatim': todo.values})


def codes_table(codebook: dict, coding: dict) -> pd.DataFrame:
    """Une ligne par code : libellé, thème, valence, nb de participants, %."""
    unknown = {c for codes in coding.values() for c in codes} - codebook.keys()
    if unknown:
        raise KeyError(f'Codes absents de la grille : {unknown}')
    rows = []
    for code, entry in codebook.items():
        (label, (theme, valence)), = entry.items()
        n = sum(code in codes for codes in coding.values())
        rows.append({'code': code, 'libelle': label, 'theme': theme,
                     'valence': valence, 'n': n,
                     '%': round(100 * n / len(coding))})
    return pd.DataFrame(rows).set_index('code')


def themes_table(codes_df: pd.DataFrame, coding: dict, codebook: dict) -> pd.Series:
    """Nb de participants ayant au moins un code dans chaque thème."""
    theme_of = {code: next(iter(e.values()))[0] for code, e in codebook.items()}
    per_participant = {p: {theme_of[c] for c in codes} for p, codes in coding.items()}
    themes = codes_df['theme'].unique()
    return pd.Series({t: sum(t in s for s in per_participant.values()) for t in themes},
                     name='n participants')


def verbatims(forms_df: pd.DataFrame, question: str, coding: dict) -> pd.DataFrame:
    """Verbatims et codes côte à côte, pour relire et corriger le codage."""
    return pd.DataFrame({'participant': list(coding),
                         'verbatim': forms_df.loc[list(coding), question].str.strip().values,
                         'codes': [', '.join(c) for c in coding.values()]})




# ---------------------------------------------------------------------------
# Graphique
# ---------------------------------------------------------------------------

INK, INK_2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
VALENCE_COLORS = {'+': '#2a78d6', '-': '#e0793b'}


def _plot_codes(ax, codes_df: pd.DataFrame, title: str, n: int):
    df = codes_df[codes_df['n'] > 0]
    labels, values, colors, y, y_pos = [], [], [], [], 0
    group_starts = []
    for theme, group in df.groupby('theme', sort=False):
        group_starts.append((y_pos, theme))
        for _, r in group.sort_values('n', ascending=False).iterrows():
            labels.append(r['libelle']); values.append(r['n'])
            colors.append(VALENCE_COLORS[r['valence']]); y.append(y_pos)
            y_pos += 1
        y_pos += 0.6                                   # espace entre thèmes
    bars = ax.barh(y, values, color=colors, height=0.65)
    ax.bar_label(bars, padding=3, color=INK, fontsize=8)
    for start, theme in group_starts:
        ax.text(-0.01, start - 0.75, theme.upper(), transform=ax.get_yaxis_transform(),
                ha='right', va='center', color=INK_2, fontsize=7.5, fontweight='bold')
    ax.set_yticks(y, labels, fontsize=8, color=INK)
    ax.set_ylim(y_pos - 0.4, -1.3)
    ax.set_xlim(0, n)
    ax.set_xticks(range(0, n + 1, 2))
    style_axes(ax, 'x')
    ax.set_title(title, loc='left', color=INK, fontsize=10)


def plot_thematic(retenu_df, questions_df, n, path='questionnaire_analyse_thematique.png'):
    fig, axes = plt.subplots(2, 1, figsize=(9, 10),
                             gridspec_kw={'height_ratios': [len(retenu_df) + 4,
                                                            len(questions_df) + 5]})
    _plot_codes(axes[0], retenu_df, '« Que retenez-vous du site ? » (nb de participants)', n)
    _plot_codes(axes[1], questions_df,
                '« Quelles questions vous restent-il avant de réserver ? » (nb de participants)', n)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in VALENCE_COLORS.values()]
    fig.legend(handles, ['Point fort', 'Manque / question ouverte'], loc='lower center',
               ncol=2, frameon=False, fontsize=8, labelcolor=INK_2)
    fig.suptitle(f'Analyse thématique des réponses ouvertes (n = {n}) – {TODAY}',
                 x=0.01, ha='left', color=INK, fontsize=13)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=200)
    return fig


def run(forms_df: pd.DataFrame, out_dir='.'):
    """Tableaux de codes, export de relecture, liste des réponses à coder."""
    n = len(forms_df)
    path = lambda name, ext='.csv': output_path(out_dir, name, n, ext)
    todo = pd.concat([check_coding(forms_df, Q_RETENU, coding_retenu),
                      check_coding(forms_df, Q_QUESTIONS, coding_questions)])
    if len(todo):
        todo.to_csv(path('reponses_a_coder'), index=False)

    # on ne garde que les participants codés encore présents dans le TSV
    retenu = {p: c for p, c in coding_retenu.items() if p in forms_df.index}
    questions = {p: c for p, c in coding_questions.items() if p in forms_df.index}
    retenu_df = codes_table(codebook_retenu, retenu)
    questions_df = codes_table(codebook_questions, questions)

    retenu_df.to_csv(path('thematique_retenu'))
    questions_df.to_csv(path('thematique_questions'))
    pd.concat([verbatims(forms_df, Q_RETENU, retenu).assign(question='retenu'),
               verbatims(forms_df, Q_QUESTIONS, questions).assign(question='questions')]
              ).to_csv(path('codage_thematique'), index=False)
    plot_thematic(retenu_df, questions_df, len(retenu),
                  path('questionnaire_analyse_thematique', '.png'))
    return retenu_df, questions_df, todo


if __name__ == '__main__':
    pd.set_option('display.width', 200, 'display.max_colwidth', 90)
    forms_df = load_forms(DATA_FILE)
    retenu_df, questions_df, todo = run(forms_df, results_dir(len(forms_df)))
    print(retenu_df, '\n\n', questions_df, sep='')
    if len(todo):
        print('\nÀ coder :\n', todo, sep='')
