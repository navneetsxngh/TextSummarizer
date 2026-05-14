from src.textsummarizer.config.configuration import ConfigurationManager
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


class PredictionPipeline:
    def __init__(self):
        self.config = ConfigurationManager().get_model_evaluation_config()

    def predict(self, text: str) -> str:
        tokenizer = AutoTokenizer.from_pretrained(self.config.tokenizer_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_path)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        model.eval()

        inputs = tokenizer(
            text,
            return_tensors="pt",
            max_length=1024,
            truncation=True,
            padding=True,
        ).to(device)

        with torch.no_grad():
            summary_ids = model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                length_penalty=0.8,
                num_beams=8,
                max_length=128,
            )

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        print("Dialogue:")
        print(text)
        print("\nModel Summary:")
        print(summary)

        return summary
