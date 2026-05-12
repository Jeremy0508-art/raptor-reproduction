import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from raptor import (
    BaseEmbeddingModel,
    BaseQAModel,
    RetrievalAugmentation,
    TreeRetrieverConfig,
)
from raptor.RetrievalAugmentation import RetrievalAugmentationConfig


class DeterministicEmbeddingModel(BaseEmbeddingModel):
    """Small offline embedding shim for wiring checks, not quality evaluation."""

    def __init__(self, dimension=1536):
        self.dimension = dimension

    def create_embedding(self, text):
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        while len(values) < self.dimension:
            for byte in digest:
                values.append((byte / 255.0) - 0.5)
                if len(values) == self.dimension:
                    break
            digest = hashlib.sha256(digest).digest()

        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]


class ContextPreviewQAModel(BaseQAModel):
    def answer_question(self, context, question):
        return context[:500]


def main():
    embedding_model = DeterministicEmbeddingModel()
    config = RetrievalAugmentationConfig(
        embedding_model=embedding_model,
        qa_model=ContextPreviewQAModel(),
        tree_retriever_config=TreeRetrieverConfig(
            context_embedding_model="OpenAI",
            embedding_model=embedding_model,
        ),
    )
    ra = RetrievalAugmentation(config=config, tree="demo/cinderella")
    context, layers = ra.retrieve(
        "How did Cinderella reach her happy ending?",
        top_k=3,
        max_tokens=800,
        return_layer_information=True,
    )

    print("Loaded demo/cinderella and retrieved context successfully.")
    print(f"Selected nodes: {layers}")
    print("Context preview:")
    print(context[:800])


if __name__ == "__main__":
    main()
