/**
 * sanitizeInsightHtml
 * -------------------
 * Lightweight allowlist-based HTML sanitizer for LLM-generated insight text.
 *
 * Allowed tags: <b>, <strong>, <span class="highlight (green|red|purple|orange|blue)">
 * All other tags and attributes are stripped.
 *
 * This avoids a full DOMPurify dependency while still preventing XSS from
 * prompt-injected or malformed LLM output.
 */

const ALLOWED_SPAN_CLASSES = /^highlight\s+(green|red|purple|orange|blue)$/;

/**
 * Parse and sanitize an HTML string.
 * @param {string} html  Raw HTML from LLM
 * @returns {string}     Safe HTML with only allowed tags/attrs
 */
export function sanitizeInsightHtml(html) {
  if (!html || typeof html !== 'string') return '';

  // Use the browser's own HTML parser via a detached element
  const template = document.createElement('template');
  template.innerHTML = html;
  const root = template.content;

  sanitizeNode(root);

  // Serialize back to string
  const div = document.createElement('div');
  div.appendChild(root.cloneNode(true));
  return div.innerHTML;
}

function sanitizeNode(node) {
  const children = Array.from(node.childNodes);
  for (const child of children) {
    if (child.nodeType === Node.TEXT_NODE) {
      // Text nodes are safe as-is
      continue;
    }
    if (child.nodeType === Node.ELEMENT_NODE) {
      const tag = child.tagName.toLowerCase();

      if (tag === 'b' || tag === 'strong') {
        // Keep tag, strip all attributes, recurse
        while (child.attributes.length > 0) {
          child.removeAttribute(child.attributes[0].name);
        }
        sanitizeNode(child);
        continue;
      }

      if (tag === 'span') {
        const cls = (child.getAttribute('class') || '').trim();
        if (ALLOWED_SPAN_CLASSES.test(cls)) {
          // Keep span with allowed class only
          while (child.attributes.length > 0) {
            child.removeAttribute(child.attributes[0].name);
          }
          child.setAttribute('class', cls);
          sanitizeNode(child);
          continue;
        }
      }

      // Any other element: replace with its text content
      const text = document.createTextNode(child.textContent || '');
      node.replaceChild(text, child);
    } else {
      // Remove comments, processing instructions, etc.
      node.removeChild(child);
    }
  }
}
