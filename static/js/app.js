/* ===================================================================
   SpellCompiler — Frontend Logic
   =================================================================== */

(function () {
    "use strict";

    // ---- DOM refs -------------------------------------------------------
    const inputText   = document.getElementById("input-text");
    const analyzeBtn  = document.getElementById("analyze-btn");
    const loader      = document.getElementById("loader");
    const results     = document.getElementById("results");
    const fileInput   = document.getElementById("file-input");
    const dropZone    = document.getElementById("drop-zone");
    const fileNameEl  = document.getElementById("file-name");
    const tabBtns     = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    // Pipeline steps
    const pipeSteps = [
        document.getElementById("pipe-lexer"),
        document.getElementById("pipe-spell"),
        document.getElementById("pipe-grammar"),
        document.getElementById("pipe-output"),
    ];

    // ---- Tab switching --------------------------------------------------
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(btn.dataset.tab).classList.add("active");
        });
    });

    // ---- File drop / pick -----------------------------------------------
    dropZone.addEventListener("click", () => fileInput.click());
    dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
    dropZone.addEventListener("drop", e => {
        e.preventDefault();
        dropZone.classList.remove("drag-over");
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            showFileName(e.dataTransfer.files[0].name);
        }
    });
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length) showFileName(fileInput.files[0].name);
    });

    function showFileName(name) {
        fileNameEl.textContent = "Selected: " + name;
    }

    // ---- Pipeline animation ---------------------------------------------
    function resetPipeline() {
        pipeSteps.forEach(s => { s.classList.remove("active", "done"); });
    }

    async function animatePipeline() {
        resetPipeline();
        for (let i = 0; i < pipeSteps.length; i++) {
            pipeSteps[i].classList.add("active");
            await sleep(350);
            pipeSteps[i].classList.remove("active");
            pipeSteps[i].classList.add("done");
        }
    }

    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    // ---- Analyze --------------------------------------------------------
    analyzeBtn.addEventListener("click", handleAnalyze);

    async function handleAnalyze() {
        const activeTab = document.querySelector(".tab-btn.active").dataset.tab;
        let body, url, opts;

        if (activeTab === "file-tab") {
            if (!fileInput.files.length) { alert("Please select a file first."); return; }
            const fd = new FormData();
            fd.append("file", fileInput.files[0]);
            url  = "/upload";
            opts = { method: "POST", body: fd };
        } else {
            const text = inputText.value.trim();
            if (!text) { alert("Please enter some text first."); return; }
            url  = "/analyze";
            opts = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            };
        }

        // UI state
        loader.classList.remove("hidden");
        results.classList.add("hidden");
        analyzeBtn.disabled = true;

        const pipelinePromise = animatePipeline();

        try {
            const res  = await fetch(url, opts);
            const data = await res.json();
            if (!res.ok) { alert(data.error || "Server error"); return; }
            await pipelinePromise;          // wait for animation to finish
            renderResults(data);
        } catch (err) {
            alert("Network error: " + err.message);
        } finally {
            loader.classList.add("hidden");
            analyzeBtn.disabled = false;
        }
    }

    // ---- Render ---------------------------------------------------------
    function renderResults(data) {
        const lex   = data.lexer;
        const spell = data.spelling;
        const gram  = data.grammar;

        // Stats
        document.getElementById("stat-words").textContent      = lex.word_count;
        document.getElementById("stat-sentences").textContent   = lex.sentence_count;
        document.getElementById("stat-tokens").textContent      = lex.total_tokens;
        document.getElementById("stat-misspelled").textContent  = spell.misspelled_count;
        document.getElementById("stat-grammar").textContent     = gram.issue_count;

        // Corrected text
        renderCorrectedText(data.original_text, spell);

        // Token stream
        renderTokenStream(lex.tokens);

        // Spelling errors
        renderSpellingErrors(spell);

        // Grammar issues
        renderGrammarIssues(gram);

        results.classList.remove("hidden");
        results.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // -- Corrected text with highlighted corrections ----------------------
    function renderCorrectedText(original, spell) {
        const el = document.getElementById("corrected-text");
        if (spell.misspelled_count === 0) {
            el.textContent = original;
            return;
        }

        // Build corrected text and highlight corrections
        let html = escapeHtml(spell.corrected_text);

        // Highlight words that were corrected
        spell.errors.forEach(err => {
            if (err.suggestions.length) {
                let suggestion = err.suggestions[0];
                // Match casing
                if (err.word[0] === err.word[0].toUpperCase()) {
                    suggestion = suggestion.charAt(0).toUpperCase() + suggestion.slice(1);
                }
                // Replace first occurrence of suggestion in the corrected html
                const escaped = escapeHtml(suggestion);
                html = html.replace(
                    escaped,
                    '<span class="correction" title="Was: ' + escapeHtml(err.word) + '">' + escaped + '</span>'
                );
            }
        });

        el.innerHTML = html;
    }

    // -- Token stream pills -----------------------------------------------
    function renderTokenStream(tokens) {
        const el = document.getElementById("token-stream");
        document.getElementById("token-badge").textContent = "Phase 1 · " + tokens.length + " tokens";
        const visibleTokens = tokens.slice(0, 500);  // limit for performance
        el.innerHTML = visibleTokens.map(t => {
            const display = t.type === "WHITESPACE" ? "␣" : escapeHtml(t.value);
            return '<span class="token token-' + t.type + '" title="' +
                   t.type + ' @ L' + t.line + ':' + t.column + '">' +
                   display + '</span>';
        }).join("");
        if (tokens.length > 500) {
            el.innerHTML += '<span class="token" style="color:var(--text-muted)">… +' + (tokens.length - 500) + ' more</span>';
        }
    }

    // -- Spelling errors list ---------------------------------------------
    function renderSpellingErrors(spell) {
        const el = document.getElementById("spelling-errors");
        document.getElementById("spell-badge").textContent = spell.misspelled_count;

        if (spell.misspelled_count === 0) {
            el.innerHTML = '<div class="no-issues">No spelling errors found!</div>';
            return;
        }

        el.innerHTML = spell.errors.map(err =>
            '<div class="error-row">' +
                '<span class="error-word">' + escapeHtml(err.word) + '</span>' +
                '<div class="error-details">' +
                    '<div>Misspelled word at line ' + err.line + ', column ' + err.column + '</div>' +
                    (err.suggestions.length
                        ? '<div class="suggestions">Suggestions: ' + err.suggestions.map(s => '<strong>' + escapeHtml(s) + '</strong>').join(", ") + '</div>'
                        : '<div class="suggestions" style="color:var(--text-muted)">No suggestions available</div>') +
                '</div>' +
                '<span class="location">L' + err.line + ':' + err.column + '</span>' +
            '</div>'
        ).join("");
    }

    // -- Grammar issues list ----------------------------------------------
    function renderGrammarIssues(gram) {
        const el = document.getElementById("grammar-issues");
        document.getElementById("grammar-badge").textContent = gram.issue_count;

        if (gram.issue_count === 0) {
            el.innerHTML = '<div class="no-issues">No grammar issues found!</div>';
            return;
        }

        el.innerHTML = gram.issues.map(issue =>
            '<div class="issue-row">' +
                '<span class="issue-label">' + escapeHtml(issue.severity) + '</span>' +
                '<div class="issue-details">' +
                    '<div>' + escapeHtml(issue.message) + '</div>' +
                    (issue.suggestion
                        ? '<div class="suggestions">Suggestion: <strong>' + escapeHtml(issue.suggestion) + '</strong></div>'
                        : '') +
                '</div>' +
                '<span class="location">L' + issue.line + ':' + issue.column + '</span>' +
            '</div>'
        ).join("");
    }

    // ---- Utility --------------------------------------------------------
    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }
})();
