import os
import time
import threading
import json
import shutil
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

from kafka import send_message

from utils import split_audio, merger_json, get_audio_duration, cut_audio

app = FastAPI()

global PROCESS_INFER, PROCESS_TRAIN
UPLOAD_AUDIOS_FOLDER =  "upload_audios"
DATASET_RAW_FOLDER_SAVE = "dataset_raw"
INFERENCE_AUDIO_FOLDER = "inference_audio"
AUDIO_TEST_FROM_UPLOAD_FOLDER = "audio_test_from_upload"
INFOR_OF_AUDIO_FOLDER = "info_of_audio"

EXPORT_AUDIO_PATH = "/home/inresai/Desktop/Inresai-source-code/book-ml/export_audios"

MAX_FILE_SIZE_MB = 100
MIN_FILE_SIZE_MB = 10
START_TIME_CUT = 0
END_TIME_CUT = 120 # 2 minutes
PROCESS_INFER = True
PROCESS_TRAIN = True


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Progess:
    def __init__(self, id, status) -> None:
        self.id = id
        self.status = status

@app.get("/processing-all/{bookId}")
def get_processing_all(bookId):
    inference_audio_path = os.path.join("logs/44k")
    path_voice_ids_call = os.path.join("voiceId_call", bookId)
    if not os.path.exists(path_voice_ids_call):
        return {"status": "failed",
                "message": "voice not in server"}
    voiceIds_call = os.listdir(path_voice_ids_call)


    if not os.path.exists(inference_audio_path):
        json_outputs = [
            {    "ebook": str(bookId),
                "progress" : str(0.0)
            },
            {
                "voice":[
                ],
                "progress": str(0.0)
            },
            {
            "summary": [
                    {
                        "name": "summary audio first",
                        "progress": str(1.0)
                    },
                    {
                        "name": "summary audio second",
                        "progress": str(1.0)
                    },
                    {
                        "name": "summary transcript first",
                        "progress": str(1.0)
                    },
                    {
                        "name": "summary transcript second",
                        "progress": str(1.0)
                    }
                ],
                "progress": str(1.0)
            }
            ]
        for voice in voiceIds_call:
            sample = {}
            sample["name"] = str(voice[:-4])
            sample["progress"] = str(0.0)
            json_outputs[1]["voice"].append(sample)
        return json_outputs

    if not os.path.exists("process_infer/{bookId}".format(bookId=bookId)):
        json_outputs = [
            {    "ebook": str(bookId),
                "progress" : str(0.0)
            },
            {
                "voice":[
                ],
                "progress": str(0.0)
            },
            {
            "summary": [
                    {
                        "name": "summary audio first",
                        "progress": str(0.0)
                    },
                    {
                        "name": "summary audio second",
                        "progress": str(0.0)
                    },
                    {
                        "name": "summary transcript first",
                        "progress": str(0.0)
                    },
                    {
                        "name": "summary transcript second",
                        "progress": str(0.0)
                    }
                ],
                "progress": str(0.0)
            }
            ]
        for voice in voiceIds_call:
            sample = {}
            sample["name"] = str(voice[:-4])
            sample["progress"] = str(0.0)
            json_outputs[1]["voice"].append(sample)
        return json_outputs
    
    voices_trained = os.listdir("logs/44k")
    process_infer_svc_voice = os.listdir("process_infer/{bookId}".format(bookId=bookId))

    if len(process_infer_svc_voice) == 0:
        json_outputs = [
            {    "ebook": str(bookId),
                "progress" : str(0.0)
            },
            {
                "voice":[
                ],
                "progress": str(0.0)
            },
            {
            "summary": [
                    {
                        "name": "summary audio first",
                        "progress": str(1.0)
                    },
                    {
                        "name": "summary audio second",
                        "progress": str(1.0)
                    },
                    {
                        "name": "summary transcript first",
                        "progress": str(1.0)
                    },
                    {
                        "name": "summary transcript second",
                        "progress": str(1.0)
                    }
                ],
                "progress": str(1.0)
            }
            ]
        for voice in voiceIds_call:
            sample = {}
            sample["name"] = str(voice[:-4])
            sample["progress"] = str(0.0)
            json_outputs[1]["voice"].append(sample)
        return json_outputs
    
    progress_book = round(len(process_infer_svc_voice) / len(voices_trained), 2)

    path_of_voice_root = os.path.join(EXPORT_AUDIO_PATH, "first", bookId)
    if not os.path.exists(path_of_voice_root) and len(os.listdir(path_of_voice_root)) > 0:
        json_outputs = [
            {    "ebook": str(bookId),
                "progress" : str(0.0)
            },
            {
                "voice":[
                ],
                "progress": str(0.0)
            },
            {
            "summary": [
                    {
                        "name": "summary audio first",
                        "progress": str(0.0)
                    },
                    {
                        "name": "summary audio second",
                        "progress": str(0.0)
                    },
                    {
                        "name": "summary transcript first",
                        "progress": str(0.0)
                    },
                    {
                        "name": "summary transcript second",
                        "progress": str(0.0)
                    }
                ],
                "progress": str(0.0)
            }
            ]
        for voice in voiceIds_call:
            sample = {}
            sample["name"] = str(voice[:-4])
            sample["progress"] = str(0.0)
            json_outputs[1]["voice"].append(sample)
        return json_outputs
    

    json_outputs = [
        {    "ebook": str(bookId),
            "progress" : str(progress_book)
        },
        {
            "voice":[
            ],
            "progress": str(1.0)
        },
        {
           "summary": [
                {
                    "name": "summary audio first",
                    "progress": str(1.0)
                },
                {
                    "name": "summary audio second",
                    "progress": str(1.0)
                },
                {
                    "name": "summary transcript first",
                    "progress": str(1.0)
                },
                {
                    "name": "summary transcript second",
                    "progress": str(1.0)
                }
            ],
            "progress": str(1.0)
        }
        ]

    sum_of_progess = 0.0
    for voice in voiceIds_call:
        sample = {}
        progress_audio = 0.0
        path_voice = os.path.join("inference_audio", bookId, voice[:-4])

        if os.path.exists(path_voice):
            len_path_audio_inference = len(os.listdir(path_voice))
        else:
            len_path_audio_inference = 0


        if len(path_of_voice_root) > 0:
            progress_audio = float(len_path_audio_inference / len(os.listdir(path_of_voice_root)))
            sum_of_progess+=progress_audio

        sample["name"] = str(voice[:-4])
        sample["progress"] = str(progress_audio)
        json_outputs[1]["voice"].append(sample)
    sum_of_progess = sum_of_progess/len(voiceIds_call)
    json_outputs[1]["progress"] = str(sum_of_progess)
    json_outputs[0]["progress"] = str(sum_of_progess)
    return json_outputs




