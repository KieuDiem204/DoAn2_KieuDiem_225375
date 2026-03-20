"""
recommendation.py — Retrieval engine kết hợp TF-IDF + Embeddings + DataEngine.
Version 3.0 — Tích hợp DataEngine để truy vấn dữ liệu thực từ CSV.
"""
import warnings, os
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")

from config import (
    TFIDF_MATRIX_PATH, TFIDF_VECTORIZER_PATH,
    EMBEDDING_CACHE_PATH, EMBEDDING_MODEL
)


class RetrievalEngine:
    """
    Retrieval với 3 tầng:
    1. DataEngine — stats thực từ CSV (cost, hotels, flights, activities)
    2. TF-IDF + Embeddings — semantic search trên Q&A corpus
    3. Keyword fallback
    """

    def __init__(self, df):
        self.df = df.reset_index(drop=True)
        self.tfidf_vectorizer = None
        self.tfidf_matrix     = None
        self.embeddings       = None
        self.embed_model      = None

        # Load DataEngine
        try:
            from data_engine import get_engine
            self.data_engine = get_engine()
            print(f"[RETRIEVAL] ✅ DataEngine loaded: {len(self.data_engine.all_destinations())} destinations")
        except Exception as e:
            print(f"[RETRIEVAL] ⚠️ DataEngine failed: {e}")
            self.data_engine = None

        self._load_artifacts()

    # ─── Artifact loading ────────────────────────────────────
    def _load_artifacts(self):
        if os.path.exists(TFIDF_VECTORIZER_PATH) and os.path.exists(TFIDF_MATRIX_PATH):
            try:
                vec = joblib.load(TFIDF_VECTORIZER_PATH)
                mat = joblib.load(TFIDF_MATRIX_PATH)
                if hasattr(vec, "idf_"):
                    self.tfidf_vectorizer = vec
                    self.tfidf_matrix     = mat
                    print("[RETRIEVAL] ✅ TF-IDF loaded.")
                else:
                    self._rebuild_tfidf()
            except Exception:
                self._rebuild_tfidf()
        else:
            self._rebuild_tfidf()

        if os.path.exists(EMBEDDING_CACHE_PATH):
            try:
                self.embeddings  = joblib.load(EMBEDDING_CACHE_PATH)
                from sentence_transformers import SentenceTransformer
                self.embed_model = SentenceTransformer(EMBEDDING_MODEL)
                print("[RETRIEVAL] ✅ Embeddings loaded.")
            except Exception as e:
                print(f"[RETRIEVAL] ⚠️ Embeddings: {e}")

    def _rebuild_tfidf(self):
        if "Combined" not in self.df.columns or len(self.df) == 0:
            return
        try:
            vec = TfidfVectorizer(max_features=20000, ngram_range=(1, 2),
                                  sublinear_tf=True, min_df=1)
            mat = vec.fit_transform(self.df["Combined"].tolist())
            self.tfidf_vectorizer = vec
            self.tfidf_matrix     = mat
            print(f"[RETRIEVAL] ✅ TF-IDF rebuilt: {mat.shape}")
            try:
                os.makedirs(os.path.dirname(TFIDF_VECTORIZER_PATH), exist_ok=True)
                joblib.dump(vec, TFIDF_VECTORIZER_PATH)
                joblib.dump(mat, TFIDF_MATRIX_PATH)
            except Exception:
                pass
        except Exception as e:
            print(f"[RETRIEVAL] ⚠️ TF-IDF rebuild failed: {e}")

    # ─── Scoring helpers ─────────────────────────────────────
    def _tfidf_scores(self, query: str) -> np.ndarray:
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
            return np.zeros(len(self.df))
        try:
            q_vec  = self.tfidf_vectorizer.transform([query])
            return cosine_similarity(q_vec, self.tfidf_matrix).flatten()
        except Exception:
            return np.zeros(len(self.df))

    def _embed_scores(self, query: str) -> np.ndarray:
        if self.embed_model is None or self.embeddings is None:
            return np.zeros(len(self.df))
        try:
            q_emb  = self.embed_model.encode([query])
            return cosine_similarity(q_emb, self.embeddings).flatten()
        except Exception:
            return np.zeros(len(self.df))

    # ─── Main retrieve ────────────────────────────────────────
    def retrieve(self, query: str, top_k: int = 6, alpha: float = 0.45) -> list[dict]:
        tfidf_s = self._tfidf_scores(query)
        embed_s = self._embed_scores(query)

        def norm(arr):
            mn, mx = arr.min(), arr.max()
            if mn == mx:
                return np.ones_like(arr) * 0.5
            return (arr - mn) / (mx - mn + 1e-9)

        if (tfidf_s == 0).all() and (embed_s == 0).all():
            # keyword fallback
            combined = np.zeros(len(self.df))
            q_low = query.lower()
            for i in range(len(self.df)):
                try:
                    q = str(self.df.iloc[i].get("Question", "")).lower()
                    a = str(self.df.iloc[i].get("Answer", "")).lower()
                    d = str(self.df.iloc[i].get("Destination", "")).lower()
                    if q_low in q:       combined[i] = 0.8
                    elif q_low in d:     combined[i] = 0.7
                    elif q_low in a:     combined[i] = 0.6
                except Exception:
                    continue
        else:
            combined = alpha * norm(tfidf_s) + (1 - alpha) * norm(embed_s)

        top_idx = np.argsort(combined)[-top_k:][::-1]
        results = []
        for i in top_idx:
            if i >= len(self.df):
                continue
            try:
                row = self.df.iloc[i]
                results.append({
                    "Destination": str(row.get("Destination", "Unknown")).strip(),
                    "Category":    str(row.get("Category",    "General")).strip(),
                    "Question":    str(row["Question"]).strip(),
                    "Answer":      str(row["Answer"]).strip(),
                    "score":       float(combined[i])
                })
            except Exception:
                continue
        return results

    # ─── Data-backed helpers (delegate to DataEngine) ────────
    def get_destination_data_context(self, destination: str, lang: str = "vi") -> str:
        """Get rich factual context from DataEngine for a destination."""
        if not self.data_engine:
            return ""
        return self.data_engine.build_context_for_llm(destination, lang)

    def compare_destinations_data(self, dest_list: list[str]) -> str:
        """Compare destinations using real data."""
        if not self.data_engine:
            return "DataEngine không khả dụng."
        return self.data_engine.compare_destinations(dest_list)

    def recommend_by_criteria(self, budget=None, duration=None, activity=None) -> str:
        """Recommend destinations based on budget/duration/activity."""
        if not self.data_engine:
            return "DataEngine không khả dụng."
        candidates = self.data_engine.recommend_destinations(
            budget=budget, duration_days=duration, activity_type=activity
        )
        return self.data_engine.format_recommendation(candidates)

    def get_available_destinations(self) -> list[str]:
        if self.data_engine:
            return self.data_engine.all_destinations()
        if "Destination" not in self.df.columns:
            return []
        return sorted([d for d in self.df["Destination"].unique() if d and d != "Unknown"])

    # ─── Legacy helpers ───────────────────────────────────────
    def retrieve_by_destination(self, destination: str, top_k: int = 5) -> list[dict]:
        if "Destination" not in self.df.columns:
            return []
        mask   = self.df["Destination"].astype(str).str.lower().str.contains(destination.lower(), na=False)
        subset = self.df[mask]
        if subset.empty:
            return []
        results = []
        for _, row in subset.head(top_k).iterrows():
            results.append({
                "Destination": str(row.get("Destination","Unknown")).strip(),
                "Category":    str(row.get("Category","General")).strip(),
                "Question":    str(row["Question"]).strip(),
                "Answer":      str(row["Answer"]).strip(),
                "score":       1.0
            })
        return results

    def retrieve_by_category(self, category: str, destination: str = "", top_k: int = 5) -> list[dict]:
        if "Category" not in self.df.columns:
            return []
        mask = self.df["Category"].astype(str).str.lower().str.contains(category.lower(), na=False)
        if destination:
            mask = mask & self.df["Destination"].astype(str).str.lower().str.contains(destination.lower(), na=False)
        subset = self.df[mask]
        if subset.empty:
            return []
        results = []
        for _, row in subset.head(top_k).iterrows():
            results.append({
                "Destination": str(row.get("Destination","Unknown")).strip(),
                "Category":    str(row.get("Category","General")).strip(),
                "Question":    str(row["Question"]).strip(),
                "Answer":      str(row["Answer"]).strip(),
                "score":       1.0
            })
        return results