/*
 * Renders a HighlightsSummary into the receipt table.
 * Expects either a global `monthly_highlight_summary` object or a
 * JSON payload inside the `#monthly-highlight-summary` script tag.
 */
(function () {
  const tableBody = document.querySelector('#receipt-rows');
  if (!tableBody) {
    console.warn('render_summary: missing #receipt-rows tbody');
    return;
  }

  const summary = resolveSummary();
  if (!summary) {
    console.warn('render_summary: no summary data found');
    return;
  }

  renderSummary(summary, tableBody);

  function resolveSummary() {
    if (window.monthly_highlight_summary) {
      return window.monthly_highlight_summary;
    }

    const dataTag = document.querySelector('#monthly-highlight-summary');
    if (!dataTag) {
      return null;
    }

    try {
      return JSON.parse(dataTag.textContent);
    } catch (error) {
      console.error('render_summary: failed to parse summary JSON', error);
      return null;
    }
  }

  function renderSummary(summary, tbody) {
    tbody.innerHTML = '';

    let rowIndex = 1;
    for (const [key, value] of Object.entries(summary)) {
      const row = document.createElement('tr');

      const indexCell = document.createElement('td');
      indexCell.className = 'begin';
      indexCell.textContent = rowIndex;

      const keyCell = document.createElement('td');
      keyCell.className = 'name';
      keyCell.textContent = key;

      const valueCell = document.createElement('td');
      valueCell.className = 'length';
      valueCell.textContent = formatValue(key, value);

      row.append(indexCell, keyCell, valueCell);
      tbody.appendChild(row);

      rowIndex += 1;
    }
  }

  function formatValue(key, value) {
    if (value === null || value === undefined) {
      return '—';
    }

    if (typeof value === 'object') {
      if (isDayRecord(value)) {
        return formatDayRecord(value);
      }

      return JSON.stringify(value);
    }

    if (typeof value === 'number' && key.toLowerCase().includes('score')) {
      return value.toFixed(2);
    }

    return String(value);
  }

  function isDayRecord(candidate) {
    return (
      typeof candidate.dt !== 'undefined' &&
      typeof candidate.day_score !== 'undefined'
    );
  }

  function formatDayRecord(day) {
    const date = formatDate(day.dt);
    const score = typeof day.day_score === 'number'
      ? day.day_score.toFixed(2)
      : day.day_score;
    const highlight = day.highlight ? ` - ${day.highlight}` : '';
    return `${date} (${score})${highlight}`;
  }

  function formatDate(value) {
    if (value instanceof Date) {
      return value.toISOString().split('T')[0];
    }

    if (typeof value === 'string') {
      // Attempt to normalise ISO-like strings
      return value.split('T')[0];
    }

    return String(value);
  }
})();
