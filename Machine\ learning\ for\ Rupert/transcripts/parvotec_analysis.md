# Parvotec Analysis - Content

## parvotec

### Projektgoal
- **Präzise Zielsteuerung zu dorsal root ganglion (DRG) Neuronen mit retrogradem Transport für modulierte Schmerzwahrnehmung**
- AAV1/AAV5 serotypes
- Peripheral pain therapy innovation
- Retrograde transport mechanism

### ML Framework
4-schichtiges System mit 5-10× Verbesserungen pro Iterationsrunde:

1. **Embedding Layer**: ESM-2 (1280-dim) / ESM-3 (2560-dim multi-modal)
   - Meta AI protein language models
   - Universal sequence representations
   - Biological grounding

2. **Predictor Layer**: Multi-task Neural Network
   - Tropismus Score Vorhersage
   - Produktionseffizienz (yield)
   - Thermostabilität
   - Trainiert auf Evotec DMS library (>1M mutanten)

3. **Generator Layer**: Conditional VAE (cVAE)
   - Target-spezifische Sequenzgenerierung
   - Constraints: "70% tropism + high yield"
   - Latent space exploration

4. **Optimizer Layer**: Multi-objective Bayesian Optimization
   - Pareto-front discovery
   - Tropismus ↔ Yield ↔ Immunogenicity balance
   - 4-round vs 6-7 classical efficiency

### Training Data
- **Evotec Library**: >1 Million AAV capsid variants
- **Deep Mutational Scanning (DMS)** enrichment scores
- **NGS-based fitness oracle** calibration
- Iterative workflow: Research → Design → Validation → Measurement → Optimization

---

## framework

### Strategy 1: Supervised Fitness Prediction
Multi-task neural network trained on DMS data:
- Input: ESM-2/3 embeddings (1280 or 2560 dimensions)
- Outputs: Tropismus score, Production efficiency, Thermal stability
- Training: Evotec library with NGS enrichment validation
- Result: 2.1× higher hit rate vs random libraries

### Strategy 2: Generative Models (VAE / cVAE / Autoregressive)
Conditional sequence generation under target specifications:
- **VAE**: Learn latent representation of functional AAV sequences
- **cVAE**: Condition on target specs (e.g., "nociceptor-targeting")
- **Autoregressive**: Token-by-token generation with fitness guidance
- Application: Sample high-fitness regions of sequence space

### Strategy 3: Bayesian Optimization
Multi-objective BO with surrogate model:
- Surrogate: Gaussian Process or Neural Network (fitness oracle)
- Acquisition function: Expected Improvement (EI) or ParEGO
- Multi-objective: Balance 3+ competing metrics
- Workflow: LLM candidates → ESM-2 ranking → BO refinement → Experimental validation

### Strategy 4: Protein Language Models (pLMs)
ESM-2 and ESM-3 as universal embeddings:
- **ESM-2**: 1280-dimensional, UniRef50 pre-trained
- **ESM-3**: 2560-dimensional, multi-modal (sequence + structure + function)
- Advantages: Zero-shot transfer, captures epistasis, no retraining needed
- Limitations: Slower inference, black-box representations

### State-of-Art: Case Studies
1. **Sanofi GMU037**: 10× improvements in liver tropism via ML-guided libraries
2. **WhiteLab CapsidFlow**: Neuronal-selective targeting with pLM-based design
3. **PackGene π-Icosa**: 50× liver / 20× CNS targeting via multi-objective BO

---

## lir

### Lir_AAV_LLM: LLM-Augmented Capsid Engineering

**Centerpiece:** "Integrating Large Language Models into multi-modal AAV engineering pipelines reveals powerful synergy: LLMs excel at zero-shot sequence ideation, while pLMs provide biological grounding. Together they accelerate discovery by 3-5× while maintaining experimental feasibility."

#### Segment 1: LLM as Ideation Engine
"We prompt GPT-4 with naturalistic descriptions: 'Design an AAV1 targeting DRG nociceptors with 5-fold retrograde improvement.' Model generates 12-20 novel sequence concepts per cycle with high structural validity."

