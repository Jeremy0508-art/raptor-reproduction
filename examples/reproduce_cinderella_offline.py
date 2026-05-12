import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from raptor import (
    BaseEmbeddingModel,
    BaseQAModel,
    BaseSummarizationModel,
    RetrievalAugmentation,
)
from raptor.RetrievalAugmentation import RetrievalAugmentationConfig

OUTPUT_PATH = "demo/cinderella_offline_reproduced"
QUESTION = "How did Cinderella reach her happy ending?"


class DeterministicEmbeddingModel(BaseEmbeddingModel):
    """Offline embedding shim for pipeline reproduction, not answer quality."""

    def __init__(self, dimension=384):
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


class ExtractiveSummarizationModel(BaseSummarizationModel):
    """Keeps the first tokens from a cluster as a deterministic local summary."""

    def summarize(self, context, max_tokens=150):
        words = context.split()
        return " ".join(words[:max_tokens])


class ContextPreviewQAModel(BaseQAModel):
    """Returns retrieved context so the experiment remains fully offline."""

    def answer_question(self, context, question):
        return context[:1000]


def build_config():
    embedding_model = DeterministicEmbeddingModel()
    return RetrievalAugmentationConfig(
        embedding_model=embedding_model,
        summarization_model=ExtractiveSummarizationModel(),
        qa_model=ContextPreviewQAModel(),
        tb_max_tokens=120,
        tb_num_layers=3,
        tb_summarization_length=80,
        tr_top_k=5,
    )


def print_query_result(ra):
    answer, layers = ra.answer_question(
        question=QUESTION,
        top_k=5,
        max_tokens=1200,
        return_layer_information=True,
    )

    print("Retrieved layers:", layers)
    print("Answer/context preview:")
    print(answer)


def main():
    config = build_config()

    if "--load-existing" in sys.argv:
        ra = RetrievalAugmentation(config=config, tree=OUTPUT_PATH)
        print(f"Loaded offline reproduced tree from {OUTPUT_PATH}.")
        print_query_result(ra)
        return

    with open("demo/sample.txt", "r", encoding="utf-8") as file:
        text = file.read()

    ra = RetrievalAugmentation(config=config)
    ra.add_documents(text)

    print("Offline RAPTOR pipeline completed.")
    print_query_result(ra)

    ra.save(OUTPUT_PATH)
    print(f"Saved offline reproduced tree to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
