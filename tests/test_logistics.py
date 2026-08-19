from src.logistics import (
    vehicle_can_transport,
    calculate_vehicle_score,
    recommend_vehicle,
    identify_stock_alerts,
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


def test_unavailable_vehicle_cannot_transport():
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


def test_recommend_vehicle_respects_origin():
    order = {
        "id": "PED-003",
        "origem": "Campinas",
        "peso_kg": 250,
        "volume_m3": 1.2,
        "prioridade": "alta",
    }

    vehicles = [
        {
            "id": "VEI-001",
            "tipo": "caminhão",
            "capacidade_kg": 5000,
            "capacidade_m3": 25,
            "disponivel": True,
            "origem": "São Paulo",
        },
        {
            "id": "VEI-002",
            "tipo": "van",
            "capacidade_kg": 1200,
            "capacidade_m3": 8,
            "disponivel": True,
            "origem": "Campinas",
        },
    ]

    vehicle = recommend_vehicle(order, vehicles)

    assert vehicle is not None
    assert vehicle["id"] == "VEI-002"


def test_recommend_vehicle_returns_none_when_impossible():
    order = {
        "id": "PED-X",
        "origem": "São Paulo",
        "peso_kg": 10000,
        "volume_m3": 50,
        "prioridade": "normal",
    }

    vehicles = [
        {
            "id": "VEI-001",
            "capacidade_kg": 5000,
            "capacidade_m3": 25,
            "disponivel": True,
            "origem": "São Paulo",
        }
    ]

    assert recommend_vehicle(order, vehicles) is None


def test_identify_stock_alerts():
    inventory = [
        {
            "produto": "Produto A",
            "estoque": 120,
            "estoque_minimo": 50,
            "local": "São Paulo",
        },
        {
            "produto": "Produto B",
            "estoque": 35,
            "estoque_minimo": 40,
            "local": "Campinas",
        },
    ]

    alerts = identify_stock_alerts(inventory)

    assert len(alerts) == 1
    assert alerts[0]["produto"] == "Produto B"


def test_consolidation_same_route():
    order1 = {
        "id": "PED-001",
        "origem": "São Paulo",
        "destino": "Campinas",
        "peso_kg": 450,
        "volume_m3": 2.4,
    }

    order2 = {
        "id": "PED-004",
        "origem": "São Paulo",
        "destino": "Campinas",
        "peso_kg": 700,
        "volume_m3": 3.1,
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


def test_consolidation_different_destinations():
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
            "destino": "Santos",
            "peso_kg": 800,
            "volume_m3": 4.1,
        },
        {
            "id": "PED-004",
            "origem": "São Paulo",
            "destino": "Campinas",
            "peso_kg": 700,
            "volume_m3": 3.1,
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
        "PED-004",
    ]
    assert opportunities[0]["peso_total_kg"] == 1150
    assert opportunities[0]["volume_total_m3"] == 5.5
