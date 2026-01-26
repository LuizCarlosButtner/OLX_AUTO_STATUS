import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def get_db_config(config_path='config/db_config.json'):
    """Carrega as credenciais do banco de dados do arquivo de configuração."""
    try:
        with open(config_path) as f:
            return json.load(f)['mysql']
    except FileNotFoundError:
        print(f"Erro: Arquivo de configuração '{config_path}' não encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: O arquivo de configuração '{config_path}' não é um JSON válido.")
        return None
    except KeyError:
        print(f"Erro: A chave 'mysql' não foi encontrada em '{config_path}'.")
        return None

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados MySQL."""
    config = get_db_config()
    if not config:
        return None
    
    try:
        connection = mysql.connector.connect(
            host=config.get('host'),
            user=config.get('user'),
            password=config.get('password'),
            database=config.get('database')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

class DatabaseManager:
    """Gerencia as operações do banco de dados para os anúncios da OLX."""

    def __init__(self, connection):
        """Inicializa o gerenciador com uma conexão de banco de dados."""
        if connection is None:
            raise ValueError("A conexão com o banco de dados não pode ser nula.")
        self.connection = connection
        self.cursor = connection.cursor()

    def ensure_table_exists(self):
        """Garante que a tabela 'anuncios' exista no banco de dados."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS anuncios (
                    id_anuncio VARCHAR(255) PRIMARY KEY,
                    titulo VARCHAR(255),
                    preco VARCHAR(100),
                    url TEXT,
                    data_extracao DATETIME NOT NULL
                )
            """)
            print("Tabela 'anuncios' verificada/criada com sucesso.")
        except Error as e:
            print(f"Erro ao criar a tabela 'anuncios': {e}")

    def get_existing_urls(self, urls):
        """
        Filtra uma lista de URLs, retornando um conjunto daquelas que já existem no banco.
        """
        if not urls:
            return set()
        
        try:
            placeholders = ', '.join(['%s'] * len(urls))
            sql = f"SELECT url FROM anuncios WHERE url IN ({placeholders})"
            
            self.cursor.execute(sql, tuple(urls))
            
            return {item[0] for item in self.cursor.fetchall()}
            
        except Error as e:
            print(f"Erro ao buscar URLs existentes: {e}")
            return set()

    def insert_anuncio(self, dados_anuncio):
        """Insere um novo anúncio no banco de dados."""
        if not dados_anuncio or 'id_anuncio' not in dados_anuncio:
            print("Dados do anúncio inválidos para inserção.")
            return False
            
        sql = """
            INSERT INTO anuncios (id_anuncio, titulo, preco, url, data_extracao)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            # Garante que todos os campos esperados tenham um valor
            titulo = dados_anuncio.get('titulo_principal', 'N/A')
            preco = dados_anuncio.get('preco', 'N/A')
            url = dados_anuncio.get('url', 'N/A')
            
            self.cursor.execute(sql, (
                dados_anuncio['id_anuncio'],
                titulo,
                preco,
                url,
                datetime.now()
            ))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Erro ao inserir o anúncio {dados_anuncio.get('id_anuncio')}: {e}")
            self.connection.rollback()
            return False

    def close(self):
        """Fecha o cursor e a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão com o banco de dados fechada.")
