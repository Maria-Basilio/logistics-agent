from datetime import date, datetime


def vehicle_can_transport(order, vehicle):
    """
    Verifica se o veículo possui capacidade suficiente
    de peso e volume e está disponível.
    """

    if not vehicle.get("disponivel", False):
        return False

    peso = order.get("peso_kg", 0)
    volume = order.get("volume_m3", 0)

    capacidade_kg = vehicle.get("capacidade_kg", 0)
    capacidade_m3 = vehicle.get("capacidade_m3", 0)

    return (
        peso <= capacidade_kg
        and volume <= capacidade_m3
    )


def calculate_vehicle_score(order, vehicle):
    """
    Calcula uma pontuação para determinar
    qual veículo é mais adequado.
    """

    if not vehicle_can_transport(order, vehicle):
        return -1

    score = 0

    # Prioridade alta
    if order.get("prioridade") == "alta":
        score += 30

    # Veículo na mesma origem do pedido
    if vehicle.get("origem") == order.get("origem"):
        score += 40

    # Eficiência de utilização da capacidade
    peso = order.get("peso_kg", 0)
    volume = order.get("volume_m3", 0)

    capacidade_kg = vehicle.get("capacidade_kg", 1)
    capacidade_m3 = vehicle.get("capacidade_m3", 1)

    peso_utilizacao = peso / capacidade_kg
    volume_utilizacao = volume / capacidade_m3

    score += peso_utilizacao * 20
    score += volume_utilizacao * 20

    return score


def recommend_vehicle(order, vehicles):
    """
    Retorna o melhor veículo disponível para o pedido.
    """

    candidates = [
        vehicle
        for vehicle in vehicles
        if vehicle_can_transport(order, vehicle)
    ]

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda vehicle: calculate_vehicle_score(
            order,
            vehicle,
        ),
    )


def identify_stock_alerts(inventory):
    """
    Identifica produtos abaixo do estoque mínimo.
    """

    return [
        item
        for item in inventory
        if item.get("estoque", 0)
        < item.get("estoque_minimo", 0)
    ]


def calculate_deadline_status(order, reference_date=None):
    """
    Analisa a proximidade do prazo de entrega.

    reference_date permite tornar o cálculo determinístico
    nos testes. Quando não informado, usa a data atual.
    """

    prazo = order.get("prazo")

    if not prazo:
        return {
            "pedido_id": order.get("id"),
            "prazo": None,
            "dias_restantes": None,
            "status": "sem_prazo",
        }

    try:
        deadline = datetime.strptime(
            prazo,
            "%Y-%m-%d",
        ).date()
    except ValueError:
        return {
            "pedido_id": order.get("id"),
            "prazo": prazo,
            "dias_restantes": None,
            "status": "prazo_invalido",
        }

    today = reference_date or date.today()
    days_remaining = (deadline - today).days

    if days_remaining < 0:
        status = "atrasado"
    elif days_remaining == 0:
        status = "vence_hoje"
    elif days_remaining == 1:
        status = "proximo_do_prazo"
    else:
        status = "normal"

    return {
        "pedido_id": order.get("id"),
        "prazo": prazo,
        "dias_restantes": days_remaining,
        "status": status,
    }


def can_consolidate_orders(order1, order2, vehicle):
    """
    Verifica se dois pedidos podem ser transportados
    juntos pelo mesmo veículo.
    """

    if not vehicle.get("disponivel", False):
        return False

    if order1.get("origem") != order2.get("origem"):
        return False

    if order1.get("destino") != order2.get("destino"):
        return False

    peso_total = (
        order1.get("peso_kg", 0)
        + order2.get("peso_kg", 0)
    )

    volume_total = (
        order1.get("volume_m3", 0)
        + order2.get("volume_m3", 0)
    )

    return (
        peso_total <= vehicle.get("capacidade_kg", 0)
        and volume_total <= vehicle.get("capacidade_m3", 0)
    )


def find_consolidation_opportunities(orders, vehicles):
    """
    Identifica pares de pedidos que podem ser consolidados.
    """

    opportunities = []

    for i in range(len(orders)):
        for j in range(i + 1, len(orders)):

            order1 = orders[i]
            order2 = orders[j]

            suitable_vehicles = []

            for vehicle in vehicles:
                if can_consolidate_orders(
                    order1,
                    order2,
                    vehicle,
                ):
                    suitable_vehicles.append(
                        vehicle["id"]
                    )

            if suitable_vehicles:
                opportunities.append(
                    {
                        "pedidos": [
                            order1["id"],
                            order2["id"],
                        ],
                        "origem": order1["origem"],
                        "destino": order1["destino"],
                        "peso_total_kg": (
                            order1.get("peso_kg", 0)
                            + order2.get("peso_kg", 0)
                        ),
                        "volume_total_m3": (
                            order1.get("volume_m3", 0)
                            + order2.get("volume_m3", 0)
                        ),
                        "veiculos_adequados": (
                            suitable_vehicles
                        ),
                    }
                )

    return opportunities


