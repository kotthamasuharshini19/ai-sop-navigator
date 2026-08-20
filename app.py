import os

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from services.document_processor import process_sop
from services.situation_matcher import get_best_match
from services.conflict_detector import find_conflicts
from services.version_detector import detect_outdated_status
from services.gap_detector import detect_gaps
from services.ai_assistant import ask_ai


# -------------------------------------------------
# Configuration
# -------------------------------------------------

load_dotenv()

app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "data",
    "sops"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


# -------------------------------------------------
# Helper Functions
# -------------------------------------------------

def allowed_file(filename):
    """Check whether uploaded file is supported."""

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# -------------------------------------------------
# Home Page
# -------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# -------------------------------------------------
# SOP Upload API
# -------------------------------------------------

@app.route(
    "/api/upload",
    methods=["POST"]
)
def upload_sop():

    if "file" not in request.files:

        return jsonify({
            "success": False,
            "error": "No file was uploaded."
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "success": False,
            "error": "Please select an SOP file."
        }), 400

    if not allowed_file(file.filename):

        return jsonify({
            "success": False,
            "error": (
                "Unsupported file type. "
                "Use PDF, DOCX or TXT."
            )
        }), 400

    filename = secure_filename(
        file.filename
    )

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(file_path)

    try:

        processed = process_sop(
            file_path
        )

        return jsonify({
            "success": True,
            "file_name": processed[
                "file_name"
            ],
            "text": processed[
                "text"
            ],
            "chunks": processed[
                "chunks"
            ],
            "chunk_count": processed[
                "chunk_count"
            ]
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# -------------------------------------------------
# Situation → SOP Matching
# -------------------------------------------------

@app.route(
    "/api/match",
    methods=["POST"]
)
def situation_match():

    data = request.get_json(
        silent=True
    ) or {}

    situation = data.get(
        "situation",
        ""
    )

    chunks = data.get(
        "chunks",
        []
    )

    if not situation.strip():

        return jsonify({
            "success": False,
            "error": "Please enter a situation."
        }), 400

    result = get_best_match(
        situation,
        chunks
    )

    return jsonify({
        "success": True,
        "result": result
    })


# -------------------------------------------------
# Conflict Detection
# -------------------------------------------------

@app.route(
    "/api/conflicts",
    methods=["POST"]
)
def conflicts():

    data = request.get_json(
        silent=True
    ) or {}

    statements = data.get(
        "statements",
        []
    )

    if not statements:

        return jsonify({
            "success": False,
            "error": "No SOP statements provided."
        }), 400

    results = find_conflicts(
        statements
    )

    return jsonify({
        "success": True,
        "conflicts": results,
        "count": len(results)
    })


# -------------------------------------------------
# Version / Outdated Detection
# -------------------------------------------------

@app.route(
    "/api/version",
    methods=["POST"]
)
def version_analysis():

    data = request.get_json(
        silent=True
    ) or {}

    sop_text = data.get(
        "text",
        ""
    )

    if not sop_text.strip():

        return jsonify({
            "success": False,
            "error": "No SOP text provided."
        }), 400

    result = detect_outdated_status(
        sop_text
    )

    return jsonify({
        "success": True,
        "result": result
    })


# -------------------------------------------------
# SOP Gap Detection
# -------------------------------------------------

@app.route(
    "/api/gaps",
    methods=["POST"]
)
def gap_analysis():

    data = request.get_json(
        silent=True
    ) or {}

    sop_text = data.get(
        "text",
        ""
    )

    if not sop_text.strip():

        return jsonify({
            "success": False,
            "error": "No SOP text provided."
        }), 400

    result = detect_gaps(
        sop_text
    )

    return jsonify({
        "success": True,
        "result": result
    })


# -------------------------------------------------
# ASK ANYTHING - AI ASSISTANT
# -------------------------------------------------

@app.route(
    "/api/ask",
    methods=["POST"]
)
def ask_anything():

    data = request.get_json(
        silent=True
    ) or {}

    question = data.get(
        "question",
        ""
    )

    sop_text = data.get(
        "sop_text",
        ""
    )

    if not question.strip():

        return jsonify({
            "success": False,
            "error": "Please enter a question."
        }), 400

    try:

        result = ask_ai(
            question,
            sop_text
        )

        return jsonify(result)

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# -------------------------------------------------
# Health Check
# -------------------------------------------------

@app.route("/api/health")
def health():

    return jsonify({
        "status": "running",
        "application": "AI SOP Navigator",
        "features": [
            "SOP Upload",
            "Situation → SOP Matching",
            "Conflict Detection",
            "Version / Outdated Detection",
            "SOP Gap Detection",
            "Ask Anything AI Assistant"
        ]
    })


# -------------------------------------------------
# Run Application
# -------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )