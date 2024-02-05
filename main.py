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

    current_time = 0
    for word in words:
        duration = len(word) / 5.0  # Estimate duration based on word length
        # Create a text clip for the word, customized as needed
        txt_clip = TextClip(word, fontsize=24, color='white', bg_color='black',
                            size=(video_clip.w, video_clip.h))
        # Set the txt_clip to be centered by manually specifying position
        # Here, we make the text clip cover the entire video frame and rely on alignment
        txt_clip = txt_clip.set_position('center').set_duration(duration).set_start(current_time)
        text_clips.append(txt_clip)
        current_time += duration
    
    # Create a composite clip that combines the video and the text clips
    # The `CompositeVideoClip` constructor takes a list of clips, where the first clip is the base,
    # and subsequent clips are layered on top. By adding `text_clips` on top of `video_clip`,
    # we ensure the text is displayed above the video content.
    if text_clips:  # Ensure there are text clips to add
        # Combine text clips into a single clip
        final_text_clip = concatenate_videoclips(text_clips, method="compose")
        # Layer the text clip over the video
        final_clip = CompositeVideoClip([video_clip, final_text_clip], size=video_clip.size)
    else:
        final_clip = video_clip  # No text clips, just use the original video
    
    # Specify the output file path
    final_video_path = "final_video_with_text_centered.mp4"
    # Write the final clip to file
    final_clip.write_videofile(final_video_path, fps=24)
    
    print(f"Video saved as {final_video_path}")
else:
    print("No suitable post found.")
