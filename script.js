const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");
const messages = document.querySelector("#messages");
const quickButtons = document.querySelectorAll("[data-question]");
const columnButtons = document.querySelectorAll("[data-column]");

function displayColumnName(column) {
  return column === "Nom_Equipament" ? "Nom Biblioteca*" : column;
}

function addMessage(text, role) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  message.appendChild(paragraph);
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
}

function addRichMessage(node, role) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  message.appendChild(node);
  messages.appendChild(message);
  // Do not auto-scroll to bottom for rich messages; return the element so callers can control scrolling
  return message;
}

function renderLibraryRows(rows) {
  const container = document.createElement("div");
  container.className = "row-detail-list";
  rows.forEach((row, index) => {
    const card = document.createElement("div");
    card.className = "row-card";
    const title = document.createElement("h3");
    // Mostrar solo el nombre de la biblioteca como título
    title.textContent = row.Nom_Equipament || "Biblioteca";
    card.appendChild(title);

    const details = document.createElement("dl");
    for (const [key, value] of Object.entries(row)) {
      const dt = document.createElement("dt");
      dt.textContent = displayColumnName(key);
      const dd = document.createElement("dd");
      dd.textContent = value ?? "";
      details.appendChild(dt);
      details.appendChild(dd);
    }

    card.appendChild(details);
    container.appendChild(card);
  });
  return container;
}

async function ask(question) {
  addMessage(question, "user");
  input.value = "";
  input.disabled = true;

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();
    addMessage(data.answer || "No he rebut una resposta vàlida.", "assistant");
    if (data.maps_url) {
      const mapMsg = document.createElement("article");
      mapMsg.className = "message assistant";
      const btn = document.createElement("button");
      btn.textContent = "Obrir a Google Maps";
      btn.addEventListener("click", () => window.open(data.maps_url, "_blank"));
      btn.style.marginTop = "8px";
      mapMsg.appendChild(btn);
      messages.appendChild(mapMsg);
      messages.scrollTop = messages.scrollHeight;
    }
  } catch (error) {
    addMessage("No s'ha pogut connectar amb el servidor local. Revisa que app.py estigui en execució.", "assistant");
  } finally {
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (question) {
    ask(question);
  }
});

quickButtons.forEach((button) => {
  button.addEventListener("click", () => {
    ask(button.dataset.question);
  });
});

columnButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const col = button.dataset.column;
    if (!col) return;
    const unique = false;
    try {
      const resp = await fetch(`/api/column?col=${encodeURIComponent(col)}&unique=${unique}`);
      const data = await resp.json();
      if (data.error) {
        addMessage(`Error: ${data.error}`, "assistant");
        return;
      }
      const values = data.values || [];
      const count = data.count || values.length;
      const listContainer = document.createElement("div");
      const title = document.createElement("p");
      title.textContent = `Mostrant tots els ${count} registres per ${displayColumnName(col)}:`;
      listContainer.appendChild(title);

      const valuesGrid = document.createElement("div");
      valuesGrid.className = "value-list";
      // Append the list container as a message and keep a reference so we can replace its content
      const listMessage = addRichMessage(listContainer, "assistant");
      values.forEach((value) => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "value-pill";
        item.textContent = value;
        item.addEventListener("click", async () => {
          try {
            const rowResp = await fetch(`/api/library?library=${encodeURIComponent(value)}`);
            const rowData = await rowResp.json();
            if (rowData.error) {
              addMessage(`Error: ${rowData.error}`, "assistant");
              return;
            }
            const rows = rowData.rows || [];
            if (rows.length === 0) {
              addMessage('No s\'han trobat files per aquesta biblioteca.', 'assistant');
            } else {
              // Mostrar solo la primera fila (principal) por petición del usuario
              const primary = rows[0];
              const detailNode = renderLibraryRows([primary]);
              // If coordinates available, add Google Maps button
              const lat = primary.Latitud || primary.Latitude || primary.lat || primary.Lat || '';
              const lon = primary.Longitud || primary.Longitud || primary.Longitude || primary.lon || '';
              if (lat && lon) {
                const mapBtn = document.createElement('button');
                mapBtn.type = 'button';
                mapBtn.textContent = 'Obrir a Google Maps';
                mapBtn.className = 'value-pill';
                const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(lat)},${encodeURIComponent(lon)}`;
                mapBtn.addEventListener('click', () => window.open(mapsUrl, '_blank'));
                detailNode.appendChild(mapBtn);
              }
              // Replace the list message content with the detail node so it's visible without scrolling to bottom
              listMessage.innerHTML = '';
              listMessage.appendChild(detailNode);
            }
          } catch (err) {
            addMessage("No s'ha pogut recuperar els detalls de la biblioteca.", "assistant");
          }
        });
        valuesGrid.appendChild(item);
      });
      listContainer.appendChild(valuesGrid);
    } catch (e) {
      addMessage("No s'ha pogut recuperar els valors del servidor.", "assistant");
    }
  });
});
