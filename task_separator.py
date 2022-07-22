import os
import sys
import glob
from pathlib import Path
import argparse
from pydub import AudioSegment

arg_parser = argparse.ArgumentParser(description="Cut wav files for each task and create its .words files")
arg_parser.add_argument("-s", "--session-folder", type=str, help="Folder with wavs, tasks and words")
arg_parser.add_argument("-o", "--output-path", help="Directory to save the output files")

def read_words(path):
    words_A = []
    words_B = []
    for filename in glob.glob(os.path.join(path, "*.words")):
        file_extensions = filename.split(".")
        with open(filename, encoding="utf-8", mode="r") as word_file:
            lines = word_file.read().splitlines() 

            if "A" in file_extensions:
                words_A = lines
            elif "B" in file_extensions:
                words_B = lines
                
    return words_A, words_B

def read_wavs(path):
    wav_A = (None, None)
    wav_B = (None, None)
    for wav_file in glob.glob(os.path.join(path, "*.wav")):
        file_extensions = wav_file.split(".")

        wav = AudioSegment.from_wav(wav_file)

        if "A" in file_extensions:
            wav_A = wav
        elif "B" in file_extensions:
            wav_B = wav
                
    return wav_A, wav_A 

def read_tasks(path):
    tasks = {}
    for filename in glob.glob(os.path.join(path, "*.tasks")):
        with open(filename, encoding="utf-8", mode="r") as tasks_file:
            lines = tasks_file.read().splitlines() 
            
            task_id = 1
            for line in lines:
                task_start, task_end, task_label = line.split(" ")
                task_start, task_end = float(task_start), float(task_end)
                if task_label.startswith("Images"):
                    tasks[task_id] = {"Start": task_start, "End": task_end, "Label": task_label}
                    task_id += 1
                
    return tasks

def read_session_name(path):
    first_file = glob.glob(os.path.join(path, "*.*.*.*.*"))[0]
    filename = os.path.split(first_file)[1]
    session_name = filename.split(".1")[0]
    return session_name

def cut_wav_for_each_task(wav, tasks, output_path, session_name, speaker):
    for task_id, task in tasks.items():
        # Convert times to milliseconds
        task_start, task_end = task["Start"] * 1000, task["End"] * 1000
        task_wav = wav[task_start:task_end]
        task_wav_name = session_name + f".1.{task_id}" + f".{speaker}.wav"
        output_dir = os.path.join(output_path, task_wav_name)
        task_wav.export(output_dir, format="wav")
        print(f'Saved wav for task {task_id} from speaker {speaker}: {task["Start"]}s - {task["End"]}s')


def create_words_for_each_task(words, tasks, output_path, session_name, speaker):
    for task_id, task in tasks.items():
        words_task_name = session_name + f".1.{task_id}" + f".{speaker}.words"
        words_filename = os.path.join(output_path, words_task_name)
        with open(words_filename, encoding="utf-8", mode="w") as word_file:
            for line in words:
                word_start, word_end, word = line.split(" ")
                word_start, word_end = float(word_start), float(word_end)
                if word_start > task["Start"] and word_end < task["End"]: # TO-ASK: What if a word is between tasks?
                    word_start, word_end = word_start - task["Start"], word_end - task["Start"] 
                    word_file.write(f"{word_start} {word_end} {word}\n")
        print(f"Wrote .words for task {task_id}")



def main() -> None:

    args = arg_parser.parse_args()
    session_path = Path(args.session_folder)

    words_A, words_B = read_words(session_path)

    wav_A, wav_B = read_wavs(session_path)

    tasks = read_tasks(session_path)
    print(f'There are {len(tasks)} tasks in this session')

    output_path = Path(args.output_path)
    session_name = read_session_name(session_path)
    cut_wav_for_each_task(wav_A, tasks, output_path, session_name, "A")
    cut_wav_for_each_task(wav_B, tasks, output_path, session_name, "B")
    
    create_words_for_each_task(words_A, tasks, output_path, session_name, "A")
    create_words_for_each_task(words_B, tasks, output_path, session_name, "B")

if __name__ == "__main__":
    main()
