import os
import praw
import pyttsx3
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import httplib2
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow, argparser
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import random

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
reddit = praw.Reddit(client_id='aYYgP0cb-iS-',
                     client_secret='',
                     user_agent='Plutus')

# List of subreddits to choose from
subreddits = ["AmItheAsshole", "stories", "relationship_advice"]

# Choose a subreddit randomly from the list
subreddit_name = random.choice(subreddits)
subreddit = reddit.subreddit(subreddit_name)

# Fetch top posts
top_posts = subreddit.top("day", limit=50)  # Adjust limit as needed

# Initialize variables to find the best post
best_post = None
best_score = -1


while best_post is None:
    for post in top_posts:
        # Calculate score based on comments and upvotes
        score = post.num_comments + post.score
        # Check if the post's content length is within the desired limit and if it has the highest score
        if score > best_score and len(post.title + ". " + post.selftext) <= 1000 and len(post.title + ". " + post.selftext) > 500:
            best_score = score
            best_post = post
            break  # Exit the loop when a suitable post is found


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
        txt_clip = TextClip(word, fontsize=48, color='yellow', font="Arial-Bold",
                            size=(video_clip.w, video_clip.h))
        txt_clip = txt_clip.set_position('center').set_duration(avg_duration_per_word).set_start(current_time)
        text_clips.append(txt_clip)
        current_time += avg_duration_per_word

    # Create a composite clip that includes the video, audio, and timed text clips
    final_clip = CompositeVideoClip([video_clip.set_audio(audio_clip)] + text_clips, size=video_clip.size)

    final_video_path = "final_synced_video.mp4"
    final_clip.write_videofile(final_video_path, fps=24)

    print(f"Video saved as {final_video_path}")
else:
    print("No suitable post found.")
