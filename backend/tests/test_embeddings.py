
import pytest

from app.services.embeddings import generate_embeddings


class FakeEmbeddings:
    shape = (2, 384)

    def tolist(self):
        return [
            [0.1] * 384,
            [0.2] * 384,
        ]


class FakeModel:
    def encode(self, texts, **kwargs):
        assert len(texts) == 2
        assert kwargs["normalize_embeddings"] is True
        return FakeEmbeddings()


def test_generate_embeddings(monkeypatch):
    fake_model = FakeModel()

    monkeypatch.setattr(
        "app.services.embeddings.get_embedding_model",
        lambda: fake_model,
    )

    texts = [
        "Employees receive annual leave.",
        "Employees can request vacation days.",
    ]

    result = generate_embeddings(texts)

    assert len(result) == 2
    assert len(result[0]) == 384
    assert len(result[1]) == 384


def test_empty_list_returns_empty_list():
    assert generate_embeddings([]) == []


def test_empty_text_is_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        generate_embeddings(["Valid text", "   "])