@app.get("/all-voice-svc")
def get_svc_voice():
    voices = []
    path_svc_voice = "upload_audios"
    voice_svc = os.listdir(path_svc_voice)

    for voiceId in voice_svc:
        path_progress_status  = os.path.join("progress_status", voiceId+".txt")
        with open(path_progress_status, "r", encoding="utf-8") as f:
            status = f.read()
        if status == "done":
            voices.append(Progess(str(voiceId), "ok"))
        elif status == "training":
            voices.append(Progess(str(voiceId), "progress"))
        elif status == "upload":
            voices.append(Progess(str(voiceId), "failed"))
        
    if len(voices) > 0:
        return {"ids": voices}
    else:
        return {"status":"failed",
                "message":"no svc voice"}
    
@app.get("/check-progress-book/{bookId}")
def check_progress_book(bookId):
        list_voice = os.listdir("logs/44k")
        status = {}
        path_process_infer_svc = os.path.join("process_infer", bookId)
        if not os.path.exists(path_process_infer_svc):
            return {"status": "Failed",
                    "message": "book not in server"}
        process_infer_svc_voice = os.listdir("process_infer/{bookId}".format(bookId=bookId))




        if len(process_infer_svc_voice) == len(list_voice):
            voice_ids = [name[:-4] for name in process_infer_svc_voice]
            status[bookId] = "OK"
            status["voiceIds"] = voice_ids

        elif len(process_infer_svc_voice) < len(list_voice) and len(process_infer_svc_voice) > 0:
            voice_ids = []
            for voice in process_infer_svc_voice:
                path_voice_exist = os.path.join("process_infer", bookId, voice)
                if os.path.exists(path_voice_exist):
                    voice_ids.append(voice[:-4])
            status[bookId] = "OK"
            status["voiceIds"] = voice_ids
        else:
            status[bookId] = "Failed"
            status["voiceIds"] = []
        return status
            


@app.get("/get-audio-svc/{bookId}/{voiceId}/{chapter}")
def get_audio_svc(bookId, voiceId, chapter):
    audio_file = os.path.join(INFERENCE_AUDIO_FOLDER, bookId, voiceId, chapter+".wav")
    if not os.path.exists(audio_file):
        return {"status": "failed",
                "message": "audio convert not found"}
    return FileResponse(path=audio_file, media_type="audio/wav")


