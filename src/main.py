from .agent import ask_agent, build_operation_context


def print_operation_dashboard():
    context = build_operation_context()
    plan = context["PLANO_LOGISTICO"]

    pedidos = plan["pedidos"]
    veiculos = plan["veiculos"]
    entregas = plan["entregas"]
    estoque = plan["estoque"]
    prazos = plan["prazos"]

    print("=" * 50)
    print("             LOGISTICS AI AGENT")
    print("=" * 50)
    print()

    print("OPERAÇÃO ATUAL")
    print("-" * 50)

    print(f"Pedidos: {pedidos['total']}")
    print(
        f"Prioridade alta: "
        f"{pedidos['prioridade_alta']}"
    )
    print(
        f"Veículos disponíveis: "
        f"{veiculos['disponiveis']}"
    )
    print(
        f"Em trânsito: "
        f"{entregas['em_transito']}"
    )
    print(
        f"Aguardando coleta: "
        f"{entregas['aguardando_coleta']}"
    )
    print(
        f"Entregues: "
        f"{entregas['entregues']}"
    )

    print()
    print("ALERTAS")
    print("-" * 50)

    alerts_found = False

    for item in estoque["alertas"]:
        alerts_found = True
        print(
            f"[!] Estoque baixo: {item['produto']} "
            f"({item['estoque']}/{item['estoque_minimo']}) "
            f"- {item['local']}"
        )

    for item in prazos:
        if item["status"] in {
            "vence_hoje",
            "atrasado",
        }:
            alerts_found = True

            if item["status"] == "vence_hoje":
                status = "vence hoje"
            else:
                status = "atrasado"

            print(
                f"[!] Prazo: {item['pedido_id']} "
                f"({status})"
            )

    if not alerts_found:
        print("Nenhum alerta operacional.")

    print()
    print("VEÍCULOS")
    print("-" * 50)

    for vehicle in context["VEICULOS"]:
        status = (
            "disponível"
            if vehicle.get("disponivel")
            else "indisponível"
        )

        print(
            f"- {vehicle['id']}: "
            f"{vehicle['tipo']} | "
            f"{vehicle['capacidade_kg']} kg | "
            f"{vehicle['capacidade_m3']} m³ | "
            f"{status}"
        )

    print()
    print("=" * 50)
    print('Digite uma pergunta ou "quit" para sair.')
    print()


def main():
    try:
        print_operation_dashboard()

    except Exception as error:
        print("Não foi possível carregar o painel inicial.")
        print(f"Erro: {error}")
        print()

    while True:
        try:
            question = input("Você: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o agente.")
            break

        if not question:
            continue

        if question.lower() in {
            "quit",
            "exit",
            "sair",
        }:
            print(
                "\nEncerrando o "
                "Logistics AI Agent."
            )
            break

        print("\nAgente:")

        try:
            answer = ask_agent(question)
            print(answer)

        except Exception as error:
            print("\nErro ao consultar o agente:")
            print(error)

        print()


if __name__ == "__main__":
    main()