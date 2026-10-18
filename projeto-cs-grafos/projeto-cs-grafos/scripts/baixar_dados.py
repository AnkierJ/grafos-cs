"""Baixa os CSVs do Kaggle para a pasta data/.

Uso:
    python scripts/baixar_dados.py            # dataset principal (results.csv e picks.csv)
    python scripts/baixar_dados.py --cs2      # também baixa o bônus CS2 (cs2_results.csv)

Fontes:
    - mateusdmachado/csgo-professional-matches  (principal, CS:GO 2015-2020)
    - ilyazored/hltv-match-resultscs2           (opcional, CS2)

Se o download automático falhar (por exemplo, por falta de credenciais do Kaggle), baixe os arquivos
manualmente nas páginas acima e copie-os para a pasta data/ (o notebook só precisa de results.csv e picks.csv).
"""
import argparse
import shutil
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

DATASETS = {
    "principal": ("mateusdmachado/csgo-professional-matches", ["results.csv", "picks.csv"]),
    "cs2": ("ilyazored/hltv-match-resultscs2", ["cs2_results.csv"]),
}


def baixar(slug, arquivos):
    import kagglehub  # importado aqui para dar uma mensagem clara se não estiver instalado

    origem = Path(kagglehub.dataset_download(slug))
    DATA_DIR.mkdir(exist_ok=True)
    for nome in arquivos:
        achados = [p for p in origem.rglob("*.csv") if p.name.lower() == nome.lower()]
        if not achados:
            print(f"  ⚠️ {nome} não encontrado em {slug} (arquivos: {sorted(p.name for p in origem.rglob('*.csv'))})")
            continue
        destino = DATA_DIR / nome
        shutil.copy(achados[0], destino)
        print(f"  ✔ {destino}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cs2", action="store_true", help="baixa também o dataset CS2 (bônus opcional)")
    args = ap.parse_args()

    alvos = ["principal"] + (["cs2"] if args.cs2 else [])
    falhas = 0
    for chave in alvos:
        slug, arquivos = DATASETS[chave]
        print(f"Baixando {slug} ...")
        try:
            baixar(slug, arquivos)
        except Exception as e:  # rede, credenciais, slug alterado...
            falhas += 1
            print(f"  ✘ falhou: {type(e).__name__}: {e}")
            print(f"    Baixe manualmente em https://www.kaggle.com/datasets/{slug} e copie {arquivos} para {DATA_DIR}/")
    sys.exit(1 if falhas and "principal" in alvos and not (DATA_DIR / "results.csv").exists() else 0)


if __name__ == "__main__":
    main()
