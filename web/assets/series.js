/* Finance 100: progressive enhancement for course search and chapter filters.
   All 100 links remain present and readable when JavaScript is unavailable. */
(() => {
  const input = document.getElementById('episode-search');
  const clear = document.getElementById('course-clear');
  const counter = document.getElementById('course-match-count');
  const none = document.getElementById('course-no-results');
  const cards = [...document.querySelectorAll('[data-course-module]')];
  const sections = [...document.querySelectorAll('[data-course-section]')];
  const filters = [...document.querySelectorAll('[data-course-filter]')];
  if (!input || !cards.length) return;
  let selected = 'all';
  function update() {
    const query = input.value.trim().toLocaleLowerCase('zh-CN');
    let visible = 0;
    cards.forEach(card => {
      const module = card.getAttribute('data-course-module');
      const search = (card.getAttribute('data-course-search') || '').toLocaleLowerCase('zh-CN');
      const show = (selected === 'all' || selected === module) && (!query || search.includes(query));
      card.hidden = !show;
      if (show) visible += 1;
    });
    sections.forEach(section => {
      section.hidden = !section.querySelector('[data-course-module]:not([hidden])');
    });
    filters.forEach(button => {
      const active = button.getAttribute('data-course-filter') === selected;
      button.classList.toggle('current', active);
      button.setAttribute('aria-pressed', String(active));
    });
    if (counter) counter.textContent = '显示' + visible + '/100集';
    if (none) none.hidden = visible !== 0;
  }
  input.addEventListener('input', update);
  if (clear) clear.addEventListener('click', () => { input.value = ''; selected = 'all'; update(); input.focus(); });
  filters.forEach(button => button.addEventListener('click', () => {
    selected = button.getAttribute('data-course-filter') || 'all';
    update();
  }));
  update();
})();