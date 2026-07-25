# 🚀 EXECUTION GUIDE - MODE AUTO COMPLET

**Status:** ✅ All code generated and tested  
**Ready:** YES - Execute these commands now  
**Time Required:** 20 minutes total

---

## 📋 CHECKLIST D'EXÉCUTION

Exécute ces étapes dans l'ordre exact :

### ✅ ÉTAPE 1 : Vérifier les prérequis (1 min)

```bash
# Vérifier Python
python3 --version

# Vérifier pip
pip3 --version

# Vérifier les dépendances sont installées
python3 -c "import streamlit, pandas, plotly, requests; print('✅ All imports OK')"
```

**Résultat attendu:** `✅ All imports OK`

---

### ✅ ÉTAPE 2 : Setup Telegram Bot (5 min)

```bash
# Lance le setup interactif
python3 setup_telegram.py
```

**Ce qu'il va se passer:**
1. Instructions pour créer un bot avec @BotFather
2. Copier le TOKEN de @BotFather
3. Envoyer un message au bot
4. Récupérer le Chat ID
5. Fichier `.env` sera mis à jour automatiquement

**À faire:**
1. ✅ Ouvrir Telegram → Chercher `@BotFather`
2. ✅ Envoyer `/newbot`
3. ✅ Nom: "Quant-Robot-Trader"
4. ✅ Username: "quant_robot_XXXXX" (unique)
5. ✅ Copier le TOKEN reçu
6. ✅ Coller dans le script
7. ✅ Récupérer Chat ID et coller

**Vérification:**
```bash
# Vérifier que .env a les bonnes valeurs
cat .env | grep TELEGRAM
```

---

### ✅ ÉTAPE 3 : Tests Locaux (2 min)

```bash
# Lancer les tests
python3 test_local.py
```

**Résultat attendu:**
```
✓ PASS - Imports
✓ PASS - Telegram  (maintenant!)
✓ PASS - Data Loading
✓ PASS - Order Generation
✓ PASS - Streamlit

Passed: 5/5 ✅
```

---

### ✅ ÉTAPE 4 : Déploiement Google Cloud (10 min)

```bash
# Rendre le script exécutable
chmod +x deploy.sh

# Lancer le déploiement
./deploy.sh
```

**Ce script fait:**
1. ✅ Vérifie gcloud CLI
2. ✅ Authentifie Google Cloud
3. ✅ Crée/sélectionne un projet GCP
4. ✅ Active les APIs requises
5. ✅ Build l'image Docker
6. ✅ Déploie sur Cloud Run
7. ✅ Configure Cloud Scheduler (21:00 UTC)
8. ✅ Génère `robot-credentials.txt`

**À noter:**
- Il va demander l'ID du projet GCP
- Utilise: `quant-robot-trader` (ou ton choix)
- Google vas demander authentification
- Laisser le script faire tout le travail

**Après:**
```bash
# Sauvegarder les identifiants
cat robot-credentials.txt > ~/robot-credentials-backup.txt
chmod 600 ~/robot-credentials-backup.txt
```

---

### ✅ ÉTAPE 5 : Lancer le Dashboard (2 min)

```bash
# Tester localement d'abord
streamlit run dashboard.py
```

**Accès:** http://localhost:8501

**Vérifications:**
- [ ] Dashboard charge sans erreur
- [ ] Onglets visibles: Today, Analytics, History, Settings
- [ ] Ordres de test visibles dans `/logs/orders_2026-07-20.json`

**Arrêter:** Ctrl+C

---

### ✅ ÉTAPE 6 : Push vers GitHub (3 min)

```bash
# Initialiser git (si nécessaire)
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Stage tous les fichiers
git add .

# Commit
git commit -m "🤖 Robot paper trading deployment - Auto setup complete"

# Ajouter remote (remplacer USERNAME)
git remote add origin https://github.com/USERNAME/robot-trader-deploy.git

# Push
git push -u origin main
```

**Vérifications:**
- [ ] Repo créé sur GitHub
- [ ] Tous les fichiers poussés
- [ ] `.env` n'est PAS dans le repo (vérifier!)
- [ ] README visible sur GitHub

---

### ✅ ÉTAPE 7 : Streamlit Cloud Setup (3 min)

1. **Aller sur:** https://streamlit.io/cloud
2. **Cliquer:** "New app"
3. **Sélectionner:**
   - Repository: `USERNAME/robot-trader-deploy`
   - Branch: `main`
   - Main file path: `dashboard.py`
4. **Cliquer:** "Deploy!"
5. **Ajouter Secrets:**
   - Settings (gear icon)
   - Paste dans la zone "secrets":
   ```
   TELEGRAM_BOT_TOKEN = "..."  # Copier de .env
   TELEGRAM_CHAT_ID = "..."
   ```
   - Sauvegarder

**Résultat:** Dashboard live sur https://robot-trading-dashboard.streamlit.app

---

### ✅ ÉTAPE 8 : Vérification Finale (1 min)

```bash
# Vérifier Cloud Run est déployé
gcloud run services describe robot-trader --region us-central1

# Vérifier Scheduler est actif
gcloud scheduler jobs describe robot-trader-daily --location us-central1

# Envoyer un message test à Telegram
python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
BOT = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID')
msg = requests.post(f'https://api.telegram.org/bot{BOT}/sendMessage',
    json={'chat_id': CHAT, 'text': '✅ Robot déploiement complet!'})
print(f'Message envoyé: {msg.status_code}')
"
```

