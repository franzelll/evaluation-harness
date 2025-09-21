from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
from .logging_config import get_logger

logger = get_logger("models")


class ModelAdapter:
    def __init__(self, model_id: str):
        """Initialisiert das Modell mit Fehlerbehandlung"""
        self.model_id = model_id
        logger.info(f"Lade Modell: {model_id}")

        try:
            # Tokenizer laden
            self.tok = AutoTokenizer.from_pretrained(model_id)
            if self.tok.pad_token is None:
                self.tok.pad_token = self.tok.eos_token

            # Modell laden mit Memory-Management
            device_map = "auto" if torch.cuda.is_available() else None
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            logger.debug(f"Device: {device_map}, dtype: {torch_dtype}")

            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map=device_map,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
            )

            self.device = next(self.model.parameters()).device
            logger.info(f"Modell erfolgreich geladen auf {self.device}")

        except Exception as e:
            logger.error(f"Fehler beim Laden des Modells {model_id}: {e}")
            raise RuntimeError(f"Modell {model_id} konnte nicht geladen werden: {e}")

    def generate(self, prompt: str, max_new_tokens: int, decoding: dict) -> str:
        """Generiert Text mit Fehlerbehandlung und Timeout"""
        try:
            start_time = time.time()

            # Input validieren
            if not prompt or not prompt.strip():
                logger.warning("Leerer Prompt erhalten")
                return ""

            inputs = self.tok(
                prompt, return_tensors="pt", truncation=True, max_length=2048
            ).to(self.device)

            # Generation-Parameter validieren
            generation_params = {
                "do_sample": decoding.get("do_sample", False),
                "temperature": max(0.01, decoding.get("temperature", 0.0)),
                "top_p": max(0.01, min(1.0, decoding.get("top_p", 1.0))),
                "max_new_tokens": min(max_new_tokens, 512),  # Limit für Stabilität
                "pad_token_id": self.tok.eos_token_id,
                "eos_token_id": self.tok.eos_token_id,
            }

            logger.debug(f"Generiere mit Parametern: {generation_params}")

            with torch.inference_mode():
                out = self.model.generate(
                    **inputs,
                    **generation_params,
                )

            text = self.tok.decode(out[0], skip_special_tokens=True)

            # Text extrahieren
            if "Vereinfachter Text:" in text:
                result = text.split("Vereinfachter Text:")[-1].strip()
            else:
                result = text[len(prompt) :].strip()  # Nur den generierten Teil

            generation_time = time.time() - start_time
            logger.debug(f"Generation abgeschlossen in {generation_time:.2f}s")

            return result

        except torch.cuda.OutOfMemoryError as e:
            logger.error(f"CUDA Out of Memory: {e}")
            raise RuntimeError(
                "Modell benötigt zu viel GPU-Speicher. Versuchen Sie CPU-Modus oder reduzieren Sie die Batch-Size."
            )

        except Exception as e:
            logger.error(f"Fehler bei der Generation: {e}")
            raise RuntimeError(f"Text-Generation fehlgeschlagen: {e}")

    def __del__(self):
        """Cleanup beim Löschen des Objekts"""
        try:
            if hasattr(self, "model"):
                del self.model
            if hasattr(self, "tok"):
                del self.tok
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass  # Ignoriere Cleanup-Fehler
