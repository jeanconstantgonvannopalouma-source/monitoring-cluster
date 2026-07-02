# 🔥 Cluster SRE – Monitoring Distribué, Alertes, Autoscaling, Dashboard Temps Réel

Un cluster de monitoring **professionnel**, entièrement codé en Python + Flask, capable de :

- surveiller des sites web en continu  
- distribuer la charge entre plusieurs agents  
- détecter les anomalies (spikes, latence élevée, instabilité)  
- envoyer des alertes Email + Telegram  
- autoscaler automatiquement selon la charge  
- analyser le réseau entre agents  
- afficher un dashboard complet :  
  - Overview  
  - Graphes  
  - Cluster Map  
  - Realtime  
  - Logs  
  - History  
  - Sites  
  - Settings  

Ce projet reproduit les fonctionnalités d’un vrai système SRE / DevOps (Grafana, Datadog, Prometheus).

---

## 🚀 Fonctionnalités principales

### ✔ Monitoring distribué
Chaque agent teste des sites et remonte :
- statut UP/DOWN  
- latence  
- erreurs HTTP  
- anomalies  

### ✔ Alertes intelligentes
Envoi automatique :
- Email  
- Telegram  
- Historique  
- Logs  

Pour :
- site DOWN  
- agent DOWN  
- réseau DOWN  
- spike de latence  
- CPU/RAM élevées  
- autoscaling UP/DOWN  

### ✔ Autoscaling dynamique
Le cluster ajuste automatiquement :
- l’intervalle de monitoring  
- la charge des agents  

### ✔ Dashboard complet
Pages disponibles :
- `/overview`  
- `/graphes`  
- `/cluster-map`  
- `/realtime`  
- `/sites`  
- `/settings`  
- `/logs`  
- `/history`  

### ✔ Historique complet
Tous les événements sont enregistrés dans :
- `logs.jsonl`  
- `history.jsonl`  

---

## 📦 Installation

### 1. Cloner le projet
```bash
git clone https://github.com/votre-repo/cluster-sre.git
cd cluster-sre