@app.get("/process-infer-voice-svc/{voiceId}/{bookId}")
def get_process_infer_voice_svc(voiceId, bookId):
    # try:
        list_voice = os.listdir("logs/44k")
        status = {}
        path_process_voice_infer = os.path.join("process_infer", bookId)
        process_infer_svc_voice = os.listdir(path_process_voice_infer)

        if len(process_infer_svc_voice) == len(list_voice):
            status[voiceId] = "OK"
            status[bookId] = "OK"
        elif voiceId + ".txt" in process_infer_svc_voice:
            status[voiceId] = "OK"
            status[bookId] = "Progress"
        else:
            status[voiceId] = "Progress"
            status[bookId] = "Progress"
        return status
    # except Exception as e:
    #     return {"status": "failed", "message": str(e)}
 

    
# @app.get("/process-training-voice-svc/{voiceSvc}")
# def get_process_training_voice_svc(voiceSvc):
#     path_process_training_svc_voice = os.path.join("process_svc", voiceSvc+".txt")
#     if os.path.exists(path_process_training_svc_voice):
#         return {"status": "OK"}
#     else:
#         return {"status": "Progess"}
    
@app.delete("/delete-audio-svc/{voiceId}/{bookId}")
def delete_voice_svc(voiceId, bookId):
    path_process_svc_voice = os.path.join("process_svc", voiceId+".txt")
    if os.path.exists(path_process_svc_voice):
        os.remove(path_process_svc_voice)
    path_audiop_svc = os.path.join("inference_audio", voiceId)
    if os.path.exists(path_audiop_svc):
        shutil.rmtree(path_audiop_svc)

    path_weight_voice = os.path.join("logs/44k", voiceId)
    if os.path.exists(path_weight_voice):
        shutil.rmtree(path_weight_voice)

    path_upload_audios = os.path.join(UPLOAD_AUDIOS_FOLDER, voiceId)
    if os.path.exists(path_upload_audios):
        shutil.rmtree(path_upload_audios)

    path_check_process_train = os.path.join("progress_status", voiceId+".txt")
    if os.path.exists(path_check_process_train):
        os.remove(path_check_process_train)
    
    path_process_infer = os.path.join("process_infer", bookId)
    if os.path.exists(path_process_infer):
        shutil.rmtree(path_process_infer)

    path_voiceId_call = os.path.join("voiceId_call", voiceId+".txt")
    if os.path.exists(path_voiceId_call):
        os.remove(path_voiceId_call)

    path_voice_sample_test = os.path.join("audio_test_from_upload", voiceId)
    if os.path.exists(path_voice_sample_test):
        shutil.rmtree(path_voice_sample_test)

    path_info_of_audio = os.path.join(INFOR_OF_AUDIO_FOLDER, voiceId)
    if os.path.exists(path_info_of_audio):
        shutil.rmtree(path_info_of_audio)

    inference_audio = os.path.join(INFERENCE_AUDIO_FOLDER, bookId, voiceId)
    if os.path.exists(inference_audio):
        shutil.rmtree(inference_audio)
    return {"status": "sucessful"}
    




def run_convert(bookId, voiceId ,PROCESS_INFER):
    while(PROCESS_INFER):
        
        status_path_check = os.path.join("/home/inresai/Desktop/Inresai-source-code/book-ml/status/second", bookId+".txt")
        print(status_path_check)
        if not os.path.exists(status_path_check):
            continue
        path_process_book_infer = os.path.join("process_infer", bookId)
        if not os.path.exists(path_process_book_infer):
            os.mkdir(path_process_book_infer)
        save_inference_book_path = os.path.join(INFERENCE_AUDIO_FOLDER, bookId)
        save_inference_voice_path = os.path.join(save_inference_book_path, voiceId)

        if not os.path.exists(save_inference_book_path):
            os.mkdir(save_inference_book_path)
        if not os.path.exists(save_inference_voice_path):
            os.mkdir(save_inference_voice_path)

        path_voice_first = os.path.join(EXPORT_AUDIO_PATH, "first", bookId)
        if not os.path.exists(path_voice_first):
            return {"status": "failed",
                    "message": "audio first not found"}

        model_path = os.path.join("/home/inresai/Desktop/Inresai-source-code/Voice-convert/logs/44k", voiceId)
        
        for chapter in os.listdir(path_voice_first):
            print(chapter)
            path_voice_chapter = os.path.join(path_voice_first, chapter)
            path_voice_chapter_infer_wav = os.path.join(save_inference_voice_path, chapter)
            if not os.path.exists(path_voice_chapter):
                continue
            os.system("svc infer {a} -o {b} -m {c}".format(a = path_voice_chapter, b = path_voice_chapter_infer_wav, c = model_path))

        path_process_voice_infer = os.path.join(path_process_book_infer, voiceId+".txt")
        with open(path_process_voice_infer, "w", encoding="utf-8") as f:
            f.write("OK!")
        f.close()

        values = {"bookId": bookId ,
                    "type": "svc"}
        send_message(values)
        PROCESS_INFER = False


