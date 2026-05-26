import torch
from transformers import T5ForConditionalGeneration, T5TokenizerFast
from peft import PeftModel
from app.core.config import settings

class NLPPipeline:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        print("Loading tokenizer and base model...")
        self.tokenizer = T5TokenizerFast.from_pretrained(settings.ADAPTER_PATH)
        base = T5ForConditionalGeneration.from_pretrained(settings.BASE_MODEL_NAME)

        print(f"Applying LoRA adapter from {settings.ADAPTER_PATH}...")
        self.model = PeftModel.from_pretrained(base, settings.ADAPTER_PATH)
        self.model.eval()
        self.model = self.model.to(self.device)
        print(f"Model successfully loaded on {self.device}. Ready for inference.")

    def unload_model(self):
        self.model = None
        self.tokenizer = None
        print("Cleaned up model resources.")

    def generate(self, command: str) -> str:
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model is not loaded.")

        input_text = settings.PREFIX + command

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=settings.MAX_INPUT_LEN,
            truncation=True,
            padding=True,
        ).to(self.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=settings.MAX_NEW_TOKENS,
                num_beams=settings.NUM_BEAMS,
                early_stopping=settings.EARLY_STOPPING,
            )

        raw_output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

        # Salvage missing braces
        if not raw_output.startswith("{") and '"action"' in raw_output:
            raw_output = "{" + raw_output
        if not raw_output.endswith("}") and '"action"' in raw_output:
            raw_output = raw_output + "}"

        return raw_output

# Global instance to be used by endpoints
nlp_pipeline = NLPPipeline()
