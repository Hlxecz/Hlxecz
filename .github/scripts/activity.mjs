import { mkdir, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

export function renderActivity(calendar, dark = false) {
  const weeks = calendar.weeks.map(week => ({
    date: week.contributionDays[0].date,
    count: week.contributionDays.reduce((sum, day) => sum + day.contributionCount, 0),
  }));
  if (!weeks.length || weeks.some(week => !/^\d{4}-\d{2}-\d{2}$/.test(week.date) || !Number.isFinite(week.count) || week.count < 0)) {
    throw new Error('Invalid contribution calendar');
  }
  const colors = dark
    ? { bg: '#111319', border: '#343842', title: '#f4f3ef', text: '#a8adb9', line: '#91aa9b', grid: '#282e31' }
    : { bg: '#fafaf8', border: '#ddddda', title: '#36393e', text: '#6b7077', line: '#8da296', grid: '#e6e8e3' };
  const left = 40, right = 852, top = 48, bottom = 172;
  const max = Math.max(1, ...weeks.map(week => week.count));
  const x = index => left + (right - left) * index / Math.max(1, weeks.length - 1);
  const y = count => bottom - (bottom - top) * count / max;
  const points = weeks.map((week, index) => `${x(index).toFixed(1)},${y(week.count).toFixed(1)}`).join(' ');
  const grid = [0, .5, 1].map(ratio => {
    const level = y(max * ratio);
    return `<line x1="${left}" y1="${level}" x2="${right}" y2="${level}" stroke="${colors.grid}"/><text x="30" y="${level + 4}" text-anchor="end" fill="${colors.text}" font-size="10">${Math.round(max * ratio)}</text>`;
  }).join('');
  const labels = weeks.flatMap((week, index) => {
    if (index && week.date.slice(0, 7) === weeks[index - 1].date.slice(0, 7)) return [];
    // Label alternate months so the wide graph stays readable on small screens.
    if (Number(week.date.slice(5, 7)) % 2) return [];
    return [`<text x="${x(index)}" y="194" text-anchor="middle" fill="${colors.text}" font-size="10">${week.date.slice(2, 7).replace('-', '/')}</text>`];
  }).join('');
  const total = weeks.reduce((sum, week) => sum + week.count, 0);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="880" height="210" viewBox="0 0 880 210" role="img" aria-labelledby="title desc"><title id="title">GitHub contributions</title><desc id="desc">${total} contributions across ${weeks.length} weeks</desc><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop stop-color="${colors.line}" stop-opacity=".38"/><stop offset="1" stop-color="${colors.line}" stop-opacity=".02"/></linearGradient></defs><rect x=".5" y=".5" width="879" height="209" rx="12" fill="${colors.bg}" stroke="${colors.border}"/><g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif"><text x="24" y="28" fill="${colors.title}" font-size="14" font-weight="600">Contributions</text><text x="852" y="28" text-anchor="end" fill="${colors.text}" font-size="11">${total} in the last year</text>${grid}<polygon points="${left},${bottom} ${points} ${x(weeks.length - 1)},${bottom}" fill="url(#area)"/><polyline points="${points}" fill="none" stroke="${colors.line}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>${labels}</g></svg>`;
}

async function main() {
  const token = process.env.GITHUB_TOKEN;
  const login = process.env.PROFILE_LOGIN || process.env.GITHUB_REPOSITORY_OWNER;
  if (!token || !login) throw new Error('GITHUB_TOKEN and profile login are required');
  const response = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }', variables: { login } }),
    signal: AbortSignal.timeout(30000),
  });
  const data = await response.json();
  if (!response.ok || data.errors?.length) throw new Error('GitHub contribution data request failed');
  const calendar = data.data?.user?.contributionsCollection?.contributionCalendar;
  if (!calendar?.weeks) throw new Error('Contribution calendar is missing');
  await mkdir('dist', { recursive: true });
  await writeFile('dist/github-activity-light.svg', renderActivity(calendar));
  await writeFile('dist/github-activity-dark.svg', renderActivity(calendar, true));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
