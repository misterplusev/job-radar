"""Read a single employer-published TeamWork Online detail page after an HTTP success."""
import json
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup


def job_id(url):
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.hostname != 'www.teamworkonline.com':
        return None
    match = re.search(r'-(\d{6,})/?$', parts.path)
    return match.group(1) if match else None


def words(value):
    return ' '.join(re.findall(r'\w+', str(value or '').casefold()))


def structured_jobs(soup):
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            value = json.loads(script.get_text())
        except (TypeError, ValueError):
            continue
        pending = list(value) if isinstance(value, list) else [value]
        for _ in range(200):
            if not pending:
                break
            item = pending.pop()
            if not isinstance(item, dict):
                continue
            if isinstance(item.get('@graph'), list):
                pending.extend(item['@graph'])
            kind = item.get('@type')
            if kind == 'JobPosting' or isinstance(kind, list) and 'JobPosting' in kind:
                yield item


def detail(page, requested_url, response_url, title, clean):
    expected = job_id(requested_url)
    if not expected or job_id(response_url) != expected or not words(title):
        raise ValueError('TeamWork detail URL or expected title mismatch')
    soup = BeautifulSoup(page, 'html.parser')
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'):
        if job_id(urljoin(response_url, canonical['href'])) != expected:
            raise ValueError('TeamWork canonical job mismatch')
    for item in structured_jobs(soup):
        if words(item.get('title')) != words(title):
            continue
        if item.get('url') and job_id(item['url']) != expected:
            continue
        description = clean(item.get('description'))
        if len(description) >= 80:
            return {**item, 'description': description}
    if not any(words(node.get_text(' ', strip=True)) == words(title) for node in soup.find_all('h1')):
        raise ValueError('TeamWork detail heading mismatch')
    # Use only regions explicitly identified as the job description by the page.
    candidates = list(soup.select('[itemprop~="description"], [data-testid="job-description"], '
                                  '#job-description, .employment-opportunity__description, '
                                  '.employment-opportunity-show__description, '
                                  '.employment-opportunity__body .trix-content'))
    for heading in soup.find_all(['h2', 'h3']):
        if words(heading.get_text(' ', strip=True)) != 'job description':
            continue
        section = heading.find_parent('section')
        if section and section.get('aria-labelledby') and section['aria-labelledby'] == heading.get('id'):
            candidates.append(section)
    found = set()
    for element in candidates:
        if element.name == 'meta' or element.find_parent(['aside', 'nav', 'footer', 'header']):
            continue
        if element.find_parent(attrs={'itemtype': re.compile(r'(?:Organization|Person)/?$')}):
            continue
        fragment = BeautifulSoup(str(element), 'html.parser')
        for other in fragment.select('script, style, nav, aside, form, footer, header, button, h2, h3, [aria-hidden="true"]'):
            other.decompose()
        body = clean(fragment.get_text(' ', strip=True))
        if len(body) >= 80:
            found.add(body)
    if len(found) != 1:
        raise ValueError('TeamWork job description region missing or ambiguous')
    return {'title': title, 'description': found.pop()}
