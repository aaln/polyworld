'use strict';

const byId = id => document.getElementById(id);
const element = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const icon = name => {
  const image = element('img');
  image.src = name.startsWith('portrait:')
    ? `../assets/characters/modular_chars/character.preset_${name.slice(9)}.profile.png`
    : `../assets/icons/${name}.png`;
  image.alt = '';
  image.width = 24;
  image.height = 24;
  return image;
};
const metric = (key, label, image, unit = 'per game', format = 'number', detail = '') =>
  ({key, label, image, unit, format, detail});
const share = (key, label, image, detail = '') => metric(key, label, image, 'share · %', 'percent', detail);
const rate = (key, label, image) => metric(key, label, image, 'orders / minute alive', 'number', 'Accepted commands, divided by minutes alive in each game, then averaged across games.');
const heroes = [
  ['Vanguard Knight', 1], ['Ranger', 13], ['Arcanist', 16], ['Druid Warden', 17],
  ['Demon Hunter', 2], ['Death Knight', 3], ['Crossbowman', 11], ['Lich', 12],
  ['Warlock', 6], ['Berserker', 14],
];
const reasonInfo = {
  ActionAbilityLocked: ['Ability locked', 'mana'],
  ActionAlreadyEquipped: ['Already equipped', 'champion'],
  ActionChanneling: ['Channeling', 'fort'],
  ActionCooldown: ['On cooldown', 'day'],
  ActionDrafting: ['Still drafting', 'champion'],
  ActionInsufficientGold: ['Not enough gold', 'gold'],
  ActionInsufficientMana: ['Not enough mana', 'mana'],
  ActionInventoryFull: ['Inventory full', 'chalice'],
  ActionNoCharges: ['No charges', 'chalice'],
  ActionNoRoute: ['No route', 'move'],
  ActionNotAlive: ['Hero not alive', 'kills'],
  ActionOutOfRange: ['Out of range', 'range'],
  ActionOutsideKeep: ['Outside own keep', 'fort'],
  ActionTargetUnavailable: ['Target unavailable', 'attack'],
};

