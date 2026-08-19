import json
from pathlib import Path

from .logistics import (
    recommend_vehicle,
    vehicle_can_transport,
)


# Diretório raiz do projeto.
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretório onde estão os JSONs.
DATA_DIR = BASE_DIR / "data"


def _load_json(filename):
    """
    Carrega um arquivo JSON da pasta data.
    """

    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def listar_pedidos():
    """
    Retorna todos os pedidos disponíveis.
    """
    return _load_json("orders.json")


def consultar_pedido(pedido_id):
    """
    Retorna os dados de um pedido específico.
    """

    pedidos = listar_pedidos()

    for pedido in pedidos:
        if pedido["id"] == pedido_id:
            return pedido

    return None


def listar_veiculos():
    """
    Retorna todos os veículos.
    """
    return _load_json("vehicles.json")


def listar_veiculos_disponiveis():
    """
    Retorna somente os veículos disponíveis.
    """

    vehicles = listar_veiculos()

    return [
        vehicle
        for vehicle in vehicles
        if vehicle.get("disponivel", False)
    ]


def consultar_estoque():
    """
    Retorna a situação atual do estoque.
    """
    return _load_json("inventory.json")


def consultar_entregas():
    """
    Retorna o status das entregas.
    """
    return _load_json("deliveries.json")


def analisar_capacidade(
    pedido_id,
    veiculo_id,
):
    """
    Verifica se determinado veículo consegue
    transportar determinado pedido.
    """

    pedido = consultar_pedido(pedido_id)

    if pedido is None:
        return {
            "erro": f"Pedido {pedido_id} não encontrado."
        }

    vehicles = listar_veiculos()

    vehicle = next(
        (
            item
            for item in vehicles
            if item["id"] == veiculo_id
        ),
        None,
    )

    if vehicle is None:
        return {
            "erro": f"Veículo {veiculo_id} não encontrado."
        }

    aprovado = vehicle_can_transport(
        pedido,
        vehicle,
    )

    return {
        "pedido_id": pedido_id,
        "veiculo_id": veiculo_id,
        "aprovado": aprovado,
        "peso_pedido_kg": pedido["peso_kg"],
        "capacidade_veiculo_kg": vehicle[
            "capacidade_kg"
        ],
        "volume_pedido_m3": pedido["volume_m3"],
        "capacidade_veiculo_m3": vehicle[
            "capacidade_m3"
        ],
        "veiculo_disponivel": vehicle[
            "disponivel"
        ],
    }


def sugerir_alocacao(pedido_id):
    """
    Analisa os veículos e sugere o mais adequado.
    """

    pedido = consultar_pedido(pedido_id)

    if pedido is None:
        return {
            "erro": f"Pedido {pedido_id} não encontrado."
        }

    vehicles = listar_veiculos()

    vehicle = recommend_vehicle(
        pedido,
        vehicles,
    )

    if vehicle is None:
        return {
            "pedido_id": pedido_id,
            "veiculo_recomendado": None,
            "mensagem": (
                "Nenhum veículo disponível possui "
                "capacidade suficiente para este pedido."
            ),
        }

    return {
        "pedido_id": pedido_id,
        "veiculo_recomendado": vehicle,
    }
