import whisper
import torch
import os
from tqdm import tqdm

# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3-turbo")


class AudioTranscriber:
    def __init__(self, model_size="base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        print(f"Loading {model_size} model...")
        self.model = whisper.load_model(model_size).to(self.device)
        print("Model loaded successfully!")
    
    def transcribe_single(self, audio_path, language=None):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        print(f"Transcribing: {audio_path}")
        options = {"language": language} if language else {}
        result = self.model.transcribe(audio_path, **options)
        return result
    
    def transcribe_batch(self, audio_dir, output_dir="transcripts", language=None):
        """
        Batch transcribe audio files in a directory
        
        Parameters:
            audio_dir (str): Audio files directory
            output_dir (str): Output directory
            language (str): Audio language code
        """
        if not os.path.exists(audio_dir):
            raise FileNotFoundError(f"Directory not found: {audio_dir}")
            
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all supported audio files
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav', '.m4a', '.flac'))]
        
        print(f"Found {len(audio_files)} audio files")
        
        # Process each audio file
        for audio_file in tqdm(audio_files, desc="Transcription progress"):
            audio_path = os.path.join(audio_dir, audio_file)
            try:
                result = self.transcribe_single(audio_path, language)
                
                # Save transcription result
                output_file = os.path.join(output_dir, f"{os.path.splitext(audio_file)[0]}.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result["text"])
                    
            except Exception as e:
                print(f"Error processing {audio_file}: {str(e)}")

# example
if __name__ == "__main__":
    transcriber = AudioTranscriber(model_size="base")
    
    result = transcriber.transcribe_single("audios/audio2-zh.mp3")  # detect the language automatically
    
    print("\nTranscription result:")
    print(result["text"])
    
    with open("audio2_transcript.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])
    
