from src.agent import ask_agent


def test_estoque_abaixo_do_minimo():
    resposta = ask_agent(
        "Existe algum problema de estoque?"
    )

    assert "Produto B" in resposta
    assert "35" in resposta
    assert "40" in resposta
    assert "Campinas" in resposta


def test_ped001_em_transito():
    resposta = ask_agent(
        "O PED-001 está em trânsito?"
    )

    assert "PED-001" in resposta
    assert "em_transito" in resposta
    assert "VEI-001" in resposta


def test_ped002_sem_alocacao():
    resposta = ask_agent(
        "O PED-002 possui veículo alocado?"
    )

    assert "PED-002" in resposta
    assert "Não existe alocação confirmada" in resposta


def test_ped003_nao_esta_em_transito():
    resposta = ask_agent(
        "O PED-003 está em trânsito?"
    )

    assert "PED-003" in resposta
    assert "Não há registro de entrega" in resposta


def test_recomendacao_ped003():
    resposta = ask_agent(
        "Qual veículo você recomenda para o PED-003?"
    )

    assert "PED-003" in resposta
    assert "VEI-002" in resposta
    assert "RECOMENDAÇÃO" in resposta
    assert "Não representa uma alocação confirmada" in resposta


def test_recomendacoes_todos_pedidos():
    resposta = ask_agent(
        "Qual veículo é recomendado para cada pedido?"
    )

    assert "PED-001" in resposta
    assert "VEI-001" in resposta

    assert "PED-002" in resposta
    assert "não há veículo recomendado" in resposta

    assert "PED-003" in resposta
    assert "VEI-002" in resposta

    assert "Não representam alocações confirmadas" in resposta


def test_pedidos_em_transito():
    resposta = ask_agent(
        "Quais pedidos estão em trânsito?"
    )

    assert "PED-001" in resposta
    assert "PED-003" not in resposta


def test_pedidos_sem_veiculo():
    resposta = ask_agent(
        "Quais pedidos estão sem veículo alocado?"
    )

    assert "PED-002" in resposta
    assert "PED-001" not in resposta


def test_alertas_operacao():
    resposta = ask_agent(
        "Quais são os alertas da operação?"
    )

    assert "Produto B" in resposta
    assert "PED-001" in resposta
    assert "PED-003" in resposta


def test_consolidacao():
    resposta = ask_agent(
        "Existe alguma oportunidade de consolidação?"
    )

    assert "Não há oportunidades de consolidação" in resposta
