
---

```markdown
# 📊 AI Data Analyst Agent

> Un agent IA qui répond à des questions métier en langage naturel en interrogeant une base de données, en générant du SQL, en produisant des graphiques et en détectant des anomalies.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Aperçu

Posez une question, l'agent fait le reste :

> **« Quels produits ont généré le plus de revenus en 2025 ? »**

→ Il explore le schéma, écrit la requête SQL, l'exécute, analyse les résultats, génère un graphique et rédige une synthèse avec les chiffres clés.

**Fonctionnalités** :
- 🧠 Compréhension du langage naturel
- 🛠️ Génération et exécution de SQL (DuckDB)
- 📈 Graphiques automatiques (bar, line, pie, scatter)
- 🧮 Statistiques et détection d'anomalies
- 💬 Mémoire conversationnelle (questions de suivi)
- 🔄 **Deux moteurs d'agent interchangeables** : boucle ReAct manuelle ou LangGraph
- 🎨 Interface Streamlit

---

## 🚀 Démarrage rapide

```bash
# 1. Cloner
git clone https://github.com/IbrahimFaye/d-tection-de-propos-haineux
cd ai-data-analyst-agent

# 2. Environnement virtuel
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac / Linux

# 3. Dépendances
pip install -r requirements.txt

# 4. Clé API Groq (gratuite) → https://console.groq.com/keys
cp .env.example .env
# Éditez .env et collez votre GROQ_API_KEY

# 5. Générer le dataset de démonstration
python src/data/setup_db.py

# 6. Lancer l'app
streamlit run src/ui/app.py
```

Ouvrez [http://localhost:8501](http://localhost:8501) et posez votre première question.

---

## 🎮 Exemples de questions

```
• Quels sont les top 3 produits en 2024 ?
• Évolution du CA mensuel en 2024 avec un graphique.
• Y a-t-il des anomalies dans les ventes ?
• Compare 2023 et 2024 par catégorie.
• Quels sont mes meilleurs clients VIP ?
```

---

## 🏗️ Architecture

```
Interface (Streamlit)
        ↓
Orchestration (boucle ReAct / LangGraph)
        ↓
Tools (SQL · Plot · Analysis)
        ↓
Données (DuckDB)
        ↓
LLM (Groq · gpt-oss-120b)
```

Chaque couche est indépendante et testable.

---

## 🛠️ Les outils de l'agent

| Outil | Rôle |
|-------|------|
| `list_tables()` | Découvrir les tables disponibles |
| `describe_table(name)` | Voir les colonnes d'une table |
| `run_sql(query)` | Exécuter une requête SQL (read-only) |
| `plot_chart(kind, x, y, title)` | Générer un graphique |
| `analyze_series(value, label)` | Stats + anomalies + tendance |

---

## 🧠 Manuel vs LangGraph

L'app permet de basculer entre deux implémentations :

| | Manuel | LangGraph |
|--|--------|-----------|
| **Latence** | Référence | +5-15% |
| **Visualisation du graphe** | ❌ | ✅ |
| **Parallélisation des tools** | ❌ | ✅ |
| **Human-in-the-loop** | ❌ | ✅ |
| **Compréhension interne** | ✅ | Partielle |

Idéal pour **comparer** les deux approches en direct.

---

## 📂 Structure

```
ai-data-analyst-agent/
├── src/
│   ├── llm/          # Wrapper Groq + system prompt
│   ├── tools/        # SQL, plot, analysis
│   ├── agent/        # loop.py (manuel) + graph.py (LangGraph)
│   ├── data/         # Génération du dataset
│   └── ui/           # Interface Streamlit
├── tests/            # Un test par brique
├── data/             # Base DuckDB
└── outputs/          # Graphiques générés
```

---

## 🔬 Tests

```bash
python tests/test_agent.py           # Boucle ReAct
python tests/test_self_healing.py    # Auto-correction
python tests/test_memory.py          # Mémoire
python tests/test_langgraph.py       # Comparaison manuel vs LangGraph
```

---

## 📦 Stack technique

- **LLM** : Groq (`gpt-oss-120b`)
- **Base de données** : DuckDB
- **UI** : Streamlit
- **Orchestration** : Python natif + LangGraph
- **Visualisation** : Matplotlib

---
