document.addEventListener("DOMContentLoaded", () => {

    const moduleSelect = document.getElementById("module-select");
    const generateButton = document.getElementById("generate-button");
    const resultOutput = document.getElementById("response-output");
    const statusBadge = document.getElementById("status-badge");

    const sections = {
        qa: document.getElementById("qa-section"),
        explain: document.getElementById("explain-section"),
        quiz: document.getElementById("quiz-section"),
        summarize: document.getElementById("summary-section"),
        learning: document.getElementById("learning-section")
    };

    // ---------------------------------------
    // Escape HTML
    // ---------------------------------------
    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // ---------------------------------------
    // Show selected module
    // ---------------------------------------
    function showModule(module) {

        Object.values(sections).forEach(section => {
            if (section) {
                section.style.display = "none";
            }
        });

        if (sections[module]) {
            sections[module].style.display = "block";
        }

        if (module) {
            generateButton.disabled = false;
        } else {
            generateButton.disabled = true;
        }

        resultOutput.innerHTML = `
            <p>Select a module and submit a request to see the result here.</p>
        `;

        statusBadge.textContent = "Ready";
        statusBadge.className = "status-badge";
    }


    // ---------------------------------------
    // Module change
    // ---------------------------------------
    moduleSelect.addEventListener("change", () => {

        const selectedModule = moduleSelect.value;

        showModule(selectedModule);
    });


    // ---------------------------------------
    // Get input data
    // ---------------------------------------
    function getRequestData(module) {

        if (module === "qa") {

            return {
                endpoint: "/qa",
                data: {
                    question:
                        document.getElementById("qa-input").value.trim()
                }
            };
        }


        if (module === "explain") {

            return {
                endpoint: "/explain",
                data: {
                    topic:
                        document.getElementById("explain-input").value.trim()
                }
            };
        }


        if (module === "quiz") {

            return {
                endpoint: "/quiz",
                data: {
                    text:
                        document.getElementById("quiz-input").value.trim()
                }
            };
        }


        if (module === "summarize") {

            return {
                endpoint: "/summarize",
                data: {
                    text:
                        document.getElementById("summary-input").value.trim()
                }
            };
        }


        if (module === "learning") {

            return {
                endpoint: "/learn/recommendations",
                data: {
                    topic:
                        document.getElementById("learning-input").value.trim(),

                    level:
                        document.getElementById("learning-level").value
                }
            };
        }


        return null;
    }


    // ---------------------------------------
    // Status
    // ---------------------------------------
    function setStatus(message, type = "") {

        statusBadge.textContent = message;

        statusBadge.className = "status-badge";

        if (type) {
            statusBadge.classList.add(type);
        }
    }


    // ---------------------------------------
    // Normal response
    // ---------------------------------------
    function renderNormalResponse(data) {

        let output = data;

        if (typeof data === "object" && data !== null) {

            if (data.answer) {
                output = data.answer;
            }

            else if (data.explanation) {
                output = data.explanation;
            }

            else if (data.summary) {
                output = data.summary;
            }

            else if (data.recommendations) {
                output = data.recommendations;
            }

            else if (data.result) {
                output = data.result;
            }

            else if (data.message) {
                output = data.message;
            }

            else {
                output = JSON.stringify(data, null, 2);
            }
        }

        resultOutput.innerHTML = `
            <div class="normal-response">
                <pre>${escapeHtml(output)}</pre>
            </div>
        `;
    }


    // ---------------------------------------
    // QUIZ UI
    // ---------------------------------------
    function renderQuiz(data) {

        /*
         Backend may return quiz directly,
         or inside quiz/result/data.
        */

        const quiz =
            data.quiz ||
            data.result ||
            data.data ||
            data;


        // Check quiz format
        if (
            !quiz ||
            !Array.isArray(quiz.questions)
        ) {

            resultOutput.innerHTML = `
                <div class="error-box">

                    <h3>Quiz Error</h3>

                    <pre>
${escapeHtml(JSON.stringify(data, null, 2))}
                    </pre>

                </div>
            `;

            return;
        }


        // ---------------------------------------
        // Quiz title
        // ---------------------------------------

        let html = `

            <div class="quiz-container">

                <h2>
                    ${escapeHtml(
                        quiz.title || "Quick Quiz"
                    )}
                </h2>

                <div id="quiz-questions">

        `;


        // ---------------------------------------
        // Questions
        // ---------------------------------------

        quiz.questions.forEach((question, index) => {

            html += `

                <div class="quiz-question">

                    <h3>
                        Question ${index + 1}
                    </h3>

                    <p>
                        ${escapeHtml(
                            question.question
                        )}
                    </p>

                    <div class="quiz-options">
            `;


            // ---------------------------------------
            // Options
            // ---------------------------------------

            question.options.forEach(
                (option, optionIndex) => {

                    const optionId =
                        `q${index}_${optionIndex}`;


                    html += `

                        <label
                            class="quiz-option"
                            for="${optionId}"
                        >

                            <input
                                type="radio"
                                name="question_${index}"
                                id="${optionId}"
                                value="${escapeHtml(option)}"
                            >

                            <span>
                                ${escapeHtml(option)}
                            </span>

                        </label>

                    `;
                }
            );


            html += `

                    </div>

                    <div
                        class="quiz-feedback"
                        id="feedback_${index}"
                    >
                    </div>

                </div>

            `;
        });


        // ---------------------------------------
        // Check answer button
        // ---------------------------------------

        html += `

                </div>

                <button
                    id="check-answers"
                    type="button"
                >
                    Check Answers
                </button>

                <div id="quiz-score"></div>

            </div>

        `;


        // Put quiz on page
        resultOutput.innerHTML = html;


        // ---------------------------------------
        // Check answers
        // ---------------------------------------

        const checkButton =
            document.getElementById("check-answers");


        checkButton.addEventListener(
            "click",
            () => {

                let score = 0;


                quiz.questions.forEach(
                    (question, index) => {

                        const selected =
                            document.querySelector(
                                `input[name="question_${index}"]:checked`
                            );


                        const feedback =
                            document.getElementById(
                                `feedback_${index}`
                            );


                        // No answer selected
                        if (!selected) {

                            feedback.innerHTML = `
                                <span>
                                    Please select an answer.
                                </span>
                            `;

                            return;
                        }


                        const selectedAnswer =
                            selected.value.trim();


                        const correctAnswer =
                            String(
                                question.answer
                            ).trim();


                        // Correct
                        if (
                            selectedAnswer ===
                            correctAnswer
                        ) {

                            score++;


                            feedback.innerHTML = `
                                <span>
                                    ✓ Correct!
                                </span>
                            `;
                        }


                        // Wrong
                        else {

                            feedback.innerHTML = `
                                <span>
                                    ✗ Incorrect.
                                    Correct answer:
                                    ${escapeHtml(
                                        correctAnswer
                                    )}
                                </span>
                            `;
                        }

                    }
                );


                // Score
                document.getElementById(
                    "quiz-score"
                ).innerHTML = `

                    <h2>
                        Score:
                        ${score} /
                        ${quiz.questions.length}
                    </h2>

                `;

            }
        );

    }


    // ---------------------------------------
    // Generate button
    // ---------------------------------------
    generateButton.addEventListener(
        "click",
        async () => {

            const module =
                moduleSelect.value;


            if (!module) {

                alert(
                    "Please select a module."
                );

                return;
            }


            const request =
                getRequestData(module);


            if (!request) {

                return;
            }


            // -----------------------------------
            // Check empty input
            // -----------------------------------

            const values =
                Object.values(request.data);


            const hasEmpty =
                values.some(
                    value =>
                        String(value).trim() === ""
                );


            if (hasEmpty) {

                alert(
                    "Please enter the required information."
                );

                return;
            }


            // -----------------------------------
            // Loading
            // -----------------------------------

            generateButton.disabled = true;

            generateButton.textContent =
                "Generating...";


            setStatus(
                "Generating...",
                "loading"
            );


            resultOutput.innerHTML = `

                <div class="loading-box">

                    <p>
                        Please wait...
                    </p>

                </div>

            `;


            try {

                // -----------------------------------
                // Send request
                // -----------------------------------

                const response =
                    await fetch(
                        request.endpoint,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    request.data
                                )
                        }
                    );


                // -----------------------------------
                // Read response
                // -----------------------------------

                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";


                let data;


                if (
                    contentType.includes(
                        "application/json"
                    )
                ) {

                    data =
                        await response.json();

                }

                else {

                    const text =
                        await response.text();

                    data = {
                        message: text
                    };

                }


                // -----------------------------------
                // Error response
                // -----------------------------------

                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        data.detail ||
                        data.message ||
                        "Request failed."
                    );

                }


                // -----------------------------------
                // Display result
                // -----------------------------------

                if (module === "quiz") {

                    renderQuiz(data);

                }

                else {

                    renderNormalResponse(data);

                }


                setStatus(
                    "Completed",
                    "success"
                );

            }


            catch (error) {

                console.error(
                    "EduGenie Error:",
                    error
                );


                resultOutput.innerHTML = `

                    <div class="error-box">

                        <h3>
                            Error
                        </h3>

                        <p>
                            ${escapeHtml(
                                error.message
                            )}
                        </p>

                    </div>

                `;


                setStatus(
                    "Error",
                    "error"
                );

            }


            finally {

                generateButton.disabled =
                    false;

                generateButton.textContent =
                    "Generate";

            }

        }
    );


    // ---------------------------------------
    // Initial state
    // ---------------------------------------

    generateButton.disabled = true;

});