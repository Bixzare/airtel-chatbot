#!/usr/bin/env python3
"""
Script de démarrage optimisé pour le serveur avec préchargement des documents.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv
load_dotenv()

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log')
    ]
)
logger = logging.getLogger(__name__)


def check_environment():
    """Vérifier la configuration de l'environnement."""
    logger.info("🔍 Vérification de l'environnement...")

    required_vars = ['GOOGLE_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"❌ Variables d'environnement manquantes: {missing_vars}")
        logger.error(
            "Veuillez configurer ces variables dans votre fichier .env")
        return False

    logger.info("✅ Configuration de l'environnement OK")
    return True


def check_documents():
    """Vérifier la présence du document statique."""
    logger.info("📄 Vérification du document statique...")

    document_path = "src/rag/static_document.txt"

    if os.path.exists(document_path):
        logger.info(f"✅ Document trouvé: {document_path}")
        return True
    else:
        logger.warning(f"⚠️ Document non trouvé: {document_path}")
        logger.error("❌ Document statique non trouvé!")
        return False


def preload_documents():
    """Précharger les documents pour optimiser les performances."""
    logger.info("🚀 Démarrage du préchargement des documents...")

    try:
        # Import après vérification de l'environnement
        from src.agent.rag_agent import LangGraphRAGAgent
        from src.memory.checkpointer import Checkpointer
        from src.config.settings import Settings

        start_time = time.time()

        # Initialisation des composants
        settings = Settings()
        checkpointer = Checkpointer(db_path=settings.checkpoint_db_path)

        # Chemin du document
        document_path = os.environ.get(
            "DOCUMENT_PATH", "src/rag/static_document.txt")
        model_name = os.environ.get("MODEL_NAME", "gemini-1.5-flash")

        # Vérifier le document
        if not os.path.exists(document_path):
            logger.error("❌ Document à précharger non trouvé!")
            return False

        # Initialiser l'agent avec document unique
        agent = LangGraphRAGAgent(
            document_path=document_path,
            model_name=model_name,
            checkpointer=checkpointer
        )

        # Test de requête pour réchauffer le système
        logger.info("🔥 Test de requête pour réchauffer le système...")
        test_query = "Airtel Niger services"
        agent.rag_tool(test_query)  # Warm up the system

        preload_time = time.time() - start_time
        logger.info(f"✅ Préchargement terminé en {preload_time:.2f} secondes")
        logger.info(f"📊 {agent.rag_tool.num_chunks} chunks chargés")
        logger.info(f"💾 Cache activé: {agent.rag_tool.cache is not None}")

        return True

    except Exception as e:
        logger.error(f"❌ Erreur lors du préchargement: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def start_server():
    """Démarrer le serveur FastAPI."""
    logger.info("🌐 Démarrage du serveur FastAPI...")

    try:
        import uvicorn

        # Configuration du serveur
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0" if os.environ.get("VERCEL") else "127.0.0.1"

        logger.info(f"🚀 Serveur démarré sur {host}:{port}")
        logger.info("📝 Logs disponibles dans server.log")

        # Démarrer le serveur
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )

    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage du serveur: {str(e)}")
        return False


def main():
    """Fonction principale."""
    logger.info("🎯 Démarrage du serveur Airtel Chatbot avec préchargement...")

    # Vérifications préliminaires
    if not check_environment():
        sys.exit(1)

    if not check_documents():
        logger.warning("⚠️ Continuation sans documents statiques...")

    # Préchargement des documents
    if not preload_documents():
        logger.warning(
            "⚠️ Préchargement échoué, continuation sans optimisation...")

    # Démarrage du serveur
    start_server()


if __name__ == "__main__":
    main()