function groupsFor(data) {
  return [
    {id: 'score', title: 'League', image: 'victory', rows: [
      metric('score', 'Score', 'victory', 'recent average / game', 'number', 'Average recorded evaluation score across this snapshot’s hero-games. Current per-game formula: max(0, floor(total XP − 200 × game minutes)). Earlier games retain their recorded score precision.'),
      metric('won', 'Win / loss', 'victory', 'win % · loss % below', 'record', 'Wins and losses as percentages of all observed hero-games. Draws are shown separately as D; wins, losses and draws together total 100% before rounding. The bar shows win rate.'),
      metric('glory', 'Average glory', 'chalice', 'recent average / game', 'number', 'Average of each game’s recorded score on a win, or zero on a loss or draw. Includes losses and draws in the average; this is not the average score among wins only.'),
    ]},
    {id: 'drafting', title: 'Drafting phase', image: 'champion', rows: heroes.map(([name, portrait], index) =>
      share(`draft_${index}`, name, `portrait:${portrait}`, `Share of hero-games in which this player ended the draft as ${name}.`))},
    {id: 'direct', title: 'Direct control', image: 'attack', rows: [
      rate('attackmoves_pm', 'Attack-move orders', 'attack'),
      rate('walks_pm', 'Walk orders', 'move'),
      rate('attacks_pm', 'Attack-target orders', 'range'),
      rate('casts_pm', 'Ability casts', 'mana'),
      rate('itemuses_pm', 'Item-use orders', 'chalice'),
      share('target_hero', 'Attacks targeting heroes', 'champion', 'Share of accepted attack-target orders. Games without an accepted attack-target order are excluded.'),
      share('target_creep', 'Attacks targeting creeps', 'minion', 'Share of accepted attack-target orders. Games without an accepted attack-target order are excluded.'),
      share('target_building', 'Attacks targeting buildings', 'tower', 'Share of accepted attack-target orders. Games without an accepted attack-target order are excluded.'),
      share('target_god', 'Attacks targeting the god', 'fort', 'Share of accepted attack-target orders. Games without an accepted attack-target order are excluded.'),
      share('time_enemy_half', 'Time in the enemy half', 'move', 'Share of alive ticks closer to the enemy god than to the own god.'),
      share('time_near_enemy_tower', 'Time near enemy towers', 'tower', 'Share of alive ticks within 12 tiles of an original enemy tower location, including destroyed towers.'),
      share('time_near_enemy_god', 'Time near the enemy god', 'fort', 'Share of alive ticks within 20 tiles of the enemy god.'),
      share('time_near_own_god', 'Time near own god', 'fort', 'Share of alive ticks within 15 tiles of the own god.'),
      metric('tiles_pm', 'Distance traveled', 'move', 'tiles / minute alive', 'number', 'Full-precision displacement between consecutive alive ticks. Death, respawn and completed portal jumps are excluded.'),
      share('hp_mean', 'Average health while alive', 'health', 'Mean current HP divided by maximum HP over alive ticks.'),
      share('time_below50', 'Time below 50% health', 'health', 'Share of alive ticks below half of maximum HP.'),
      share('time_below25', 'Time below 25% health', 'health', 'Share of alive ticks below one quarter of maximum HP.'),
      metric('lowhp_walks', 'Walk orders below 30% health', 'move', 'issued orders / game', 'number', 'Issued walk commands while alive and below 30% HP. This is a retreat proxy, not proof of retreat, and may include rejected commands.'),
      metric('orders_pm', 'All orders issued', 'stats', 'orders / minute alive', 'number', 'All issued commands, including rejected commands and commands issued while dead, divided by minutes alive.'),
      share('dup_share', 'Identical consecutive orders', 'stats', 'Share of issued commands identical to the previous command from that hero, including kind, slot, arguments and offset. Repetition is not necessarily harmful.'),
      metric('dup_pm', 'Identical order repeats', 'stats', 'repeats / minute alive'),
      metric('cpu_pct', 'Instruction allowance used', 'stats', 'CPU · %', 'rawPercent', 'Final replay CPU telemetry as a percentage of the instruction allowance. Missing telemetry is excluded, not counted as zero.'),
    ]},
    {id: 'rejected', title: 'Rejected orders', image: 'damage', rows: [
      share('rejected_share', 'Orders rejected by the engine', 'damage', 'Share of all issued commands that the game engine refused. Policies issue orders; the engine accepts or rejects them.'),
      metric('rejected_pm', 'Rejected order rate', 'damage', 'orders / minute alive'),
      ...data.rejections.map(key => {
        const reason = key.slice(4);
        const fallback = reason.replace(/^Action/, '').replace(/([a-z])([A-Z])/g, '$1 $2');
        const [label, image] = reasonInfo[reason] || [fallback, 'damage'];
        return metric(key, label, image, 'rejections / game', 'number', `${reason}: mean rejected commands per hero-game. A missing reason in a verified game is counted as zero.`);
      }),
    ]},
    {id: 'indirect', title: 'Indirect statistics', image: 'gold', rows: [
      metric('gold_earned', 'Gold earned', 'gold'), metric('gold_spent', 'Gold spent', 'gold'),
      metric('gold_end', 'Gold left unspent', 'gold', 'at game end'),
      metric('buy_gear', 'Equipment purchased', 'champion'),
      metric('buy_heal', 'Healing items purchased', 'health'),
      metric('buy_mana', 'Mana items purchased', 'mana'),
      metric('buy_portal', 'Portal scrolls purchased', 'fort'),
      metric('buy_poison', 'Poison purchased', 'damage'),
      metric('items_consumed', 'Consumables used', 'chalice'),
      metric('buybacks', 'Buybacks', 'champion'),
      metric('buyback_gold', 'Gold spent on buybacks', 'gold'),
    ]},
    {id: 'downstream', title: 'Downstream statistics', image: 'victory', rows: [
      metric('xp', 'Lifetime experience', 'experience'),
      metric('xp_lasthit', 'XP from creep last hits', 'minion'),
      metric('xp_shared', 'XP from nearby creep deaths', 'experience'),
      metric('xp_herokill', 'XP from hero kills', 'kills'),
      metric('xp_building', 'XP from buildings', 'tower'),
      metric('xp_god', 'XP from the god', 'fort'),
      metric('kills', 'Hero kills', 'kills'), metric('assists', 'Assists', 'attack'),
      metric('deaths', 'Deaths', 'damage'), metric('building_kills', 'Buildings destroyed', 'tower'),
      metric('tower_kills', 'Towers destroyed', 'tower'),
      metric('barracks_kills', 'Barracks destroyed', 'fort'),
      metric('level', 'Final level', 'champion', 'at game end'),
      share('alive_share', 'Time alive', 'health', 'Share of recorded game ticks in which the hero was alive, including the drafting phase.'),
      metric('minutes', 'Game duration', 'day', 'minutes / game'),
    ]},
  ];
}

