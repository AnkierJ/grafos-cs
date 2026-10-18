# Pasta `data/`

Coloque aqui os CSVs do dataset **CS:GO Professional Matches** (Mateus Dauernheimer Machado, Kaggle):
<https://www.kaggle.com/datasets/mateusdmachado/csgo-professional-matches>

| arquivo | uso no projeto |
|---|---|
| `results.csv` | **obrigatório**: uma linha por mapa jogado (placar, vencedor do mapa, ranking HLTV dos times) |
| `picks.csv` | **obrigatório**: uma linha por partida, com a sequência de bans/picks do veto |
| `cs2_results.csv` | opcional (bônus CS2): <https://www.kaggle.com/datasets/ilyazored/hltv-match-resultscs2> |

Para obter: `python scripts/baixar_dados.py` (ou baixe manualmente e copie os arquivos para esta pasta).
Os dados foram raspados do HLTV.org por terceiros e são usados aqui apenas para fins acadêmicos.
