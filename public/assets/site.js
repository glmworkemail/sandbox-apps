'use strict';
const menu = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
function closeMenu() { menu.setAttribute('aria-expanded', 'false'); navigation.classList.remove('open'); }
menu.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); navigation.classList.toggle('open', open); });
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => { if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { closeMenu(); menu.focus(); } });
window.matchMedia('(min-width: 801px)').addEventListener('change', event => { if (event.matches) closeMenu(); });
document.querySelector('#year').textContent = new Date().getFullYear();
const form = document.querySelector('#contact-form');
const button = document.querySelector('#send-button');
const status = document.querySelector('#form-status');
let available = false;
function showStatus(message, type = '') { status.textContent = message; status.className = 'form-status ' + type; }
async function prepareForm() {
  button.disabled = true;
  try {
    const response = await fetch('contact.php', { credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'application/json' } });
    const data = await response.json();
    if (!response.ok || !data.csrf) throw new Error('Unavailable');
    document.querySelector('#csrf').value = data.csrf;
    available = data.ready === true;
    button.disabled = !available;
    showStatus(available ? 'Ready for your inquiry.' : 'The contact form is not connected to email yet. No messages can be sent at this time.');
  } catch { available = false; showStatus('The contact form is currently unavailable. Please try again later.', 'error'); }
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (!available || !form.reportValidity()) return;
  button.disabled = true; showStatus('Sending your inquiry…');
  try {
    const response = await fetch('contact.php', { method: 'POST', body: new FormData(form), credentials: 'same-origin', headers: { Accept: 'application/json' } });
    const data = await response.json();
    if (!response.ok) { showStatus(data.message || 'Your message could not be sent. Please try again later.', 'error'); if (response.status === 403) { await prepareForm(); showStatus('Your form session expired. Please send your message again.', 'error'); } }
    else { form.reset(); showStatus(data.message, 'success'); }
  } catch { showStatus('Your message could not be confirmed. Please try again later.', 'error'); }
  finally { button.disabled = !available; }
});
document.querySelectorAll('[data-interest]').forEach(link => link.addEventListener('click', () => { const field = document.querySelector('#message'); if (!field.value.trim()) field.value = "I'm interested in " + link.dataset.interest + '.\n\n'; }));
prepareForm();
