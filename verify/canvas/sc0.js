
(function () {
  try {
    if (localStorage.getItem('ruang.theme.v1') === 'light') {
      document.body.classList.add('theme--light', 'light-theme');
      document.body.setAttribute('data-theme', 'light');
    }
  } catch (e) {}
})();
