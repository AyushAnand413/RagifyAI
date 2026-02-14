import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

import UploadPanel from "./components/UploadPanel";
import ChatPanel from "./components/ChatPanel";

const queryClient = new QueryClient();

function Workspace() {
  const [uploadInfo, setUploadInfo] = useState(null);

  return (
    <main>
      <h1>Corporate Bot</h1>
      <UploadPanel onUploadSuccess={setUploadInfo} />
      {uploadInfo && <p>Active document: {uploadInfo.filename}</p>}
      <ChatPanel />
    </main>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Workspace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