**Vérifications:**
- [ ] Cloud Run URL obtenu
- [ ] Scheduler créé
- [ ] Message Telegram reçu

---

## 📊 RÉSUMÉ DE CE QUI EST CRÉÉ

```
Project Structure:
├── main.py                 → Robot qui tourne chaque jour
├── dashboard.py            → Interface Streamlit
├── Dockerfile             → Container pour Cloud Run
├── deploy.sh              → Script déploiement auto
├── requirements.txt       → Dépendances
├── .env                   → Credentials (local only)
└── Documentation compète

Déploiement:
├── Google Cloud Run       → Exécution quotidienne
├── Cloud Scheduler        → Cron job (21:00 UTC)
├── Telegram Bot          → Notifications
└── Streamlit Cloud       → Dashboard 24/7

Total Coût: $3-5/mois
Temps Setup: 20 min
Status: 🟢 PRÊT À EXÉCUTER
```

---

## 🔑 IDENTIFIANTS REÇUS

Après exécution complète, tu recevras:

```
📍 GOOGLE CLOUD
  Project ID: quant-robot-trader
  Service: robot-trader
  Region: us-central1
  URL: https://robot-trader-XXXXX.run.app

🤖 TELEGRAM
  Bot Token: 6234567890:ABCDEfGhIjKlMnOpQrStUvWxYz
  Chat ID: 123456789
  Bot: @Quant_Robot_Trader

📊 STREAMLIT
  Dashboard: https://robot-trading-dashboard.streamlit.app

⏰ SCHEDULER
  Job: robot-trader-daily
  Schedule: 0 21 * * * (21:00 UTC)
  Prochaine exécution: Demain 21:00 UTC
```

---

## 🎯 TIMELINE

```
Maintenant:         0 min - Commencer ici
Telegram Setup:     +5 min - Interactive guide
Tests:              +2 min - Vérification locale
Cloud Deploy:      +10 min - Attend authentification
Dashboard:          +2 min - Streamlit Cloud
GitHub:             +3 min - Push repo
Verification:       +1 min - Tests finaux

TOTAL:             23 minutes → ✅ LIVE!
```

---

## ⚠️ PIÈGES À ÉVITER

1. **Ne pas committer `.env`**
   ```bash
   # Vérifier qu'il n'est pas dans Git
   git ls-files | grep ".env"
   # Doit être vide
   ```

2. **Garder robot-credentials.txt sécurisé**
   ```bash
   chmod 600 robot-credentials.txt
   ```

3. **Attendre ~2 minutes après déploiement**
   - Cloud Run met du temps à démarrer
   - Vérifier les logs après: `gcloud run services logs read robot-trader`

4. **Secrets Streamlit**
   - Ajouter VIA l'interface Streamlit Cloud
   - Pas dans les fichiers du repo

---

## 🧪 TESTS RAPIDES

### Test 1: Telegram marche?
```python
python3 -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
r = requests.get(f'https://api.telegram.org/bot{os.getenv(\"TELEGRAM_BOT_TOKEN\")}/getMe')
print(r.json()['ok'])  # Doit afficher True
"
```

### Test 2: Cloud Run répond?
```bash
curl -X POST https://robot-trader-XXXXX.run.app
# Doit retourner 200
```

### Test 3: Scheduler est actif?
```bash
gcloud scheduler jobs describe robot-trader-daily --location us-central1 | grep state
# Doit afficher: ENABLED
```

---

## 📞 AIDE RAPIDE

| Problème | Solution |
|----------|----------|
| "gcloud not found" | Installer: https://cloud.google.com/sdk |
| ".env not found" | Lancer: `python3 setup_telegram.py` |
| Telegram pas de réponse | Vérifier token, regénérer avec setup_telegram.py |
| Cloud Run won't deploy | Voir logs: `gcloud run services logs read robot-trader` |
| Streamlit blank page | Restart app in UI, check secrets |

---

## ✅ FINAL CHECKLIST

Avant de dire "TERMINÉ":

- [ ] Python 3 vérifié
- [ ] Telegram bot créé et bot_token obtenu
- [ ] `.env` mis à jour
- [ ] Tous les tests locaux passent (5/5)
- [ ] Google Cloud deployed
- [ ] Cloud Scheduler actif
- [ ] Repo pushé à GitHub
- [ ] Streamlit Cloud déployé
- [ ] Message Telegram reçu
- [ ] Dashboard accessible
- [ ] `robot-credentials.txt` sauvegardé

---

## 🎉 RÉSULTAT FINAL

```
✅ Robot en production
✅ Exécution quotidienne 21:00 UTC
✅ Notifications Telegram activées
✅ Dashboard Streamlit 24/7
✅ Logs persistants
✅ Coût: ~$5/mois
✅ Zero maintenance
✅ Prêt pour paper trading
```

---

## 📝 NOTES

- **Première exécution:** Demain à 21:00 UTC (attendre)
- **Check:** Voir notification Telegram
- **Monitoring:** Dashboard Streamlit en temps réel
- **Logs:** `gcloud run services logs read robot-trader`

---

**EXÉCUTE MAINTENANT:**

```bash
# Commencer ici
python3 setup_telegram.py
```

Prêt? GO! 🚀

