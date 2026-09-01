import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import ATSGauge from "./components/ATSGauge.jsx";
import CodeEditor from "./components/CodeEditor.jsx";
import FileUpload from "./components/FileUpload.jsx";
import JDInput from "./components/JDInput.jsx";

const API = axios.create({ baseURL: import.meta.env.VITE_API_URL || "" });

const emptyLatex = String.raw`\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.65in]{geometry}
\begin{document}
\section*{Optimized Resume}
Upload a resume and optimize it against a job description.
\end{document}
`;

function loadStored(key, fallback) {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}

export default function App() {
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState(() => loadStored("jdText", ""));
  const [targetTitle, setTargetTitle] = useState(() => loadStored("targetTitle", "Software Engineer"));
  const [proficiencies, setProficiencies] = useState(() => loadStored("userProficiencies", ""));
  const [atsScore, setAtsScore] = useState(null);
  const [matchedKeywords, setMatchedKeywords] = useState([]);
  const [missingKeywords, setMissingKeywords] = useState([]);
  const [latexCode, setLatexCode] = useState(() => loadStored("latexCode", emptyLatex));
  const [isUploading, setIsUploading] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isCompiling, setIsCompiling] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => localStorage.setItem("jdText", jdText), [jdText]);
  useEffect(() => localStorage.setItem("targetTitle", targetTitle), [targetTitle]);
  useEffect(() => localStorage.setItem("userProficiencies", proficiencies), [proficiencies]);
  useEffect(() => localStorage.setItem("latexCode", latexCode), [latexCode]);

  const canScore = useMemo(() => resumeText.trim() && jdText.trim(), [resumeText, jdText]);

  async function handleFile(file) {
    setIsUploading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await API.post("/api/upload", formData);
      setResumeText(response.data.text || "");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not extract text from that file.");
    } finally {
      setIsUploading(false);
    }
  }

  async function scoreResume() {
    if (!canScore) return;
    setError("");
    try {
      const response = await API.post("/api/ats-score", { resume_text: resumeText, jd_text: jdText });
      setAtsScore(response.data.score);
      setMatchedKeywords(response.data.matched_keywords || []);
      setMissingKeywords(response.data.missing_keywords || []);
    } catch (err) {
      setError(err.response?.data?.detail || "ATS scoring failed.");
    }
  }

  async function optimizeResume() {
    if (!canScore) {
      setError("Upload a resume and paste a job description first.");
      return;
    }
    setIsOptimizing(true);
    setError("");
    try {
      const response = await API.post("/api/optimize", {
        resume_text: resumeText,
        jd_text: jdText,
        target_title: targetTitle,
        user_proficiencies: proficiencies.split(",").map((item) => item.trim()).filter(Boolean)
      });
      setAtsScore(response.data.ats?.score ?? null);
      setMatchedKeywords(response.data.ats?.matched_keywords || []);
      setMissingKeywords(response.data.ats?.missing_keywords || []);
      setLatexCode(response.data.latex_code || emptyLatex);
    } catch (err) {
      setError(err.response?.data?.detail || "Optimization failed.");
    } finally {
      setIsOptimizing(false);
    }
  }

  async function downloadPdf() {
    setIsCompiling(true);
    setError("");
    try {
      const response = await API.post("/api/compile", { latex: latexCode }, { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = "Optimized_Resume.pdf";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || "PDF compilation failed. Confirm Tectonic is installed on the backend.");
    } finally {
      setIsCompiling(false);
    }
  }

  return (
    <main className="min-h-screen bg-paper">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-5 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-4 border-b border-line pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-ink">Resume Optimizer</h1>
            <p className="mt-1 text-sm text-slate-600">Upload, match, optimize, edit, and compile.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={scoreResume}
              disabled={!canScore}
              className="focus-ring rounded bg-white px-4 py-2 text-sm font-semibold text-ink shadow-sm ring-1 ring-line disabled:cursor-not-allowed disabled:opacity-50"
            >
              Score
            </button>
            <button
              onClick={optimizeResume}
              disabled={isOptimizing}
              className="focus-ring rounded bg-mint px-4 py-2 text-sm font-semibold text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isOptimizing ? "Optimizing..." : "Optimize Resume"}
            </button>
            <button
              onClick={downloadPdf}
              disabled={isCompiling || !latexCode.trim()}
              className="focus-ring rounded bg-ink px-4 py-2 text-sm font-semibold text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isCompiling ? "Compiling..." : "Download PDF"}
            </button>
          </div>
        </header>

        {error ? <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

        <div className="grid gap-6 lg:grid-cols-[420px_minmax(0,1fr)]">
          <aside className="space-y-5">
            <FileUpload onFile={handleFile} isUploading={isUploading} resumeText={resumeText} />
            <JDInput
              jdText={jdText}
              setJdText={setJdText}
              targetTitle={targetTitle}
              setTargetTitle={setTargetTitle}
              proficiencies={proficiencies}
              setProficiencies={setProficiencies}
            />
            <ATSGauge score={atsScore} />
            <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
              <KeywordList title="Matched" items={matchedKeywords} tone="text-mint" />
              <KeywordList title="Missing" items={missingKeywords} tone="text-coral" />
            </section>
          </aside>
          <CodeEditor latexCode={latexCode} setLatexCode={setLatexCode} />
        </div>
      </div>
    </main>
  );
}

function KeywordList({ title, items, tone }) {
  return (
    <div className="rounded border border-line bg-white p-4 shadow-sm">
      <h3 className={`text-sm font-semibold ${tone}`}>{title} Keywords</h3>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.length ? (
          items.slice(0, 30).map((item) => (
            <span key={item} className="rounded border border-line bg-paper px-2 py-1 text-xs text-slate-700">
              {item}
            </span>
          ))
        ) : (
          <span className="text-sm text-slate-500">No keywords yet.</span>
        )}
      </div>
    </div>
  );
}
