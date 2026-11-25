import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from common import (TODAY, INK, INK_2, GRID, SERIES, POSITIVE_BG, NEGATIVE_BG,
                    DATA_FILE, load_forms, output_path, results_dir, require_columns,
                    style_axes)

# Qualité Pragmatique
## Décrit l’utilisabilité du produit et indique le niveau de facilité perçue des utilisateurs à atteindre leurs buts
qp = {'QP1': {'Humain / Technique': True},
      'QP2' : {'Simple / Compliqué': True},
      'QP3' : {'Pratique / Pas pratique': True},
      'QP4' : {'Fastidieux / Efficace': False},
      'QP5' : {'Prévisible / Imprévisible': True},
      'QP6' : {'Confus / Clair': False},
      'QP7' : {'Incontrôlable / Maîtrisable': False}}

# Qualité Hédonique - Stimulation
## Indique dans quelle mesure le produit soutient le besoin de stimulation en proposant des contenus, fonctionnalités, styles
## d’interaction nouveaux, intéressants et stimulants
qhs = {'QHS1': {'Original / Conventionnel': True},
       'QHS2' : {'Sans imagination / Créatif': False},
       'QHS3' : {'Audacieux / Prudent': True},
       'QHS4' : {'Novateur / Conservateur': True},
       'QHS5' : {'Ennuyeux / Captivant': False},
       'QHS6' : {'Peu exigeant / Challenging': False},
       'QHS7' : {'Nouveau / Commun': True}}

# Qualité Hédonique - Identité
## Indique dans quelle mesure le produit soutient une fonction sociale et communique une certaine identité de l’utilisateur
qhi = {'QHI1': {"M'isole / Me sociabilise": False},
       'QHI2' : {'Professionnel / Amateur': True},
       'QHI3' : {'De bon goût / De mauvais goût': True},
       'QHI4' : {'Bas de gamme / Haut de gamme': False},
       'QHI5' : {"M'exclut / M'intègre": False},
       'QHI6' : {'Me rapproche des autres / Me sépare des autres': True},
       'QHI7' : {'Non présentable / Présentable': False}}

# Attractivité globale
## Décrit la valeur globale perçue du produit basée sur la perception des qualités pragmatiques et hédoniques
att = {'ATT1': {'Plaisant / Déplaisant': True},
       'ATT2' : {'Laid / Beau': False},
       'ATT3' : {'Agréable / Désagréable': True},
       'ATT4' : {'Rebutant / Attirant': False},
       'ATT5' : {'Bon / Mauvais': True},
       'ATT6' : {'Repoussant / Attrayant': False},
       'ATT7' : {'Motivant / Décourageant': True}}

scales = {'QP': qp, 'QHS': qhs, 'QHI': qhi, 'ATT': att}

def build_items_df(forms_df: pd.DataFrame, scales: dict) -> pd.DataFrame:
    """Un DataFrame : une ligne par participant, une colonne par code d'item,
    valeurs recodées de [1..7] vers [-3..+3], items inversés (*) retournés."""
    require_columns(forms_df, [next(iter(p)) for items in scales.values()
                               for p in items.values()], 'AttrakDiff')
    columns = {}
    for items in scales.values():
        for code, pair in items.items():
            (label, inverted), = pair.items()
            score = pd.to_numeric(forms_df[label], errors='coerce') - 4
            columns[code] = -score if inverted else score
    return pd.DataFrame(columns)


def compute(forms_df: pd.DataFrame):
    """Renvoie (items_df, scales_df). Les participants sans aucune réponse
    AttrakDiff sont écartés."""
    items_df = build_items_df(forms_df, scales).dropna(how='all')
    # Score de chaque échelle par participant (moyenne de ses 7 items)
    scales_df = pd.DataFrame({name: items_df[list(items)].mean(axis=1)
                              for name, items in scales.items()})
    # QH = moyenne de QH-S et QH-I
    scales_df['QH'] = scales_df[['QHS', 'QHI']].mean(axis=1)
    return items_df, scales_df


def summary_table(scales_df: pd.DataFrame) -> pd.DataFrame:
    """Moyenne, écart-type et IC 95 % de chaque échelle."""
    return scales_df.agg(['mean', 'std', ci95]).T.round(2)


# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------
SCALE_LABELS = {'QP': 'QP', 'QHI': 'QH-I', 'QHS': 'QH-S', 'ATT': 'ATT'}


def _style(ax):
    style_axes(ax)


