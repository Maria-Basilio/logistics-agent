def format_vehicle_recommendations(context):
    """
    Formata as recomendações de veículo para todos os pedidos.

    Esta função apenas apresenta dados já calculados
    pelo plano logístico. Não cria nem altera recomendações.
    """

    lines = [
        "RECOMENDAÇÕES",
        "",
    ]

    for order in context["PEDIDOS"]:
        pedido_id = order["id"]

        recommended_id = context[
            "VEICULOS_RECOMENDADOS"
        ].get(pedido_id)

        if recommended_id is None:
            lines.append(
                f"- {pedido_id}: "
                "não há veículo recomendado."
            )
            continue

        vehicle = None

        for item in context["VEICULOS"]:
            if item["id"] == recommended_id:
                vehicle = item
                break

        if vehicle is None:
            lines.append(
                f"- {pedido_id}: "
                f"{recommended_id} "
                "(veículo recomendado)."
            )
            continue

        lines.append(
            f"- {pedido_id}: "
            f"{vehicle['id']} "
            f"({vehicle['tipo']}, "
            f"{vehicle['capacidade_kg']} kg, "
            f"{vehicle['capacidade_m3']} m³)"
        )

    lines.extend(
        [
            "",
            "Estas são recomendações. "
            "Não representam alocações confirmadas.",
        ]
    )

    return "\n".join(lines)

def format_stock_alerts(context):
    """
    Formata os alertas de estoque.

    Esta função apenas apresenta os alertas
    já calculados pelos dados da operação.
    """

    alerts = context["ALERTAS_ESTOQUE"]

    if not alerts:
        return (
            "ESTOQUE\n\n"
            "Não existem produtos abaixo do estoque mínimo."
        )

    lines = [
        "ALERTAS DE ESTOQUE",
        "",
    ]

    for item in alerts:
        lines.append(
            f"- {item['produto']}: "
            f"{item['estoque']} unidades, "
            f"mínimo {item['estoque_minimo']} "
            f"({item['local']})"
        )

    return "\n".join(lines)

def format_available_vehicles(context):
    """
    Formata a lista de veículos atualmente disponíveis.

    Esta função apenas apresenta os veículos marcados
    como disponíveis nos dados oficiais.
    """

    vehicles = [
        vehicle
        for vehicle in context["VEICULOS"]
        if vehicle.get("disponivel", False)
    ]

    lines = [
        "VEÍCULOS DISPONÍVEIS",
        "",
    ]

    for vehicle in vehicles:
        lines.append(
            f"- {vehicle['id']} "
            f"({vehicle['tipo']}): "
            f"{vehicle['capacidade_kg']} kg, "
            f"{vehicle['capacidade_m3']} m³, "
            f"origem: {vehicle['origem']}"
        )

    return "\n".join(lines)

def format_delivery_status(pedido_id, delivery):
    """
    Formata o status de uma entrega.

    Esta função apenas apresenta os dados oficiais
    da entrega recebida.
    """

    if delivery is None:
        return (
            "FATO\n\n"
            f"Não há registro de entrega para "
            f"{pedido_id} nos dados da operação.\n\n"
            "Portanto, não é possível afirmar "
            "que o pedido esteja em trânsito, "
            "aguardando coleta ou entregue."
        )

    result = (
        "FATO\n\n"
        f"{pedido_id}: {delivery['status']}."
    )

    if delivery.get("veiculo_id"):
        result += (
            f"\nVeículo associado: "
            f"{delivery['veiculo_id']}."
        )

    if delivery.get("previsao_entrega"):
        result += (
            f"\nPrevisão de entrega: "
            f"{delivery['previsao_entrega']}."
        )

    return result

def format_deadline(pedido_id, order):
    """
    Formata o prazo de um pedido.

    Esta função apenas apresenta o prazo
    registrado nos dados oficiais.
    """

    if order is None:
        return (
            f"O pedido {pedido_id} não foi encontrado."
        )

    return (
        "FATO\n\n"
        f"O prazo do {pedido_id} é {order['prazo']}."
    )

def format_vehicle_allocation(pedido_id, allocation):
    """
    Formata a alocação confirmada de um pedido.

    Esta função apenas apresenta dados oficiais
    de uma alocação existente.
    """

    if allocation is None:
        return (
            "FATO\n\n"
            f"Não existe alocação confirmada para "
            f"{pedido_id} nos dados da operação."
        )

    return (
        "FATO\n\n"
        f"{pedido_id} possui alocação confirmada "
        f"com o veículo {allocation['veiculo_id']}.\n"
        f"Status: {allocation['status']}."
    )
def format_unallocated_orders(order_ids):
    if not order_ids:
        return (
            "FATO\n\n"
            "Todos os pedidos possuem uma alocação confirmada."
        )

    lines = [
        "FATO",
        "",
        "Pedidos sem veículo alocado:",
    ]

    for pedido_id in order_ids:
        lines.append(f"- {pedido_id}")

    return "\n".join(lines)
def format_in_transit_orders(deliveries):
    """
    Formata os pedidos que estão em trânsito.

    Esta função apenas apresenta os dados oficiais
    das entregas recebidas.
    """

    if not deliveries:
        return (
            "FATO\n\n"
            "Não há pedidos em trânsito nos dados oficiais."
        )

    lines = [
        "FATO",
        "",
        "Pedidos em trânsito:",
    ]

    for delivery in deliveries:
        lines.append(
            f"- {delivery['pedido_id']}"
        )

    return "\n".join(lines)

def format_operation_alerts(context):
    lines = ["ALERTAS DA OPERAÇÃO", ""]

    alerts_found = False

    for item in context["ALERTAS_ESTOQUE"]:
        alerts_found = True
        lines.append(
            f"- Estoque: {item['produto']} "
            f"com {item['estoque']} unidades; "
            f"mínimo {item['estoque_minimo']} "
            f"({item['local']})"
        )

    for item in context["PLANO_LOGISTICO"].get(
        "prazos",
        [],
    ):
        if item.get("status") in {
            "vence_hoje",
            "atrasado",
        }:
            alerts_found = True
            lines.append(
                f"- Prazo: {item['pedido_id']} "
                f"({item['status']})"
            )

    if not alerts_found:
        return (
            "ALERTAS DA OPERAÇÃO\n\n"
            "Não existem alertas registrados."
        )

    return "\n".join(lines)

def format_consolidation(opportunities):
    if not opportunities:
        return (
            "CONSOLIDAÇÃO\n\n"
            "Não há oportunidades de consolidação "
            "entre os pedidos atuais."
        )

    lines = [
        "CONSOLIDAÇÃO",
        "",
        "Oportunidades encontradas:",
    ]

    for item in opportunities:
        lines.append(
            f"- Pedidos: "
            f"{', '.join(item['pedidos'])}; "
            f"origem: {item['origem']}; "
            f"destino: {item['destino']}; "
            f"peso total: {item['peso_total_kg']} kg; "
            f"volume total: {item['volume_total_m3']} m³; "
            f"veículos adequados: "
            f"{', '.join(item['veiculos_adequados'])}"
        )

    return "\n".join(lines)