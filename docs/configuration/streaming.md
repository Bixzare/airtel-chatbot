# Configuration du Streaming - Airtel Chatbot

## État actuel : Streaming désactivé

Le streaming a été désactivé dans l'application mais le code est conservé pour permettre une réactivation facile.

## Modifications apportées

### 1. Frontend (`frontend/components/chat/chat.tsx`)

- **Fonction par défaut** : `handleSend()` utilise maintenant `handleSendNonStreaming()`
- **Code streaming conservé** : `handleSendStreaming()` reste disponible mais n'est pas utilisée
- **Commentaires explicatifs** : Ajout de commentaires pour clarifier l'état et comment réactiver

### 2. API Route (`frontend/app/api/chat/route.ts`)

- **Gestion du paramètre `stream`** : L'API route gère déjà correctement `stream: false`
- **Endpoint non-streaming** : Utilise l'endpoint `/chat` au lieu de `/chat/stream`

## Comment réactiver le streaming

### Option 1 : Réactivation simple

Dans `frontend/components/chat/chat.tsx`, ligne ~160, changez :

```typescript
const handleSend = async () => {
  // STREAMING DISABLED - Using non-streaming endpoint
  // To re-enable streaming, change this line to: await handleSendStreaming();
  await handleSendNonStreaming();
};
```

Par :

```typescript
const handleSend = async () => {
  // STREAMING ENABLED
  await handleSendStreaming();
};
```

### Option 2 : Réactivation conditionnelle

Vous pouvez aussi ajouter une variable d'environnement pour contrôler le streaming :

```typescript
const handleSend = async () => {
  const useStreaming = process.env.NEXT_PUBLIC_ENABLE_STREAMING === 'true';
  if (useStreaming) {
    await handleSendStreaming();
  } else {
    await handleSendNonStreaming();
  }
};
```

## Avantages de la désactivation

1. **Réponses plus stables** : Pas de problèmes de troncature de texte
2. **Meilleure gestion des erreurs** : Réponses complètes ou erreurs claires
3. **Performance** : Moins de complexité côté client
4. **Compatibilité** : Fonctionne mieux avec certains navigateurs/proxies

## Avantages du streaming

1. **Expérience utilisateur** : Réponses en temps réel
2. **Perception de vitesse** : L'utilisateur voit la réponse se construire
3. **Feedback immédiat** : L'utilisateur sait que le système fonctionne

## Backend

Le backend supporte toujours les deux modes :
- `/chat` : Endpoint non-streaming
- `/chat/stream` : Endpoint streaming

Aucune modification backend n'est nécessaire pour basculer entre les modes.

## Configuration avancée

### Variables d'environnement

```bash
# Frontend (.env.local)
NEXT_PUBLIC_ENABLE_STREAMING=true

# Backend (.env)
STREAMING_ENABLED=true
STREAMING_CHUNK_SIZE=100
```

### Paramètres de streaming

```typescript
// Configuration du streaming côté frontend
const streamingConfig = {
  chunkSize: 100,
  delay: 50,
  maxRetries: 3,
  timeout: 30000
};
```

## Dépannage du streaming

### Problème : Réponses tronquées
```typescript
// Solution : Augmenter le buffer de réception
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message, session_id }),
  signal: AbortSignal.timeout(60000) // 60s timeout
});
```

### Problème : Connexion interrompue
```typescript
// Solution : Implémenter un retry automatique
const retryStreaming = async (fn: () => Promise<any>, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

### Problème : Performance dégradée
```typescript
// Solution : Optimiser le traitement des chunks
const processChunk = (chunk: string) => {
  // Traitement minimal pour éviter les blocages
  return chunk.trim();
};
```

## Métriques de streaming

### Endpoints de monitoring
```bash
# Métriques de streaming
curl http://localhost:8000/streaming-metrics

# Statistiques de performance
curl http://localhost:8000/performance | jq '.streaming'
```

### Logs de streaming
```
2024-01-15 10:30:15 - INFO - Streaming started for session abc123
2024-01-15 10:30:16 - INFO - Chunk sent: "Bonjour, je peux vous aider"
2024-01-15 10:30:17 - INFO - Streaming completed for session abc123
```

## Recommandations

### Quand utiliser le streaming
- **Utilisateurs finaux** : Pour une meilleure UX
- **Développement** : Pour tester les performances
- **Démo** : Pour montrer les capacités en temps réel

### Quand désactiver le streaming
- **Production critique** : Pour la stabilité
- **Réseaux instables** : Pour éviter les interruptions
- **Compatibilité** : Pour supporter tous les navigateurs

## Migration entre modes

### De streaming vers non-streaming
1. Modifier `handleSend()` dans `chat.tsx`
2. Tester les réponses complètes
3. Vérifier la gestion d'erreurs

### De non-streaming vers streaming
1. Activer le streaming dans `chat.tsx`
2. Tester la réception des chunks
3. Implémenter la gestion d'erreurs
4. Optimiser les performances

## Tests de streaming

### Test manuel
```bash
# Test avec curl
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "Bonjour"}'
```

### Test automatisé
```typescript
// Test de streaming côté frontend
const testStreaming = async () => {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Test', session_id: 'test' })
  });
  
  const reader = response.body?.getReader();
  let result = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    result += new TextDecoder().decode(value);
  }
  
  return result;
};
```
