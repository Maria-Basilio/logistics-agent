from datetime import date

from src.logistics import (
    vehicle_can_transport,
    calculate_vehicle_score,
    recommend_vehicle,
    identify_stock_alerts,
    calculate_deadline_status,
    can_consolidate_orders,
    find_consolidation_opportunities,
)


def test_vehicle_can_transport():
    order = {
        "peso_kg": 450,
        "volume_m3": 2.4,
    }

    vehicle = {
        "capacidade_kg": 1200,
        "capacidade_m3": 8,
        "disponivel": True,
    }

    assert vehicle_can_transport(order, vehicle) is True


def test_vehicle_cannot_transport_weight():
    order = {
        "peso_kg": 2000,
        "volume_m3": 2,
    }

    vehicle = {
        "capacidade_kg": 1200,
        "capacidade_m3": 8,
        "disponivel": True,
    }

    assert vehicle_can_transport(order, vehicle) is False


def test_vehicle_cannot_transport_volume():
    order = {
        "peso_kg": 500,
        "volume_m3": 10,
    }

    vehicle = {
        "capacidade_kg": 1200,
        "capacidade_m3": 8,
        "disponivel": True,
    }

    assert vehicle_can_transport(order, vehicle) is False


def test_vehicle_cannot_transport_if_unavailable():
    order = {
        "peso_kg": 450,
        "volume_m3": 2.4,
    }

    vehicle = {
        "capacidade_kg": 5000,
        "capacidade_m3": 25,
        "disponivel": False,
    }

    assert vehicle_can_transport(order, vehicle) is False


def test_calculate_vehicle_score():
    order = {
        "peso_kg": 450,
        "volume_m3": 2.4,
        "prioridade": "alta",
        "origem": "São Paulo",
    }

    vehicle = {
        "capacidade_kg": 1200,
        "capacidade_m3": 8,
        "disponivel": True,
        "origem": "São Paulo",
    }

    score = calculate_vehicle_score(order, vehicle)

    assert score > 0


def test_calculate_vehicle_score_invalid_vehicle():
    order = {
        "peso_kg": 2000,
        "volume_m3": 10,
        "prioridade": "normal",
        "origem": "São Paulo",
    }

    vehicle = {
        "capacidade_kg": 1200,
        "capacidade_m3": 8,
        "disponivel": True,
        "origem": "São Paulo",
    }

    assert calculate_vehicle_score(order, vehicle) == -1


def test_recommend_vehicle():
    order = {
        "peso_kg": 450,
        "volume_m3": 2.4,
        "prioridade": "alta",
        "origem": "São Paulo",
    }

    vehicles = [
        {
            "id": "VEI-001",
            "capacidade_kg": 5000,
            "capacidade_m3": 25,
            "disponivel": True,
            "origem": "São Paulo",
        },
        {
            "id": "VEI-002",
            "capacidade_kg": 1200,
            "capacidade_m3": 8,
            "disponivel": True,
            "origem": "Campinas",
        },
    ]

    vehicle = recommend_vehicle(order, vehicles)

    assert vehicle is not None
    assert vehicle["id"] == "VEI-001"


def test_recommend_vehicle_returns_none_when_no_vehicle():
    order = {
        "peso_kg": 6000,
        "volume_m3": 30,
    }

    vehicles = [
        {
            "id": "VEI-001",
            "capacidade_kg": 5000,
            "capacidade_m3": 25,
            "disponivel": True,
        }
    ]

    assert recommend_vehicle(order, vehicles) is None


def test_identify_stock_alerts():
    inventory = [
        {
            "produto": "Produto A",
            "estoque": 120,
            "estoque_minimo": 100,
        },
        {
            "produto": "Produto B",
            "estoque": 35,
            "estoque_minimo": 40,
        },
    ]

    alerts = identify_stock_alerts(inventory)

    assert len(alerts) == 1
    assert alerts[0]["produto"] == "Produto B"


def test_identify_stock_alerts_empty():
    inventory = [
        {
            "produto": "Produto A",
            "estoque": 120,
            "estoque_minimo": 100,
        },
    ]

    alerts = identify_stock_alerts(inventory)

    assert alerts == []