def generate_logistics_plan(
    orders,
    vehicles,
    inventory,
    deliveries,
):
    """
    Gera um plano logístico considerando:

    - disponibilidade real dos veículos;
    - veículos já ocupados;
    - capacidade;
    - prioridade;
    - prazos;
    - estoque;
    - consolidação.
    """

    high_priority_orders = [
        order
        for order in orders
        if order.get("prioridade") == "alta"
    ]

    # Veículos já associados a entregas ativas.
    occupied_vehicle_ids = {
        delivery.get("veiculo_id")
        for delivery in deliveries
        if (
            delivery.get("status")
            in {"em_transito", "aguardando_coleta"}
            and delivery.get("veiculo_id")
        )
    }

    # Veículos realmente livres.
    available_vehicles = [
        vehicle
        for vehicle in vehicles
        if (
            vehicle.get("disponivel", False)
            and vehicle.get("id")
            not in occupied_vehicle_ids
        )
    ]

    # Pedidos prioritários primeiro.
    ordered_orders = sorted(
        orders,
        key=lambda order: (
            order.get("prioridade") != "alta",
            order.get("prazo", ""),
        ),
    )

    recommendations = []

    # Cópia dos veículos livres para controle
    # das recomendações dentro deste plano.
    remaining_vehicles = list(
        available_vehicles
    )

    for order in ordered_orders:

        # Verifica se já existe uma entrega registrada.
        existing_delivery = next(
            (
                delivery
                for delivery in deliveries
                if delivery.get("pedido_id")
                == order.get("id")
            ),
            None,
        )

        if existing_delivery:

            confirmed_vehicle = (
                existing_delivery.get("veiculo_id")
            )

            if confirmed_vehicle:
                allocation_type = "confirmado"
            else:
                allocation_type = "sem_veiculo"

            recommendations.append(
                {
                    "pedido_id": order["id"],
                    "veiculo_recomendado": confirmed_vehicle,
                    "status": existing_delivery.get(
                        "status"
                    ),
                    "tipo_recomendacao": allocation_type,
                }
            )

            continue

        # Não possui entrega registrada.
        # Procuramos um veículo livre.
        vehicle = recommend_vehicle(
            order,
            remaining_vehicles,
        )

        if vehicle:

            recommendations.append(
                {
                    "pedido_id": order["id"],
                    "veiculo_recomendado": vehicle["id"],
                    "status": "disponivel",
                    "tipo_recomendacao": "recomendado",
                }
            )

            # Reserva o veículo para não
            # recomendá-lo simultaneamente
            # para outro pedido.
            remaining_vehicles = [
                item
                for item in remaining_vehicles
                if item["id"] != vehicle["id"]
            ]

        else:

            recommendations.append(
                {
                    "pedido_id": order["id"],
                    "veiculo_recomendado": None,
                    "status": "sem_veiculo",
                    "tipo_recomendacao": "sem_alternativa",
                }
            )

    stock_alerts = identify_stock_alerts(
        inventory
    )

    deadline_analysis = [
        calculate_deadline_status(order)
        for order in orders
    ]

    consolidation = find_consolidation_opportunities(
        orders,
        available_vehicles,
    )

    waiting_collection = [
        delivery
        for delivery in deliveries
        if delivery.get("status")
        == "aguardando_coleta"
    ]

    in_transit = [
        delivery
        for delivery in deliveries
        if delivery.get("status")
        == "em_transito"
    ]

    delivered = [
        delivery
        for delivery in deliveries
        if delivery.get("status")
        == "entregue"
    ]

    orders_without_vehicle = [
        item
        for item in recommendations
        if item["veiculo_recomendado"] is None
    ]

    return {
        "pedidos": {
            "total": len(orders),
            "prioridade_alta": len(
                high_priority_orders
            ),
            "pedidos_prioritarios": [
                order["id"]
                for order in high_priority_orders
            ],
        },

        "veiculos": {
            "total": len(vehicles),
            "disponiveis": len(
                available_vehicles
            ),
            "em_utilizacao": (
                len(vehicles)
                - len(available_vehicles)
            ),
        },

        "recomendacoes": recommendations,

        "pedidos_sem_veiculo": (
            orders_without_vehicle
        ),

        "estoque": {
            "total_produtos": len(inventory),
            "alertas": stock_alerts,
        },

        "entregas": {
            "aguardando_coleta": len(
                waiting_collection
            ),
            "em_transito": len(in_transit),
            "entregues": len(delivered),
        },

        "prazos": deadline_analysis,

        "consolidacao": consolidation,
    }

from datetime import date


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