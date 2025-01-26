"""Provides the core API server for sebastian."""
import socket
import sys
import whisperx

from filelock import FileLock
from flask import Flask, g, request, Response
from logging import Logger
from os import makedirs
from os.path import join as path_join
from waitress import serve as waitress_serve
from werkzeug.utils import secure_filename

from sebastian.core import get_logger, json_dumper
from sebastian.core.config import get_api_host, get_api_path, get_api_port, get_gpu_lockfile, get_data_dir, get_huggingface_token
from sebastian.core.time import cur_timestamp, time_since
from sebastian.core.utils import report_memory_use, clear_gpu_memory

CMD_STRING = 'api:start'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'm4a'}

app = Flask(__name__)
logger = get_logger()
gpu_lock = FileLock(get_gpu_lockfile())

@app.before_request
def before_request():
    """Set the start time for the request."""
    g.start = cur_timestamp()

@app.route("/")
def default():
    """Default endpoint."""
    return "Endpoint Disabled."

@app.route(get_api_path(), methods=['POST'])
def transcribe():
    """Transcribe a document."""

    if 'file' not in request.files:
        return malformed_request_response("No file submitted", logger)

    file = request.files['file']
    if file.filename == '':
        return malformed_request_response("No filename provided", logger)

    if file and not allowed_file(file.filename):
        file_type_error = f"File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
        return malformed_request_response("No filename provided", file_type_error)
    
    filename = secure_filename(file.filename)
    file.save(path_join(app.config['UPLOAD_FOLDER'], filename))
    file.close()

    results = {}
    debug = request.form.get('debug', 'false').lower() == 'true'
    model = request.form.get('model', 'large-v3-turbo')
    model_dir = app.config['MODEL_DIR']
    device = request.form.get('device', 'cuda')
    compute_type = request.form.get('compute_type', 'float16')
    batch_size = int(request.form.get('batch_size', 16))
    language = request.form.get('language', 'en')
    align = request.form.get('align', 'false').lower() == 'false'
    diarize = request.form.get('diarize', 'false').lower() == 'false'
    min_speakers = int(request.form.get('min_speakers', 1))
    max_speakers = int(request.form.get('max_speakers', 4))

    gpu_lock_wait_time = 0
    model_load_time = 0
    file_load_time = 0
    transcribe_time = 0
    align_time = 0
    diarize_time = 0

    gpu_request_lock_start = cur_timestamp()
    with gpu_lock:
        clear_gpu_memory()
        gpu_lock_wait_time = time_since(gpu_request_lock_start)
        logger.info("GPU lock acquired after %s seconds.", gpu_lock_wait_time)
        batch_size = 16 # reduce if low on GPU mem

        model_load_start = cur_timestamp()
        model = whisperx.load_model("large-v2", device, compute_type=compute_type, download_root=model_dir)
        model_load_time = time_since(model_load_start)

        file_load_start = cur_timestamp()
        audio = whisperx.load_audio(filename)
        file_load_time = time_since(file_load_start)

        transcribe_start = cur_timestamp()
        result = model.transcribe(audio, batch_size=batch_size, language=language)
        transcribe_time = time_since(transcribe_start)

        if align or diarize:
            align_start = cur_timestamp()
            model_a, metadata = whisperx.load_align_model(language_code=language, device=device)
            result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
            align_time = time_since(align_start)
        
        if diarize:
            huggingface_token = get_huggingface_token()
            diarize_start = cur_timestamp()
            diarize_model = whisperx.DiarizationPipeline(use_auth_token=huggingface_token, device=device)
            diarize_segments = diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            diarize_time = time_since(diarize_start)

        results['segments'] = result["segments"]    

    results['align_time'] = align_time
    results['align'] = align
    results['diarize_time'] = diarize_time
    results['diarize'] = diarize
    results['file_load_time'] = file_load_time
    results['gpu_lock_wait_time'] = gpu_lock_wait_time
    results['model_load_time'] = model_load_time
    results['total_request_time'] = time_since(g.start)
    results['transcribe_time'] = transcribe_time

    results['generated_at'] = cur_timestamp()
    results['agent'] = 'sebastian'
    results['version'] = '1.0.0'

    if not debug:
        pass

    write_response_data(results)
    return Response(json_dumper(results, pretty=False), status=200, mimetype='application/json')

def malformed_request_response(reason: str, logger) -> Response:
    """Returns a response for a malformed request."""
    logger.error(reason)
    response = {
        "error": reason,
        "status": 400
    }
    return Response(json_dumper(response, pretty=False), status=400, mimetype='application/json')

def start() -> None:
    """Starts the API server."""
    report_memory_use(logger)
    logger.info("Starting API server...")

    data_dir = get_data_dir()
    app.config['DATA_DIR'] = data_dir
    upload_folder = path_join(data_dir, 'sebastian_uploads')
    makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    model_dir = path_join(data_dir, 'models')
    makedirs(model_dir, exist_ok=True)
    app.config['MODEL_DIR'] = model_dir

    waitress_serve(app, host=get_api_host(), port=get_api_port())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_api_server_exit(log: Logger):
    """Exits if the API server is not running."""
    if not api_server_up():
        log.error("API server not running")
        sys.exit(1)

def api_server_up() -> bool:
    """Checks if the API server is running."""
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (get_api_host(), get_api_port())
    return a_socket.connect_ex(location) == 0

def write_response_data(data: dict) -> None:
    """Writes the response data to a file."""
    data_dir = app.config['DATA_DIR']
    summary_response_dir = f"{data_dir}/sebastian_responses"
    makedirs(summary_response_dir, exist_ok=True)
    final_filepath = f"{summary_response_dir}/response_{cur_timestamp()}.json"
    with open(final_filepath, 'w') as f:
        f.write(json_dumper(data, pretty=True))