document.addEventListener("DOMContentLoaded", () => {
  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const historyPanel = document.getElementById("historyPanel");
  const historyEntries = document.getElementById("historyEntries");
  const historyToggleBtn = document.getElementById("historyToggleBtn");
  const newChatBtn = document.getElementById("newChatBtn");

  let chatHistory = JSON.parse(localStorage.getItem("chatHistory") || "[]");
  let currentChat = [];
  let currentChatIndex = -1;

  const urlParams = new URLSearchParams(window.location.search);
  const initialQuery = urlParams.get("query");
  if (initialQuery) {
    chatInput.value = initialQuery;
    sendMessage(initialQuery);
  }

  function updateChatHistory() {
    localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
  }

  function renderHistory() {
    historyEntries.innerHTML = chatHistory
      .map(
        (_, index) => `
        <div class="history-item">
          <button type="button" onclick="loadChat(${index})">Cuộc trò chuyện ${index + 1}</button>
          <button type="button" class="danger" onclick="deleteChat(${index})">Xóa</button>
        </div>`
      )
      .join("");
  }

  function appendUserMessage(query) {
    const node = document.createElement("div");
    node.className = "user-message";
    node.innerHTML = `<strong>Bạn:</strong> ${escapeHtml(query)}`;
    chatMessages.appendChild(node);
  }

  function renderRecommendations(movies) {
    const fragment = document.createDocumentFragment();
    const intro = document.createElement("div");
    intro.className = "bot-message";
    intro.innerHTML = "<strong>Cinemate:</strong> Đây là các phim phù hợp nhất với bạn:";
    fragment.appendChild(intro);

    movies.forEach((movie) => {
      const card = document.createElement("div");
      card.className = "movie-card";
      card.dataset.movieTitle = movie.title;
      card.innerHTML = `
        <img class="movie-poster" src="${escapeHtml(movie.poster || "")}" alt="${escapeHtml(movie.title)}" loading="lazy"
             onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
        <h3>${escapeHtml(movie.title)}</h3>
        <p class="movie-score">⭐ IMDb ${escapeHtml(movie.total_rating ?? "N/A")}</p>
        ${movie.explanation ? `<p class="movie-explanation">${escapeHtml(movie.explanation)}</p>` : ""}
      `;
      fragment.appendChild(card);
    });
    chatMessages.appendChild(fragment);
  }

  function sendMessage(query) {
    appendUserMessage(query);

    const loadingDiv = document.createElement("div");
    loadingDiv.className = "loading-container";
    loadingDiv.innerHTML = `<div class="loading-spinner"></div><div>Đang tìm phim phù hợp...</div>`;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    fetch(apiUrl("/recommend"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => {
        loadingDiv.remove();
        const movies = data.recommended_movies || [];
        if (!movies.length) {
          const empty = document.createElement("div");
          empty.className = "bot-message";
          empty.textContent = "Không tìm thấy phim phù hợp. Hãy thử mô tả thể loại, diễn viên hoặc đạo diễn.";
          chatMessages.appendChild(empty);
        } else {
          renderRecommendations(movies);
        }

        currentChat.push({ query, response: "Recommendations", movies });
        updateChatHistory();
        chatMessages.scrollTop = chatMessages.scrollHeight;
      })
      .catch((error) => {
        loadingDiv.remove();
        showToast(`Lỗi kết nối backend: ${error.message}`, "error");
        const errorNode = document.createElement("div");
        errorNode.className = "error-message";
        errorNode.textContent = "Không thể kết nối API. Hãy chắc chắn backend đang chạy ở cổng 5000.";
        chatMessages.appendChild(errorNode);
      });
  }

  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && chatInput.value.trim()) {
      sendMessage(chatInput.value.trim());
      chatInput.value = "";
    }
  });

  newChatBtn.addEventListener("click", () => {
    if (currentChat.length > 0) {
      const slot = currentChatIndex !== -1 ? currentChatIndex : chatHistory.length;
      chatHistory[slot] = [...currentChat];
      updateChatHistory();
      renderHistory();
    }
    currentChat = [];
    currentChatIndex = -1;
    chatMessages.innerHTML = "";
  });

  historyToggleBtn.addEventListener("click", () => {
    historyPanel.classList.toggle("open");
  });

  window.loadChat = function loadChat(index) {
    currentChatIndex = index;
    currentChat = JSON.parse(JSON.stringify(chatHistory[index]));
    chatMessages.innerHTML = "";
    currentChat.forEach((chat) => {
      appendUserMessage(chat.query);
      if (chat.movies?.length) renderRecommendations(chat.movies);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  window.deleteChat = function deleteChat(index) {
    chatHistory.splice(index, 1);
    updateChatHistory();
    renderHistory();
  };

  renderHistory();
});
