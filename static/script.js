// =================================================
// AI SOP NAVIGATOR
// COMPLETE FRONTEND SCRIPT
// =================================================

// =================================================
// GLOBAL STATE
// =================================================

let uploadedSOPText = "";
let uploadedSOPChunks = [];


// =================================================
// DOM ELEMENTS
// =================================================

const fileInput = document.getElementById("fileInput");
const selectFileBtn = document.getElementById("selectFileBtn");
const uploadBox = document.getElementById("uploadBox");
const fileName = document.getElementById("fileName");
const analysisStatus = document.getElementById("analysisStatus");
const analysisPanel = document.getElementById("analysisPanel");
const panelTitle = document.getElementById("panelTitle");


// =================================================
// FILE SELECTION
// =================================================

if (selectFileBtn && fileInput) {

    selectFileBtn.addEventListener("click", function () {
        fileInput.click();
    });

}


if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (fileInput.files.length > 0) {

            uploadSOP(fileInput.files[0]);

        }

    });

}


// =================================================
// DRAG AND DROP
// =================================================

if (uploadBox) {

    uploadBox.addEventListener("dragover", function (event) {

        event.preventDefault();

        uploadBox.classList.add("dragging");

    });


    uploadBox.addEventListener("dragleave", function () {

        uploadBox.classList.remove("dragging");

    });


    uploadBox.addEventListener("drop", function (event) {

        event.preventDefault();

        uploadBox.classList.remove("dragging");

        const files = event.dataTransfer.files;

        if (files.length > 0) {

            uploadSOP(files[0]);

        }

    });

}


// =================================================
// UPLOAD SOP
// =================================================

