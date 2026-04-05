from collections import defaultdict


def heuristica_agendamento(M, J, w, p, d=None):
    """
    M: lista de Núcleos
    J: lista de pessoas em situação de rua 
    w: dict {j: prioridade}
    p: dict {(i,j): tempo de processamento no Núcleo i}
    d: dict opcional {(i,j): tempo de deslocamento};
       se None, usa p/w como proxy do índice.

    Retorna:
        atribuicoes: {j: i}
        sequencia_por_nucleo: {i: [j1, j2, ...]}
        S_heur: {j: início do atendimento}
        C_heur: {j: conclusão do atendimento}
        valor_obj: soma_j w[j] * C_j
    """

    # estado da fila em cada Núcleo (tempo acumulado); começa em 1.0
    fila_nucleo = {i: 1.0 for i in M}

    # 1) Atribuição de cada poprua j ao Núcleo i usando (tempo/prioridade) * fila
    atribuicoes = {}
    for j in J:
        melhor_i = None
        melhor_idx = float("inf")
        for i in M:
            # tempo base: deslocamento, se existir; senão, processamento
            if d is not None:
                base = d[(i, j)]
            else:
                base = p[(i, j)]

            # índice ajustado: (tempo / prioridade) * fila atual do Núcleo i
            h_ij = (base / w[j]) * fila_nucleo[i]

            if h_ij < melhor_idx:
                melhor_idx = h_ij
                melhor_i = i

        atribuicoes[j] = melhor_i
        # atualiza fila do Núcleo escolhido somando o tempo de processamento
        fila_nucleo[melhor_i] += p[(melhor_i, j)]

    # 2) Agrupar poprua por Núcleo
    tarefas_por_nucleo = defaultdict(list)
    for j, i in atribuicoes.items():
        tarefas_por_nucleo[i].append(j)

    # 3) Ordenar cada fila de Núcleo pelo mesmo índice (tempo/prioridade) * fila
    sequencia_por_nucleo = {}
    for i in M:
        lista = tarefas_por_nucleo[i]
        lista_ord = sorted(
            lista,
            key=lambda j: (
                ((d[(i, j)] if d is not None else p[(i, j)]) / w[j])
                * fila_nucleo[i],
                j,
            ),
        )
        sequencia_por_nucleo[i] = lista_ord

    # 4) Calcular tempos de início (S) e conclusão (C) em cada Núcleo
    S_heur = {}
    C_heur = {}
    for i in M:
        tempo = 0.0
        for j in sequencia_por_nucleo[i]:
            S_heur[j] = tempo
            tempo += p[(i, j)]
            C_heur[j] = tempo

    # 5) Função objetivo heurística
    valor_obj = sum(w[j] * C_heur[j] for j in J)

    return atribuicoes, sequencia_por_nucleo, S_heur, C_heur, valor_obj