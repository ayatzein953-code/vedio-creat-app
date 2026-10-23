import os
import subprocess
import glob
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip, concatenate_videoclips

def convert_to_child_voice(input_path, output_path, pitch_steps=4.5):
    """رفع خامة الصوت وتردده ليبدو كأنه صوت طفل صغير"""
    y, sr = librosa.load(input_path, sr=None)
    y_child = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_steps)
    sf.write(output_path, y_child, sr)

def process_audio_files(input_audio_dir, output_audio_dir, young_indices=[0, 2, 4, 6, 7]):
    """معالجة كافة الملفات الصوتية وتعديل أصوات الأطفال"""
    os.makedirs(output_audio_dir, exist_ok=True)
    
    for idx in range(9):
        raw_audio = os.path.join(input_audio_dir, f"line_{idx}.wav")
        out_audio = os.path.join(output_audio_dir, f"line_{idx}_final.wav")
        
        if os.path.exists(raw_audio):
            if idx in young_indices:
                convert_to_child_voice(raw_audio, out_audio, pitch_steps=4.5)
            else:
                y, sr = librosa.load(raw_audio, sr=None)
                sf.write(out_audio, y, sr)
    return True

def generate_sadtalker_videos(young_img_path, old_img_path, processed_audio_dir, output_sadtalker_dir="./sadtalker_outputs"):
    """استدعاء SadTalker لتحريك الصور بناءً على المقاطع الصوتية"""
    os.makedirs(output_sadtalker_dir, exist_ok=True)
    
    dialogue_map = [
        {"audio": os.path.join(processed_audio_dir, "line_0_final.wav"), "image": young_img_path, "clip_id": 0},
        {"audio": os.path.join(processed_audio_dir, "line_1_final.wav"), "image": old_img_path,   "clip_id": 1},
        {"audio": os.path.join(processed_audio_dir, "line_2_final.wav"), "image": young_img_path, "clip_id": 2},
        {"audio": os.path.join(processed_audio_dir, "line_3_final.wav"), "image": old_img_path,   "clip_id": 3},
        {"audio": os.path.join(processed_audio_dir, "line_4_final.wav"), "image": young_img_path, "clip_id": 4},
        {"audio": os.path.join(processed_audio_dir, "line_5_final.wav"), "image": old_img_path,   "clip_id": 5},
        {"audio": os.path.join(processed_audio_dir, "line_6_final.wav"), "image": young_img_path, "clip_id": 6},
        {"audio": os.path.join(processed_audio_dir, "line_7_final.wav"), "image": young_img_path, "clip_id": 7},
        {"audio": os.path.join(processed_audio_dir, "line_8_final.wav"), "image": old_img_path,   "clip_id": 8},
    ]

    for item in dialogue_map:
        if os.path.exists(item["audio"]):
            cmd = f"""python SadTalker/inference.py \
                --driven_audio {item['audio']} \
                --source_image {item['image']} \
                --result_dir {output_sadtalker_dir} \
                --still \
                --preprocess full"""
            subprocess.run(cmd, shell=True)

def assemble_final_video(output_sadtalker_dir="./sadtalker_outputs", final_output_path="final_ai_conversation_video.mp4"):
    """تجميع المقاطع النهائية باستخدام MoviePy"""
    generated_clips = sorted(glob.glob(os.path.join(output_sadtalker_dir, "*.mp4")))
    if not generated_clips:
        return None
        
    clips = [VideoFileClip(c) for c in generated_clips]
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(final_output_path, fps=24, codec="libx264", audio_codec="aac")
    
    return final_output_path
