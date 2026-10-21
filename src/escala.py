"""Funções da Trilha 3 (mudança da escala 6x1 para 5x2).

Para entregar o mesmo serviço, a folha varia na razão inversa da carga semanal de cada integrante:

    folha_nova / folha_atual = horas semanais atuais / horas semanais novas

Isso vale para a folha inteira de quem muda de escala (posições e cobertura de ausências), porque a
cobertura de ausências é proporcional à folha. O fator depende de o que acontece com a jornada:
  jornada diária mantida   -> cada pessoa passa a trabalhar 5 dias em vez de 6 (fator = dias atuais / 5)
  limite semanal de 40 h   -> fator = 44 / 40
  carga semanal mantida    -> o dia de trabalho fica mais longo (fator = 1)
"""
import numpy as np
import pandas as pd


def perfil_jornada(ponto, min_dias=60):
    """Dias por semana, minutos por dia trabalhado e horas por semana de cada integrante.

    Usa só dias normais (situação A, sem feriado) para não confundir jornada com ausência.
    """
    n = ponto[(ponto.situacao == 'A') & (ponto.FERIADO == 0) & (ponto.grupo != 'Aprendiz')]
    trab = n.MINUTOS_PREVISTOS > 0
    g = (n.assign(trab=trab)
          .groupby(['ID_INTEGRANTE', 'empresa', 'grupo', 'escala'], observed=True)
          .agg(dias=('DATA', 'size'), dias_trab=('trab', 'sum'), minutos=('MINUTOS_PREVISTOS', 'sum'))
          .reset_index())
    g = g[(g.dias >= min_dias) & (g.dias_trab > 0)].copy()
    g['dias_sem'] = 7 * g.dias_trab / g.dias
    g['min_dia'] = g.minutos / g.dias_trab
    g['h_sem'] = 7 * g.minutos / g.dias / 60
    return g


def media_bootstrap(valores, n=500, seed=11, q=(.05, .95)):
    """Média e intervalo por reamostragem de integrantes."""
    v = np.asarray(valores, dtype=float)
    rng = np.random.default_rng(seed)
    m = [rng.choice(v, size=len(v), replace=True).mean() for _ in range(n)]
    return v.mean(), np.quantile(m, q[0]), np.quantile(m, q[1])


def fatores(dias_sem_6x1, horas_sem_6x1, dias_novos=5, horas_limite=40, horas_legais_atuais=44):
    """Fator de folha (folha nova / folha atual) em cada cenário de jornada."""
    return {'jornada diária mantida': dias_sem_6x1 / dias_novos,
            'limite semanal de 40 h': horas_legais_atuais / horas_limite,
            'carga semanal mantida': 1.0}


def quadro_adicional(folha, fator):
    """Integrantes a mais para o mesmo serviço, dada a folha atual de quem muda de escala."""
    return folha * (fator - 1)


def decompor_adicional(folha, fator, perda_ausencia):
    """Separa o adicional entre posições e cobertura de ausências (a folha = posições + cobertura).

    perda_ausencia: fração da folha que é cobertura de ausências (Trilha 2).
    """
    total = quadro_adicional(folha, fator)
    return {'posições': total * (1 - perda_ausencia), 'cobertura de ausências': total * perda_ausencia}


def efeito_rotatividade(folha, fator, turnover_pct, multiplicador, dias_vaga=30):
    """Efeito da mudança sobre saídas por ano e sobre vagas abertas.

    A folha maior gera mais saídas mesmo com a mesma taxa; o multiplicador representa uma mudança
    na taxa (a escala 5x2 pode reduzir ou aumentar a rotatividade; os dados não permitem estimá-lo).
    """
    saidas_antes = folha * turnover_pct / 100
    saidas_depois = folha * fator * turnover_pct / 100 * multiplicador
    return {'saídas/ano antes': saidas_antes, 'saídas/ano depois': saidas_depois,
            'variação de saídas/ano': saidas_depois - saidas_antes,
            'vagas abertas em média (depois)': saidas_depois * dias_vaga / 365,
            'vagas abertas em média (antes)': saidas_antes * dias_vaga / 365}
