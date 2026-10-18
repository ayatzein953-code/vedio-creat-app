# ==========================================
# الخلية 1: إعداد البيئة وتثبيت المكتبات وتنزيل SadTalker
# ==========================================
!git clone https://github.com/OpenTalker/SadTalker.git
%cd SadTalker

# تثبيت المكتبات المطلوبة للتعامل مع الفيديو والصوت
!pip install -q moviepy librosa soundfile gtts
!pip install -q torch torchvision torchaudio

# تنزيل ملفات الأوزان والموديلات الخاصة بـ SadTalker
!bash scripts/download_models.sh

print("✅ تم إعداد البيئة وتنزيل جميع المكتبات والأنماط بنجاح!")
#===============================================================

# ==========================================
# الخلية 2: المطالبة (Prompt) المخصصة لتوليد الصور عبر Midjourney
# ==========================================
"""
انسخ الموجه التالي واستخدمه في Midjourney أو أي أداة توليد صور لإنشاء الشخصيتين:

MIDJOURNEY PROMPT:
/imagine prompt: A photorealistic close-up of two people who look like younger and older versions of the same person, sitting across from each other in a softly lit, cozy room. The younger one (around 8 years old) is looking up with hopeful eyes. The older one (around 25 years old) has a gentle, knowing smile. A sense of warmth and wisdom. Shallow depth of field. --ar 16:9 --v 6.0
"""
print("📌 يرجى إنشاء الصور باستخدام الـ Prompt أعلاه وحفظ صورة الطفل باسم young_me.png وصورة الكهول باسم older_me.png")


#===============================================================
# ==========================================
# الخلية 3: رفع الصوتيات والصور من جهازك إلى Colab
# ==========================================
import os
from google.colab import files

os.makedirs("input_audio", exist_ok=True)
os.makedirs("input_images", exist_ok=True)

print("📁 1. قم برفع التسجيلات الصوتية بصوتك (أو الملفات الـ 9 الكاملة):")
uploaded_audios = files.upload()
for filename in uploaded_audios.keys():
    os.rename(filename, os.path.join("input_audio", filename))

print("\n🖼️ 2. قم برفع صورتي الشخصيتين (young_me.png و older_me.png):")
uploaded_images = files.upload()
for filename in uploaded_images.keys():
    os.rename(filename, os.path.join("input_images", filename))

print("✅ تم رفع الملفات بنجاح!")

#=================================================================
# ==========================================
# الخلية 4: تحويل أصوات النسخة الصغرى لتبدو كصوت طفل (RVC / Pitch Shift Process)
# ==========================================
import librosa
import soundfile as sf

def convert_to_child_voice(input_path, output_path, pitch_steps=4.5):
    """رفع خامة الصوت وتردده ليبدو كأنه صوت طفل صغير"""
    y, sr = librosa.load(input_path, sr=None)
    y_child = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_steps)
    sf.write(output_path, y_child, sr)

# تحويل كافة الملفات الصوتية الخاصة بالشخصية الصغرى
young_indices = [0, 2, 4, 6, 7]
os.makedirs("processed_audio", exist_ok=True)

for idx in range(9):
    raw_audio = f"input_audio/line_{idx}.wav" # أو امتداد mp3 بحسب ملفك
    out_audio = f"processed_audio/line_{idx}_final.wav"
    
    if idx in young_indices:
        print(f"🎵 جاري تحويل صوت الجملة {idx} إلى صوت طفل...")
        convert_to_child_voice(raw_audio, out_audio, pitch_steps=4.5)
    else:
        # الإبقاء على الصوت الحقيقي للنسخة الكبرى دون تعديل
        y, sr = librosa.load(raw_audio, sr=None)
        sf.write(out_audio, y, sr)

print("✅ تم تجهيز واستخراج الأصوات المعدلة بنجاح!")
#===================================================================
# ==========================================
# الخلية 5: تحريك الشفاه والصور عبر SadTalker
# ==========================================
import subprocess

young_img = "input_images/young_me.png"
old_img = "input_images/older_me.png"

# خريطة تربط كل جملة بالصورة المقابلة لها
dialogue_map = [
    {"audio": "processed_audio/line_0_final.wav", "image": young_img, "clip_id": 0},
    {"audio": "processed_audio/line_1_final.wav", "image": old_img,   "clip_id": 1},
    {"audio": "processed_audio/line_2_final.wav", "image": young_img, "clip_id": 2},
    {"audio": "processed_audio/line_3_final.wav", "image": old_img,   "clip_id": 3},
    {"audio": "processed_audio/line_4_final.wav", "image": young_img, "clip_id": 4},
    {"audio": "processed_audio/line_5_final.wav", "image": old_img,   "clip_id": 5},
    {"audio": "processed_audio/line_6_final.wav", "image": young_img, "clip_id": 6},
    {"audio": "processed_audio/line_7_final.wav", "image": young_img, "clip_id": 7},
    {"audio": "processed_audio/line_8_final.wav", "image": old_img,   "clip_id": 8},
]

os.makedirs("sadtalker_outputs", exist_ok=True)

for item in dialogue_map:
    print(f"🎬 جاري توليد تحريك المقطع رقم {item['clip_id']}...")
    cmd = f"""python inference.py \
        --driven_audio {item['audio']} \
        --source_image {item['image']} \
        --result_dir ./sadtalker_outputs/ \
        --still \
        --preprocess full"""
    subprocess.run(cmd, shell=True)

print("✅ تم تحريك كافة الصور ومطابقة الشفاه بالصوت بنجاح!")

#===============================================================
# ==========================================
# الخلية 6: تجميع المقاطع والمونتاج النهائي عبر MoviePy وتحميل الفيديو
# ==========================================
import glob
from moviepy.editor import VideoFileClip, concatenate_videoclips
from google.colab import files

# تجميع الفيديوهات المولدة من مجلد مخرجات SadTalker
generated_clips = sorted(glob.glob("sadtalker_outputs/*.mp4"))

clips = [VideoFileClip(c) for c in generated_clips]

# دمج جميع المقاطع بالترتيب الصحيح للحوار
final_video = concatenate_videoclips(clips, method="compose")
output_filename = "final_ai_conversation_video.mp4"

# تصدير الفيديو بأفضل جودة وصوت
final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")

print("🎉 الفيديو النهائي جاهز للتحميل!")
files.download(output_filename)
