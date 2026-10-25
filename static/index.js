const list = document.getElementById("authors");
const statusEl = document.getElementById("status");
const filterInput = document.getElementById("author-filter");
let authorRows = [];
let authorsLoaded = false;

function filterAuthors() {
  if (!authorsLoaded) return;
  const prefix = filterInput.value.trim().toLocaleLowerCase();
  const matchingRows = authorRows.filter(({ author }) =>
    author.name.toLocaleLowerCase().startsWith(prefix)
  );
  list.replaceChildren(...matchingRows.map(({ element }) => element));
  statusEl.textContent = authorRows.length
    ? matchingRows.length ? "" : "No authors match this filter."
    : "No authors found.";
}

function renderAuthor(author) {
  const li = document.createElement("li");
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  const books = document.createElement("ul");
  summary.textContent = author.name;
  details.append(summary, books);
  li.appendChild(details);

  let loaded = false;
  details.addEventListener("toggle", async () => {
    if (!details.open || loaded) return;
    books.replaceChildren(Object.assign(document.createElement("li"), { textContent: "Loading..." }));
    try {
      const response = await fetch("/authors/" + author.id);
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      books.replaceChildren();
      if (!data.books.length) {
        books.appendChild(Object.assign(document.createElement("li"), { textContent: "No books found." }));
      }
      for (const book of data.books) {
        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = "/book?id=" + book.id;
        link.textContent = book.title;
        item.appendChild(link);
        books.appendChild(item);
      }
      loaded = true;
    } catch (err) {
      books.replaceChildren(Object.assign(document.createElement("li"), {
        className: "error",
        textContent: "Failed to load books: " + err.message,
      }));
    }
  });
  return li;
}

async function fetchAuthors() {
  statusEl.className = "";
  statusEl.textContent = "Loading...";
  list.replaceChildren();
  authorRows = [];
  authorsLoaded = false;
  try {
    const response = await fetch("/authors/");
    if (!response.ok) throw new Error("HTTP " + response.status);
    const authors = await response.json();
    authorRows = authors.map((author) => ({ author, element: renderAuthor(author) }));
    authorsLoaded = true;
    filterAuthors();
  } catch (err) {
    statusEl.className = "error";
    statusEl.textContent = "Failed to load authors: " + err.message;
  }
}

document.getElementById("load").addEventListener("click", fetchAuthors);
filterInput.addEventListener("input", filterAuthors);
fetchAuthors();
