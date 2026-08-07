# Parvotec · AAV Capsid ML — Knowledge Snippets
Generated: 2026-08-06 | Sources: DOCX files from `Machine learning for Rupert`

---

## 1. Das Parvotec-Projekt (Final description AIML Parvotec.docx)

### Ziel
- AAV capsid mit **neuronal tropism + retrograde transport** für nociceptive Peripheral Neurons (Schmerztherapie)
- Multi-objektive Optimierung: Manufacturability + Transduction efficiency + Cell-type specificity + Cross-species function

### Kernproblem
> "Optimizing for one metric — such as neuronal tropism — can inadvertently decrease another, like packaging efficiency or increase immunogenicity."

### ML-Framework: 4-Schichten-Architektur

| Schicht | Technologie | Aufgabe |
|---|---|---|
| Embedding | **ESM-2** (Protein Language Model) | Sequenz → context-aware Vektor |
| Predictor | **Multi-task supervised NN** | Gleichzeitige Vorhersage aller Eigenschaften (Fitness Oracle) |
| Generator | **cVAE** (conditional Variational Autoencoder) | Neue Sequenzen generieren die auf Ziel-Properties konditioniert sind |
| Optimizer | **Multi-objective Bayesian Optimization** | Pareto-optimale Kandidaten, balanciert Exploration vs. Exploitation |

### Iterativer Workflow
1. **Round 1 (Seeding):** Großes Random-Library in vivo screenen → NGS quantifiziert packaging yield, transduction, retrograde transport
2. **Computational Design:** pLM + Predictor + cVAE trainieren → BO schlägt Pareto-optimale Sequenzen vor
3. **Smart Library:** Fokussierte Bibliothek aus computationell designten Peptiden (gedruckte Oligonukleotid-Pools, tens of thousands of variants)
4. **Iteration:** Neues NGS → Modell verfeinern → weiter bis handful optimaler Varianten

> "5-10 fold improvements in target properties within 3-4 experimental rounds"

### Datenquelle
- **Evotec library** (in Verhandlung) — 7-mer Peptid-Insertions, in vivo gescreent
- Backup: De novo Library → direkt in vitro panning (überspringt Round 1 in vivo)

---

## 2. ML-Strategien für AAV (Machine learning AAV capsids summary.docx)

### Das zentrale Problem
> "The number of possible amino acid combinations far exceeds what can be explored" — Sequenzraum ist astronomisch groß

### Strategien im Überblick

**Strategy 1: Supervised ML (Fitness Predictor)**
- Trainiert auf Screening-Daten → lernt Sequenz-Funktions-Beziehung
- Schnelle in silico Vorhersage → priorisiert vielversprechende Varianten
- Limitierung: Extrapoliert schlecht außerhalb des Trainingsraums

**Strategy 2: Generative Modelle**
- VAE (Variational Autoencoder): Kontinuierlicher latenter Raum → neue Sequenzen durch Interpolation
- cVAE: Konditioniert auf gewünschte Eigenschaften → gezielte Generierung
- Autoregressive Modelle: Sequenzielle Generierung, nutzen die Struktur von Proteinsequenzen

**Strategy 3: Bayesian Optimization**
- Surrogate-Modell ersetzt teures Wet-Lab Experiment
- Acquisition function balanciert Exploration vs. Exploitation
- Sample-effizient → minimiert Anzahl teurer Experimente

**Strategy 4: Protein Language Models (pLM)**
- ESM-2, ESM-3: Pre-trained auf Millionen Proteinsequenzen
- Transfer learning: Domain-spezifisches Fine-tuning auf AAV-Daten
- Liefert biologisch plausible Embeddings für downstream ML

### Schlüsselerkenntnis
> "The strategic challenge is navigating the astronomical size of protein sequence space through intelligent, data-driven exploration rather than brute-force screening."

---

## 3. ESGCT 2025 — State of the Art (All abstracts machine learning ESGCT 2025.docx)

### Hauptakteure und Ansätze

