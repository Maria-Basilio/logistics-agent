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