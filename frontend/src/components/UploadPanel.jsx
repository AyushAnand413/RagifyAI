import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { uploadDocument } from "../api/client";

export default function UploadPanel({ onUploadSuccess }) {
  const [file, setFile] = useState(null);

  const uploadMutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: (data) => {
      onUploadSuccess(data);
    },
  });

  const handleUpload = () => {
    if (!file) return;
    uploadMutation.mutate(file);
  };

  return (
    <section>
      <h2>Upload PDF</h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button onClick={handleUpload} disabled={!file || uploadMutation.isPending}>
        {uploadMutation.isPending ? "Uploading..." : "Upload"}
      </button>

      {uploadMutation.isSuccess && <p>Upload successful.</p>}
      {uploadMutation.isError && <p>Upload failed.</p>}
    </section>
  );
}
