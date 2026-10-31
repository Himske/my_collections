const FOUND_FIELDS = [
  ["title", "Title", "text"],
  ["sub_title", "Subtitle", "text"],
  ["author", "Author (not changed by the update)", "readonly"],
  ["publisher", "Publisher", "text"],
  ["publication_date", "Publication date", "text"],
  ["format", "Format", "text"],
  ["nof_pages", "Pages", "number"],
  ["language", "Language", "text"],
  ["language_iso", "Language code", "text"],
  ["isbn_13", "ISBN-13", "text"],
  ["isbn_10", "ISBN-10", "text"],
  ["description", "Description", "textarea"],
];

const CURRENT_FIELDS = [
  ["title", "Title"],
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

const statusEl = document.getElementById("status");
const form = document.getElementById("search-form");
const searchButton = document.getElementById("search");
const searchStatus = document.getElementById("search-status");
const foundCover = document.getElementById("found-cover");
const foundForm = document.getElementById("found-form");
const foundFields = document.getElementById("found-fields");
const applyButton = document.getElementById("apply");
const applyStatus = document.getElementById("apply-status");
const replaceCover = document.getElementById("replace-cover");
const replaceCoverLabel = document.getElementById("replace-cover-label");
const cover = document.getElementById("cover");
const details = document.getElementById("details");
let bookId;
let bookData;
let searchedIsbn = "";

function showMessage(el, text, isError = false) {
  el.className = isError ? "error" : "";
  el.textContent = text;
}

async function responseError(response) {
  const body = await response.json().catch(() => ({}));
  return body.detail || "HTTP " + response.status;
}

function hasValue(value) {
  return value !== null && value !== undefined && value !== "";
}

function renderCurrent(book) {
  bookData = book;
  document.title = "Update " + book.title;
  details.replaceChildren();
  for (const [key, label] of CURRENT_FIELDS) {
    const value = key === "authors" ? book.authors.map((author) => author.name).join(", ") : book[key];
    if (!hasValue(value)) continue;
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    details.append(dt, dd);
  }
  cover.hidden = !book.cover;
  // The cover file keeps its name when replaced, so bypass the browser cache
  if (book.cover) cover.src = "/static/book_covers/" + encodeURIComponent(book.cover) + "?t=" + Date.now();
}

function renderFound(book) {
  foundFields.replaceChildren();
  for (const [key, labelText, type] of FOUND_FIELDS) {
    const label = document.createElement("label");
    label.htmlFor = "found-" + key;
    label.textContent = labelText;
    const input = type === "textarea" ? document.createElement("textarea") : document.createElement("input");
    input.id = "found-" + key;
    input.name = key;
    if (type === "readonly") {
      input.type = "text";
      input.readOnly = true;
    } else if (type !== "textarea") {
      input.type = type;
    }
    if (type === "number") input.min = "0";
    if (hasValue(book[key])) input.value = book[key];
    label.appendChild(input);
    foundFields.appendChild(label);
  }
  if (book.image_url) {
    foundCover.src = book.image_url;
    foundCover.hidden = false;
  }
  replaceCoverLabel.hidden = !book.image_url;
  applyButton.disabled = false;
  foundForm.hidden = false;
}

function clearFound() {
  foundFields.replaceChildren();
  foundCover.hidden = true;
  replaceCoverLabel.hidden = true;
  foundForm.hidden = true;
  applyStatus.textContent = "";
}

function buildUpdate(book) {
  const update = { ...book, author_ids: book.authors.map((author) => author.id) };
  delete update.id;
  delete update.authors;
  const edited = (key) => foundFields.querySelector("[name=" + key + "]").value.trim();
  const text = { title: "title", sub_title: "sub_title", publisher: "publisher", print_format: "format",
    language: "language", language_iso: "language_iso", isbn_13: "isbn_13", isbn_10: "isbn_10",
    description: "description" };
  for (const [target, source] of Object.entries(text)) {
    const value = edited(source);
    if (!value) continue;
    update[target] = target.startsWith("isbn") ? value.replaceAll("-", "") : value;
  }
  const pages = edited("nof_pages");
  if (/^\d+$/.test(pages)) update.pages = Number(pages);
  const year = edited("publication_date").slice(0, 4);
  if (/^\d{4}$/.test(year)) update.org_publication_year = Number(year);
  return update;
}

async function applyFound(event) {
  event.preventDefault();
  applyButton.disabled = true;
  showMessage(applyStatus, "Updating...");
  try {
    const response = await fetch("/books/" + encodeURIComponent(bookId), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildUpdate(bookData)),
    });
    if (!response.ok) throw new Error(await responseError(response));
    let updated = await response.json();
    renderCurrent(updated);
    if (replaceCover.checked && !replaceCoverLabel.hidden) {
      const coverResponse = await fetch(
        "/books/" + encodeURIComponent(bookId) + "/cover?isbn=" + encodeURIComponent(searchedIsbn),
        { method: "POST" }
      );
      if (!coverResponse.ok) {
        throw new Error("Book updated, but the cover could not be replaced: " + (await responseError(coverResponse)));
      }
      updated = await coverResponse.json();
      renderCurrent(updated);
    }
    showMessage(applyStatus, "Book updated.");
  } catch (err) {
    showMessage(applyStatus, "Could not update book: " + err.message, true);
  } finally {
    applyButton.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const isbn = document.getElementById("isbn").value.trim();
  clearFound();
  searchButton.disabled = true;
  showMessage(searchStatus, "Searching...");
  try {
    const response = await fetch("/books/search/" + encodeURIComponent(isbn));
    if (response.status === 404) {
      showMessage(searchStatus, "No book found for ISBN " + isbn + ".", true);
      return;
    }
    if (!response.ok) throw new Error(await responseError(response));
    const found = await response.json();
    searchedIsbn = isbn.replaceAll("-", "");
    showMessage(searchStatus, "");
    renderFound(found);
  } catch (err) {
    showMessage(searchStatus, "Search failed: " + err.message, true);
  } finally {
    searchButton.disabled = false;
  }
});

foundForm.addEventListener("submit", applyFound);

// Restores the search result handed over from the find page, if it is for this book
function restoreFound() {
  let handover;
  try {
    handover = JSON.parse(sessionStorage.getItem("foundBook"));
  } catch {
    handover = null;
  }
  sessionStorage.removeItem("foundBook");
  if (!handover || String(handover.bookId) !== String(bookId) || !handover.book) return;
  searchedIsbn = handover.isbn;
  document.getElementById("isbn").value = handover.isbn;
  renderFound(handover.book);
}

async function loadBook() {
  bookId = new URLSearchParams(location.search).get("id");
  if (!bookId) {
    showMessage(statusEl, "No book specified.", true);
    form.hidden = true;
    return;
  }
  document.getElementById("back").href = "/book?id=" + encodeURIComponent(bookId);
  document.getElementById("back").textContent = "\u2190 Back to book";
  try {
    const response = await fetch("/books/" + encodeURIComponent(bookId));
    if (!response.ok) throw new Error(await responseError(response));
    const book = await response.json();
    renderCurrent(book);
    if (book.isbn_13) document.getElementById("isbn").value = book.isbn_13;
    restoreFound();
  } catch (err) {
    showMessage(statusEl, "Failed to load book: " + err.message, true);
    form.hidden = true;
  }
}

loadBook();
