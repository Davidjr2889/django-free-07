import math
from datetime import datetime
from statistics import mean
from typing import Dict

from prev_log.pydantic_model.product import PyTendency

from ...utils.indexes import generate_index


def calculate_new_tendency(history: Dict[int, float]) -> PyTendency:
    """
    Método para calcular a tendência anual de um produto específico na virada do mês.

    Para o cálculo, deveremos receber um produto e nele
    constar o histórico de vendas de 02 anos atrás até o mes corrente (O mes corrente não será analisado).

    Médias simples. no ano ou trimestre.
    O cálculo é feito sempre num período homólogo ao anterior
    (e.x.: para a tendência trimestral, usamos os tres meses atras e o mesmo período de meses do ano anterior)

    tendency ponderada: Atualmente usamos 60% no ano e 40% no trimestre.

    tendency anual base será um input manual do utilizador
    """
    tendency = PyTendency()
    history_copy = {**history}

    # Estamos usando o mes atual como ultimo elemento da lista
    today = datetime.today()
    current_index = generate_index(target_date=today)
    if not history_copy.get(current_index):
        history_copy[current_index] = 0

    sorted_history = sorted(history_copy.items())
    sales_history_list = [item[1] for item in sorted_history]

    # Precisamos de pelo menos um ano e tres meses para o calculo trimestral.
    # 16 porque levamos em conta o mes atual
    if len(sales_history_list) < 16:
        return tendency

    # Vamos começar pela trimestral
    ultimos_tres_meses = sales_history_list[-4:-1]
    tres_meses_homologos = sales_history_list[-16:-13]

    tendency.average_trimester = math.floor(mean(ultimos_tres_meses))

    raw_tendency = (sum(ultimos_tres_meses) / sum(tres_meses_homologos)) - 1
    tendency.tendency_trimester = round(raw_tendency, 4)

    # Precisamos de dois anos para o calculo das tendencys anuais
    # 25 porque levamos em conta o mes atual
    if len(sales_history_list) < 25:
        return tendency

    ultimo_ano = sales_history_list[-13:-1]
    ano_homologo = sales_history_list[-25:-13]

    tendency.average_anual = math.floor(mean(ultimo_ano))

    raw_tendency = (sum(ultimo_ano) / sum(ano_homologo)) - 1
    tendency.tendency_anual = round(raw_tendency, 4)

    # Tendencia ponderada será 60% do ano e 40$ do trimestre
    raw_tendency = 0.4 * tendency.tendency_trimester + 0.6 * tendency.tendency_anual
    tendency.weighted_tendency = round(raw_tendency, 4)
    return tendency
