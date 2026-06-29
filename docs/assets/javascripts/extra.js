/* AutonomyLoops Documentation - Extra JavaScript */

// Auto-copy code blocks notification
document.addEventListener("DOMContentLoaded", function() {
  // Add copy feedback
  document.querySelectorAll(".md-clipboard").forEach(function(btn) {
    btn.addEventListener("click", function() {
      const original = btn.getAttribute("data-clipboard-text");
      if (original) {
        btn.classList.add("copied");
        setTimeout(() => btn.classList.remove("copied"), 2000);
      }
    });
  });
});