const numberFormat = new Intl.NumberFormat('en-US', {maximumFractionDigits: 1, minimumFractionDigits: 1});
function formatted(value, format, player) {
  if (value === null || value === undefined) return '—';
  if (format === 'record') {
    const record = player.record;
    return `${formatted(record.wins / player.games, 'percent')} W / ${formatted(record.losses / player.games, 'percent')} L` +
      (record.draws ? ` · ${formatted(record.draws / player.games, 'percent')} D` : '') +
      ` (${record.wins} wins, ${record.losses} losses, ${record.draws} draws)`;
  }
  if (format === 'percent') return numberFormat.format(value * 100) + '%';
  if (format === 'rawPercent') return numberFormat.format(value) + '%';
  return numberFormat.format(value);
}

function byScore(left, right) {
  const leftScore = left.values.score;
  const rightScore = right.values.score;
  if (leftScore == null && rightScore != null) return 1;
  if (rightScore == null && leftScore != null) return -1;
  return (rightScore ?? 0) - (leftScore ?? 0) ||
    left.name.localeCompare(right.name) || left.id.localeCompare(right.id);
}

function snapshotFor(player, versionId) {
  const version = player.policyVersions.find(version => version.id === versionId);
  if (!version) return player;
  return {...player, ...version, id: player.id, name: player.name,
    versionId: version.id, versionLabel: `${version.name}:v${version.version}`};
}

function paintCell(cell, row, player, max) {
  const value = player.values[row.key];
  cell.classList.toggle('missing', value == null);
  cell.textContent = formatted(value, row.format, player);
  if (row.format === 'record' && value != null) {
    cell.replaceChildren(element('span', 'record-count', formatted(value, 'percent')));
    cell.append(element('span', 'record-losses', `${formatted(player.values.lost, 'percent')} L`));
    if (player.record.draws) cell.append(element('span', 'record-draws', `${formatted(player.values.drawn, 'percent')} D`));
  }
  const scope = player.versionLabel || 'All versions';
  cell.title = `${player.name} · ${scope} · ${row.label}: ${formatted(value, row.format, player)} · ${player.samples[row.key] || 0} observed hero-games`;
  if (value != null && max > 0) {
    const bar = element('span', 'bar'); bar.style.setProperty('--fill', Math.max(0, value / max));
    bar.setAttribute('aria-hidden', 'true'); cell.append(bar);
  }
}

