/**
 * DOMPurify sanitization wrapper — client-side layer of the
 * defense-in-depth artifact security model (ADR-003).
 */
import DOMPurify from 'dompurify';

/**
 * Sanitize HTML string, stripping dangerous tags and attributes.
 *
 * @param {string} dirty - Raw HTML from the server
 * @returns {string} Sanitized HTML safe for iframe srcdoc injection
 */
export function sanitizeHtml(dirty) {
  return DOMPurify.sanitize(dirty, {
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'],
    ALLOW_DATA_ATTR: false,
  });
}
