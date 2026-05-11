import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def main() -> None:
    # Carrega variáveis do arquivo env na raiz do projeto
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "env"))

    mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError(
            "Variável MONGODB_URI ou MONGO_URI não encontrada. Verifique o arquivo 'env' ou o ambiente."
        )

    print("Tentando conectar ao MongoDB...")

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("Conexão com MongoDB bem-sucedida!")
        print(f"URI usada: {mongo_uri}")
    except PyMongoError as error:
        print("Falha ao conectar ao MongoDB:")
        print(error)
        raise
    finally:
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
