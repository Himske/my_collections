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

async function loadBook() {
  const statusEl = document.getElementById("status");
  const id = new URLSearchParams(location.search).get("id");
  if (!id) {
    statusEl.className = "error";
    statusEl.textContent = "No book specified.";
    return;
  }
  try {
    const response = await fetch("/books/" + encodeURIComponent(id));
    if (!response.ok) throw new Error(response.status === 404 ? "Book not found" : "HTTP " + response.status);
    const book = await response.json();
    document.title = book.title;
    document.getElementById("title").textContent = book.title;
    showCover(book.cover);
    const dl = document.getElementById("details");
    for (const [key, label] of FIELDS) {
      const value = key === "authors" ? book.authors.map((a) => a.name).join(", ") : book[key];
      if (value === null || value === undefined || value === "") continue;
      const dt = document.createElement("dt");
      dt.textContent = label;
      const dd = document.createElement("dd");
      dd.textContent = value;
      dl.append(dt, dd);
    }
  } catch (err) {
    statusEl.className = "error";
    statusEl.textContent = "Failed to load book: " + err.message;
  }
}

loadBook();
