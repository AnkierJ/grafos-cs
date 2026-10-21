# Hierarquia e "freguesia" no CS:GO profissional: uma análise em grafos

Projeto da Unidade 01 · Algoritmos e Estruturas de Dados II · Grafos

## Integrantes

Ankier José Barreira Lima (20230020941)

## Vídeo
https://youtu.be/haW7CYK9F04

## Problema e pergunta

**Problema.** O cenário profissional de Counter-Strike é decidido por uma hierarquia simples ("quem tem o melhor ranking ganha") ou existem estruturas que o ranking não captura: times que perdem sempre para um rival específico, ciclos de vitórias, preferências de mapa? Analistas, comissões técnicas, jogadores e fãs se beneficiam da resposta, porque ela orienta a preparação de vetos, ajuda a entender confrontos incômodos e a antecipar resultados.

**Pergunta central.** *A posição estrutural de um time na rede de confrontos explica seu desempenho além do ranking HLTV?*

**Por que isso é uma pergunta de rede.** O resultado de uma partida é uma **relação** entre dois times, não um atributo de um time isolado. Só em rede aparecem a qualidade das vitórias (vencer quem vence muito), as pontes entre grupos, os ciclos A→B→C→A e o núcleo coeso da elite.

| # | Pergunta | Ferramentas (semana) |
|---|---|---|
| Q1 | Quem são os times centrais? Isso coincide com o ranking HLTV? | grau/força, eigenvector, closeness, betweenness (S2, S4) |
| Q1b | Quem forma o núcleo da elite? | k-core, k-shell, core number, onion layers (S5) |
| Q2 | Quem é "freguês" de quem, além do que o ranking explicaria? Há ciclos de intransitividade? | subrede/ego network (S2); componentes, triângulos (S4) |
| Q2b | Quão provável é o time A vencer o B? | eigenvector calculado só com o passado, contra um baseline de ranking (S2, S4) |
| Q3 | Que mapa cada time tende a banir? Os times banem os mapas em que são mais fracos? | rede bipartida, projeção, Jaccard (S6); camadas por mapa (S2) |
| Q4 | Quantas vitórias encadeadas separam qualquer time de um time-alvo? | BFS, mundo pequeno (S3) |
| Q5 | O que acontece com a rede se removermos os maiores hubs? | componentes, caminho médio (S4) |

## Dados (fonte, como obter, limpeza)

**Fonte.** *CS:GO Professional Matches*, de Mateus Dauernheimer Machado (Kaggle): <https://www.kaggle.com/datasets/mateusdmachado/csgo-professional-matches>. São partidas profissionais raspadas do HLTV.org, de 11/2015 a 03/2020. Bônus opcional: *HLTV Match Results | CS2* (ilyazored), usado só para comparar a estrutura da rede entre as duas eras, **sem misturar CS:GO e CS2 no mesmo grafo**.

**Tabelas usadas.** `results.csv` (uma linha por **mapa jogado**: placar, vencedor do mapa, ranking HLTV dos dois times) e `picks.csv` (uma linha por **partida**: sequência de bans e picks do veto). `economy.csv` e `players.csv` não entram, porque a pergunta é sobre relações entre times.