async function uploadSOP(file) {

    const allowedExtensions = [
        ".pdf",
        ".docx",
        ".txt"
    ];

    const fileExtension =
        file.name
            .substring(file.name.lastIndexOf("."))
            .toLowerCase();


    if (!allowedExtensions.includes(fileExtension)) {

        alert(
            "Please upload PDF, DOCX or TXT file."
        );

        return;
    }


    if (fileName) {

        fileName.textContent =
            "Uploading: " + file.name;

    }


    if (analysisStatus) {

        analysisStatus.classList.remove("hidden");

    }


    const formData = new FormData();

    formData.append("file", file);


    try {

        const response = await fetch(
            "/api/upload",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (!data.success) {

            throw new Error(
                data.error || "Upload failed."
            );

        }


        uploadedSOPText =
            data.text || "";


        uploadedSOPChunks =
            data.chunks || [];


        if (fileName) {

            fileName.textContent =
                "✓ " +
                data.file_name +
                " uploaded successfully";

        }


        if (analysisStatus) {

            analysisStatus.classList.add("hidden");

        }


        alert(
            "SOP uploaded successfully!"
        );


        console.log(
            "Uploaded SOP:",
            data.file_name
        );


        console.log(
            "Extracted text:",
            uploadedSOPText
        );


    }

    catch (error) {

        if (analysisStatus) {

            analysisStatus.classList.add("hidden");

        }


        if (fileName) {

            fileName.textContent = "";

        }


        alert(
            "Upload Error: " +
            error.message
        );

    }

}


// =================================================
// OPEN FEATURE
// =================================================

function openFeature(feature) {

    if (!analysisPanel) {

        return;

    }


    analysisPanel.classList.remove("hidden");


    const interfaces =
        document.querySelectorAll(
            ".feature-interface"
        );


    interfaces.forEach(function (element) {

        element.classList.add("hidden");

    });


    const selectedInterface =
        document.getElementById(
            feature + "Interface"
        );


    if (selectedInterface) {

        selectedInterface.classList.remove(
            "hidden"
        );

    }


    const titles = {

        matching:
            "Situation → SOP Matching",

        conflict:
            "Conflict Detection",

        version:
            "Version / Outdated Detection",

        gap:
            "SOP Gap Detection",

        ask:
            "Ask Anything AI"

    };


    if (panelTitle) {

        panelTitle.textContent =
            titles[feature] ||
            "SOP Intelligence";

    }

}


// =================================================
// CLOSE FEATURE
// =================================================

function closeFeature() {

    if (analysisPanel) {

        analysisPanel.classList.add("hidden");

    }

}


// =================================================
// SITUATION → SOP MATCHING
// =================================================

async function analyzeSituation() {

    const input =
        document.getElementById(
            "situationInput"
        );


    const resultBox =
        document.getElementById(
            "matchingResult"
        );


    const situation =
        input.value.trim();


    if (!situation) {

        resultBox.innerHTML =
            "Please describe the situation.";

        return;

    }


    if (!uploadedSOPChunks.length) {

        resultBox.innerHTML =
            "Please upload an SOP first.";

        return;

    }


    resultBox.innerHTML = `
        <strong>
            🤖 AI is analyzing...
        </strong>

        <p>
            Finding the most relevant SOP section.
        </p>
    `;


    try {

        const response =
            await fetch(
                "/api/match",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        situation:
                            situation,

                        chunks:
                            uploadedSOPChunks

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            resultBox.innerHTML =
                escapeHTML(
                    data.error ||
                    "Matching failed."
                );

            return;

        }


        const result =
            data.result;


        if (!result.matched) {

            resultBox.innerHTML = `

                <strong>
                    No Strong Match Found
                </strong>

                <p>
                    ${escapeHTML(
                        result.message ||
                        "No relevant SOP section was found."
                    )}
                </p>

            `;

            return;

        }


        resultBox.innerHTML = `

            <strong>
                ✓ Relevant SOP Found
            </strong>

            <p>

                <b>
                    Match Score:
                </b>

                ${result.score}%

            </p>

            <div class="ai-result-text">

                ${escapeHTML(
                    result.text
                )}

            </div>

        `;

    }


    catch (error) {

        resultBox.innerHTML =
            "Error: " +
            escapeHTML(
                error.message
            );

    }

}


// =================================================
// CONFLICT DETECTION
// =================================================

async function analyzeConflict() {

    const statementA =
        document
            .getElementById("statementA")
            .value
            .trim();


    const statementB =
        document
            .getElementById("statementB")
            .value
            .trim();


    const resultBox =
        document
            .getElementById("conflictResult");


    if (!statementA || !statementB) {

        resultBox.innerHTML =
            "Please enter both SOP statements.";

        return;

    }


    resultBox.innerHTML = `

        <strong>
            🤖 Checking for conflicts...
        </strong>

    `;


    try {

        const response =
            await fetch(
                "/api/conflicts",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        statements: [
                            statementA,
                            statementB
                        ]

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            resultBox.innerHTML =
                escapeHTML(
                    data.error ||
                    "Conflict detection failed."
                );

            return;

        }


        if (data.count === 0) {

            resultBox.innerHTML = `

                <strong>
                    ✓ No Obvious Conflict Detected
                </strong>

                <p>
                    The preliminary analysis did not
                    identify an obvious contradiction
                    between these statements.
                </p>

            `;

            return;

        }


        const conflict =
            data.conflicts[0];


        resultBox.innerHTML = `

            <strong>
                ⚠ Potential Conflict Detected
            </strong>

            <p>

                <b>
                    Confidence:
                </b>

                ${conflict.confidence}%

            </p>

            <p>

                ${escapeHTML(
                    conflict.reason
                )}

            </p>

            <hr>

            <p>

                <b>
                    Statement 1
                </b>

            </p>

            <p>

                ${escapeHTML(
                    conflict.statement_a
                )}

            </p>

            <p>

                <b>
                    Statement 2
                </b>

            </p>

            <p>

                ${escapeHTML(
                    conflict.statement_b
                )}

            </p>

        `;

    }


    catch (error) {

        resultBox.innerHTML =
            "Error: " +
            escapeHTML(
                error.message
            );

    }

}


// =================================================
// VERSION / OUTDATED DETECTION
// =================================================

async function analyzeVersion() {

    const text =
        document
            .getElementById("versionInput")
            .value
            .trim();


    const resultBox =
        document
            .getElementById("versionResult");


    if (!text) {

        resultBox.innerHTML =
            "Please enter SOP content.";

        return;

    }


    resultBox.innerHTML = `

        <strong>
            🔄 Checking SOP version...
        </strong>

        <p>
            Analyzing version and date information.
        </p>

    `;


    try {

        const response =
            await fetch(
                "/api/version",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        text: text

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            resultBox.innerHTML =
                escapeHTML(
                    data.error ||
                    "Version analysis failed."
                );

            return;

        }


        const result =
            data.result;


        resultBox.innerHTML = `

            <strong>

                ${
                    result.potentially_outdated

                    ? "⚠ Potentially Outdated SOP"

                    : "✓ No Obvious Outdated Indicator"

                }

            </strong>


            <p>

                <b>
                    Detected Version:
                </b>

                ${
                    escapeHTML(
                        result.version ||
                        "Not detected"
                    )
                }

            </p>


            <p>

                <b>
                    Latest Date:
                </b>

                ${
                    escapeHTML(
                        result.latest_date ||
                        "Not detected"
                    )
                }

            </p>


            <p>

                <b>
                    Estimated Age:
                </b>

                ${
                    result.age_years !== null &&
                    result.age_years !== undefined

                    ? result.age_years + " years"

                    : "Not available"

                }

            </p>


            <p>

                ${
                    escapeHTML(
                        result.message ||
                        "Version analysis completed."
                    )
                }

            </p>

        `;

    }


    catch (error) {

        resultBox.innerHTML =
            "Error: " +
            escapeHTML(
                error.message
            );

    }

}


// =================================================
// SOP GAP DETECTION
// =================================================

async function analyzeGap() {

    const text =
        document
            .getElementById("gapInput")
            .value
            .trim();


    const resultBox =
        document
            .getElementById("gapResult");


    if (!text) {

        resultBox.innerHTML = `

            <strong>
                ⚠ Please provide SOP content
            </strong>

            <p>
                Paste your SOP content and
                click Detect SOP Gaps.
            </p>

        `;

        return;

    }


    resultBox.innerHTML = `

        <strong>
            🤖 AI is analyzing the SOP...
        </strong>

        <p>
            Checking for missing, unclear,
            or incomplete procedures.
        </p>

    `;


    try {

        const response =
            await fetch(
                "/api/gaps",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        text: text

                    })

                }
            );


        const data =
            await response.json();


        console.log(
            "GAP API RESPONSE:",
            data
        );


        if (!data.success) {

            resultBox.innerHTML = `

                <strong>
                    ⚠ AI Error
                </strong>

                <p>

                    ${escapeHTML(
                        data.error ||
                        "Gap analysis failed."
                    )}

                </p>

            `;

            return;

        }


        const result =
            data.result || {};


        const gaps =
            Array.isArray(result.gaps)
                ? result.gaps
                : [];


        const weakAreas =
            Array.isArray(result.weak_areas)
                ? result.weak_areas
                : [];


        // =========================================
        // NO GAPS
        // =========================================

        if (

            result.gaps_found === false &&

            gaps.length === 0 &&

            weakAreas.length === 0

        ) {

            resultBox.innerHTML = `

                <strong>
                    ✓ No Major Gaps Detected
                </strong>

                <p>

                    ${escapeHTML(
                        result.summary ||
                        "The AI did not identify any significant potential gaps."
                    )}

                </p>

            `;

            return;

        }


        // =========================================
        // BUILD RESULT
        // =========================================

        let html = `

            <strong>
                ⚠ Potential SOP Gaps Found
            </strong>

            <p>

                The AI identified

                <b>
                    ${gaps.length}
                </b>

                potential area(s) that may require
                clarification or review.

            </p>

        `;


        // =========================================
        // GAP CARDS
        // =========================================

        if (gaps.length > 0) {

            html += `

                <h4>
                    🔎 Potentially Missing / Unclear Areas
                </h4>

            `;


            gaps.forEach(function (gap) {

                html += `

                    <div class="ai-gap-card">

                        <p>

                            <strong>
                                ${escapeHTML(
                                    gap.section ||
                                    "Unspecified Area"
                                )}
                            </strong>

                        </p>


                        <p>

                            <b>
                                Status:
                            </b>

                            ${escapeHTML(
                                gap.status ||
                                "Potential Gap"
                            )}

                        </p>


                        <p>

                            <b>
                                Why flagged:
                            </b>

                            ${escapeHTML(
                                gap.reason ||
                                "The AI identified this area as potentially incomplete."
                            )}

                        </p>


                        ${
                            gap.evidence

                            ? `

                                <p>

                                    <b>
                                        Evidence:
                                    </b>

                                    ${escapeHTML(
                                        gap.evidence
                                    )}

                                </p>

                              `

                            : ""

                        }


                        ${
                            gap.severity

                            ? `

                                <p>

                                    <b>
                                        Severity:
                                    </b>

                                    ${escapeHTML(
                                        gap.severity
                                    )}

                                </p>

                              `

                            : ""

                        }

                    </div>

                `;

            });

        }


        // =========================================
        // WEAK AREAS
        // =========================================

        if (weakAreas.length > 0) {

            html += `

                <h4>
                    ⚠ Areas That May Need Clarification
                </h4>

            `;


            weakAreas.forEach(function (area) {

                html += `

                    <div class="ai-gap-card">

                        <p>

                            <strong>

                                ${escapeHTML(
                                    area.type ||
                                    "Potentially Vague Instruction"
                                )}

                            </strong>

                        </p>


                        ${
                            area.phrase

                            ? `

                                <p>

                                    <b>
                                        Phrase:
                                    </b>

                                    "${escapeHTML(
                                        area.phrase
                                    )}"

                                </p>

                              `

                            : ""

                        }


                        <p>

                            <b>
                                Why flagged:
                            </b>

                            ${escapeHTML(
                                area.reason ||
                                "This instruction may require additional clarification."
                            )}

                        </p>

                    </div>

                `;

            });

        }


        // =========================================
        // AI SUMMARY
        // =========================================

        if (result.summary) {

            html += `

                <div class="ai-summary">

                    <h4>
                        🧠 AI Explanation
                    </h4>

                    <p>

                        ${escapeHTML(
                            result.summary
                        )}

                    </p>

                </div>

            `;

        }


        resultBox.innerHTML =
            html;

    }


    catch (error) {

        console.error(
            "Gap Detection Error:",
            error
        );


        resultBox.innerHTML = `

            <strong>
                ⚠ Request Failed
            </strong>

            <p>

                ${escapeHTML(
                    error.message
                )}

            </p>

        `;

    }

}


