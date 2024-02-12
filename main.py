import os
import praw
import pyttsx3
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
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
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='')

# List of subreddits to choose from
subreddits = ["AmItheAsshole", "stories", "relationship_advice"]

# Fetch a random post from the selected subreddits with content length between 500 and 1000 characters
selected_post = None

# Keep trying different subreddits until a suitable post is found
while selected_post is None and subreddits:
    subreddit_name = random.choice(subreddits)
    subreddit = reddit.subreddit(subreddit_name)
    posts = list(subreddit.hot(limit=100))  # Fetch up to 100 hot posts

    # Filter posts by content length criteria
    filtered_posts = [post for post in posts if 500 < len(post.title + ". " + post.selftext) <= 1000]

    if filtered_posts:
        selected_post = random.choice(filtered_posts)
    else:
        subreddits.remove(subreddit_name)  # Remove the subreddit from the list if no suitable post is found

# Define the path to your Minecraft parkour video
video_file_path = "minecraft_parkour.mp4"

if selected_post:
    # Text from the selected post within character limit
    text_to_speech = selected_post.title + ". " + selected_post.selftext
    
    # Generate speech from text
    audio_file_path = "output_tts.mp3"
    generate_speech(text_to_speech, audio_file_path)
    
    # Load video and audio
    video_clip = VideoFileClip(video_file_path)
    audio_clip = AudioFileClip(audio_file_path)
    video_clip = video_clip.set_audio(audio_clip).subclip(0, min(video_clip.duration, audio_clip.duration))

    # Generate speech audio and get estimated duration and word count
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

    total_duration, word_count = generate_speech_and_get_duration(text_to_speech, audio_file_path)

    # Load the audio to get its actual duration
    audio_clip = AudioFileClip(audio_file_path)
    actual_duration = audio_clip.duration

    # Calculate average duration per word based on actual audio duration
    avg_duration_per_word = actual_duration / word_count

    # Create text clips using the calculated average duration
    speed_up_factor = 0.9
    avg_duration_per_word *= speed_up_factor

    # Create text clips using the adjusted average duration, with a black border around the text
    text_clips = []
    current_time = 0
    for word in text_to_speech.split():
        # Determine duration; if word ends with a period, add a pause
        duration = avg_duration_per_word
        if word.endswith('.'):
            duration += 1.5  # Add an extra second for a pause, adjust as needed for speed up
        
        # Adjust duration for speeding up
        duration *= speed_up_factor  # This line is actually redundant if avg_duration_per_word has been adjusted globally
        
        txt_clip = TextClip(word, fontsize=48, color='yellow', font="Arial-Bold",
                            size=(video_clip.w, video_clip.h),
                            stroke_color='black', stroke_width=1)
        txt_clip = txt_clip.set_position('center').set_duration(duration).set_start(current_time)
        text_clips.append(txt_clip)
        current_time += duration

    # Create a composite clip that includes the video, audio, and timed text clips with black borders
    final_clip = CompositeVideoClip([video_clip.set_audio(audio_clip)] + text_clips, size=video_clip.size)

    final_video_path = "final_synced_video.mp4"
    final_clip.write_videofile(final_video_path, fps=24)

    print(f"Video saved as {final_video_path}")
else:
    print("No suitable post found.")