def ci95(series: pd.Series) -> float:
    """Demi-largeur de l'IC 95 % (loi de Student, adaptée aux petits n)."""
    s = series.dropna()
    return stats.t.ppf(0.975, len(s) - 1) * s.std(ddof=1) / len(s) ** 0.5


def plot_mean_values(scales_df: pd.DataFrame, path='attrakdiff_valeurs_moyennes.png'):
    order = ['QP', 'QHI', 'QHS', 'ATT']            # ordre du diagramme AttrakDiff
    summary = (scales_df[order]
               .agg(['mean', 'std', ci95]).T
               .rename(index=SCALE_LABELS,
                       columns={'mean': 'moyenne', 'std': 'ecart_type', 'ci95': 'ic95'}))

    ax = summary['moyenne'].plot(yerr=summary['ic95'], figsize=(7, 4.5),
                                 ylim=(-3, 3), yticks=range(-3, 4), rot=0,
                                 color=SERIES, lw=2, marker='o', ms=8, capsize=4,
                                 elinewidth=1.5, markeredgecolor='white', markeredgewidth=2,
                                 xlim=(-0.3, len(order) - 0.7))
    ax.axhline(0, color=INK_2, lw=1, zorder=1)
    # Zone neutre [-1 ; +1], scindée en neutre positif / neutre négatif
    ax.axhspan(0, 1, color=POSITIVE_BG, zorder=0, lw=0)
    ax.axhspan(-1, 0, color=NEGATIVE_BG, zorder=0, lw=0)
    for y, label in ((0.5, 'neutre positif'), (-0.5, 'neutre négatif')):
        ax.text(1.0, y, label, transform=ax.get_yaxis_transform(), ha='right',
                va='center', color=INK_2, fontsize=8)
    for xi, m in enumerate(summary['moyenne']):
        ax.annotate(f'{m:.2f}', (xi, m), xytext=(10, 0), textcoords='offset points',
                    va='center', color=INK, fontsize=9,
                    bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='none'))
    ax.set_xlabel('')
    # Écart-type (ET) sous chaque échelle : dispersion des scores individuels,
    # à ne pas confondre avec la barre d'erreur (IC 95 % de la moyenne)
    ax.set_xticks(range(len(summary)),
                  [f'{name}\nET = {sd:.2f}' for name, sd in summary['ecart_type'].items()])
    ax.grid(axis='y', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    _style(ax)
    ax.set_title(f'Diagramme des valeurs moyennes (n = {len(scales_df)}, barres : IC 95 %) – {TODAY}',
                 loc='left', color=INK, fontsize=12)
    fig = ax.figure
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return fig


def plot_word_pairs(items_df: pd.DataFrame, scales: dict, path='attrakdiff_paires_de_mots.png'):
    order = ['QP', 'QHI', 'QHS', 'ATT']
    rows = []                                      # (code, pôle négatif, pôle positif)
    for name in order:
        for code, pair in scales[name].items():
            (label, inverted), = pair.items()
            left, right = (s.strip() for s in label.split('/'))
            rows.append((name, code, *((right, left) if inverted else (left, right))))

    means = [items_df[code].mean() for _, code, _, _ in rows]
    y = list(range(len(rows)))

    fig, ax = plt.subplots(figsize=(8, 10))
    ax.axvline(0, color=INK_2, lw=1)
    # Zones des valeurs extrêmes : [-3 ; -2] négatif, [+2 ; +3] positif
    ax.axvspan(2, 3, color=POSITIVE_BG, zorder=0, lw=0)
    ax.axvspan(-3, -2, color=NEGATIVE_BG, zorder=0, lw=0)
    for x, label in ((2.5, 'extrême positif'), (-2.5, 'extrême négatif')):
        ax.text(x, 1.0, label, transform=ax.get_xaxis_transform(), ha='center',
                va='bottom', color=INK_2, fontsize=8)
    # séparateurs et noms d'échelles
    for i, name in enumerate(order):
        start = i * 7
        if i:
            ax.axhline(start - 0.5, color=GRID, lw=1)
        ax.text(-2.95, start - 0.35, SCALE_LABELS[name], va='center', ha='left',
                color=INK_2, fontsize=9, fontweight='bold')
    # une ligne par échelle (pas de ligne entre deux échelles différentes)
    for i in range(len(order)):
        sl = slice(i * 7, i * 7 + 7)
        ax.plot(means[sl], y[sl], color=SERIES, lw=2, marker='o', ms=7,
                markeredgecolor='white', markeredgewidth=1.5)

    ax.set_yticks(y, [r[2] for r in rows], color=INK, fontsize=9)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    sec = ax.secondary_yaxis('right')
    sec.set_yticks(y, [r[3] for r in rows], color=INK, fontsize=9)
    sec.tick_params(length=0, pad=4)
    sec.spines['right'].set_visible(False)
    ax.set_xlim(-3, 3)
    ax.set_xticks(range(-3, 4))
    ax.grid(axis='x', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    _style(ax)
    ax.set_title(f'Profil des paires de mots (n = {len(items_df)}) – {TODAY}',
                 loc='left', color=INK, fontsize=12, pad=20)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return fig


def plot_portfolio(scales_df: pd.DataFrame, path='attrakdiff_portfolio.png'):
    """Portfolio AttrakDiff : QP en x, QH en y, rectangle de confiance à 95 %."""
    # Zones du portfolio (Hassenzahl, 2003 ; libellés FR : Lallemand et al., 2015)
    # clé = (colonne, ligne), 0 = bas/gauche, 2 = haut/droite
    zones = {(0, 2): 'trop orienté\nvers le soi', (1, 2): 'orienté\nvers le soi',
             (2, 2): 'désiré', (1, 1): 'neutre', (2, 1): 'orienté\nvers la tâche',
             (0, 0): 'superflu', (2, 0): 'trop orienté\nvers la tâche'}

    qp_m, qh_m = scales_df['QP'].mean(), scales_df['QH'].mean()
    qp_ci, qh_ci = ci95(scales_df['QP']), ci95(scales_df['QH'])

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    for b in (-1, 1):
        ax.axvline(b, color=GRID, lw=1, zorder=0)
        ax.axhline(b, color=GRID, lw=1, zorder=0)
    for (col, row), label in zones.items():
        ax.text(-3 + 2 * col + 0.1, -1 + 2 * row - 0.1, label, ha='left', va='top',
                color=INK_2, fontsize=8, zorder=0)

    ax.scatter(scales_df['QP'], scales_df['QH'], s=36, color='#b9b8b2',
               edgecolor='white', lw=1, zorder=2, label='Participants')
    ax.add_patch(plt.Rectangle((qp_m - qp_ci, qh_m - qh_ci), 2 * qp_ci, 2 * qh_ci,
                               fc=SERIES, alpha=0.18, ec=SERIES, lw=1.5, zorder=3,
                               label='Rectangle de confiance (IC 95 %)'))
    ax.scatter([qp_m], [qh_m], s=80, color=SERIES, edgecolor='white', lw=2,
               zorder=4, label='Moyenne')
    ax.annotate(f'QP = {qp_m:.2f}\nQH = {qh_m:.2f}', (qp_m - qp_ci, qh_m + qh_ci),
                xytext=(-6, 0), textcoords='offset points', ha='right', va='top',
                color=INK, fontsize=9)

    ax.set_xlim(-3, 3); ax.set_ylim(-3, 3)
    ax.set_xticks(range(-3, 4)); ax.set_yticks(range(-3, 4))
    ax.set_aspect('equal')
    ax.set_xlabel('Qualité pragmatique (QP)', color=INK)
    ax.set_ylabel('Qualité hédonique (QH)', color=INK)
    for side in ax.spines.values():
        side.set_color(GRID)
    ax.tick_params(colors=INK_2, length=0)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False,
              fontsize=8, labelcolor=INK_2)
    ax.set_title(f'Portfolio des résultats (n = {len(scales_df)}) – {TODAY}',
                 loc='left', color=INK, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    return fig


def run(forms_df: pd.DataFrame, out_dir='.'):
    """Calcule les scores, enregistre graphiques et tableaux dans out_dir."""
    items_df, scales_df = compute(forms_df)
    n = len(scales_df)
    summary_table(scales_df).to_csv(output_path(out_dir, 'attrakdiff_scores', n, '.csv'))
    plot_mean_values(scales_df, output_path(out_dir, 'attrakdiff_valeurs_moyennes', n))
    plot_word_pairs(items_df, scales, output_path(out_dir, 'attrakdiff_paires_de_mots', n))
    plot_portfolio(scales_df, output_path(out_dir, 'attrakdiff_portfolio', n))
    return items_df, scales_df


if __name__ == '__main__':
    forms_df = load_forms(DATA_FILE)
    items_df, scales_df = run(forms_df, results_dir(len(forms_df)))
    print(items_df)
    print(scales_df.round(2))
    print(summary_table(scales_df))
