function initializeMovieModal() {
  const modal = document.getElementById("movieModal");
  if (!modal) return;
  modal.addEventListener("click", (event) => {
    if (event.target.classList.contains("close") || event.target === modal) {
      modal.style.display = "none";
    }
  });
}

function handleMovieClicks() {
  document.addEventListener("click", async (event) => {
    const card = event.target.closest(".movie-card");
    if (!card || !card.dataset.movieTitle) return;

    const movieTitle = card.dataset.movieTitle;
    const modal = document.getElementById("movieModal");
    if (!modal) return;

    try {
      modal.innerHTML = `
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <div>Đang tải thông tin phim...</div>
        </div>`;
      modal.style.display = "flex";

      const response = await fetch(apiUrl(`/movie/${encodeURIComponent(movieTitle)}`));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const movie = await response.json();
      modal.innerHTML = `
        <div class="modal-content">
          <span class="close" aria-label="Đóng">&times;</span>
          <img src="${escapeHtml(movie.poster || "")}" class="modal-poster" alt="${escapeHtml(movie.title)}">
          <div class="modal-info">
            <h2 class="movie-title">${escapeHtml(movie.title)}</h2>
            <p><span class="label">Thể loại:</span> ${escapeHtml(movie.genre)}</p>
            <p><span class="label">Diễn viên:</span> ${escapeHtml(movie.actors)}</p>
            <p><span class="label">Đạo diễn:</span> ${escapeHtml(movie.director)}</p>
            <p><span class="label">Mô tả:</span> ${escapeHtml(movie.overview)}</p>
            <p><span class="label">Thời lượng:</span> ${escapeHtml(movie.runtime)} phút</p>
            <p><span class="label">IMDb:</span> ${escapeHtml(movie.ratingIMDB)}</p>
            ${movie.trailer
              ? `<a href="${escapeHtml(movie.trailer)}" target="_blank" rel="noopener" class="trailer-button">Xem trailer</a>`
              : "<p class='no-trailer'>Chưa có trailer</p>"}
          </div>
        </div>`;
    } catch (error) {
      modal.innerHTML = `
        <div class="modal-content error">
          <span class="close">&times;</span>
          <p>Không tải được phim: ${escapeHtml(error.message)}</p>
        </div>`;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initializeMovieModal();
  handleMovieClicks();
});
