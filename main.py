import os
import praw
import pyttsx3
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Set the path to the ImageMagick binary (update the path according to your installation)
os.environ["IMAGEMAGICK_BINARY"] = "C:\\Program Files\\ImageMagick-7.0.11-Q16-HDRI\\magick.exe"

def generate_speech(text, output_file):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Choose the desired voice
    engine.setProperty('rate', 150)  # Adjust speech rate as needed
    engine.save_to_file(text, output_file)
    engine.runAndWait()

# Setup for Reddit API
reddit = praw.Reddit(client_id='aYYgP0cb-iS-BBxJr6BNbA',
                     client_secret='OLzyI472QBfgJ40ai1sBiGvUi9GcCA',
                     user_agent='Plutus')

# Choose your subreddit
subreddit_name = 'stories'  # Target subreddit
subreddit = reddit.subreddit(subreddit_name)

# Fetch top posts
top_posts = subreddit.top("day", limit=50)  # Adjust limit as needed

# Initialize variables to find the best post
best_post = None
best_score = -1

for post in top_posts:
    # Calculate score based on comments and upvotes
    score = post.num_comments + post.score
    # Check if the post's content length is within the desired limit and if it has the highest score
    if score > best_score and len(post.title + ". " + post.selftext) <= 1000:
        best_score = score
        best_post = post

# Define the path to your Minecraft parkour video
video_file_path = "minecraft_parkour.mp4"

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

    # Create text clips for each word and set their durations
    current_time = 0
    for word in words:
        duration = len(word) / 5.0  # Adjust the duration based on word length
        txt_clip = TextClip(word, fontsize=24, color='white', align='center', size=(video_clip.w, 30), bg_color='black')
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration).set_start(current_time)
        text_clips.append(txt_clip)
        current_time += duration

    # Concatenate the text clips and add them to the video
    final_text_clip = concatenate_videoclips(text_clips)
    final_clip = CompositeVideoClip([video_clip, final_text_clip])

    # Save the final video with synchronized text overlay
    final_video_path = "final_video_with_text.mp4"
    final_clip.write_videofile(final_video_path, fps=24)
    
    print(f"Video saved as {final_video_path}")
else:
    print("No suitable post found.")
