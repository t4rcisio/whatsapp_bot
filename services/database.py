import sqlite3
from datetime import datetime

import sqlite3
from datetime import datetime
import json
import os

os.makedirs(".\\database", exist_ok=True)

class LojaDB:

    def __init__(self):

        db_name = ".\\database\\loja.db"

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        #self.populate_tables()

    def create_tables(self):
        # Criação da tabela Pedidos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_cliente TEXT,
                telefone TEXT,
                produtos TEXT,
                status TEXT
            )
        ''')

        # Criação da tabela Contas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_cliente TEXT,
                conta REAL,
                vencimento TEXT,
                data TEXT
            )
        ''')

        # Criação da tabela Estoque
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto TEXT,
                descricao TEXT,
                preco REAL,
                preco_promocional REAL
            )
        ''')
        self.conn.commit()

    def insert_pedido(self, nome_cliente, telefone, produtos, status="EM PROCESSAMENTO"):

        if telefone == '33988955154':
            return f"ESSE É O TELEFONE DA LOJA ! NÃO PODE CRIAR PEDIDOS COM ESSE TELEFONE"

        produtos_str = ', '.join(produtos)

        # Verificar se já existe pedido igual
        self.cursor.execute('''
                SELECT id FROM Pedidos 
                WHERE nome_cliente = ? AND telefone = ? AND produtos = ? AND status = ?
            ''', (nome_cliente, telefone, produtos_str, status))

        pedido_existente = self.cursor.fetchone()

        if pedido_existente:
            return f"⚠️ Já existe um pedido idêntico registrado (ID: {pedido_existente[0]})."


        self.cursor.execute('''
            INSERT INTO Pedidos (nome_cliente, telefone, produtos, status)
            VALUES (?, ?, ?, ?)
        ''', (nome_cliente, telefone, produtos_str, status))
        self.conn.commit()

        return f"✅ Pedido inserido com sucesso para {nome_cliente}."

    def insert_conta(self, nome_cliente, conta, vencimento, data=None):
        if data is None:
            data = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
            INSERT INTO Contas (nome_cliente, conta, vencimento, data)
            VALUES (?, ?, ?, ?)
        ''', (nome_cliente, conta, vencimento, data))
        self.conn.commit()

    def insert_estoque(self, produto, descricao, preco, preco_promocional=None):
        self.cursor.execute('''
            INSERT INTO Estoque (produto, descricao, preco, preco_promocional)
            VALUES (?, ?, ?, ?)
        ''', (produto, descricao, preco, preco_promocional))
        self.conn.commit()

    # ============ FUNÇÕES DE CONSULTA ============

    def get_pedidos(self):
        """Retorna todos os pedidos como string formatada."""
        self.cursor.execute("SELECT id, nome_cliente, telefone, produtos, status FROM Pedidos")
        rows = self.cursor.fetchall()
        if not rows:
            return "Não há pedidos cadastrados."
        result = "=== PEDIDOS ===\n"
        for row in rows:
            result += f"ID: {row[0]} | Cliente: {row[1]} | Tel: {row[2]} | Status: {row[4]} | Produtos: {row[3]}\n"
        return result.strip()

    def get_contas(self):
        """Retorna todas as contas como string formatada."""
        self.cursor.execute("SELECT id, nome_cliente, conta, vencimento, data FROM Contas")
        rows = self.cursor.fetchall()
        if not rows:
            return "Resposta do banco de dados: Não há contas cadastradas."
        result = "=== CONTAS ===\n"
        for row in rows:
            result += f"ID: {row[0]} | Cliente: {row[1]} | Valor: R${row[2]:.2f} | Vencimento: {row[3]} | Data Registro: {row[4]}\n"
        return result.strip()

    def get_estoque(self):
        """Retorna todos os produtos em estoque como string formatada."""
        self.cursor.execute("SELECT id, produto, descricao, preco, preco_promocional FROM Estoque")
        rows = self.cursor.fetchall()
        if not rows:
            return "Resposta do banco de dados: Não há produtos no estoque."
        result = "=== ESTOQUE ===\n"
        for row in rows:
            promo = f" (PROMO: R${row[4]:.2f})" if row[4] else ""
            result += f"ID: {row[0]} | Produto: {row[1]} | Desc: {row[2]} | Preço: R${row[3]:.2f}{promo}\n"
        return result.strip()

    def get_pedidos_por_cliente(self, nome_cliente):
        """Busca pedidos por nome do cliente."""
        self.cursor.execute(
            "SELECT id, nome_cliente, telefone, produtos, status FROM Pedidos WHERE nome_cliente LIKE ?",
            (f'%{nome_cliente}%',)
        )
        rows = self.cursor.fetchall()
        if not rows:
            return f"Resposta do banco de dados: Não há pedidos para {nome_cliente}."
        result = f"=== PEDIDOS PARA CLIENTE '{nome_cliente}' ===\n"
        for row in rows:
            result += f"ID: {row[0]} | Cliente: {row[1]} | Tel: {row[2]} | Status: {row[4]} | Produtos: {row[3]}\n"
        return result.strip()

    def get_contas_por_cliente(self, nome_cliente):
        """Busca contas por nome do cliente."""
        self.cursor.execute(
            "SELECT id, nome_cliente, conta, vencimento, data FROM Contas WHERE nome_cliente LIKE ?",
            (f'%{nome_cliente}%',)
        )
        rows = self.cursor.fetchall()
        if not rows:
            return f"Resposta do banco de dados: Não há contas para {nome_cliente}."
        result = f"=== CONTAS PARA CLIENTE '{nome_cliente}' ===\n"
        for row in rows:
            result += f"ID: {row[0]} | Cliente: {row[1]} | Valor: R${row[2]:.2f} | Vencimento: {row[3]} | Data Registro: {row[4]}\n"
        return result.strip()

    def get_produto_estoque(self, nome_produto):
        """Busca produto no estoque pelo nome."""
        self.cursor.execute(
            "SELECT id, produto, descricao, preco, preco_promocional FROM Estoque WHERE produto LIKE ?",
            (f'%{nome_produto}%',)
        )
        rows = self.cursor.fetchall()
        if not rows:
            return f"Resposta do banco de dados: Não há produto '{nome_produto}' no estoque."
        result = f"=== RESULTADO DA BUSCA POR '{nome_produto}' ===\n"
        for row in rows:
            promo = f" (PROMO: R${row[4]:.2f})" if row[4] else ""
            result += f"ID: {row[0]} | Produto: {row[1]} | Desc: {row[2]} | Preço: R${row[3]:.2f}{promo}\n"
        return result.strip()

    def fetch_all(self, table):
        self.cursor.execute(f"SELECT * FROM {table}")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def populate_tables(self):
        # Populando Estoque
        produtos = [
            ("Batom Matte Ruby Rose", "Batom com acabamento matte e longa duração", 19.90, 14.90),
            ("Creme Facial Nivea 50g", "Hidratação profunda para pele seca", 24.90, 19.90),
            ("Perfume Chanel No.5", "Fragrância clássica feminina", 399.90, 359.90),
            ("Shampoo Seda Brilho Extremo", "Shampoo para cabelos opacos", 12.90, 9.90),
            ("Esmalte Risqué Cremoso", "Esmalte vermelho cremoso", 7.90, 5.90),
            ("Loção Hidratante Dove 200ml", "Hidratação diária para pele macia", 18.90, 15.90),
            ("Paleta de Sombras Ruby Rose", "12 cores neutras e vibrantes", 39.90, 29.90)
        ]
        for p in produtos:
            self.insert_estoque(*p)

        # Populando Pedidos
        pedidos = [
            ("Ana Silva", "31987654321", ["Batom Matte Ruby Rose", "Esmalte Risqué Cremoso"], "ENVIADO"),
            ("Bruno Costa", "31991234567", ["Perfume Chanel No.5", "Loção Hidratante Dove 200ml"], "EM SEPARAÇÃO"),
            ("Carla Souza", "31999887766", ["Paleta de Sombras Ruby Rose", "Creme Facial Nivea 50g"], "AGUARDANDO PAGAMENTO")
        ]
        for p in pedidos:
            self.insert_pedido(*p)

        # Populando Contas
        contas = [
            ("Ana Silva", 55.80, "2025-09-10"),
            ("Bruno Costa", 374.80, "2025-09-15"),
            ("Carla Souza", 64.80, "2025-09-12")
        ]
        for c in contas:
            self.insert_conta(*c)

# Exemplo de uso
def create():
    db = LojaDB()
    #db.populate_tables()
    print("Estoque:")
    for item in db.fetch_all("Estoque"):
        print(item)
    print("\nPedidos:")
    for pedido in db.fetch_all("Pedidos"):
        print(pedido)
    print("\nContas:")
    for conta in db.fetch_all("Contas"):
        print(conta)
    db.close()






