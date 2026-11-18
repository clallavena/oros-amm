"""Point d'entrée unique

Usage :
    python analyse.py                         # data/attrakdiff_orosens.tsv -> resultats/<date>_n<n>/
    python analyse.py export.tsv              # autre fichier
    python analyse.py export.tsv --show       # affiche aussi les graphiques
"""
import argparse
import warnings
from pathlib import Path

import matplotlib

from common import DATA_FILE, EXCLUDED_PARTICIPANTS, load_forms, results_dir


def main():
    parser = argparse.ArgumentParser(description="Analyse AttrakDiff + questionnaire")
    parser.add_argument('tsv', nargs='?', default=str(DATA_FILE))
    parser.add_argument('--out', default=None,
                        help='dossier de sortie (défaut : resultats/<DDMMAAAA>_n<n>)')
    parser.add_argument('--show', action='store_true', help='afficher les graphiques')
    args = parser.parse_args()

    if not args.show:
        matplotlib.use('Agg')                   # pas de fenêtre, juste les fichiers
    import matplotlib.pyplot as plt
    import attrakdiffReader, questionnaireReader, qualitativeReader

    forms_df = load_forms(args.tsv)
    if args.out:
        out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    else:
        out = results_dir(len(forms_df))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        _, scales_df = attrakdiffReader.run(forms_df, out)
        _, quiz_scores, _ = questionnaireReader.run(forms_df, out)
        _, _, todo = qualitativeReader.run(forms_df, out)

    # Résumé console
    print(f'{len(forms_df)} réponses lues dans {args.tsv} -> {out}/')
    for i, reason in EXCLUDED_PARTICIPANTS.items():
        print(f'  (participant {i} écarté : {reason})')
    print('\nAttrakDiff (moyenne ± IC 95 %) :')
    summary = attrakdiffReader.summary_table(scales_df)
    for scale, row in summary.iterrows():
        print(f"  {scale:<4} {row['mean']:+.2f} ± {row['ci95']:.2f}")
    print(f"\nQuiz AMM : score moyen {quiz_scores['score_%'].mean():.0f} %")

    if caught:
        print('\nÀ vérifier :')
        for w in caught:
            print(f'  - {w.message}')
        (out / 'avertissements.txt').write_text('\n'.join(str(w.message) for w in caught),
                                                encoding='utf-8')
    if len(todo):
        print(f'\n{len(todo)} réponse(s) ouverte(s) à coder -> voir reponses_a_coder_*.csv')
        print('  Ajoute-les dans coding_retenu / coding_questions (qualitativeReader.py).')

    plt.close('all') if not args.show else plt.show()


if __name__ == '__main__':
    main()
