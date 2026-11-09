/* Progressive enhancement: the site is fully usable without JavaScript. */
(() => {
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('[data-category]')];
  const empty = document.getElementById('empty-filter');
  if (!buttons.length || !cards.length) return;
  buttons.forEach(button => button.addEventListener('click', () => {
    const value = button.getAttribute('data-filter');
    let visible = 0;
    buttons.forEach(el => {
      const selected = el === button;
      el.classList.toggle('active', selected);
      el.setAttribute('aria-pressed', String(selected));
    });
    cards.forEach(card => {
      const show = value === 'all' || card.getAttribute('data-category') === value;
      card.hidden = !show;
      if (show) visible++;
    });
    if (empty) empty.hidden = visible !== 0;
  }));
})();
