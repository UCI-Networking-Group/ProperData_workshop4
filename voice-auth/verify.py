from speechbrain.inference.speaker import SpeakerRecognition
import sys

f1, f2 = sys.argv[1:]

verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
score, prediction = verification.verify_files(f1, f2)
print(score.item(), prediction.item())