// =================================================
// ASK ANYTHING AI
// =================================================

async function askAnything() {

    const input =
        document.getElementById(
            "questionInput"
        );


    const resultBox =
        document.getElementById(
            "askResult"
        );


    if (!input || !resultBox) {

        console.error(
            "Ask Anything UI elements not found."
        );

        return;

    }


    const question =
        input.value.trim();


    if (!question) {

        resultBox.innerHTML = `

            <strong>
                ⚠ Please enter a question.
            </strong>

        `;

        return;

    }


    resultBox.innerHTML = `

        <strong>
            🤖 AI is thinking...
        </strong>

        <p>
            Generating your answer...
        </p>

    `;


    try {

        const response =
            await fetch(
                "/api/ask",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        sop_text:
                            uploadedSOPText

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            resultBox.innerHTML = `

                <strong>
                    ⚠ AI Error
                </strong>

                <p>

                    ${escapeHTML(
                        data.answer ||
                        data.error ||
                        "Unable to generate answer."
                    )}

                </p>

            `;

            return;

        }


        resultBox.innerHTML = `

            <strong>
                🤖 AI Answer
            </strong>

            <div class="ai-result-text">

                ${formatAIAnswer(
                    data.answer
                )}

            </div>

        `;

    }


    catch (error) {

        resultBox.innerHTML = `

            <strong>
                ⚠ Request Failed
            </strong>

            <p>

                ${escapeHTML(
                    error.message
                )}

            </p>

        `;

    }

}


// =================================================
// FORMAT AI ANSWER
// =================================================

function formatAIAnswer(text) {

    if (!text) {

        return "No answer received.";

    }


    return escapeHTML(text)

        .replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        )

        .replace(
            /\n/g,
            "<br>"
        );

}


// =================================================
// HTML ESCAPE
// =================================================

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// =================================================
// DEBUG HELPER
// =================================================

console.log(
    "✓ AI SOP Navigator script loaded successfully."
);