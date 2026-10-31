const FIELDS = [
  ["sub_title", "Subtitle"],
  ["authors", "Authors"],
  ["org_title", "Original title"],
  ["org_sub_title", "Original subtitle"],
  ["org_publication_year", "Original publication year"],
  ["publisher", "Publisher"],
  ["print_format", "Format"],
  ["pages", "Pages"],
  ["language", "Language"],
  ["language_iso", "Language code"],
  ["isbn_13", "ISBN-13"],
  ["isbn_10", "ISBN-10"],
  ["description", "Description"],
];

const EDIT_FIELDS = [
  ["title", "Title", "text"],
  ["sub_title", "Subtitle", "text"],
  ["org_title", "Original title", "text"],
  ["org_sub_title", "Original subtitle", "text"],
  ["org_publication_year", "Original publication year", "number"],
  ["print_format", "Format", "text"],
  ["pages", "Pages", "number"],
  ["publisher", "Publisher", "text"],
  ["cover", "Cover filename", "text"],
  ["language", "Language", "text"],
  ["language_iso", "Language code", "text"],
  ["isbn_13", "ISBN-13", "text"],
  ["isbn_10", "ISBN-10", "text"],
  ["description", "Description", "textarea"],
];

const statusEl = document.getElementById("status");
const detailsEl = document.getElementById("details");
const editForm = document.getElementById("edit-form");
const editFields = document.getElementById("edit-fields");
const actions = document.getElementById("actions");
let bookId;
let bookData;

function showStatus(message, isError = false) {
  statusEl.className = isError ? "error" : "";
  statusEl.textContent = message;
}

async function responseError(response) {
  const body = await response.json().catch(() => ({}));
  return body.detail || body.message || "HTTP " + response.status;
}

function showCover(cover) {
  if (!cover) return;
  const COVER_DIR = "/static/book_covers/";
  const thumb = document.getElementById("cover");
  const overlay = document.getElementById("overlay");
  const full = document.getElementById("full");
  thumb.src = COVER_DIR + encodeURIComponent(cover);
  thumb.hidden = false;
  if (cover.startsWith("placeholder")) return;

  thumb.classList.add("zoomable");
  const largeName = cover.replace(/(\.[^.]+)$/, "_large$1");
  thumb.addEventListener("click", () => {
    full.onerror = () => {
      full.onerror = null;
      full.src = thumb.src;
    };
    full.src = COVER_DIR + encodeURIComponent(largeName);
    overlay.classList.add("open");
  });
  overlay.addEventListener("click", () => overlay.classList.remove("open"));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") overlay.classList.remove("open");
  });
}

function renderBook(book) {
  bookData = book;
  document.title = book.title;
  document.getElementById("title").textContent = book.title;
  detailsEl.replaceChildren();
  for (const [key, label] of FIELDS) {
    if (key === "authors" && !book.authors.length) continue;
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    if (key === "authors") {
      for (const [index, author] of book.authors.entries()) {
        if (index > 0) dd.append(", ");
        const entry = document.createElement("span");
        const name = document.createElement("span");
        name.textContent = author.name;
        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.setAttribute("aria-label", "Edit author " + author.name);
        editButton.addEventListener("click", () => editAuthor(author, entry));
        entry.append(name, " ", editButton);
        dd.appendChild(entry);
      }
      detailsEl.append(dt, dd);
      continue;
    }
    const value = book[key];
    if (value === null || value === undefined || value === "") continue;
    dd.textContent = value;
    detailsEl.append(dt, dd);
  }
  const cover = document.getElementById("cover");
  cover.hidden = true;
  cover.classList.remove("zoomable");
  cover.replaceWith(cover.cloneNode(true));
  showCover(book.cover);
  actions.hidden = false;
  editForm.hidden = true;
  detailsEl.hidden = false;
}

function editAuthor(author, entry) {
  const form = document.createElement("form");
  const input = document.createElement("input");
  input.type = "text";
  input.name = "name";
  input.value = author.name;
  input.required = true;
  input.setAttribute("aria-label", "Author name");
  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.textContent = "Save";
  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.textContent = "Cancel";
  cancelButton.addEventListener("click", () => renderBook(bookData));
  form.append(input, saveButton, cancelButton);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = input.value.trim();
    if (!name) {
      input.setCustomValidity("Enter an author name.");
      input.reportValidity();
      return;
    }
    input.setCustomValidity("");
    saveButton.disabled = true;
    try {
      const response = await fetch("/authors/" + encodeURIComponent(author.id), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) throw new Error(await responseError(response));
      const updatedAuthor = await response.json();
      bookData.authors = bookData.authors.map((item) =>
        item.id === updatedAuthor.id ? updatedAuthor : item
      );
      renderBook(bookData);
      showStatus("Author updated.");
    } catch (err) {
      showStatus("Could not update author: " + err.message, true);
      saveButton.disabled = false;
    }
  });
  entry.replaceChildren(form);
  input.focus();
  input.select();
}