@app.get("/run-convert-audio-svc/{bookId}/{voiceId}")
def convert_audio_svc(bookId, voiceId):
    global PROCESS_INFER

    path_voiceId_book_call = os.path.join("voiceId_call", bookId)
    if not os.path.exists(path_voiceId_book_call):
        os.mkdir(path_voiceId_book_call)
    path_save_voiId = os.path.join(path_voiceId_book_call, voiceId+".txt")
    with open(path_save_voiId, "w", encoding="utf-8") as f:
        f.write("OK!")
    f.close()
    path_check_process_train = os.path.join("process_infer", bookId, voiceId+".txt")
    if os.path.exists(path_check_process_train):
        PROCESS_INFER = False
    else:
        PROCESS_INFER = True


    if PROCESS_INFER == True:
        proces = threading.Thread(target = run_convert, args=(bookId, voiceId, PROCESS_INFER))
        proces.daemon = True
        proces.start()
        return {'status': 'OK'}
    else:
        return {'status':'failed',
                'message': 'process is runing'}
    


@app.get("/train-model-audio-convert-svc")
def train_audio_from_voice_svc(voiceId):
    global PROCESS_TRAIN

    path_check_process_train = os.path.join("process_svc", voiceId+".txt")
    if os.path.exists(path_check_process_train):
        PROCESS_TRAIN = False
    else:
        PROCESS_TRAIN = True
    input_file_audio_origin = os.path.join(UPLOAD_AUDIOS_FOLDER, voiceId)
    file_audio = os.path.join(input_file_audio_origin, os.listdir(input_file_audio_origin)[0])

    if os.path.exists(DATASET_RAW_FOLDER_SAVE):
        shutil.rmtree(DATASET_RAW_FOLDER_SAVE)
    
    if not os.path.exists(DATASET_RAW_FOLDER_SAVE):
        os.mkdir(DATASET_RAW_FOLDER_SAVE)
    output_dir = os.path.join(DATASET_RAW_FOLDER_SAVE, voiceId)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)


    if PROCESS_TRAIN == True:
        output_model_path = os.path.join("logs/44k", voiceId)

        path_progress_status  = os.path.join("progress_status", voiceId+".txt")
        with open(path_progress_status, "w", encoding="utf-8") as f:
            f.write("training")
        f.close()
        proces = threading.Thread(target = run_script, args=(PROCESS_TRAIN, voiceId, output_model_path, file_audio, output_dir))
        proces.daemon = True
        proces.start()
        return {'status': 'OK'}
    else:
        return {'status':'failed',
                'message': 'process is runing'}


@app.post("/upload-audio-svc/{voiceId}")
async def upload_audio_svc(voiceId, file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file.file.seek(0, 2)  # Seek to end of file
    file_size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)  # Reset file pointer to beginning

    # if file_size_mb < MIN_FILE_SIZE_MB:
    #     return {"status": "failed",
    #             "message": "size of file < 10 mb"}
    # if file_size_mb > MAX_FILE_SIZE_MB:
    #     return {"status": "failed",
    #             "message": "size of file > 50 mb"}
    

    

    path_voice = os.path.join(UPLOAD_AUDIOS_FOLDER, voiceId)
    if os.path.exists(path_voice):
        shutil.rmtree(path_voice)

    if not os.path.exists(path_voice):
        os.mkdir(path_voice)
    with open(f"{path_voice}/{file.filename}", "wb") as f:
        f.write(file.file.read())
    
    path_voice = os.path.join(UPLOAD_AUDIOS_FOLDER, voiceId)
    file_audio = os.path.join(path_voice, os.listdir(path_voice)[0])
    if not os.path.exists(file_audio):
        return {"status": "failed",
                "message": "audio not found"}
    
    file_save_audio_test = os.path.join(AUDIO_TEST_FROM_UPLOAD_FOLDER, voiceId)
    if not os.path.exists(file_save_audio_test):
        os.mkdir(file_save_audio_test)
    

    cut_audio(file_audio, os.path.join(file_save_audio_test, voiceId+".wav"), 0, 120)
    time.sleep(3)


    file_size_mb = get_file_size(file_audio)
    file_duration = get_audio_duration(file_audio)
    path_info_of_audio = os.path.join(INFOR_OF_AUDIO_FOLDER, voiceId)
    if not os.path.exists(path_info_of_audio):
        os.mkdir(path_info_of_audio)
    with open(os.path.join(path_info_of_audio, voiceId+".txt"), "w", encoding="utf-8") as f:
        f.write(str(round(file_size_mb))+"\n")
        f.write(str(round(file_duration, 2)))   

    path_progress_status  = os.path.join("progress_status", voiceId+".txt")
    with open(path_progress_status, "w", encoding="utf-8") as f:
        f.write("upload")
    f.close()


    return {"message": f"File '{file.filename}' uploaded successfully"}



