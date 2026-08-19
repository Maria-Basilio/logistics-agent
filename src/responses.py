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