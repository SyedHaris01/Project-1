import { api } from "./api";

export async function getSubjects() {
  return api("/subjects/");
}

export async function createSubject(name) {
  return api("/subjects/", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function updateSubject(id, name) {
  return api(`/subjects/${id}/`, {
    method: "PUT",
    body: JSON.stringify({ name }),
  });
}

export async function deleteSubject(id) {
  return api(`/subjects/${id}/`, {
    method: "DELETE",
  });
}