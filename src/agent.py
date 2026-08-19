import json
import re

import ollama

from .logistics import (
    generate_logistics_plan,
    identify_stock_alerts,
    recommend_vehicle,
)

from .tools import (
    listar_pedidos,
    listar_veiculos,
    consultar_estoque,
    consultar_entregas,
)

from .responses import format_vehicle_recommendations

SYSTEM_PROMPT = """
Você é um analista de logística.

Responda em português brasileiro.

RESPONDA SOMENTE COM BASE NOS DADOS OFICIAIS.

NÃO CONFUNDA:
- pedido com entrega;
- veículo disponível com veículo alocado;
- veículo recomendado com veículo alocado;
- recomendação com fato;
- estoque normal com estoque abaixo do mínimo.

Nunca invente informações.
Nunca altere valores.
Nunca transforme uma recomendação em uma alocação.

Diferencie claramente:
- FATO
- RECOMENDAÇÃO
- ESTIMATIVA

Se uma informação não estiver disponível,
diga claramente que ela não está disponível.
"""


def build_operation_context():
    orders = listar_pedidos()
    vehicles = listar_veiculos()
    inventory = consultar_estoque()
    deliveries = consultar_entregas()

    plan = generate_logistics_plan(
        orders=orders,
        vehicles=vehicles,
        inventory=inventory,
        deliveries=deliveries,
    )

    stock_alerts = identify_stock_alerts(inventory)

    # Recomendações devem ser obtidas do plano logístico,
    # pois ele considera disponibilidade, ocupação e prioridade.
    vehicle_recommendations = {}

    for item in plan.get("recomendacoes", []):
        vehicle_recommendations[item["pedido_id"]] = (
            item.get("veiculo_recomendado")
        )

    confirmed_allocations = []

    for delivery in deliveries:
        if delivery.get("veiculo_id") is not None:
            confirmed_allocations.append(
                {
                    "pedido_id": delivery["pedido_id"],
                    "veiculo_id": delivery["veiculo_id"],
                    "status": delivery["status"],
                }
            )

    return {
        "PEDIDOS": orders,
        "VEICULOS": vehicles,
        "ESTOQUE": inventory,
        "ENTREGAS": deliveries,
        "ALERTAS_ESTOQUE": stock_alerts,
        "VEICULOS_RECOMENDADOS": vehicle_recommendations,
        "ALOCACOES_CONFIRMADAS": confirmed_allocations,
        "PLANO_LOGISTICO": plan,
    }


def _find_order(context, pedido_id):
    for order in context["PEDIDOS"]:
        if order["id"] == pedido_id:
            return order

    return None


def _find_delivery(context, pedido_id):
    for delivery in context["ENTREGAS"]:
        if delivery["pedido_id"] == pedido_id:
            return delivery

    return None


def _find_vehicle(context, vehicle_id):
    for vehicle in context["VEICULOS"]:
        if vehicle["id"] == vehicle_id:
            return vehicle

    return None


def _confirmed_allocation(context, pedido_id):
    for allocation in context["ALOCACOES_CONFIRMADAS"]:
        if allocation["pedido_id"] == pedido_id:
            return allocation

    return None