def get_file_size(file_path):
    # Check if file exists
    if os.path.exists(file_path):
        # Get file size in bytes
        size_bytes = os.path.getsize(file_path)
        # Convert bytes to megabytes
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    else:
        print("File not found.")
        return None


@app.get("/get-info-of-audio-file/{voiceId}")
def get_info_of_audio_file(voiceId):
    path_info_of_audio = os.path.join(INFOR_OF_AUDIO_FOLDER, voiceId)
    if not os.path.exists(path_info_of_audio):
        return {"status": "failed",
                "message": "audio not found"}
    with open(os.path.join(path_info_of_audio, voiceId+".txt"), "r", encoding="utf-8") as f:
        data = f.readlines()
    return {"size": data[0],
            "duration": data[1]}



# @app.get("/get-audio-sample/{voiceId}")
# def get_audio_sample(voiceId):
#     path_voice = os.path.join(UPLOAD_AUDIOS_FOLDER, voiceId)
#     if not os.path.exists(path_voice):
#         return {"status": "failed",
#                 "message": "voice not found"}
#     file_audio = os.path.join(path_voice, os.listdir(path_voice)[0])
#     if not os.path.exists(file_audio):
#         return {"status": "failed",
#                 "message": "audio not found"}
#     return FileResponse(path=file_audio, media_type="audio/wav")


@app.get("/get-audio-sample/{voiceId}")
def get_audio_sample(voiceId):
    audio_file = os.path.join(AUDIO_TEST_FROM_UPLOAD_FOLDER, voiceId)
    if not os.path.exists(audio_file):
        return {"status": "failed",
                "message": "voice not found"}
    wav_file = os.path.join(audio_file, voiceId+".wav")
    if not os.path.exists(wav_file):
        return {"status": "failed",
                "message": "audio not found"}
    return FileResponse(path=wav_file, media_type="audio/wav")
    



def run_script(PROCESS_TRAIN, voiceId, output_model_path, file_audio, output_dir):
    split_audio(file_audio, output_dir)
    while(PROCESS_TRAIN):
        # Execute each command sequentially
        # if os.path.exists("dataset_raw"):
        #     shutil.rmtree("dataset_raw")
        if os.path.exists("dataset/44k"):
            shutil.rmtree("dataset/44k")
        if os.path.exists("configs/44k"):
            shutil.rmtree("configs/44k")
        if os.path.exists("filelists/44k"):
            shutil.rmtree("filelists/44k")

        os.system("svc pre-resample")
        os.system("svc pre-config")
        try:
            with open("configs/44k/config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            data["train"]["epochs"] = 500
            with open("configs/44k/config.json", "w") as f:
                json.dump(data, f, indent=4)
        except:
            print("cannot edit epochs")

        os.system("svc pre-hubert")
        os.system(f"svc train -m {output_model_path}".format(output_model_path))

        path_process_svc_train = os.path.join("process_svc", voiceId+".txt")
        with open(path_process_svc_train, "w", encoding="utf-8") as f:
            f.write("OK!")
        f.close()
        path_progress_status  = os.path.join("progress_status", voiceId+".txt")
        with open(path_progress_status, "w", encoding="utf-8") as fp:
            fp.write("done")
        fp.close()
        PROCESS_TRAIN = False



if __name__ == "__main__":
    # run_script()
    uvicorn.run(app, host="0.0.0.0", port=4501)
    
