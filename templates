<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Monitoring</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

<nav>
    <a href="/">Status</a>
    <a href="/historique">Historique</a>
    <a href="/graphes">Graphiques</a>
</nav>

<div class="content">
    {% block content %}{% endblock %}
</div>
const toggleBtn = document.getElementById("theme-toggle");

// Charger le thème sauvegardé
let theme = localStorage.getItem("theme") || "dark";
document.body.className = theme;
toggleBtn.textContent = theme === "dark" ? "Mode clair" : "Mode sombre";

toggleBtn.onclick = () => {
    theme = theme === "dark" ? "light" : "dark";
    document.body.className = theme;
    localStorage.setItem("theme", theme);
    toggleBtn.textContent = theme === "dark" ? "Mode clair" : "Mode sombre";
};
</body>
</html>
<script>
    setInterval(() => {
        fetch("/tester")
    }, 30000); // toutes les 30 secondes
</script>
<button id="theme-toggle" class="theme-btn">Mode clair</button>
<a href="/overview">Résumé SRE</a>
<a href="/realtime">Graphiques temps réel</a>
<a href="/server-health">Santé du serveur</a>
<a href="/analyse">Analyse des pannes</a>
<a href="/heatmap">Heatmap</a>
<a href="/performance">Performance globale</a>
<a href="/prediction/google.com">Prédiction</a>
<a href="/categories">Catégories</a>
<a href="/anomalies">Anomalies</a>
<a href="/comparaison">Comparaison</a>
<a href="/balancing">Load Balancing</a>
<a href="/cluster">Cluster Health</a>
<a href="/network">Réseau</a>
<a href="/agent_logs">Logs Agents</a>
<a href="/topology">Topology</a>
