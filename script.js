const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");
const messages = document.querySelector("#messages");
const quickButtons = document.querySelectorAll("[data-question]");

function addMessage(text, role) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  message.appendChild(paragraph);
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
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
