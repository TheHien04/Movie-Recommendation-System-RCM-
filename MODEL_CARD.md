# Cinemate Model Card — Hybrid Recommender v3

## Model Summary
- **Name:** Cinemate Hybrid Recommender v3
- **Type:** Multi-stage ensemble (classical ML + neural networks + rules + RAG)
- **Version:** artifact manifest at `backend/artifacts/v1/manifest.json`

## ML Stack (Advanced)

| Component | Algorithm | Type |
|-----------|-----------|------|
| Semantic retrieval | `all-MiniLM-L6-v2` (Sentence-BERT) or TF-IDF | **Transformer / sparse** |
| Collaborative | TruncatedSVD on genre-user matrix | Matrix factorization |
| Neural CF | NeuMF (GMF + MLP) | **PyTorch neural network** |
| Fusion | Weighted linear ensemble + grid-search tuning | Ensemble learning |
| Diversity | Maximal Marginal Relevance (MMR) | Submodular ranking |
| Conversational | RAG + GPT-4o-mini | **LLM (neural)** |
| Evaluation | NDCG@K, MAP, Precision@K, Recall@K | Learning-to-rank metrics |

## Training Pipeline
```bash
python Movie_Recommend_System/backend/scripts/train_models.py
```
1. Validate dataset schema
2. Fit TF-IDF + optional Transformer embeddings
3. Fit SVD item factors
4. Train NeuMF on implicit genre/director personas (BCE loss, Adam)
5. Grid-search hybrid fusion weights (maximize NDCG@5)
6. Export artifacts + manifest

## Neural CF (NeuMF)
- **Architecture:** user/item embeddings → element-wise product (GMF) + MLP on concatenated features
- **Loss:** Binary cross-entropy on implicit feedback
- **Data:** Virtual taste personas (genre, director) × movie interactions from IMDb ratings

## Hyperparameter Tuning
Grid search over fusion weights (`hyperopt.py`), objective = average NDCG@5 on 20-case benchmark.

## Limitations
- ~500 movie catalog; not billion-scale
- Neural CF uses synthetic personas, not real user clickstream
- Transformer embeddings require Python 3.10+ or CI environment

## Ethical Considerations
Popularity debiasing term; English-first NLP; Western catalog bias.
