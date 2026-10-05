/* Saving without the GitHub editor: one call to the Actions API starts the
   workflow that writes the patch into db.json.

   Each device keeps its own fine-grained token in this browser's storage. The
   token has the Actions permission on this one repository and nothing else, so
   it can start workflows and can neither read nor change the code. Tokens are
   created and revoked on GitHub one by one, which is what lets a phone and a
   tablet hold separate ones and lose them separately. A revoked or expired token
   answers 401, and the page falls back to the editor route.

   It lives in its own file so Node can test it without a browser. The page hands
   it fetch, storage and the repository, and it never touches the DOM. */
(function (root) {
  'use strict';

  const KEY = 'kids-activities-token-v1';
  const API = 'https://api.github.com';
  const VERSION = '2022-11-28';
  const TIMEOUT_MS = 15 * 1000;
  // Only fine-grained tokens. A classic token cannot be limited to one repository.
  const TOKEN_FORMAT = /^github_pat_[A-Za-z0-9_]{20,}$/;
  // The workflow refuses more than this, so refuse it here before sending.
  const MAX_CHARS = 20000;
  const TARGETS = {
    decisions: { workflow: 'apply-decisions.yml', input: 'patch' },
    hide: { workflow: 'hide-events.yml', input: 'ids' },
  };

  const MESSAGES = {
    format: 'To ni žeton GitHub. Začne se z github_pat_.',
    storage: 'Brskalnik žetona ne shranjuje.',
    offline: 'GitHub ni dosegljiv.',
    rejected: 'GitHub žetona ne sprejme. Je pretekel ali preklican?',
    forbidden: 'Žeton nima pravice Actions: Read and write za ta repozitorij.',
    missing: 'Žeton ne vidi repozitorija ali delovnega toka.',
    refused: 'GitHub je zavrnil zahtevo. Delovni tok morda še nima sprožilca.',
    tooBig: 'Preveč odločitev za en klic.',
    unknown: 'Repozitorij ni znan.',
    failed: 'GitHub je vrnil napako.',
  };

  function createClient(env) {
    const repo = env.repo || {};
    const known = Boolean(repo.owner && repo.repo);
    const branch = repo.branch || 'main';
    let rejected = false;

    function read() {
      try { return (env.storage && env.storage.getItem(KEY)) || ''; } catch (error) { return ''; }
    }

    function write(value) {
      try {
        if (!env.storage) return false;
        if (value) env.storage.setItem(KEY, value);
        else env.storage.removeItem(KEY);
        return true;
      } catch (error) {
        return false;
      }
    }

    function address(path) {
      return `${API}/repos/${encodeURIComponent(repo.owner)}/${encodeURIComponent(repo.repo)}${path}`;
    }

    function headers(token, json) {
      const base = {
        Accept: 'application/vnd.github+json',
        Authorization: `Bearer ${token}`,
        'X-GitHub-Api-Version': VERSION,
      };
      return json ? Object.assign({ 'Content-Type': 'application/json' }, base) : base;
    }

    // A network failure and a timeout both end as null, which callers read as offline.
    async function call(url, options) {
      const controller = typeof AbortController === 'function' ? new AbortController() : null;
      const timer = controller ? setTimeout(() => controller.abort(), TIMEOUT_MS) : null;
      try {
        return await env.fetch(url, Object.assign({}, options, controller ? { signal: controller.signal } : {}));
      } catch (error) {
        return null;
      } finally {
        if (timer) clearTimeout(timer);
      }
    }

    function failure(status) {
      if (status === 401) return { ok: false, reason: 'rejected', status, message: MESSAGES.rejected };
      if (status === 403) return { ok: false, reason: 'forbidden', status, message: MESSAGES.forbidden };
      if (status === 404) return { ok: false, reason: 'missing', status, message: MESSAGES.missing };
      if (status === 422) return { ok: false, reason: 'refused', status, message: MESSAGES.refused };
      return { ok: false, reason: 'failed', status, message: `${MESSAGES.failed} (${status}).` };
    }

    return {
      // Whether the repository is known, which is what a token is used against.
      available: () => known,
      // Whether a token is stored. Not whether GitHub still accepts it.
      enabled: () => known && Boolean(read()),
      // True once GitHub has turned the stored token down in this session.
      rejected: () => rejected,

      // Store a token after one harmless read shows GitHub knows it. A token that
      // is merely missing a permission passes here and fails at the first save,
      // where the page falls back to the editor.
      remember: async (value) => {
        const token = String(value || '').trim();
        if (!known) return { ok: false, reason: 'unknown', message: MESSAGES.unknown };
        if (!TOKEN_FORMAT.test(token)) return { ok: false, reason: 'format', message: MESSAGES.format };
        const url = address(`/actions/workflows/${TARGETS.decisions.workflow}`);
        const response = await call(url, { method: 'GET', headers: headers(token, false) });
        if (!response) return { ok: false, reason: 'offline', message: MESSAGES.offline };
        if (!response.ok) return failure(response.status);
        if (!write(token)) return { ok: false, reason: 'storage', message: MESSAGES.storage };
        rejected = false;
        return { ok: true };
      },

      // Remove this device's token. It stays valid on GitHub until revoked there.
      forget: () => {
        rejected = false;
        return write('');
      },

      // Start the workflow for one kind of patch. Never throws.
      send: async (kind, text) => {
        const target = TARGETS[kind];
        const token = read();
        if (!target || !known) return { ok: false, reason: 'unknown', message: MESSAGES.unknown };
        if (!token) return { ok: false, reason: 'disabled', message: '' };
        if (String(text).length > MAX_CHARS) return { ok: false, reason: 'tooBig', message: MESSAGES.tooBig };
        const response = await call(address(`/actions/workflows/${target.workflow}/dispatches`), {
          method: 'POST',
          headers: headers(token, true),
          body: JSON.stringify({ ref: branch, inputs: { [target.input]: text } }),
        });
        if (!response) return { ok: false, reason: 'offline', message: MESSAGES.offline };
        if (response.ok) return { ok: true };
        const result = failure(response.status);
        if (result.reason === 'rejected') rejected = true;
        return result;
      },

      // A GitHub page that opens the token form with the permission filled in.
      // The repository cannot be preselected, so the person picks it there.
      templateUrl: () => {
        if (!known) return '';
        const query = new URLSearchParams({
          name: 'kids-activities swipe app',
          description: `Starts the save workflows of ${repo.owner}/${repo.repo}. Nothing else.`,
          target_name: repo.owner,
          expires_in: '365',
          actions: 'write',
        });
        return `https://github.com/settings/personal-access-tokens/new?${query}`;
      },
    };
  }

  const api = { KEY, MAX_CHARS, TARGETS, TOKEN_FORMAT, createClient };
  root.Dispatch = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
