const list = document.getElementById("authors");
const statusEl = document.getElementById("status");

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
  try {
    const response = await fetch("/authors/");
    if (!response.ok) throw new Error("HTTP " + response.status);
    const authors = await response.json();
    statusEl.textContent = authors.length ? "" : "No authors found.";
    for (const author of authors) {
      list.appendChild(renderAuthor(author));
    }
  } catch (err) {
    statusEl.className = "error";
    statusEl.textContent = "Failed to load authors: " + err.message;
  }
}

document.getElementById("load").addEventListener("click", fetchAuthors);
fetchAuthors();
