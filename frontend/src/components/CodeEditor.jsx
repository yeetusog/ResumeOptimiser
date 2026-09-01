import React, { Suspense } from "react";

const MonacoEditor = React.lazy(() => import("@monaco-editor/react"));

export default function CodeEditor({ latexCode, setLatexCode }) {
  return (
    <section className="space-y-3">
      <h2 className="text-base font-semibold text-ink">LaTeX Editor</h2>
      <div className="h-[520px] overflow-hidden rounded border border-line bg-white shadow-sm">
        <Suspense fallback={<div className="p-4 text-sm text-slate-600">Loading editor...</div>}>
          <MonacoEditor
            height="520px"
            defaultLanguage="latex"
            theme="vs-light"
            value={latexCode}
            onChange={(value) => setLatexCode(value || "")}
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              wordWrap: "on",
              scrollBeyondLastLine: false,
              automaticLayout: true
            }}
          />
        </Suspense>
      </div>
    </section>
  );
}
