import os
import streamlit as st
from core_logic import process_audio_files, generate_sadtalker_videos, assemble_final_video

st.set_page_config(page_title="AI Dialogue Video Generator", layout="centered")

st.title("🎬 أداة توليد فيديو الحوار الذكي (SadTalker)")
st.write("قم برفع صور الشخصيتين وملفات الصوت الخاصة بالحوار، وسيتولى الذكاء الاصطناعي معالجة الدمج وتوليد الفيديو!")

# إنشاء المجلدات المؤقتة
os.makedirs("input_audio", exist_ok=True)
os.makedirs("input_images", exist_ok=True)

# --- واجهة رفع الملفات ---
st.subheader("1️⃣ رفع الصور الشخصية")
col1, col2 = st.columns(2)
with col1:
    young_img_file = st.file_uploader("صورة النسخة الصغرى (Young)", type=['jpg', 'jpeg', 'png'])
with col2:
    old_img_file = st.file_uploader("صورة النسخة الكبرى (Older)", type=['jpg', 'jpeg', 'png'])

st.subheader("2️⃣ رفع ملفات الصوت للحوار (من line_0 إلى line_8)")
uploaded_audios = st.file_uploader("اختر ملفات الصوت (WAV أو MP3)", type=['wav', 'mp3'], accept_multiple_files=True)

# --- زر التنفيذ وبدء المعالجة ---
if st.button("🚀 ابدأ توليد الفيديو النهائي", type="primary"):
    if young_img_file and old_img_file and uploaded_audios:
        
        # حفظ الصور في المجلدات
        young_img_path = "input_images/young_me.png"
        old_img_path = "input_images/older_me.png"
        
        with open(young_img_path, "wb") as f:
            f.write(young_img_file.getbuffer())
        with open(old_img_path, "wb") as f:
            f.write(old_img_file.getbuffer())
            
        # حفظ ملفات الصوت المرفوعة
        for audio_file in uploaded_audios:
            audio_path = os.path.join("input_audio", audio_file.name)
            with open(audio_path, "wb") as f:
                f.write(audio_file.getbuffer())
                
        with st.status("⏳ جاري تنفيذ مراحل المعالجة والتحريك...", expanded=True) as status:
            st.write("🎵 مرحلة معالجة وتعديل الأصوات...")
            process_audio_files("input_audio", "processed_audio")
            
            st.write("🎬 مرحلة تحريك الشفاه عبر SadTalker (قد تستغرق وقتاً)...")
            generate_sadtalker_videos(young_img_path, old_img_path, "processed_audio")
            
            st.write("🎞 مرحلة تجميع المقاطع والمونتاج النهائي...")
            final_video_path = assemble_final_video()
            
            status.update(label="✅ تمت العملية بنجاح!", state="complete", expanded=False)
            
        if final_video_path and os.path.exists(final_video_path):
            st.success("🎉 الفيديو جاهز للعرض والتحميل!")
            st.video(final_video_path)
            
            with open(final_video_path, "rb") as file:
                st.download_button(
                    label="📥 تحميل الفيديو النهائي",
                    data=file,
                    file_name="final_ai_conversation_video.mp4",
                    mime="video/mp4"
                )
        else:
            st.error("❌ حدث خطأ أثناء تجميع الفيديو، تأكد من رفع كافة ملفات الصوت المطلوبة.")
    else:
        st.warning("⚠️ الرجاء رفع صورتي الشخصيتين وملفات الصوت المعتمدة أولاً.")
