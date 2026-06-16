
import os
import json
from natsort import natsorted
from pydub import AudioSegment


def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_in_ms = len(audio)
    duration_in_seconds = duration_in_ms / 1000
    duration_in_minutes = duration_in_seconds / 60
    return duration_in_minutes

def cut_audio(input_file, output_file, start_time, end_time):
    # Load the audio file
    if input_file.endswith('.wav'):
        audio = AudioSegment.from_file(input_file)
    else:
        audio = AudioSegment.from_mp3(input_file)
    # Cut the audio
    start_time_ms = start_time * 1000
    end_time_ms = end_time * 1000

    cut_audio = audio[start_time_ms:end_time_ms]
    cut_audio.export(output_file, format="wav")
    print("pass")



def split_audio(input_file, output_dir):
    # Load the audio file
    if input_file.endswith('.wav'):
        audio = AudioSegment.from_file(input_file)
    else:
        audio = AudioSegment.from_mp3(input_file)
    # Length of each segment in milliseconds
    segment_length_ms = 10000  # 10 seconds

    # Iterate through the audio, creating segments
    for i in range(0, len(audio), segment_length_ms):
        segment = audio[i:i+segment_length_ms]

        # Export each segment to a separate file
        segment.export(os.path.join(output_dir, f"segment_{i//10000}.wav"), format="wav")



def export_file_audio(file_paths, output_path):
    # Load each audio file
    files = natsorted(os.listdir(file_paths))
    audio_segments = [AudioSegment.from_file(os.path.join(file_paths, file_path)) for file_path in files]

    # merged = AudioSegment.empty()
    # for audio in audio_segments:
    #     break_duration_ms=300
    #     merged += audio
    #     break_segment = AudioSegment.silent(duration=break_duration_ms)
    #     merged += break_segment
    # merged.export(output_path, format="wav")

    # Concatenate the audio segments
    merged_audio = sum(audio_segments)
    # Export the merged audio to a new file
    merged_audio.export(output_path, format="wav")
    return output_path


def merger_json(file_path, chapter):
    with open(file_path, "r") as file:
        data = json.load(file)
    start_time = data[0]["startTime"]
    end_time = data[-1]["endTime"]
    text_content = '. '.join(item["text"] for item in data)
    outputs_dict = {}
    outputs_dict["chapter"] = str(chapter)
    outputs_dict["startTime"] = start_time
    outputs_dict["endTime"] = end_time
    outputs_dict["text"] = text_content
    return outputs_dict