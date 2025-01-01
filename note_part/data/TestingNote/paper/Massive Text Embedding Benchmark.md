---
tags:
  - future directions
  - benchmark tasks
  - retrieval tasks
  - embedding models
  - multilingual models
  - open-source leaderboard
  - classification tasks
  - model performance
  - text embedding evaluation
  - semantic textual similarity
---
#### **1. Overview**

- **Purpose**: Address gaps in text embedding evaluation by providing a diverse and comprehensive benchmark across tasks, datasets, and languages.
- **Features**:
    - 8 tasks, 58 datasets, 112 languages.
    - Evaluates 33 models using a consistent framework.
    - Emphasizes tasks beyond Semantic Textual Similarity (STS), such as retrieval, classification, and clustering.
    - Open-source code and leaderboard for reproducibility and community contributions.

---

#### **2. Key Objectives**

- Identify strengths and weaknesses of embedding models across varied tasks.
- Bridge the gap between model performance on specialized benchmarks and real-world applications.
- Provide a clear basis for selecting models for industry or research use cases.

---

#### **3. Benchmark Tasks**

1. **Bitext Mining**:
    - Matches translations across languages.
    - Metric: F1 score.
2. **Classification**:
    - Logistic regression over embeddings to predict labels.
    - Metric: Accuracy.
3. **Clustering**:
    - Embeddings grouped using k-means clustering.
    - Metric: V-measure.
4. **Pair Classification**:
    - Classify text pairs (e.g., duplicate detection).
    - Metric: Average Precision.
5. **Reranking**:
    - Rank documents based on query relevance.
    - Metric: Mean Average Precision (MAP).
6. **Retrieval**:
    - Find relevant documents for given queries.
    - Metric: nDCG@10.
7. **STS**:
    - Evaluate similarity between sentences.
    - Metric: Spearman Correlation.
8. **Summarization**:
    - Score machine-generated summaries against human references.
    - Metric: Spearman Correlation.

---

#### **4. Evaluation Insights**

- No single model excels across all tasks.
- **Top Models by Task**:
    - **Classification**: ST5-XXL performs best.
    - **Clustering**: MPNet is competitive with larger models.
    - **Retrieval**: SGPT-5.8B-msmarco dominates.
    - **STS**: ST5-XXL leads in similarity-based tasks.
    - **Multilingual Tasks**: LaBSE and MPNet-multilingual outperform others.
- Models fine-tuned for specific tasks often perform poorly in unrelated tasks (e.g., retrieval models underperform in STS).

---

#### **5. Model Groups**

1. **Self-Supervised**:
    - Examples: Glove, SimCSE-unsup.
    - Strengths: Simplicity, speed.
    - Weaknesses: Lacks context-awareness.
2. **Supervised**:
    - Examples: ST5, MPNet, SGPT-msmarco.
    - Strengths: Task-specific optimization.
    - Weaknesses: Higher computational cost.
3. **Multilingual Models**:
    - Examples: LaBSE, MiniLM-multilingual.
    - Strengths: Effective across languages.
    - Weaknesses: Varying performance on unseen languages.

---

#### **6. Performance Trends**

- Larger models generally achieve higher scores but at greater computational expense.
- Models such as MiniLM and MPNet provide a balance between speed and performance.
- Clustering and retrieval tasks require coherent embeddings across diverse topics; fine-tuning on large datasets improves results.

---

#### **7. Future Directions**

- Expand MTEB with new tasks, datasets, and evaluation metrics.
- Investigate methods for creating universal text embeddings.
- Address challenges in multilingual and cross-lingual tasks.