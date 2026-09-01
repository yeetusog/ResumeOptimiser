import { useDropzone } from "react-dropzone";

export default function FileUpload({ onFile, isUploading, resumeText }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt", ".tex"]
    },
    multiple: false,
    onDrop: (accepted) => {
      if (accepted[0]) onFile(accepted[0]);
    }
  });

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-ink">Resume Source</h2>
        {resumeText ? <span className="text-xs font-medium text-mint">Loaded</span> : null}
      </div>
      <div
        {...getRootProps()}
        className={`focus-ring flex min-h-36 cursor-pointer items-center justify-center rounded border border-dashed px-5 py-8 text-center transition ${
          isDragActive ? "border-mint bg-emerald-50" : "border-line bg-white hover:border-mint"
        }`}
      >
        <input {...getInputProps()} />
        <div>
          <p className="text-sm font-semibold text-ink">
            {isUploading ? "Extracting text..." : "Drop PDF, DOCX, or TEX resume"}
          </p>
          <p className="mt-2 text-sm text-slate-600">or click to choose a file</p>
        </div>
      </div>
      <textarea
        value={resumeText}
        readOnly
        className="h-44 w-full resize-none rounded border border-line bg-white p-3 text-sm text-slate-700 shadow-sm"
        placeholder="Extracted resume text appears here."
      />
    </section>
  );
}
