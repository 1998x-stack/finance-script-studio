/* The full audit queue remains readable when JavaScript is unavailable. */
(() => {
  const input = document.getElementById('prod-search');
  const list = [...document.querySelectorAll('[data-prod-queue]')];
  const buttons = [...document.querySelectorAll('[data-prod-filter]')];
  const counter = document.getElementById('prod-count');
  const empty = document.getElementById('prod-no-results');
  if (!input || !list.length) return;
  let selected = 'all';
  function update() {
    const query = input.value.trim().toLocaleLowerCase('zh-CN');
    let total = 0;
    list.forEach(item => {
      const text = (item.getAttribute('data-prod-search') || '').toLocaleLowerCase('zh-CN');
      const priority = item.getAttribute('data-prod-queue');
      const visible = (selected === 'all' || selected === priority) &&
                      (!query || text.includes(query));
      item.hidden = !visible;
      if (visible) total += 1;
    });
    buttons.forEach(button => {
      const yes = button.getAttribute('data-prod-filter') === selected;
      button.classList.toggle('current', yes);
      button.setAttribute('aria-pressed', String(yes));
    });
    if (counter) counter.textContent = '显示' + total + '/100期';
    if (empty) empty.hidden = total !== 0;
  }
  input.addEventListener('input', update);
  buttons.forEach(button => button.addEventListener('click', () => {
    selected = button.getAttribute('data-prod-filter') || 'all';
    update();
  }));
  update();
})();