**Key insight**: LLMs don't need training data; they leverage general knowledge of protein structure + AAV biology to generate creative, never-before-seen sequences.

#### Segment 2: ESM-2 Validation & Scoring
"Each LLM sequence feeds into ESM-2 embedding. Top 20% fitness percentile advance to validation. 2.1× higher hit rate vs. random libraries."

**Workflow**: LLM → ESM-2 embedding → Multi-task predictor → Rank by fitness → Top candidates to experiment

#### Segment 3: Hybrid Bayesian Optimization
"BO initialized with LLM candidates. Samples acquisition function for underexplored regions. Multi-objective Pareto: tropism × yield × immunogenicity. 4-round vs 6-7 classical. 40% efficiency gain."

**Advantage**: Warm-starting BO with LLM-generated pool drastically reduces sample complexity.

#### Segment 4: LLM vs pLM Trade-offs
- **LLM**: Fast ideation, creative, no training required, but requires validation
- **pLM**: Precise predictions, biology-grounded embeddings, captures epistasis, slower
- **Hybrid Strategy**: LLM exploration (breadth) + pLM exploitation (depth) = Pareto-optimal discovery

---

## videos

### Video 1: Lir_AAV_LLM [CENTERPIECE] ⭐⭐⭐⭐⭐
**Priority 1 | ~45 minutes**

"Large Language Models provide zero-shot design capabilities for novel capsid sequences, complementary to pLM-based fitness prediction. Hybrid workflow: LLM → ideation → ESM-2 → oracle → BO."

**Key excerpts:**
- Zero-shot design without domain-specific training
- GPT-4 generates structurally valid AAV mutants
- 2.1× hit rate improvement over random
- LLM-BO hybrid outperforms classical optimization

**Relevance to Parvotec:** Directly applicable to nociceptive neuron targeting; LLMs can ideate novel peptide insertions for DRG selectivity.

### Video 2: AAV_Engineering_III ⭐⭐⭐⭐
**High Priority | ~60 minutes**

"Directed evolution + deep mutational scanning maps entire fitness landscape. 7-mer insertion libraries achieve 3-5× tropism improvements with minimal yield loss."

**Key excerpts:**
- DMS enrichment scores identify functional regions
- 7-mer insertion mutagenesis is optimal for AAV1/5
- Fitness landscape is highly epistatic
- Tropism-yield trade-offs are navigable

### Video 3: AAV_Engineering_IV ⭐⭐⭐⭐
**High Priority | ~50 minutes**

"Bayesian Optimization with multi-objective functions enables Pareto-optimal selection. Balance tropism, yield, and immunogenicity in single framework."

**Key excerpts:**
- Pareto-front discovery is essential
- BO converges 40% faster than grid search
- Immunogenicity must be predicted alongside tropism
- Multi-objective BO is computationally efficient

### Video 4: AAV_Trafficking [CRITICAL] ⭐⭐⭐⭐
**CRITICAL Priority | ~45 minutes**

"Retrograde transport in nociceptive neurons depends critically on receptor interactions at axon terminal. DRG targeting requires careful balance of peptide exposure and native function."

**Key excerpts:**
- Retrograde transport requires intact capsid structure
- Nociceptor-specific receptors enable DRG selectivity
- Over-modification kills retrograde transport
- Peptide insertion sites must preserve infectivity

**Relevance to Parvotec:** This is the bottleneck; must maintain 7-mer insertion while enabling retrograde transport.

### Video 5: ShapeTX_AAV5 ⭐⭐⭐
**Medium Priority | ~40 minutes**

"AAV5 architecture differs from AAV1 in β-sheet topology. We've identified optimal 7-mer insertion site maintaining infectivity while enabling tropism redirection."

**Key excerpts:**
- AAV5 has different insertion tolerance than AAV1
- Position 587-589 optimal for AAV5 insertions
- Structure-guided mutagenesis is essential
- Serotype differences matter