def test_prazo_vence_hoje_com_data_de_referencia():
    order = {
        "id": "PED-TESTE",
        "prazo": "2026-08-19",
    }

    result = calculate_deadline_status(
        order,
        reference_date=date(2026, 8, 19),
    )

    assert result["dias_restantes"] == 0
    assert result["status"] == "vence_hoje"


def test_prazo_atrasado_com_data_de_referencia():
    order = {
        "id": "PED-TESTE",
        "prazo": "2026-08-18",
    }

    result = calculate_deadline_status(
        order,
        reference_date=date(2026, 8, 19),
    )

    assert result["dias_restantes"] == -1
    assert result["status"] == "atrasado"


def test_prazo_proximo_com_data_de_referencia():
    order = {
        "id": "PED-TESTE",
        "prazo": "2026-08-20",
    }

    result = calculate_deadline_status(
        order,
        reference_date=date(2026, 8, 19),
    )

    assert result["dias_restantes"] == 1
    assert result["status"] == "proximo_do_prazo"


def test_prazo_sem_data():
    order = {
        "id": "PED-TESTE",
    }

    result = calculate_deadline_status(
        order,
        reference_date=date(2026, 8, 19),
    )

    assert result["dias_restantes"] is None
    assert result["status"] == "sem_prazo"


def test_prazo_invalido():
    order = {
        "id": "PED-TESTE",
        "prazo": "data-invalida",
    }

    result = calculate_deadline_status(
        order,
        reference_date=date(2026, 8, 19),
    )

    assert result["dias_restantes"] is None
    assert result["status"] == "prazo_invalido"


def test_can_consolidate_orders():
    order1 = {
        "id": "PED-001",
        "origem": "São Paulo",
        "destino": "Campinas",
        "peso_kg": 450,
        "volume_m3": 2.4,
    }

    order2 = {
        "id": "PED-002",
        "origem": "São Paulo",
        "destino": "Campinas",
        "peso_kg": 800,
        "volume_m3": 4.1,
    }

    vehicle = {
        "id": "VEI-001",
        "capacidade_kg": 5000,
        "capacidade_m3": 25,
        "disponivel": True,
    }

    assert can_consolidate_orders(
        order1,
        order2,
        vehicle,
    ) is True


def test_cannot_consolidate_different_origins():
    order1 = {
        "id": "PED-001",
        "origem": "São Paulo",
        "destino": "Campinas",
        "peso_kg": 450,
        "volume_m3": 2.4,
    }

    order2 = {
        "id": "PED-002",
        "origem": "Campinas",
        "destino": "Campinas",
        "peso_kg": 800,
        "volume_m3": 4.1,
    }

    vehicle = {
        "id": "VEI-001",
        "capacidade_kg": 5000,
        "capacidade_m3": 25,
        "disponivel": True,
    }

    assert can_consolidate_orders(
        order1,
        order2,
        vehicle,
    ) is False


def test_cannot_consolidate_different_destinations():
    order1 = {
        "id": "PED-001",
        "origem": "São Paulo",
        "destino": "Campinas",
        "peso_kg": 450,
        "volume_m3": 2.4,
    }

    order2 = {
        "id": "PED-002",
        "origem": "São Paulo",
        "destino": "Santos",
        "peso_kg": 800,
        "volume_m3": 4.1,
    }

    vehicle = {
        "id": "VEI-001",
        "capacidade_kg": 5000,
        "capacidade_m3": 25,
        "disponivel": True,
    }

    assert can_consolidate_orders(
        order1,
        order2,
        vehicle,
    ) is False


def test_find_consolidation_opportunities():
    orders = [
        {
            "id": "PED-001",
            "origem": "São Paulo",
            "destino": "Campinas",
            "peso_kg": 450,
            "volume_m3": 2.4,
        },
        {
            "id": "PED-002",
            "origem": "São Paulo",
            "destino": "Campinas",
            "peso_kg": 800,
            "volume_m3": 4.1,
        },
    ]

    vehicles = [
        {
            "id": "VEI-001",
            "capacidade_kg": 5000,
            "capacidade_m3": 25,
            "disponivel": True,
        }
    ]

    opportunities = find_consolidation_opportunities(
        orders,
        vehicles,
    )

    assert len(opportunities) == 1
    assert opportunities[0]["pedidos"] == [
        "PED-001",
        "PED-002",
    ]
    assert opportunities[0]["veiculos_adequados"] == [
        "VEI-001",
    ]