**Como obter.** `python scripts/baixar_dados.py` (ver [Como executar](#como-executar)), ou baixe manualmente e copie os CSVs para `data/`. Os dados foram raspados do HLTV.org por terceiros e são usados aqui apenas para fins acadêmicos.

**Limpeza** (notebook, §2, cél. 2 a 6):

1. **Conferência de colunas** logo no carregamento: se o arquivo vier diferente do esperado, o erro aparece ali.
2. **Tipos e datas:** descarte de linhas sem data, time ou vencedor do mapa; `map_winner` restrito a {1, 2}; nomes de mapa padronizados.
3. **Resolução de identidade:** o mesmo time pode aparecer com grafias diferentes. Uma chave normalizada (minúsculas, só letras e números) une as variantes, e o nome canônico é o mais frequente. Apelidos que a regra não une podem ser registrados em `ALIASES`. Isso é feito **antes** de montar qualquer grafo; depois, as arestas já estariam duplicadas.
4. **De mapas para partidas:** a rede é por **partida**. Agrupa-se por `match_id`, vence quem ganhou mais mapas, e partidas empatadas ou com times inconsistentes entre mapas são descartadas e **contadas** no relatório.
5. **Filtro de volume mínimo:** só entram partidas em que os dois times têm ao menos `MIN_MATCHES` (15) partidas. O notebook mostra uma **tabela de sensibilidade** de como cada limiar muda o tamanho da rede, porque a escolha não é neutra.
6. **Datas de início diferentes por tabela:** os vetos só existem a partir de 2016, e as análises de veto usam apenas esse recorte.

## Modelagem (nó, aresta, peso, direção, o que ficou de fora)

**Grafo A: confrontos entre times** (Q1, Q1b, Q2, Q2b, Q4, Q5)

| Elemento | Definição |
|---|---|
| **Nó** | time (nome canônico) |
| **Aresta** | existe se os dois times se enfrentaram ao menos uma vez |
| **Direção** | **perdedor → vencedor** (grafo dirigido) |
| **Peso** | nº de partidas que o vencedor ganhou do perdedor |
| **Ficou de fora** | trocas de elenco (um nó é um *rótulo*, não uma formação), LAN × online, nível do torneio, rounds, mapa |

*Por que perdedor → vencedor?* O **grau de entrada ponderado** de um nó é o total de vitórias e o de saída é o de derrotas. Na centralidade de autovetor, a pontuação de um time soma a dos times que ele venceu ("vencer quem vence muito"). A direção carrega informação (A→B ≠ B→A); um grafo não dirigido perderia justamente a hierarquia.

**Grafo B: bipartido time × mapa** (Q3)

| Elemento | Definição |
|---|---|
| **Nós** | dois tipos: times e mapas |
| **Aresta** | time–mapa, se o time baniu o mapa ao menos uma vez |
| **Peso** | nº de bans, **normalizado pela exposição** (partidas em que o mapa estava no pool) e suavizado; o *lift* compara a taxa do time com a taxa geral do mapa |
| **Ficou de fora** | a ordem exata do veto (só o 1º ban é tratado à parte), o formato (bo1/bo3/bo5) e os picks (só usados para reconstruir o pool de mapas de cada partida) |

**Alternativas consideradas.** *Multicamada por mapa* (uma rede de vitórias por mapa, §9.5), *subredes por ano* (§12) e *bipartido jogador × time* para mobilidade de elenco (próximo passo). Para os vetos, a alternativa de **projetar** o bipartido sobre os times (C = BBᵀ) tem um artefato conhecido: o peso bruto tende a crescer com o **volume** de partidas (times muito ativos viram hubs falsos). O notebook mede essa correlação (§9.4) e a comparação entre times usa **Jaccard ponderado** sobre os perfis normalizados.

## Conteúdo do curso utilizado

Legenda: **cél. N** é a N-ésima célula de **código** do `analise.ipynb` (o `In [N]` ao rodar de cima para baixo); **§** é a seção do notebook.

| conceito | semana | onde aparece | para que serviu |
|---|---|---|---|
| Grafo dirigido e ponderado | 2 | `analise.ipynb`, cél. 1 (`build_win_graph`), cél. 7 (§3) | modelar perdedor → vencedor com peso = nº de vitórias |
| Densidade e grau médio | 2 | cél. 7 (§3) | mostrar que a rede é esparsa |
| Matriz de adjacência | 2 | cél. 7 (§3) | mostrar a esparsidade e a assimetria (hierarquia) da matriz |
| Grau e distribuição de grau | 2 | cél. 8 (§3) | identificar hubs; mostrar que a média descreve mal a rede |
| Subredes | 2 | cél. 6 (§2.7, filtro), cél. 16 (§7, ego network), cél. 27 (§12, por ano) | restringir a times com volume mínimo; ver os adversários de um time; comparar anos |
| Dirigido × não dirigido; camadas | 2 | cél. 1 (`to_undirected_weighted`), cél. 24 (§9.5, uma rede por mapa) | distâncias e k-core ignoram direção; camadas como alternativa ao multigrafo |
| Grau de entrada e de saída | 3 | cél. 10 (§5) | vitórias (entrada) e derrotas (saída) de cada time |
| Efeito da amostragem na estrutura | 3 | cél. 6 (§2.7), cél. 10 (betweenness amostrada) | quantificar quanto o filtro de volume e a amostragem de pivôs alteram a rede |
| BFS | 3 | cél. 25 (§10) | menor cadeia de vitórias até um time-alvo (Q4) |
| DFS | 3 | cél. 25 (§10) | contraste: a DFS acha caminhos bem mais longos que o ótimo da BFS |
| Mundo pequeno | 3 e 4 | cél. 9 (§4) | caminho médio e clustering contra um G(n,m) aleatório (coeficiente σ) |
| Caminhos, distâncias, diâmetro | 4 | cél. 9 (§4), cél. 26 (§11) | quão longe estão dois times; dano das remoções |
| Componentes (WCC, SCC, GCC) | 4 | cél. 9 (§4), cél. 10 (SCC para o autovetor), cél. 26 (GCC sob remoção) | miolo onde todos se alcançam; resiliência |
| Triângulos, clustering, transitividade | 4 | cél. 9 (§4), cél. 17 (§7.1, censo de tríades) | medir intransitividade (ciclos A→B→C→A) contra orientação aleatória |
| Closeness | 4 | cél. 10 (§5) | quão "perto" de todos um time está |
| Betweenness | 4 | cél. 10 (§5), cél. 26 (§11) | times que fazem ponte; ataque dirigido na resiliência |
| Eigenvector | 4 | cél. 10 (§5), cél. 18 e 19 (§8) | qualidade das vitórias; variável da previsão (Q2b) |
| Visualização com nxviz | 4 | cél. 14 (§6) | circos plot dos times por k-shell |
| k-core, k-shell, core number, degeneracy | 5 | cél. 13 (§6) | núcleo interno da elite (Q1b) |
| Onion layers | 5 | cél. 13 (§6) | refinar a ordem de remoção dentro de cada casca |
| Rede bipartida e matriz de incidência | 6 | cél. 21 (§9.1) | grafo time × mapa de bans (Q3) |
| Projeção e co-ocorrência | 6 | cél. 23 (§9.4) | C = BBᵀ entre times e entre mapas (co-ban); mostra o artefato de volume |
| Jaccard e esqueleto por limiar | 6 | cél. 23 (§9.4) | similaridade de perfis de ban sem o artefato de volume; grafo de similaridade |
| Unir menções da mesma entidade (análogo ao NER) | 6 | cél. 4 (§2.5) | resolução de identidade dos nomes de times |

**Ferramentas de fora do curso** (usadas como apoio, e não substituem as acima): regressão logística (cél. 1, 15 e 19), teste binomial com correção de Benjamini-Hochberg para testes múltiplos (cél. 15), PageRank (cél. 10 e 18), validação progressiva *walk-forward* contra vazamento temporal (cél. 18) e correlação de Spearman (cél. 11, 13, 23 e 24).

## Como executar

Testado com **Python 3.13**, em ambiente virtual limpo, com duas pilhas de versões (as mais recentes e uma mais antiga: pandas 2.2, matplotlib 3.9, networkx 3.4); o notebook executou de ponta a ponta, sem erros, nas duas. Dependências em `requirements.txt` (faixas compatíveis) e `requirements-lock.txt` (versões exatas da pilha mais recente). Tempo de execução: poucos minutos.

```bash
git clone <URL-DESTE-REPOSITORIO>
cd <pasta-do-repositorio>

python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt      # ou requirements-lock.txt, para as versões exatas

python scripts/baixar_dados.py       # baixa results.csv e picks.csv para data/
# opcional (bônus CS2): python scripts/baixar_dados.py --cs2

jupyter nbconvert --to notebook --execute analise.ipynb --inplace   # executa tudo
# ou abra interativamente: jupyter lab analise.ipynb  → Run All
```

- As **figuras** (`figuras/`) e as **tabelas** (`resultados/`, incluindo `resumo.md`) são geradas pelo código.
- Se o download automático falhar (ele pode exigir credenciais do Kaggle), baixe `results.csv` e `picks.csv` na página do dataset e copie-os para `data/`.
- Os parâmetros (`MIN_MATCHES`, `TEAM_FOCO`, `TEAM_ALVO`, `ALIASES`...) ficam no começo do notebook (cél. 1). `RUN_RESILIENCE = False` pula a seção mais lenta.

## Resultados

Dados. 26,781 partidas válidas entre 1,539 times; a rede de trabalho (≥ 15 partidas) tem 531 times e 11,314 arestas, com densidade 0.040.
Estrutura (S3/S4). GCC com 100% dos times; caminho médio 2.43 (aleatório: 2.05), clustering 0.52 (aleatório: 0.063), σ = 6.9. Maior SCC com 99% dos times.
Q1 (hierarquia). A medida mais alinhada ao ranking HLTV é eig (ρ = -0.82, forte); autovetor: ρ = -0.82; nº de adversários: ρ = -0.58.
Q1b (núcleo, S5). Degenerescência k = 34 com 73 times no núcleo interno; ρ(core, ranking) = -0.66, ρ(core, nº de adversários) = 0.92. O núcleo acompanha mais o calendário do que a força.
Q2 (freguesia). 1 de 3,038 pares passam no teste (FDR 10%) de vencer acima do esperado pelo ranking; o mais marcante: Chiefs sobre Legacy (25/25).
Intransitividade. 14.8% dos triângulos de dominância são cíclicos (aleatório: 24.9%): há hierarquia, mas imperfeita.
Q2b (previsão, teste n = 5,418). Ranking sozinho: 65.3% de acerto (logloss 0.634); ranking + rede: 64.6% (logloss 0.625). A rede melhora ligeiramente a qualidade das probabilidades (logloss 0.634 → 0.625), mas a acurácia é estatisticamente equivalente (Δ = -0.7 p.p., IC95% ≈ ±1.3). Sozinha, a melhor medida de rede (Razão de vitórias (S2): 61.0%) fica abaixo do ranking.
Q3 (vetos). Correlação entre taxa de ban e desempenho relativo no mapa: ρ = -0.40 (agrupado) e -0.45 (mediana dentro dos times; 82% negativos). Os times tendem a banir os mapas em que são relativamente mais fracos. Na projeção, o peso bruto acompanha o volume (ρ = 0.98) e o Jaccard o neutraliza (ρ = -0.12).
Q4 (BFS, S3). 99% dos times alcançam Natus Vincere por cadeias de vitórias; distância média 2.57, máxima 5. A DFS acha caminhos ≈ 92.4× mais longos que o ótimo da BFS.
Q5 (resiliência). Remover 10% dos times não fragmenta a rede (100% dos restantes seguem no componente gigante), mas alonga os caminhos: média de 2.43 → 2.99 no pior ataque ('maior betweenness'), contra 2.48 na remoção aleatória; a eficiência global cai de 0.451 para 0.377.
Dados. 26,781 partidas válidas entre 1,539 times; a rede de trabalho (≥ 15 partidas) tem 531 times e 11,314 arestas, com densidade 0.040.
Estrutura (S3/S4). GCC com 100% dos times; caminho médio 2.43 (aleatório: 2.05), clustering 0.52 (aleatório: 0.063), σ = 6.9. Maior SCC com 99% dos times.
Q1 (hierarquia). A medida mais alinhada ao ranking HLTV é eig (ρ = -0.82, forte); autovetor: ρ = -0.82; nº de adversários: ρ = -0.58.
Q1b (núcleo, S5). Degenerescência k = 34 com 73 times no núcleo interno; ρ(core, ranking) = -0.66, ρ(core, nº de adversários) = 0.92. O núcleo acompanha mais o calendário do que a força.
Q2 (freguesia). 1 de 3,038 pares passam no teste (FDR 10%) de vencer acima do esperado pelo ranking; o mais marcante: Chiefs sobre Legacy (25/25).
Intransitividade. 14.8% dos triângulos de dominância são cíclicos (aleatório: 25.1%): há hierarquia, mas imperfeita.
Q2b (previsão, teste n = 5,418). Ranking sozinho: 65.3% de acerto (logloss 0.634); ranking + rede: 64.6% (logloss 0.625). A rede melhora ligeiramente a qualidade das probabilidades (logloss 0.634 → 0.625), mas a acurácia é estatisticamente equivalente (Δ = -0.7 p.p., IC95% ≈ ±1.3). Sozinha, a melhor medida de rede (Razão de vitórias (S2): 61.0%) fica abaixo do ranking.
Q3 (vetos). Correlação entre taxa de ban e desempenho relativo no mapa: ρ = -0.40 (agrupado) e -0.45 (mediana dentro dos times; 82% negativos). Os times tendem a banir os mapas em que são relativamente mais fracos. Na projeção, o peso bruto acompanha o volume (ρ = 0.98) e o Jaccard o neutraliza (ρ = -0.12).
Q4 (BFS, S3). 99% dos times alcançam Natus Vincere por cadeias de vitórias; distância média 2.57, máxima 5. A DFS acha caminhos ≈ 96.0× mais longos que o ótimo da BFS.
Q5 (resiliência). Remover 10% dos times não fragmenta a rede (100% dos restantes seguem no componente gigante), mas alonga os caminhos: média de 2.43 → 2.99 no pior ataque ('maior betweenness'), contra 2.47 na remoção aleatória; a eficiência global cai de 0.451 para 0.377.

### Figuras

| pergunta | figura |
|---|---|
| Estrutura e hubs (§3) | `figuras/01_distribuicao_graus.png` |
| Q1: centralidades × ranking (§5) | `figuras/02_pairgrid_centralidades.png`, `figuras/03_autovetor_vs_ranking.png` |
| Q1b: núcleo da elite (§6) | `figuras/04_kshell_concentrico.png`, `figuras/05_circos_nxviz.png` |
| Q2: freguesia (§7) | `figuras/06_ego_network.png` |
| Q2b: previsão (§8) | `figuras/07_calibracao.png` |
| Q3: vetos (§9) | `figuras/08_heatmap_bans.png`, `figuras/09_veto_racional.png` |
| Q4: BFS (§10) | `figuras/10_bfs_camadas.png` |
| Q5: resiliência (§11) | `figuras/11_resiliencia.png` |

### Resposta à pergunta central
A rede dos confrontos confirma a hierarquia que o ranking já descreve e revela estrutura nos vetos e na topologia, mas não melhora a previsão de resultados de forma demonstrável.

## Limitações e próximos passos

**Limitações e artefatos**

- **Time ≠ elenco.** Um nó é um rótulo que atravessa várias formações; trocas de jogadores diluem os resultados.
- **Amostragem.** O HLTV registra mais os times grandes; times pequenos aparecem pouco e quase só contra vizinhos de ranking. O filtro de volume reduz o ruído, mas introduz viés de seleção (a tabela de sensibilidade mostra o efeito).
- **Rede estática.** Misturar 2015 a 2020 numa rede única ignora a evolução dos times; a seção 12 compara anos.
- **Centralidade não é força causal.** O autovetor mede *com quem* se venceu; não vê mapa, formato (bo1/bo3/bo5) nem forma recente.
- **K-core reflete calendário** (nº de adversários distintos), não só força; por isso o notebook o compara com o ranking e com o grau.
- **Testes múltiplos.** Centenas de pares testados em "freguesia": usa-se FDR, mas a análise segue exploratória.
- **Previsão.** Sem vazamento temporal (validação *walk-forward*), mas o modelo só usa ranking e resultados passados; não vê elenco, lesões, mapa ou formato.
- **Vetos.** O formato e a ordem de bans mudam o significado de um ban, e o *map pool* mudou no período (tratado pela exposição por partida). A relação ban × desempenho sofre seleção: quem escolhe um mapa joga mais nele, então vale como associação, não como causa.
- **Dados terminam em 03/2020** (CS:GO) e não descrevem o CS2.

**Próximos passos**

- Rede **jogador–time** (bipartida) para capturar mobilidade de elenco e pontes entre times (S6 e S5).
- **Grafo temporal em janelas deslizantes**, em vez de fatias anuais.
- **Formato (bo1/bo3/bo5)** e **mapa** como camadas; modelar também os picks.
- Repetir o pipeline com dados **CS2** recentes e ranking contemporâneo.

## Referências

- Machado, M. D. *CS:GO Professional Matches*. Kaggle. <https://www.kaggle.com/datasets/mateusdmachado/csgo-professional-matches> (dados do HLTV.org).
- ilyazored. *HLTV Match Results | CS2*. Kaggle (bônus opcional). <https://www.kaggle.com/datasets/ilyazored/hltv-match-resultscs2>
- HLTV.org, fonte original dos dados: <https://www.hltv.org>
- Hagberg, A.; Schult, D.; Swart, P. *NetworkX*. <https://networkx.org>
- Material da disciplina Algoritmos e Estruturas de Dados II (UFRN), semanas 2 a 6.