async function render() {
  const response = await fetch('data.json', {cache: 'no-cache'});
  if (!response.ok) throw new Error('Snapshot could not be loaded.');
  const data = await response.json();
  data.players.sort(byScore);
  const groups = groupsFor(data);
  const table = byId('matrix');
  const scroller = byId('matrix-scroll');
  const topScroll = byId('top-scroll');
  const picker = byId('player-select');
  const versionPicker = byId('version-select');
  const chosenVersions = new Map();
  let displayedPlayers = data.players;
  const metricRows = [];
  const selectable = new Map(data.players.map(player => [player.id, []]));
  const buttons = new Map();
  const groupBodies = [];
  const navButtons = [];
  let selected = '';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const behavior = reducedMotion ? 'auto' : 'smooth';

  byId('player-count').textContent = data.players.length;
  byId('replay-count').textContent = data.episodes.toLocaleString();
  byId('stat-count').textContent = groups.reduce((count, group) => count + group.rows.length, 0);
  const start = new Date(data.windowStart), end = new Date(data.windowEnd);
  const date = value => value.toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC'});
  const time = value => value.toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit', timeZone: 'UTC'});
  byId('window-date').textContent = date(start) === date(end) ? date(end) : `${date(start)} – ${date(end)}`;
  byId('window-time').textContent = `${time(start)}–${time(end)} UTC · ${data.hours} hours`;
  byId('coverage').textContent = `${data.episodes.toLocaleString()} hash-verified replays · ${data.heroGames.toLocaleString()} hero-games · rounds ${data.rounds[0]}–${data.rounds.at(-1)}. ` +
    `Episode creation window: ${start.toISOString()} to ${end.toISOString()} (end excluded). ` +
    `Engines: ${Object.entries(data.engines).map(([version, count]) => `v${version}: ${count} games`).join(', ')}. ` +
    `${data.unavailableEpisodes} unavailable or incomplete episodes. Snapshot generated ${new Date(data.generatedAt).toUTCString()}. This page updates when a new snapshot is published.`;

  function register(node, player) {
    node.dataset.player = player.id;
    selectable.get(player.id).push(node);
  }
  function selectPlayer(id, scroll = true) {
    for (const node of selectable.get(selected) || []) node.classList.remove('selected');
    buttons.get(selected)?.setAttribute('aria-pressed', 'false');
    selected = selectable.has(id) ? id : '';
    for (const node of selectable.get(selected) || []) node.classList.add('selected');
    buttons.get(selected)?.setAttribute('aria-pressed', 'true');
    picker.value = selected;
    byId('clear-selection').hidden = !selected;
    const player = data.players.find(player => player.id === selected);
    const status = byId('selection');
    status.replaceChildren();
    versionPicker.replaceChildren();
    versionPicker.disabled = !player || !player.policyVersions.length;
    if (player) {
      const shown = snapshotFor(player, chosenVersions.get(player.id));
      versionPicker.add(new Option(`All versions · ${player.games} games`, ''));
      player.policyVersions.forEach((version, index) => {
        versionPicker.add(new Option(`${version.name}:v${version.version} · ${version.games} games${index === 0 ? ' · latest played' : ''}`, version.id));
      });
      versionPicker.value = chosenVersions.get(player.id) || '';
      status.append(element('strong', '', player.name), ` · ${shown.games} hero-games`);
      const scope = shown.versionLabel
        ? `${shown.versionLabel} · Last played ${time(new Date(shown.lastGameAt))} UTC in this snapshot`
        : `All ${player.policyVersions.length} policy versions in this snapshot`;
      status.append(element('small', '', player.games ? scope : 'No games in this window.'));
      if (scroll) {
        const heading = selectable.get(selected)[0];
        const labelWidth = parseFloat(getComputedStyle(scroller).getPropertyValue('--label-width'));
        const delta = heading.getBoundingClientRect().left - scroller.getBoundingClientRect().left;
        scroller.scrollTo({left: scroller.scrollLeft + delta - labelWidth - (scroller.clientWidth - labelWidth - heading.offsetWidth) / 2, behavior});
      }
    } else {
      versionPicker.add(new Option('Select a player first', ''));
      status.textContent = 'Select a name to highlight its column.' +
        (chosenVersions.size ? ` ${chosenVersions.size} columns use a specific version.` : '');
    }
    try {
      if (selected) localStorage.setItem('gota-selected-player', selected);
      else localStorage.removeItem('gota-selected-player');
    } catch { /* Selection still works when browser storage is unavailable. */ }
  }

  function updateVersions() {
    displayedPlayers = data.players.map(player => snapshotFor(player, chosenVersions.get(player.id))).sort(byScore);
    for (const player of displayedPlayers) {
      const heading = selectable.get(player.id)[0];
      const count = heading.querySelector('.sample-count');
      heading.classList.toggle('has-version', Boolean(player.versionId));
      count.replaceChildren();
      if (player.versionId) count.append(element('span', 'column-version', `v${player.version}`));
      count.append(element('span', '', `${player.games} games`));
      buttons.get(player.id).title = `${player.name} · ${player.versionLabel || 'All versions'} · ${player.games} hero-games`;
    }
    for (const {row, cells} of metricRows) {
      const max = Math.max(0, ...displayedPlayers.map(player => player.values[row.key] ?? 0));
      for (const player of displayedPlayers) paintCell(cells.get(player.id), row, player, max);
    }
    // Move existing cells so headers, highlights and row associations stay intact.
    for (const row of table.rows) {
      const cells = new Map([...row.children].filter(cell => cell.dataset.player).map(cell => [cell.dataset.player, cell]));
      const end = row.lastElementChild;
      for (const player of displayedPlayers) row.insertBefore(cells.get(player.id), end);
    }
    const options = new Map([...picker.options].map(option => [option.value, option]));
    for (const player of displayedPlayers) picker.append(options.get(player.id));
    selectPlayer(selected);
  }

  const header = element('tr');
  const corner = element('th', 'stat-label');
  corner.scope = 'col';
  corner.append(element('span', 'corner-title', 'Player statistics'), element('span', 'corner-note', 'Choose a name above a column. Your highlight follows you through every statistic.'));
  header.append(corner);
  data.players.forEach((player, index) => {
    const th = element('th', 'player');
    th.id = `player-${index}`;
    th.scope = 'col';
    register(th, player);
    const button = element('button', 'player-name', player.name);
    button.type = 'button';
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-label', `Highlight ${player.name}`);
    button.title = `${player.name} · ${player.games} hero-games${player.baseline ? ' · Built-in opponent' : ''}`;
    button.addEventListener('click', () => selectPlayer(selected === player.id ? '' : player.id, false));
    buttons.set(player.id, button);
    th.append(button, element('span', 'sample-count', `${player.games} games`));
    header.append(th);
    picker.add(new Option(player.name + (player.baseline ? ' (baseline)' : ''), player.id));
  });
  const padding = () => { const cell = element('td', 'end-space'); cell.setAttribute('aria-hidden', 'true'); return cell; };
  header.append(padding());
  byId('matrix-head').append(header);

  groups.forEach((group, groupIndex) => {
    const body = element('tbody');
    body.id = group.id;
    groupBodies.push(body);
    const groupRow = element('tr', group.id === 'score' ? 'group-row score-group' : 'group-row');
    const heading = element('th', 'stat-label');
    heading.scope = 'row';
    const title = element('span', 'group-title');
    title.append(icon(group.image), group.title, element('span', 'group-number', String(groupIndex + 1).padStart(2, '0')));
    heading.append(title);
    groupRow.append(heading);
    for (const player of data.players) {
      const cell = element('td'); register(cell, player); groupRow.append(cell);
    }
    groupRow.append(padding());
    body.append(groupRow);
    for (const row of group.rows) {
      const tr = element('tr', row.key === 'score' ? 'metric-row score-row' : 'metric-row');
      const th = element('th', 'stat-label');
      th.scope = 'row'; th.id = `metric-${row.key}`;
      const label = element('button', 'metric-label');
      label.type = 'button';
      const description = row.detail || `Mean ${row.label.toLowerCase()} across this player's hero-games. Unit: ${row.unit}.`;
      label.title = description;
      const words = element('span', '', row.label);
      words.append(element('span', 'unit', row.unit));
      label.append(icon(row.image), words);
      label.addEventListener('click', () => {
        const detail = byId('metric-detail');
        detail.hidden = false;
        detail.replaceChildren(element('strong', '', row.label), description);
      });
      th.append(label); tr.append(th);
      const max = Math.max(0, ...data.players.map(player => player.values[row.key] ?? 0));
      const cells = new Map();
      metricRows.push({row, cells});
      data.players.forEach((player, index) => {
        const cell = element('td');
        paintCell(cell, row, player, max);
        register(cell, player);
        cells.set(player.id, cell);
        cell.setAttribute('headers', `metric-${row.key} player-${index}`);
        tr.append(cell);
      });
      tr.append(padding()); body.append(tr);
    }
    table.append(body);
    const tab = element('button');
    tab.type = 'button';
    tab.append(icon(group.image), group.title);
    tab.addEventListener('click', () => {
      const offset = body.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop - byId('matrix-head').offsetHeight;
      scroller.scrollTo({top: offset, behavior});
    });
    navButtons.push(tab); byId('sections').append(tab);
  });
  picker.addEventListener('change', () => selectPlayer(picker.value));
  versionPicker.addEventListener('change', () => {
    if (!selected) return;
    if (versionPicker.value) chosenVersions.set(selected, versionPicker.value);
    else chosenVersions.delete(selected);
    updateVersions();
  });
  byId('clear-selection').addEventListener('click', () => selectPlayer(''));
  byId('scroll-left').addEventListener('click', () => scroller.scrollBy({left: -400, behavior}));
  byId('scroll-right').addEventListener('click', () => scroller.scrollBy({left: 400, behavior}));
  let frame = false;
  let syncedLeft = 0;
  const sync = () => {
    syncedLeft = scroller.scrollLeft;
    topScroll.scrollLeft = syncedLeft;
    byId('scroll-left').disabled = scroller.scrollLeft < 1;
    byId('scroll-right').disabled = scroller.scrollLeft + scroller.clientWidth >= scroller.scrollWidth - 1;
    const edge = scroller.getBoundingClientRect().top + byId('matrix-head').offsetHeight + 20;
    let current = 0;
    groupBodies.forEach((body, index) => { if (body.getBoundingClientRect().top <= edge) current = index; });
    navButtons.forEach((button, index) => button.setAttribute('aria-current', index === current ? 'true' : 'false'));
    frame = false;
  };
  scroller.addEventListener('scroll', () => { if (!frame) { frame = true; requestAnimationFrame(sync); } }, {passive: true});
  topScroll.addEventListener('scroll', () => {
    // Ignore scroll events from our own synchronization during an animation.
    if (Math.abs(topScroll.scrollLeft - syncedLeft) > 1) {
      syncedLeft = topScroll.scrollLeft;
      scroller.scrollLeft = syncedLeft;
    }
  }, {passive: true});
  const resize = () => { topScroll.firstElementChild.style.width = `${scroller.scrollWidth}px`; sync(); };
  new ResizeObserver(resize).observe(scroller);
  byId('loading').hidden = true;
  table.hidden = false;
  resize();
  try { selectPlayer(localStorage.getItem('gota-selected-player') || ''); } catch { /* Storage is optional. */ }
}

render().catch(error => {
  byId('loading').textContent = 'The player snapshot could not be loaded. Please reload the page to try again.';
  byId('loading').setAttribute('role', 'alert');
  byId('window-date').textContent = 'Snapshot unavailable';
  console.error(error);
});