**Sanofi / Genomic Medicine Unit (GMU)**
- `GMU037`: Dual-fitness Capsid via **generative AI (proximal exploration framework + dual-fitness filter)**
- Ergebnis: 10× mehr Transduktion in Cyno-Makaken-Retina + 10× höhere Produktionsausbeute vs. klinischer Comparator
- Ansatz: Untersucht >100× mehr Capsids als biologisches HTS möglich

**WhiteLab Genomics, Paris**
- `CapsidFlow`: Automatisierte NGS-Analysepipeline (Nextflow) für AAV-Bibliotheken
  - NGS → Read filtering → Variant quantification → Enrichment scores
  - Validiert in HEK293 + Gewebemodellen
- `In silico Directed Evolution`: Residue-scanning → systematische Einzelaminosäure-Substitutionen → Receptor binding affinity
  - Korrelation zwischen predicted affinity und experimenteller Performance bestätigt
- AI-guided rational strategies für target-spezifisches Binding

**PackGene Biotech (π-Icosa Platform)**
- Transformer-Architektur + Protein Language Models → Tissue-specific tropism prediction (AUC 0.83)
- Library von 10,000 Varianten → in vivo Screen
- `π-Liver-01`: 50× höhere Lebertransduktion vs. AAV9
- `π-CNS-03`: 20× verbesserter CNS-Tropismus + Liver-Detargeting

**In-silico Targets (WhiteLab + Nantes)**
- scRNA-seq zur Identifikation von microglial-spezifischen Oberflächenrezeptoren (Integrins, purinergic receptors)
- IHC-Validierung → AI-guided Capsid Engineering für Microglia-Targeting

### Emerging Patterns 2025
- **LLM-Integration:** Direkte Anwendung von Large Language Models auf Capsid-Sequenzdesign (Lir group, ASGCT 2026)
- **Multi-objective Optimization** wird Standard: Simultane Optimierung Tropismus + Yield + Immunogenität
- **Closed-loop in silico → in vivo** Zyklen mit 3-4 Runden als Industriestandard
- **Generative AI** schlägt klassische gerichtete Evolution bei multi-trait Optimierung
- **Compute-Scale:** VSC5-äquivalente HPC-Infrastruktur wird notwendig für Screening-Scale-up

---

## 4. Relevanz für das Parvotec-Projekt

### Was der State of the Art zeigt
- Parvotecs Ansatz (pLM + cVAE + BO) ist **state-of-the-art konform**
- Sanofi GMU037 beweist: Generative AI kann 10× Performance-Sprünge liefern
- WhiteLab's in silico directed evolution ist die komplementäre Methode für Receptor-Targeting

### Was Parvotec differenziert
- **Spezifisches Target:** Nociceptive peripheral neurons + retrograde transport — nicht retinal/liver/CNS wie die Hauptakteure
- **Peripheral pain** ist ein underserved therapeutic area in der AAV-Welt
- Die Evotec-Library ist ein potenzieller Wettbewerbsvorteil wenn sie gelizensiert werden kann

### Offene Fragen / Gaps
- Ist die Evotec-Library-Lizenzierung gesichert?
- Welche in vitro Assays für retrograde transport?
- Wie wird die Multi-species transferability sichergestellt?
- HPC-Infrastruktur: Läuft das auf VSC5 oder eigener Compute?

---

## 5. Technologie-Glossar (Parvotec context)

| Term | Bedeutung |
|---|---|
| **7-mer peptide insertion** | 7 Aminosäuren in die AAV-Capsid-Schleife eingefügt → verändert Tropismus |
| **NGS enrichment score** | Relatives Anreichern erfolgreicher Varianten nach in vivo/vitro Selektion |
| **Pareto-optimal** | Keine weitere Verbesserung einer Eigenschaft ohne Verschlechterung einer anderen |
| **cVAE** | Conditional Variational Autoencoder — generiert neue Sequenzen die auf gewünschte Properties konditioniert sind |
| **Retrograde transport** | AAV wandert retrograd durch Neuron zurück zum Zellkörper — wichtig für periphere Nervensysteme |
| **pLM** | Protein Language Model (z.B. ESM-2) — vortrainiert auf großen Proteindatenbanken |
| **Fitness oracle** | ML-Modell das die experimentelle Fitness einer Variante vorhersagt ohne Wet-Lab |