def deterministic_answer(question, context):
    q = question.lower().strip()

    # =========================================================
    # ESTOQUE
    # =========================================================

    if "estoque" in q and any(
        word in q
        for word in [
            "problema",
            "alerta",
            "abaixo",
            "mínimo",
            "minimo",
        ]
    ):
        alerts = context["ALERTAS_ESTOQUE"]

        if not alerts:
            return (
                "ESTOQUE\n\n"
                "Não existem produtos abaixo do estoque mínimo."
            )

        lines = ["ALERTAS DE ESTOQUE", ""]

        for item in alerts:
            lines.append(
                f"- {item['produto']}: "
                f"{item['estoque']} unidades, "
                f"mínimo {item['estoque_minimo']} "
                f"({item['local']})"
            )

        return "\n".join(lines)

    # =========================================================
    # VEÍCULOS DISPONÍVEIS
    # =========================================================

    if (
        ("veículos" in q or "veiculos" in q)
        and (
            "disponíveis" in q
            or "disponiveis" in q
        )
    ):
        vehicles = [
            vehicle
            for vehicle in context["VEICULOS"]
            if vehicle.get("disponivel", False)
        ]

        lines = ["VEÍCULOS DISPONÍVEIS", ""]

        for vehicle in vehicles:
            lines.append(
                f"- {vehicle['id']} "
                f"({vehicle['tipo']}): "
                f"{vehicle['capacidade_kg']} kg, "
                f"{vehicle['capacidade_m3']} m³, "
                f"origem: {vehicle['origem']}"
            )

        return "\n".join(lines)

    # =========================================================
    # IDENTIFICA PEDIDO
    # =========================================================

    match = re.search(
        r"PED-\d+",
        question.upper(),
    )

    pedido_id = match.group(0) if match else None

    # =========================================================
    # PRAZO
    # =========================================================

    if pedido_id and "prazo" in q:
        order = _find_order(
            context,
            pedido_id,
        )

        if order is None:
            return f"O pedido {pedido_id} não foi encontrado."

        return (
            "FATO\n\n"
            f"O prazo do {pedido_id} é {order['prazo']}."
        )

    # =========================================================
    # PERGUNTA SOBRE VEÍCULO ALOCADO
    # =========================================================

    if pedido_id and any(
        phrase in q
        for phrase in [
            "veículo alocado",
            "veiculo alocado",
            "veículo associado",
            "veiculo associado",
            "possui veículo",
            "possui veiculo",
            "tem veículo",
            "tem veiculo",
        ]
    ):
        allocation = _confirmed_allocation(
            context,
            pedido_id,
        )

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

    # =========================================================
    # STATUS / TRÂNSITO / ENTREGA
    # =========================================================

    if pedido_id and any(
        word in q
        for word in [
            "trânsito",
            "transito",
            "status",
            "entrega",
        ]
    ):
        delivery = _find_delivery(
            context,
            pedido_id,
        )

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

    # =========================================================
    # VEÍCULO RECOMENDADO
    # =========================================================

    if pedido_id and (
        "recomenda" in q
        or "melhor veículo" in q
        or "melhor veiculo" in q
    ):
        order = _find_order(
            context,
            pedido_id,
        )

        if order is None:
            return f"O pedido {pedido_id} não foi encontrado."

        recommended_id = context[
            "VEICULOS_RECOMENDADOS"
        ].get(pedido_id)

        if recommended_id is None:
            return (
                "RECOMENDAÇÃO\n\n"
                f"Não há veículo recomendado para "
                f"{pedido_id} nos dados do plano logístico."
            )

        vehicle = _find_vehicle(
            context,
            recommended_id,
        )

        if vehicle is None:
            return (
                "RECOMENDAÇÃO\n\n"
                f"Veículo recomendado: {recommended_id}."
            )

        return (
            "RECOMENDAÇÃO\n\n"
            f"Pedido: {pedido_id}\n"
            f"Veículo recomendado: {vehicle['id']}\n"
            f"Tipo: {vehicle['tipo']}\n"
            f"Capacidade: "
            f"{vehicle['capacidade_kg']} kg / "
            f"{vehicle['capacidade_m3']} m³\n"
            f"Origem do veículo: {vehicle['origem']}\n"
            f"Disponível: "
            f"{'sim' if vehicle.get('disponivel') else 'não'}\n\n"
            "Esta é uma recomendação. "
            "Não representa uma alocação confirmada."
        )
    # =========================================================
    # RECOMENDAÇÃO DE VEÍCULO PARA CADA PEDIDO
    # =========================================================

    if (
        ("veículo" in q or "veiculo" in q)
        and (
            "cada pedido" in q
            or "todos os pedidos" in q
            or "para cada pedido" in q
        )
        and (
            "recomenda" in q
            or "recomendado" in q
        )
    ):
        return format_vehicle_recommendations(context)
    # =========================================================
    # PEDIDOS EM TRÂNSITO
    # =========================================================

    if (
        "pedidos" in q
        and (
            "em trânsito" in q
            or "em transito" in q
        )
    ):
        deliveries = [
            delivery
            for delivery in context["ENTREGAS"]
            if delivery.get("status") == "em_transito"
        ]

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

    # =========================================================
    # PEDIDOS SEM VEÍCULO ALOCADO
    # =========================================================

    if (
        "pedidos" in q
        and (
            "sem veículo" in q
            or "sem veiculo" in q
        )
    ):
        result = []

        for order in context["PEDIDOS"]:
            allocation = _confirmed_allocation(
                context,
                order["id"],
            )

            if allocation is None:
                result.append(order["id"])

        if not result:
            return (
                "FATO\n\n"
                "Todos os pedidos possuem uma alocação confirmada."
            )

        lines = [
            "FATO",
            "",
            "Pedidos sem veículo alocado:",
        ]

        for pedido in result:
            lines.append(f"- {pedido}")

        return "\n".join(lines)

    # =========================================================
    # ALERTAS DA OPERAÇÃO
    # =========================================================

    if (
        "alertas" in q
        or "alertas da operação" in q
        or "alertas da operacao" in q
    ):
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

    # =========================================================
    # CONSOLIDAÇÃO
    # =========================================================

    if "consolida" in q:
        opportunities = context[
            "PLANO_LOGISTICO"
        ].get(
            "consolidacao",
            [],
        )

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

    return None


def ask_agent(question):
    context = build_operation_context()

    deterministic = deterministic_answer(
        question,
        context,
    )

    if deterministic is not None:
        return deterministic

    prompt = f"""
DADOS OFICIAIS DA OPERAÇÃO:

{json.dumps(
    context,
    ensure_ascii=False,
    indent=2,
)}

PERGUNTA DO USUÁRIO:

{question}

Responda somente com base nos dados acima.

Regras obrigatórias:
1. Não invente informações.
2. Não transforme recomendação em alocação.
3. Não transforme veículo disponível em veículo alocado.
4. Não transforme pedido em entrega.
5. Se não houver registro, diga que não há registro.
6. Se for recomendação, escreva explicitamente "RECOMENDAÇÃO".
7. Se for fato, escreva explicitamente "FATO".
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response["message"]["content"]