### Video 6: TuningReceptor_Caltech ⭐⭐⭐⭐
**High Priority | ~55 minutes**

"Rational design of receptor-binding peptides using AlphaFold enables cell-type-specific tropism. 10× selectivity improvement for neural targets."

**Key excerpts:**
- AlphaFold predicts receptor-peptide interactions
- Rational design outperforms random mutagenesis
- 10× selectivity is achievable
- Neural receptors are well-characterized

---

## papers

### Category: Industrial Case Studies (Voyager Series)
**3 papers from ASGCT 2023-2025**

Papers showing foundational ML-guided AAV capsid evolution:
- Poster 1: 5-10× improvements via supervised learning
- Poster 2: Multi-objective optimization advances
- Poster 3: Hybrid LLM + pLM integration

### Category: AAV Tropism & Directed Evolution
**2 core papers**

- Systematic capsid evolution in vivo + comprehensive fitness landscape
- Deep mutational scanning with NGS enrichment scores
- pLM embeddings correlate with fitness
- 7-mer insertion optimization

### Category: ML for Viral Design
**3 papers on design automation**

- ML for viral assembly prediction
- Deep generative models for sequence diversification
- Latent space interpolation for trait optimization

### Category: Protein Language Models (pLMs)
**2 papers on foundation models**

- ESM-2: Universal protein embeddings (Meta AI)
- ESM-3: Multi-modal protein language models
- Structure prediction with ESMFold

### Category: Specialized Methods
**3 tool papers**

- ProteinVAE: Variational autoencoders for protein design
- Hammock: HMM-based peptide motif clustering
- Multi-objective trade-off control in optimization

### Category: Multi-Trait AAV Engineering
**1 integration paper**

- Systematic multi-trait AAV engineering
- Balancing tropism, yield, immunogenicity
- Mirrors Parvotec's multi-output oracle design

---

## glossary

### AAV (Adeno-Associated Virus)
Small, non-enveloped DNA virus (~27 nm diameter). 13 known serotypes with distinct tropisms determined by capsid protein sequence and receptor-binding interactions.

### Tropismus (Cell-Type Selectivity)
Specific infectivity of a virus to particular cell types (e.g., liver-tropism, neuronal-tropism, DRG-targeting). Determined by capsid-receptor interactions and intracellular trafficking pathways.

### Retrograde Transport
Axonal transport mechanism moving cargo from peripheral axon terminals back to the neuronal cell body. Critical for gene therapy targeting distant neuron populations (e.g., DRG neurons innervating peripheral tissue).

### ESM-2 / ESM-3
Evolutionary Scale Modeling protein language models from Meta AI. ESM-2: 1280-dimensional embeddings trained on UniRef50. ESM-3: 2560-dimensional multi-modal embeddings (sequence + structure + function).

### cVAE (Conditional Variational Autoencoder)
Generative model that learns latent representations of sequences and can generate new sequences conditional on specifications (e.g., "design AAV with 70% nociceptor tropism and high yield").

### Bayesian Optimization
Hyperparameter optimization using a surrogate model (Gaussian Process or Neural Network) + acquisition function (Expected Improvement). Multi-objective BO balances competing metrics (Pareto optimality).

### DMS (Deep Mutational Scanning)
High-throughput mutagenesis + next-generation sequencing (NGS) to measure fitness effects of all single mutations in a protein. Generates comprehensive fitness landscape.

### Pareto-Optimal
Solution where no other solution is strictly better in all objectives. Pareto front = set of all Pareto-optimal candidates balancing tropism, yield, immunogenicity.

### pLM (Protein Language Model)
Foundation model trained on massive protein sequence databases to learn universal representations. ESM-2/3 are state-of-art pLMs.

### BO (Bayesian Optimization)
Sample-efficient optimization using probabilistic surrogate model + acquisition function. Key advantage: explores uncertain regions intelligently without exhaustive search.

### 7-Mer Insertion
7 amino acid peptide insertion into AAV capsid for tropism modification. Position-specific (e.g., position 587-589 for AAV5). Optimal length balances modification capability with function preservation.
