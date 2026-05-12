import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from raptor import (
    BaseEmbeddingModel,
    BaseQAModel,
    BaseSummarizationModel,
    RetrievalAugmentation,
)
from raptor.RetrievalAugmentation import RetrievalAugmentationConfig


def required_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this script.")
    return value


def explain_compatible_error(error):
    message = str(error)
    lower_message = message.lower()
    if "quota" in lower_message or "balance" in lower_message:
        return "The provider rejected the request because quota, balance, or billing is unavailable."
    if "invalid" in lower_message and ("key" in lower_message or "token" in lower_message):
        return "The provider rejected the API key. Check COMPAT_API_KEY and project permissions."
    if "model" in lower_message and ("not found" in lower_message or "does not exist" in lower_message):
        return "The configured model name is not available for this provider or API key."
    if "base_url" in lower_message or "connection" in lower_message:
        return "The compatible API endpoint may be wrong. Check COMPAT_BASE_URL."
    return "Compatible API request failed. See the raw error above for details."


class CompatibleEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, client, model, dimensions=None):
        self.client = client
        self.model = model
        self.dimensions = dimensions

    def create_embedding(self, text):
        kwargs = build_embedding_kwargs(
            self.model,
            [text.replace("\n", " ")],
            self.dimensions,
        )
        return self.client.embeddings.create(**kwargs).data[0].embedding


def build_embedding_kwargs(model, input_text, dimensions=None):
    kwargs = {
        "model": model,
        "input": input_text,
    }
    if dimensions is not None:
        # openai==1.3.3 does not expose dimensions as a first-class argument,
        # but compatible providers can still receive it through extra_body.
        kwargs["extra_body"] = {"dimensions": dimensions}
    return kwargs


class CompatibleChatSummarizationModel(BaseSummarizationModel):
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def summarize(self, context, max_tokens=500):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": (
                        "Write a summary of the following, including as many "
                        f"key details as possible: {context}"
                    ),
                },
            ],
            max_tokens=max_tokens,
            temperature=0,
        )
        return response.choices[0].message.content


class CompatibleChatQAModel(BaseQAModel):
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def answer_question(self, context, question):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You answer questions from the given context."},
                {
                    "role": "user",
                    "content": f"Given context:\n{context}\n\nAnswer this question:\n{question}",
                },
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()


def build_client():
    return OpenAI(
        api_key=required_env("COMPAT_API_KEY"),
        base_url=required_env("COMPAT_BASE_URL"),
    )


def check_access(client, chat_model, embedding_model, dimensions):
    client.chat.completions.create(
        model=chat_model,
        messages=[{"role": "user", "content": "Reply with OK."}],
        max_tokens=3,
    )

    client.embeddings.create(
        **build_embedding_kwargs(
            embedding_model,
            ["RAPTOR compatible API smoke test"],
            dimensions,
        )
    )


def main():
    chat_model = required_env("COMPAT_CHAT_MODEL")
    embedding_model = required_env("COMPAT_EMBEDDING_MODEL")
    dimensions = os.environ.get("COMPAT_EMBEDDING_DIMENSIONS")
    dimensions = int(dimensions) if dimensions else None

    client = build_client()

    try:
        if "--check-api" in sys.argv:
            check_access(client, chat_model, embedding_model, dimensions)
            print("Compatible chat and embedding calls succeeded.")
            return

        with open("demo/sample.txt", "r", encoding="utf-8") as file:
            text = file.read()

        embedding = CompatibleEmbeddingModel(client, embedding_model, dimensions)
        config = RetrievalAugmentationConfig(
            embedding_model=embedding,
            summarization_model=CompatibleChatSummarizationModel(client, chat_model),
            qa_model=CompatibleChatQAModel(client, chat_model),
        )

        ra = RetrievalAugmentation(config=config)
        ra.add_documents(text)
        answer, layers = ra.answer_question(
            question="How did Cinderella reach her happy ending?",
            return_layer_information=True,
        )

        output_path = os.environ.get(
            "COMPAT_OUTPUT_PATH",
            "demo/cinderella_compatible_api_reproduced",
        )
        print("Answer:", answer)
        print("Selected layers:", layers)
        ra.save(output_path)
        print(f"Saved compatible API reproduced tree to {output_path}")
    except Exception as error:
        print("Raw compatible API error:", error)
        raise RuntimeError(explain_compatible_error(error)) from error


if __name__ == "__main__":
    main()
