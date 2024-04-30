import os
import Levenshtein
import ffmpeg
import random
import subprocess

from IPython.display import Audio
from faster_whisper import WhisperModel
import json

from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips,VideoFileClip, AudioFileClip
import numpy as np


#delete most similar word
def find_most_similar_word(word, word_list, threshold=3):
    min_distance = float('inf')
    most_similar_word = None
    for candidate in word_list:
        distance = Levenshtein.distance(word, candidate)
        if distance < min_distance and distance <= threshold:
          min_distance = distance
          most_similar_word = candidate
          word_list.remove(candidate)
    return most_similar_word
def split_text_into_lines(data):

    MaxChars = 3
    #maxduration in seconds
    MaxDuration = 2.5
    #Split if nothing is spoken (gap) for these many seconds
    MaxGap = 1.5

    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0


    for idx,word_data in enumerate(data):
        word = word_data["word"]
        if(word != ""):
          start = word_data["start"]
          end = word_data["end"]

          line.append(word_data)
          line_duration += end - start

          temp = " ".join(item["word"] for item in line)


          # Check if adding a new word exceeds the maximum character count or duration
          new_line_chars = len(temp)

          duration_exceeded = line_duration > MaxDuration
          chars_exceeded = new_line_chars > MaxChars
          if idx>0:
            gap = word_data['start'] - data[idx-1]['end']
            # print (word,start,end,gap)
            maxgap_exceeded = gap > MaxGap
          else:
            maxgap_exceeded = False


          if duration_exceeded or chars_exceeded or maxgap_exceeded:
              if line:
                  subtitle_line = {
                      "word": " ".join(item["word"] for item in line),
                      "start": line[0]["start"],
                      "end": line[-1]["end"],
                      "textcontents": line
                  }
                  subtitles.append(subtitle_line)
                  line = []
                  line_duration = 0
                  line_chars = 0


    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)

    return subtitles
def create_caption(textJSON, framesize,font = "Liberation-Sans-Bold",color='white',stroke_color='black',stroke_width=1.5):
    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end']-textJSON['start']

    word_clips = []
    xy_textclips_positions =[]

    x_pos = 0
    y_pos = 0
    line_width = 0  # Total width of words in the current line
    frame_width = framesize[0]
    frame_height = framesize[1]

    x_buffer = frame_width*1/10

    max_line_width = frame_width - 2 * (x_buffer)

    fontsize = int(frame_height * 0.055) #7.5 percent of video height

    space_width = ""
    space_height = ""

    for index,wordJSON in enumerate(textJSON['textcontents']):
      duration = wordJSON['end']-wordJSON['start']
      word_clip = TextClip(wordJSON['word'], font = font,fontsize=fontsize, color=color,stroke_color=stroke_color,stroke_width=stroke_width).set_start(textJSON['start']).set_duration(full_duration)
      word_clip_space = TextClip(" ", font = font,fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)
      word_width, word_height = word_clip.size
      space_width,space_height = word_clip_space.size
      if line_width + word_width+ space_width <= max_line_width:
            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos,
                "y_pos": y_pos,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos, y_pos))
            #word_clip = word_clip.set_position('center')
            word_clip_space = word_clip_space.set_position((x_pos+ word_width, y_pos))

            x_pos = x_pos + word_width+ space_width
            line_width = line_width+ word_width + space_width
      else:
            # Move to the next line
            x_pos = 0
            y_pos = y_pos+ word_height+10
            line_width = word_width + space_width

            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos,
                "y_pos": y_pos,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_space = word_clip_space.set_position((x_pos+ word_width , y_pos))
            x_pos = word_width + space_width


      word_clips.append(word_clip)
      word_clips.append(word_clip_space)


    #for highlight_word in xy_textclips_positions:

      #word_clip_highlight = TextClip(highlight_word['word'], font = font,fontsize=fontsize, color=highlight_color,stroke_color=stroke_color,stroke_width=stroke_width).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
      #word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
      #word_clips.append(word_clip_highlight)

    return word_clips,xy_textclips_positions




audio = "audio.mp3"
videofilename = "/content/Subway Surfer.MP4"

model_size = "medium"
model = WhisperModel(model_size)

