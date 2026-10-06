"""
Tool d'analyse statistique.
Prend une série de valeurs + labels et retourne un résumé complet
"""

import statistics
from src.tools.sql_tools import get_last_result


def analyze_series(
    value_column: str,
    label_column: str,
    anomaly_threshold: float = 2.0,
) -> str:
    """
    Analyse la colonne numérique du DERNIER run_sql.
    Détecte les anomalies (au-delà de N écarts-types), calcule variations et tendances.
    
    Args:
        value_column: nom de la colonne de valeurs numériques
        label_column: nom de la colonne de labels (mois, produits...)
        anomaly_threshold: seuil en écarts-types (2.0 par défaut)
    
    Returns:
        Un résumé statistique en texte.
    """
    df = get_last_result()
    if df is None:
        return "❌ Aucune donnée. Appelle run_sql d'abord."
    if value_column not in df.columns:
        return f"❌ Colonne '{value_column}' introuvable. Dispo : {list(df.columns)}"
    if label_column not in df.columns:
        return f"❌ Colonne '{label_column}' introuvable. Dispo : {list(df.columns)}"
    
    values = df[value_column].astype(float).tolist()
    labels = df[label_column].astype(str).tolist()
    
    if len(values) < 2:
        return "❌ Pas assez de points pour analyser (< 2)."
    
    mean = statistics.mean(values)
    median = statistics.median(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0
    vmin, vmax = min(values), max(values)
    total = sum(values)
    
    lines = []
    lines.append(f"📊 ANALYSE STATISTIQUE de '{value_column}' ({len(values)} points)")
    lines.append(f"   Total      : {total:,.2f}")
    lines.append(f"   Moyenne    : {mean:,.2f}")
    lines.append(f"   Médiane    : {median:,.2f}")
    lines.append(f"   Écart-type : {stdev:,.2f}")
    lines.append(f"   Min        : {vmin:,.2f}  ({labels[values.index(vmin)]})")
    lines.append(f"   Max        : {vmax:,.2f}  ({labels[values.index(vmax)]})")
    
    # Variations vs moyenne
    lines.append("")
    lines.append(f"   Répartition vs moyenne :")
    for lbl, v in zip(labels, values):
        delta_pct = ((v - mean) / mean * 100) if mean else 0
        sign = "+" if delta_pct >= 0 else ""
        lines.append(f"     • {lbl:<20} {v:>12,.2f}   ({sign}{delta_pct:>6.1f}%)")
    
    # Anomalies
    if stdev > 0:
        anomalies = [
            (lbl, v, (v - mean) / stdev)
            for lbl, v in zip(labels, values)
            if abs((v - mean) / stdev) > anomaly_threshold
        ]
        lines.append("")
        if anomalies:
            lines.append(f"🚨 ANOMALIES détectées (seuil {anomaly_threshold}σ) :")
            for lbl, v, z in anomalies:
                lines.append(f"     • {lbl} : {v:,.2f} (z = {z:+.2f})")
        else:
            lines.append(f"✅ Aucune anomalie (seuil {anomaly_threshold}σ).")
    
    # Tendance (régression linéaire simple)
    n = len(values)
    x_mean = (n - 1) / 2
    num = sum((i - x_mean) * (v - mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den else 0
    direction = "croissante ↗" if slope > 0 else "décroissante ↘" if slope < 0 else "stable →"
    lines.append("")
    lines.append(f"📈 Tendance globale : {direction} (pente {slope:+,.2f} / période)")
    
    return "\n".join(lines)


ANALYSIS_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_series",
            "description": (
                "Analyse statistique d'une colonne numérique issue du DERNIER run_sql. "
                "Calcule moyenne, médiane, écart-type, min, max, variations vs moyenne, "
                "détecte les anomalies (points au-delà de N écarts-types) et la tendance. "
                "À utiliser SYSTÉMATIQUEMENT après un run_sql quand la question porte sur "
                "une évolution, une comparaison ou une détection d'anomalie."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "value_column": {
                        "type": "string",
                        "description": "Nom de la colonne numérique à analyser (ex: 'revenue').",
                    },
                    "label_column": {
                        "type": "string",
                        "description": "Nom de la colonne de labels (ex: 'month', 'name').",
                    },
                    "anomaly_threshold": {
                        "type": "number",
                        "description": "Seuil d'anomalie en écarts-types (défaut 2.0).",
                    },
                },
                "required": ["value_column", "label_column"],
            },
        },
    },
]