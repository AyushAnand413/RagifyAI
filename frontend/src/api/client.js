import axios from "axios";

const api = axios.create({
  baseURL: "/",
});

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function sendChat(query) {
  const response = await api.post("/chat", { query });
  return response.data;
}
