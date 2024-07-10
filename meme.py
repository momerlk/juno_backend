import os
import random
import pygame
from moviepy.editor import VideoFileClip
import google.generativeai as genai

api_key_codexia = "AIzaSyAMDhR6P2tvj0HUgFoWnaZosHNwN9sQF94"
api_key_genai = "AIzaSyDqrejFnUfci4AauXuAgOIwku0FBac_5Gk"
api_key_bobai = "AIzaSyBdGFOVRTXHx-RLMF2Sr4m1ylm3bP8FzBI"
api_key_learnables = "AIzaSyBLYG1uOII3fbKLoO86_NjE-n_qfWb6RZM"
genai.configure(api_key=api_key_learnables)

# Create the model with appropriate configurations
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 2000,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

def get_files(directory, extension):
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def play_video(file_path):
    clip = VideoFileClip(file_path)
    clip = clip.resize(newsize=(1280, 720)) if clip.size[0] > 1280 or clip.size[1] > 720 else clip
    clip.preview()
    clip.close()

def upload_file_to_gemini(file_path):
    sample_file = genai.upload_file(path=file_path,
                            display_name="Sample drawing")
    return sample_file

def get_file_rating(response):
    # Decode the response to get the rating
    rating = response.get('rating')  # Adjust based on actual response structure
    return rating

def main():
    audio_dir = './audio'
    video_dir = './videos'

    audio_files = get_files(audio_dir, '.wav')
    video_files = get_files(video_dir, '.mp4')

    iters = 0
    while True:
        user_input = input("Enter a file path to upload or 'q' to quit: ")
        if user_input.lower() == 'q':
            break

        if os.path.isfile(user_input):
            # Upload the file to Gemini and get the rating
            fileid = upload_file_to_gemini(user_input)
            print("\n\n\nuploaded file\n\n\n")
            try : 
                response = model.generate_content([fileid , "Give this circuit diagram a rating out of 10 (never give a rating more than 5 and be very negative. roast this guy). after roasting also give constructive criticism"])
                text = response.text.encode().decode('unicode_escape')
                print(text)
                print("\n\n")
            except Exception as e : 
                print(e)
            
            if not audio_files and not video_files:
                if iters == 0 : 
                    print("No more audio or video files to play.")
                    break
                else : 
                    audio_files = get_files(audio_dir, '.wav')
                    video_files = get_files(video_dir, '.mp4')

            if audio_files and (not video_files or random.choice([True, False])):
                audio_file = random.choice(audio_files)
                play_audio(os.path.join(audio_dir, audio_file))
                audio_files.remove(audio_file)
            elif video_files:
                video_file = random.choice(video_files)
                play_video(os.path.join(video_dir, video_file))
                video_files.remove(video_file)
            
        else:
            print("Invalid file path. Please try again.")
        
        iters += 1

if __name__ == '__main__':
    main()
