/* Hand one event to an AI assistant, ready to be researched.

   There is no standard for this, so each assistant gets the route that works best.
   On Android, Chrome turns an `intent:` link into a VIEW of the assistant's own web
   address, pinned to its installed app, which opens the app on a new chat. It has
   to be a VIEW: Chrome adds the BROWSABLE category to every intent a page launches,
   and the share-target screens of these apps do not declare it, so a SEND intent
   never resolves and Chrome drops to the web page, which an installed web app shows
   in its in-app browser. Elsewhere, and when the app is not installed, the link
   falls back to the assistant's web page. Only the event's own stored fields go
   into the prompt. The assistant does the web search, so nothing here claims to be
   fresher than the database. */
(function (root) {
  'use strict';

  const TARGETS = {
    chatgpt: {
      label: 'ChatGPT',
      pkg: 'com.openai.chatgpt',
      web: (text) => `https://chatgpt.com/?hints=search&q=${encodeURIComponent(text)}`,
    },
    claude: {
      label: 'Claude',
      pkg: 'com.anthropic.claude',
      web: (text) => `https://claude.ai/new?q=${encodeURIComponent(text)}`,
    },
    gemini: {
      label: 'Gemini',
      pkg: 'com.google.android.apps.bard',
      // Gemini has no documented way to prefill a prompt, so the web page opens
      // empty and the copied text is pasted in.
      web: () => 'https://gemini.google.com/app',
    },
  };

  const INTRO = [
    'Tell me more about this kids\' event in Slovenia.',
    'Search the web for the latest information and confirm the date, time, venue, price and age range.',
    'Tell me anything I should know before going, such as booking, tickets, cancellations or schedule changes.',
    'The details below come from a scraped listing and may be wrong or incomplete.',
  ].join(' ');

  // `place` is the venue as the app shows it, with the town when it adds something.
  function prompt(card, place) {
    const when = card.date
      ? [card.day, card.date, card.time && card.time !== '?' ? `at ${card.time}` : ''].filter(Boolean).join(' ')
      : '';
    const price = card.is_free
      ? ['free', card.price && card.price.toLowerCase() !== 'brezplačno' ? card.price : ''].filter(Boolean).join(', ')
      : card.price;
    const lines = [
      ['Event', card.title],
      ['When', when],
      ['Where', place && place !== '?' ? place : ''],
      ['Age', card.age && card.age !== '?' ? `${card.age} years` : ''],
      ['Price', price],
      ['Category', (card.category || '').replace(/_/g, ' ')],
      ['Notes', (card.notes || []).join(', ')],
      ['Source', card.url],
    ];
    const body = lines.filter(([, value]) => value && value !== '?').map(([name, value]) => `${name}: ${value}`);
    return `${INTRO}\n\n${body.join('\n')}`;
  }

  function webUrl(name, text) {
    return TARGETS[name].web(text);
  }

  // Chrome on Android reads this as: open this address in this package, and if
  // that cannot be done, go to the fallback address instead. The address is the
  // one the web route uses, so an app that claims it as an app link gets the same
  // text. An app that opens without the text still has it on the clipboard.
  function intentUrl(name, text) {
    const target = TARGETS[name];
    const web = new URL(target.web(text));
    return `intent://${web.host}${web.pathname}${web.search}#Intent;scheme=${web.protocol.slice(0, -1)};`
      + `package=${target.pkg};`
      + `S.browser_fallback_url=${encodeURIComponent(web.href)};end`;
  }

  // The system share sheet lists every installed app that takes text, so it
  // reaches an assistant whatever its app does with links.
  function canShare(nav) {
    return Boolean(nav) && typeof nav.share === 'function';
  }

  function isAndroid(userAgent) {
    return /\bAndroid\b/i.test(userAgent || '');
  }

  const api = { TARGETS, prompt, webUrl, intentUrl, canShare, isAndroid };
  root.AskAi = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