sentence = "Being constantly blocked unblocked, blocked, unblocked is actually wild, you wanna do something ask it and say it with your chest"

actual_words = [(word, False) for word in sentence.split()]
actual_words = [[word, flag] for word, flag in actual_words]
segments, info = model.transcribe(audio, word_timestamps=True)
segments = list(segments) 

wordlevel_info = []
holder = []
global_index = 0

for segment in segments:
    for word in segment.words:
        word_info = {
            'word': word.word,
            'start': word.start,
            'end': word.end,
            'match': False,
            'index': global_index
        }
        wordlevel_info.append(word_info)
        global_index += 1
    
for i in range(len(wordlevel_info)):
  wordlevel_info[i]['word'] = wordlevel_info[i]['word'].strip()
  holder.append(wordlevel_info[i]['word'])


  duration_output = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', videofilename])

# Convert the output to string and extract the duration
duration = float(duration_output.decode('utf-8').strip())
# Generate a random start time within the valid range
duration = float(duration_output.decode('utf-8').strip())
crop_duration = wordlevel_info[len(wordlevel_info)-1]['end']

# Generate a random start time within the valid range
start_time = random.uniform(0, duration - crop_duration)
shortened = "shortened.mp4"
subprocess.run(['ffmpeg', '-ss', str(start_time), '-i', videofilename, '-t', str(crop_duration), '-c', 'copy', shortened])


#Matching words that are already the same

for i in range(len(actual_words)):
  for j in range(len(holder)):
    if(actual_words[i][0].lower() == holder[j].lower()):
      holder[j] = ""
      wordlevel_info[j]['word'] = actual_words[i][0]
      wordlevel_info[j]['match'] = True
      actual_words[i][1] = True
      break

#repeat in word
new = []
for j in range(len(wordlevel_info)):
  if(wordlevel_info[j]['match'] == False):
    new.append(wordlevel_info[j]['word'])

temp_actual = []
for j in range(len(actual_words)):
  if(actual_words[j][1] == False):
    temp_actual.append(actual_words[j][0])

# Correcting transcribed words of non same words
for transcribed_word in new:
    most_similar_actual_word = find_most_similar_word(transcribed_word, temp_actual)
    for word in wordlevel_info:
      if(word['word'] == transcribed_word):
        word['word'] = most_similar_actual_word

#correcting the timing
for i in range(len(wordlevel_info)):
  if wordlevel_info[i]['word'] == None:
    wordlevel_info[i]['word'] = ""
    if(i == 0):
      wordlevel_info[1]['start'] = wordlevel_info[i]['start']
      break
    else:
      wordlevel_info[i-1]['end'] = wordlevel_info[i]['end']

with open('data.json', 'w') as f:
    json.dump(wordlevel_info, f,indent=4)


linelevel_subtitles = split_text_into_lines(wordlevel_info)
for line in linelevel_subtitles:
  json_str = json.dumps(line, indent=4)


input_video = VideoFileClip(shortened)
frame_size = input_video.size

all_linelevel_splits=[]

for line in linelevel_subtitles:
  out_clips,positions = create_caption(line,frame_size)

  max_width = 0
  max_height = 0

  for position in positions:
    # print (out_clip.pos)
    # break
    x_pos, y_pos = position['x_pos'],position['y_pos']
    width, height = position['width'],position['height']

    max_width = max(max_width, x_pos + width)
    max_height = max(max_height, y_pos + height)

  color_clip = ColorClip(size=(int(max_width*1.1), int(max_height*1.1)),
                       color=(64, 64, 64))
  color_clip = color_clip.set_opacity(0)
  color_clip = color_clip.set_start(line['start']).set_duration(line['end']-line['start'])

  centered_clips = [each.set_position('center') for each in out_clips]

  clip_to_overlay = CompositeVideoClip([color_clip]+ out_clips)
  clip_to_overlay = clip_to_overlay.set_position("center")


  all_linelevel_splits.append(clip_to_overlay)

input_video_duration = input_video.duration


final_video = CompositeVideoClip([input_video] + all_linelevel_splits)

# Set the audio of the final video to be the same as the input video
final_video = final_video.set_audio(AudioFileClip(audio))


# Save the final clip as a video file with the audio included
final_video.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")
