const FIELDS = [
  ["title", "Title"],
  ["sub_title", "Subtitle"],
  ["author", "Author"],
  ["publisher", "Publisher"],
  ["publication_date", "Publication date"],
  ["format", "Format"],
  ["nof_pages", "Pages"],
  ["language", "Language"],
  ["language_iso", "Language code"],
  ["isbn_13", "ISBN-13"],
  ["isbn_10", "ISBN-10"],
  ["description", "Description"],
];

const form = document.getElementById("search-form");
const statusEl = document.getElementById("status");
const button = document.getElementById("search");
const cover = document.getElementById("cover");
const dl = document.getElementById("details");
const addButton = document.getElementById("add");
const addStatus = document.getElementById("add-status");
const existsDialog = document.getElementById("exists-dialog");
let foundIsbn = null;
let foundBook = null;
let searchedIsbn = "";
let existingBookId = null;

function showMessage(text, isError) {
  statusEl.className = isError ? "error" : "";
  statusEl.textContent = text;
}

function showExistsDialog(bookId) {
  existingBookId = bookId;
  existsDialog.showModal();
}

document.getElementById("exists-update").addEventListener("click", () => {
  // Hand the search result over so the update page doesn't need a new search
  sessionStorage.setItem("foundBook", JSON.stringify({ bookId: existingBookId, isbn: searchedIsbn, book: foundBook }));
  window.location.assign("/update?id=" + encodeURIComponent(existingBookId));
});

addButton.addEventListener("click", async () => {
  addButton.disabled = true;
  addStatus.className = "";
  addStatus.textContent = "Adding...";
  try {
    const response = await fetch("/books/import/" + encodeURIComponent(foundIsbn), { method: "POST" });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      if (response.status === 409 && body.detail && body.detail.book_id) {
        showExistsDialog(body.detail.book_id);
        throw new Error(body.detail.message);
      }
      throw new Error(typeof body.detail === "string" ? body.detail : "HTTP " + response.status);
    }
    const book = await response.json();
    addButton.hidden = true;
    addStatus.replaceChildren("Book added. ");
    const link = document.createElement("a");
    link.href = "/book?id=" + book.id;
    link.textContent = "View book";
    addStatus.appendChild(link);
  } catch (err) {
    addStatus.className = "error";
    addStatus.textContent = "Could not add book: " + err.message;
    addButton.disabled = false;
  }
});

function showBook(book) {
  for (const [key, label] of FIELDS) {
    const value = book[key];
    if (value === null || value === undefined || value === "") continue;
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    dl.append(dt, dd);
  }
  if (book.image_url) {
    cover.src = book.image_url;
    cover.hidden = false;
  }
  foundIsbn = (book.isbn_13 || "").replaceAll("-", "");
  addButton.disabled = false;
  addButton.hidden = !foundIsbn;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const isbn = document.getElementById("isbn").value.trim();
  dl.replaceChildren();
  cover.hidden = true;
  addButton.hidden = true;
  addStatus.textContent = "";
  button.disabled = true;
  showMessage("Searching...", false);
  try {
    const response = await fetch("/books/search/" + encodeURIComponent(isbn));
    if (response.status === 404) {
      showMessage("No book found for ISBN " + isbn + ".", true);
      return;
    }
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || "HTTP " + response.status);
    }
    showMessage("", false);
    foundBook = await response.json();
    searchedIsbn = isbn.replaceAll("-", "");
    showBook(foundBook);
  } catch (err) {
    showMessage("Search failed: " + err.message, true);
  } finally {
    button.disabled = false;
  }
});
