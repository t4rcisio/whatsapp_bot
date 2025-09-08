import json
from langchain.tools import Tool

from services.database import LojaDB

# Instância global (ou passe como parâmetro se preferir injeção)
db = LojaDB()


# ===== WRAPPERS DE INSERÇÃO (mantidos e ajustados) =====

def insert_pedido_wrapper(input_str: str) -> str:
    try:
        data = json.loads(input_str)
        nome_cliente = data.get("nome_cliente")
        telefone = data.get("telefone")
        produtos = data.get("produtos", [])

        if not nome_cliente or not telefone or not isinstance(produtos, list):
            return "Erro: Campos obrigatórios ausentes ou inválidos. Esperado: {\"nome_cliente\": \"...\", \"telefone\": \"...\", \"produtos\": [\"...\"]}"

        return db.insert_pedido(nome_cliente, telefone, produtos)
    except Exception as e:
        return f"❌ Erro ao inserir pedido: {str(e)}"


def insert_conta_wrapper(input_str: str) -> str:
    try:
        data = json.loads(input_str)
        nome_cliente = data.get("nome_cliente")
        conta = data.get("conta")
        vencimento = data.get("vencimento")
        data_reg = data.get("data", None)

        if not nome_cliente or not conta or not vencimento:
            return "Erro: Campos obrigatórios ausentes. Esperado: {\"nome_cliente\": \"...\", \"conta\": valor, \"vencimento\": \"YYYY-MM-DD\"}"

        db.insert_conta(nome_cliente, conta, vencimento, data_reg)
        return f"✅ Conta inserida com sucesso para {nome_cliente}."
    except Exception as e:
        return f"❌ Erro ao inserir conta: {str(e)}"


def insert_estoque_wrapper(input_str: str) -> str:
    try:
        data = json.loads(input_str)
        produto = data.get("produto")
        descricao = data.get("descricao")
        preco = data.get("preco")
        preco_promocional = data.get("preco_promocional", None)

        if not produto or not descricao or preco is None:
            return "Erro: Campos obrigatórios ausentes. Esperado: {\"produto\": \"...\", \"descricao\": \"...\", \"preco\": valor}"

        db.insert_estoque(produto, descricao, preco, preco_promocional)
        return f"✅ Produto '{produto}' inserido no estoque com sucesso."
    except Exception as e:
        return f"❌ Erro ao inserir no estoque: {str(e)}"


# ===== WRAPPERS DE CONSULTA =====

def get_pedidos_wrapper(_: str = "{}") -> str:
    """Consulta todos os pedidos. Não precisa de parâmetros."""
    return db.get_pedidos()


def get_contas_wrapper(_: str = "{}") -> str:
    """Consulta todas as contas. Não precisa de parâmetros."""
    return db.get_contas()


def get_estoque_wrapper(_: str = "{}") -> str:
    """Consulta todo o estoque. Não precisa de parâmetros."""
    return db.get_estoque()


def get_pedidos_por_cliente_wrapper(input_str: str) -> str:
    try:
        data = json.loads(input_str)
        nome_cliente = data.get("nome_cliente")
        if not nome_cliente:
            return "Erro: Campo 'nome_cliente' é obrigatório."
        return db.get_pedidos_por_cliente(nome_cliente)
    except Exception as e:
        return f"❌ Erro na consulta: {str(e)}"


def get_contas_por_cliente_wrapper(nome_cliente: str) -> str:

    print(f"-------------------> input: {nome_cliente}")
    try:
        if not nome_cliente or nome_cliente.strip() == "":
            return "Erro: Campo 'nome_cliente' é obrigatório."
        return db.get_contas_por_cliente(nome_cliente)
    except Exception as e:
        return f"❌ Erro na consulta: {str(e)}"


def get_produto_estoque_wrapper(input_str: str) -> str:
    try:
        data = json.loads(input_str)
        nome_produto = data.get("produto")
        if not nome_produto:
            return "Erro: Campo 'produto' é obrigatório."
        return db.get_produto_estoque(nome_produto)
    except Exception as e:
        return f"❌ Erro na consulta: {str(e)}"


# ===== DEFINIÇÃO DAS TOOLS =====

tools = [
    # Inserção
    Tool(
        name="InserirPedido",
        description="Insere um novo pedido. Requer JSON: {\"nome_cliente\": string, \"telefone\": string, \"produtos\": lista de strings}. Ex: {\"nome_cliente\": \"João\", \"telefone\": \"11999999999\", \"produtos\": [\"floratta\"]}",
        func=insert_pedido_wrapper
    ),
    # Consulta por Filtro
    Tool(
        name="BuscarPedidosPorCliente",
        description="Busca pedidos por nome do cliente. Basta passar o nome do cliente como parâmetro para a função",
        func=get_pedidos_por_cliente_wrapper
    ),
    Tool(
        name="BuscarContasPorCliente",
        description="Busca contas por nome do cliente. Requer JSON: {\"nome_cliente\": string}. Ex: {\"nome_cliente\": \"Bruno\"}",
        func=get_contas_por_cliente_wrapper
    ),
    Tool(
        name="BuscarProdutoNoEstoque",
        description="Busca produto no estoque pelo nome. Requer JSON: {\"produto\": string}. Ex: {\"produto\": \"Batom\"}",
        func=get_produto_estoque_wrapper
    )
]