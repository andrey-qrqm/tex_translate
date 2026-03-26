from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
tokenizer = M2M100Tokenizer.from_pretrained(
    "facebook/m2m100_418M",
    src_lang="en",
    tgt_lang="ru",
    use_auth_token=HF_TOKEN
)

model.to("cpu")
print("Model loaded successfully!")


def translate_text(text: str) -> str:
    """Перевод одной строки — обёртка над батч-функцией."""
    return translate_batch([text])[0]


def translate_batch(texts: list[str]) -> list[str]:
    """
    Переводит список строк за один вызов модели.
    Порядок результатов соответствует порядку входных строк.
    """
    tokenizer.src_lang = "en"

    model_inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,        # выравниваем строки до одной длины
        truncation=True,     # обрезаем слишком длинные строки
        max_length=512
    )

    generated_tokens = model.generate(
        **model_inputs,
        forced_bos_token_id=tokenizer.get_lang_id("ru")
    )

    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)


if __name__ == "__main__":
    samples = [
        "Hello world, how are you?",
        "This is a second sentence.",
        "Neural networks are powerful tools."
    ]
    results = translate_batch(samples)
    for src, tgt in zip(samples, results):
<<<<<<< HEAD
        print(f"{src!r} -> {tgt!r}")
=======
        print(f"{src!r} - {tgt!r}")
>>>>>>> dev
