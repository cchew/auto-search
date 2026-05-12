from unittest.mock import MagicMock, patch
import numpy as np
from models import SentenceTransformerEmbedder


def test_embed_calls_encode_with_normalization():
    with patch("models.SentenceTransformer") as mock_st:
        mock_st.return_value.encode.return_value = np.zeros((2, 384), dtype=np.float32)
        embedder = SentenceTransformerEmbedder("any-model")
        embedder.embed(["text a", "text b"])
        mock_st.return_value.encode.assert_called_once_with(
            ["text a", "text b"], normalize_embeddings=True
        )


def test_embed_returns_numpy_array_with_correct_shape():
    with patch("models.SentenceTransformer") as mock_st:
        mock_st.return_value.encode.return_value = np.zeros((3, 384), dtype=np.float32)
        embedder = SentenceTransformerEmbedder("any-model")
        result = embedder.embed(["a", "b", "c"])
        assert result.shape == (3, 384)
        assert result.dtype == np.float32
