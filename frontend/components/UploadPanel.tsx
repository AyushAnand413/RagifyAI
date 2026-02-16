"use client";

import React from "react";

type UploadStatus = "idle" | "loading" | "success" | "error";

type UploadPanelProps = {
  onUpload: (file: File) => Promise<void>;
  isLoading: boolean;
  uploadedFilename: string | null;
  status: UploadStatus;
  errorMessage?: string | null;
};

export default function UploadPanel({
  onUpload,
  isLoading,
  uploadedFilename,
  status,
  errorMessage,
}: UploadPanelProps) {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedFile || isLoading) {
      return;
    }
    await onUpload(selectedFile);
  };

  return (
    <section className="card">
      <h2>1) Upload PDF</h2>
      <form onSubmit={handleSubmit}>
        <div className="row row-wrap">
          <input
            className="file"
            type="file"
            accept="application/pdf"
            onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
            disabled={isLoading}
          />
          <button className="button" type="submit" disabled={!selectedFile || isLoading}>
            {isLoading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </form>

      {status === "loading" ? (
        <div className="upload-progress" aria-live="polite">
          <div className="progress-track">
            <div className="progress-indeterminate" />
          </div>
          <p className="help">Uploading and indexing document...</p>
        </div>
      ) : null}

      {status === "success" && uploadedFilename ? <p className="help">Uploaded: {uploadedFilename}</p> : null}
      {status === "error" && errorMessage ? <p className="help error-text">{errorMessage}</p> : null}
      {!uploadedFilename && status !== "loading" ? <p className="help">Upload a PDF to enable chat.</p> : null}
    </section>
  );
}
