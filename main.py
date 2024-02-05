import os
import praw
import pyttsx3
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Set the path to the ImageMagick binary (update the path according to your installation)
os.environ["IMAGEMAGICK_BINARY"] = "C:\\Program Files\\ImageMagick-7.0.11-Q16-HDRI\\magick.exe"

def generate_speech_and_get_duration(text, output_file):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 150)
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    # Assuming the speech rate is 150 words per minute, calculate average duration per word
    words_per_minute = 150
    words = text.split()
    total_duration = len(words) / words_per_minute * 60  # Convert to seconds
    return total_duration, len(words)

# Generate speech audio and get estimated duration and word count
audio_file_path = "output_tts.mp3"
total_duration, word_count = generate_speech_and_get_duration(text_to_speech, audio_file_path)

# Load the audio to get its actual duration
audio_clip = AudioFileClip(audio_file_path)
actual_duration = audio_clip.duration

# Calculate average duration per word based on actual audio duration
avg_duration_per_word = actual_duration / word_count

# Create text clips using the calculated average duration
text_clips = []
current_time = 0
for word in text_to_speech.split():
    txt_clip = TextClip(word, fontsize=48, color='white', font="Arial-Bold",
                        size=(video_clip.w, video_clip.h))
    txt_clip = txt_clip.set_position('center').set_duration(avg_duration_per_word).set_start(current_time)
    text_clips.append(txt_clip)
    current_time += avg_duration_per_word

# Create a composite clip that includes the video, audio, and timed text clips
final_clip = CompositeVideoClip([video_clip.set_audio(audio_clip)] + text_clips, size=video_clip.size)

final_video_path = "final_synced_video.mp4"
final_clip.write_videofile(final_video_path, fps=24)

if best_post:
    # Text from the best post within character limit
    text_to_speech = best_post.title + ". " + best_post.selftext
    
    # Generate speech from text
    audio_file_path = "output_tts.mp3"
    generate_speech(text_to_speech, audio_file_path)
    
    # Load video and audio
    video_clip = VideoFileClip(video_file_path)
    audio_clip = AudioFileClip(audio_file_path)
    video_clip = video_clip.set_audio(audio_clip).subclip(0, min(video_clip.duration, audio_clip.duration))

    # Split the text into words
    words = text_to_speech.split()

    # Create a list to store text clips for each word
    text_clips = []

    current_time = 0
    for word in words:
        duration = len(word) / 5.0  # Estimate duration based on word length
        # Create a text clip for the word, make it larger (e.g., fontsize=48) and bold
        # You might need to replace 'Arial-Bold' with a bold font available on your system
        txt_clip = TextClip(word, fontsize=48, color='white', font="Arial-Bold",
                            size=(video_clip.w, video_clip.h))
        # Set the txt_clip to be centered by manually specifying position
        txt_clip = txt_clip.set_position('center').set_duration(duration).set_start(current_time)
        text_clips.append(txt_clip)
        current_time += duration
    
    # Create a composite clip that combines the video and the text clips
    if text_clips:  # Ensure there are text clips to add
        final_text_clip = concatenate_videoclips(text_clips, method="compose")
        final_clip = CompositeVideoClip([video_clip, final_text_clip], size=video_clip.size)
    else:
        final_clip = video_clip  # No text clips, just use the original video
    
    # Specify the output file path
    final_video_path = "final_video_with_large_bold_text.mp4"
    # Write the final clip to file
    final_clip.write_videofile(final_video_path, fps=24)
    
    print(f"Video saved as {final_video_path}")
else:
    print("No suitable post found.")