function addEditField(key, labelText, type, value) {
  const label = document.createElement("label");
  label.htmlFor = "edit-" + key;
  label.textContent = labelText;

  const input = type === "textarea" ? document.createElement("textarea") : document.createElement("input");
  input.id = "edit-" + key;
  input.name = key;
  if (type !== "textarea") input.type = type;
  if (type === "number") input.step = "1";
  if (value !== null && value !== undefined) input.value = value;
  if (key === "title") input.required = true;
  label.appendChild(input);
  editFields.appendChild(label);
}

async function openEditForm() {
  const editButton = document.getElementById("edit");
  editButton.disabled = true;
  showStatus("Loading authors...");
  try {
    const response = await fetch("/authors/");
    if (!response.ok) throw new Error(await responseError(response));
    const authors = await response.json();
    editFields.replaceChildren();
    for (const [key, label, type] of EDIT_FIELDS) {
      addEditField(key, label, type, bookData[key]);
    }

    const authorLabel = document.createElement("label");
    authorLabel.htmlFor = "edit-author_ids";
    authorLabel.textContent = "Authors (hold Ctrl or Command to select multiple)";
    const authorSelect = document.createElement("select");
    authorSelect.id = "edit-author_ids";
    authorSelect.name = "author_ids";
    authorSelect.multiple = true;
    const selectedAuthorIds = new Set(bookData.authors.map((author) => author.id));
    for (const author of authors) {
      const option = document.createElement("option");
      option.value = author.id;
      option.textContent = author.name;
      option.selected = selectedAuthorIds.has(author.id);
      authorSelect.appendChild(option);
    }
    authorLabel.appendChild(authorSelect);
    editFields.appendChild(authorLabel);

    detailsEl.hidden = true;
    document.getElementById("cover").hidden = true;
    editForm.hidden = false;
    showStatus("");
  } catch (err) {
    showStatus("Could not open edit form: " + err.message, true);
  } finally {
    editButton.disabled = false;
  }
}

async function saveBook(event) {
  event.preventDefault();
  const saveButton = document.getElementById("save");
  saveButton.disabled = true;
  showStatus("Saving changes...");
  try {
    const formData = new FormData(editForm);
    const updatedBook = {};
    for (const [key, , type] of EDIT_FIELDS) {
      const value = formData.get(key);
      updatedBook[key] = type === "number" ? (value === "" ? null : Number(value)) : (value || null);
    }
    updatedBook.author_ids = formData.getAll("author_ids").map(Number);
    const response = await fetch("/books/" + encodeURIComponent(bookId), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedBook),
    });
    if (!response.ok) throw new Error(await responseError(response));
    renderBook(await response.json());
    showStatus("Book updated.");
  } catch (err) {
    showStatus("Could not save book: " + err.message, true);
  } finally {
    saveButton.disabled = false;
  }
}

async function deleteBook() {
  if (!window.confirm("Delete this book from your collection?")) return;
  const deleteButton = document.getElementById("delete");
  deleteButton.disabled = true;
  showStatus("Deleting book...");
  try {
    const response = await fetch("/books/" + encodeURIComponent(bookId), { method: "DELETE" });
    if (!response.ok) throw new Error(await responseError(response));
    const result = await response.json();
    if (result.message === "Book not found!") throw new Error(result.message);
    window.location.assign("/");
  } catch (err) {
    showStatus("Could not delete book: " + err.message, true);
    deleteButton.disabled = false;
  }
}

async function loadBook() {
  bookId = new URLSearchParams(location.search).get("id");
  if (!bookId) {
    showStatus("No book specified.", true);
    return;
  }
  try {
    const response = await fetch("/books/" + encodeURIComponent(bookId));
    if (!response.ok) throw new Error(await responseError(response));
    renderBook(await response.json());
  } catch (err) {
    showStatus("Failed to load book: " + err.message, true);
  }
}

document.getElementById("edit").addEventListener("click", openEditForm);
document.getElementById("update-info").addEventListener("click", () => {
  window.location.assign("/update?id=" + encodeURIComponent(bookId));
});
document.getElementById("delete").addEventListener("click", deleteBook);
document.getElementById("cancel-edit").addEventListener("click", () => {
  editForm.hidden = true;
  detailsEl.hidden = false;
  const cover = document.getElementById("cover");
  cover.hidden = !bookData.cover;
  showStatus("");
});
editForm.addEventListener("submit", saveBook);

loadBook();
