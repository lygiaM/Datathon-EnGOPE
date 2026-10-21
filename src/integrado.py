"""Modelo integrado das três trilhas.

Base única: a posição, isto é, a pessoa escalada para trabalhar num dia (já descontada a folga semanal
da escala atual). Cada trilha entra como um multiplicador sobre ela:

    cobertura (T2)   a / (1 - a)                    a = fração da folha que é cobertura de ausências
    escala (T3)      s (f - 1) / (1 - a)            s = parcela da folha em 6x1, f = fator de folha
    vagas (T1)       T * dias_vaga / 365 * folha    T = turnover anual, dias_vaga = prazo para repor

Folha necessária por posição = (1 + s (f - 1)) / (1 - a) * (1 + T * dias_vaga / 365).

Para a operação atual, a folha F (quadro ativo) já contém a cobertura: posições = F (1 - a), e a
cobertura dentro da folha é F * a. A mudança de escala soma F * s * (f - 1), sem depender de a.
"""
import numpy as np
import pandas as pd


def multiplicadores(a, s, f, turnover_pct, dias_vaga=30):
    """Componentes da folha, em pessoas por posição (posição = 1)."""
    base = 1.0
    cobertura = a / (1 - a)
    escala = s * (f - 1) / (1 - a)
    sem_vagas = base + cobertura + escala
    vagas = sem_vagas * turnover_pct / 100 * dias_vaga / 365
    return {'posições': base, 'cobertura (T2)': cobertura, 'escala (T3)': escala,
            'vagas (T1)': vagas, 'total': sem_vagas + vagas}


def operacao_atual(folha, a, s, f, turnover_pct, dias_vaga=30):
    """Componentes em pessoas para a operação atual (folha = quadro ativo, que já inclui cobertura)."""
    posicoes = folha * (1 - a)
    m = multiplicadores(a, s, f, turnover_pct, dias_vaga)
    return {k: v * posicoes for k, v in m.items()}


def custo_anual(pessoas, salario_mensal, encargos=1.0):
    """Custo anual em R$: pessoas x salário x 12 x multiplicador de encargos (1,0 = só salário)."""
    return pessoas * salario_mensal * 12 * encargos
