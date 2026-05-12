import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def explain_openai_error(error):
    message = str(error)
    lower_message = message.lower()
    if "insufficient_quota" in lower_message or "quota" in lower_message:
        return (
            "OpenAI rejected the request because the API project has no available "
            "quota or billing credit. Add billing/credits in the OpenAI dashboard, "
            "or use a different API key/project with available quota."
        )
    if "invalid_api_key" in lower_message or "incorrect api key" in lower_message:
        return "OpenAI rejected the key. Create a new API key and set OPENAI_API_KEY again."
    if "rate_limit" in lower_message or "rate limit" in lower_message:
        return "OpenAI rate-limited the request. Wait a bit and rerun the script."
    return "OpenAI request failed. See the raw error above for details."


def check_openai_access(chat_model):
    from openai import OpenAI

    client = OpenAI()
    client.chat.completions.create(
        model=chat_model,
        messages=[{"role": "user", "content": "Reply with OK."}],
        max_tokens=3,
    )
    client.embeddings.create(input=["RAPTOR smoke test"], model="text-embedding-ada-002")


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY before running this script.")

    from raptor import (
        GPT3TurboQAModel,
        GPT3TurboSummarizationModel,
        RetrievalAugmentation,
    )
    from raptor.RetrievalAugmentation import RetrievalAugmentationConfig

    chat_model = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    if "--check-openai" in sys.argv:
        try:
            check_openai_access(chat_model)
        except Exception as error:
            print("Raw OpenAI error:", error)
            raise RuntimeError(explain_openai_error(error)) from error
        print("OpenAI chat and embedding calls succeeded.")
        return

    with open("demo/sample.txt", "r", encoding="utf-8") as file:
        text = file.read()

    config = RetrievalAugmentationConfig(
        qa_model=GPT3TurboQAModel(model=chat_model),
        summarization_model=GPT3TurboSummarizationModel(model=chat_model),
    )

    try:
        ra = RetrievalAugmentation(config=config)
        ra.add_documents(text)
        question = "How did Cinderella reach her happy ending?"
        answer, layers = ra.answer_question(
            question=question,
            return_layer_information=True,
        )
    except Exception as error:
        print("Raw OpenAI error:", error)
        raise RuntimeError(explain_openai_error(error)) from error

    print("Answer:", answer)
    print("Selected layers:", layers)
    ra.save("demo/cinderella_reproduced")


if __name__ == "__main__":
    main()
