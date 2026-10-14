"""Run against scripts/serve.sh. Requires Python Playwright and Chromium."""
from pathlib import Path
from urllib.parse import urlsplit
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'var'
OUTPUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1440,'height':1000})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:8080/', wait_until='networkidle')
    assert page.locator('.service-card').count() == 6
    assert page.locator('.training-features > div').count() == 4
    assert page.locator('#send-button').is_disabled()
    assert 'not connected to email yet' in page.locator('#form-status').inner_text()
    assert page.locator('h1').count() == 1
    for href in page.locator('a[href^="#"]').evaluate_all('(els) => els.map(el => el.getAttribute("href"))'):
        assert page.locator(href).count() == 1, href
    for src in page.locator('img').evaluate_all('(els) => els.map(el => el.getAttribute("src"))'):
        assert page.request.get('http://127.0.0.1:8080/' + src).status == 200
    for width in [320,375,390,520,768,800,801,1024,1440]:
        page.set_viewport_size({'width':width,'height':900})
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), width
        for card in page.locator('.service-card').all():
            assert card.is_visible()
    page.set_viewport_size({'width':1440,'height':1000})
    assert page.locator('.service-card').nth(0).bounding_box()['y'] == page.locator('.service-card').nth(2).bounding_box()['y']
    page.screenshot(path=str(OUTPUT / 'desktop.png'), full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUTPUT / 'mobile.png'), full_page=True)
    toggle = page.get_by_role('button', name='Menu')
    toggle.click(); assert toggle.get_attribute('aria-expanded') == 'true'
    page.keyboard.press('Escape'); assert toggle.get_attribute('aria-expanded') == 'false'
    assert toggle.evaluate('(el) => document.activeElement === el')
    toggle.click()
    page.locator('#navigation').get_by_role('link', name='Services', exact=True).click()
    assert toggle.get_attribute('aria-expanded') == 'false'
    page.locator('.service-card').first.click()
    assert 'Custom Software' in page.locator('#message').input_value()
    page.emulate_media(reduced_motion='reduce')
    assert page.evaluate('getComputedStyle(document.documentElement).scrollBehavior') == 'auto'
    # Explicitly mocked SMTP-ready state exercises client validation/error handling.
    # No email is sent and this does not claim SMTP integration was validated.
    def mock_form(route):
        if route.request.method == 'GET':
            route.fulfill(status=200,content_type='application/json',body=json.dumps({'ready':True,'csrf':'mock-browser-token'}))
        else:
            route.fulfill(status=503,content_type='application/json',body=json.dumps({'message':'Your message could not be sent. Please try again later.'}))
    page.route('**/contact.php', mock_form)
    page.reload(wait_until='networkidle')
    page.locator('#name').fill('Test Visitor')
    page.locator('#email').fill('invalid-email')
    page.locator('#message').fill('Test inquiry, no real mail will be sent.')
    assert not page.locator('#email').evaluate('(el) => el.checkValidity()')
    page.locator('#email').fill('visitor@example.com')
    page.locator('#send-button').click()
    page.wait_for_function('document.querySelector("#form-status").textContent.includes("could not be sent")')
    assert page.locator('#message').input_value().startswith('Test inquiry')
    assert page.locator('#send-button').is_enabled()
    assert not errors, errors
    browser.close()
print('Browser checks passed: 9 viewport widths, anchors/assets, menu keyboard controls, form validation/error state, reduced motion, no JS errors. SMTP responses in client interaction tests were mocked.')
