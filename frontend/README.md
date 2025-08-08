# Airtel Chatbot - Frontend

Interface utilisateur Next.js pour le chatbot Airtel Niger avec RAG (Retrieval-Augmented Generation).

## 🚀 Quick Start

```bash
# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

Ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur.

## 📚 Documentation complète

Pour une documentation détaillée, consultez le dossier [`../docs/`](../docs/) :

- [Guide de démarrage rapide](../docs/getting-started.md)
- [Configuration du streaming](../docs/configuration/streaming.md)
- [Déploiement local](../docs/deployment/local.md)
- [Problèmes courants](../docs/troubleshooting/common-issues.md)

## 🔧 Features

- **Interface moderne** avec Next.js 14 et App Router
- **Chat en temps réel** avec le backend RAG
- **Design responsive** optimisé mobile/desktop
- **Thème sombre/clair** automatique
- **Gestion des sessions** persistante
- **Streaming optionnel** des réponses

## 🎨 Technologies

- **Next.js 14** - Framework React
- **TypeScript** - Typage statique
- **Tailwind CSS** - Styling
- **shadcn/ui** - Composants UI
- **Lucide React** - Icônes

## 📁 Structure

```
frontend/
├── app/                 # Pages et API routes
│   ├── api/            # API routes Next.js
│   └── page.tsx        # Page principale
├── components/         # Composants React
│   ├── chat/          # Composants de chat
│   ├── ui/            # Composants UI
│   └── theme/         # Gestion du thème
└── lib/               # Utilitaires
```
