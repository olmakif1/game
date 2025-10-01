let toastTimer = null;

const storageKeys = {
  read: 'starwave.read',
  pinned: 'starwave.pinned',
  draft: 'starwave.draft',
};

const qs = (selector, scope = document) => scope.querySelector(selector);
const qsa = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

const parseJSONScript = (id) => {
  const element = document.getElementById(id);
  if (!element) {
    return [];
  }
  try {
    return JSON.parse(element.textContent || '[]');
  } catch (error) {
    console.error('Failed to parse initial payload', error);
    return [];
  }
};

const getCSRFToken = () => {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
};

const createAnnouncementCard = (announcement) => {
  const article = document.createElement('article');
  article.className = 'announcement';
  article.dataset.announcement = '';
  article.dataset.id = announcement.id;
  article.dataset.category = announcement.category;
  article.dataset.pinned = String(Boolean(announcement.is_pinned));

  const badges = [
    `<span class="badge badge--category">${announcement.category_label}</span>`,
  ];
  if (announcement.is_pinned) {
    badges.push('<span class="badge badge--pinned">Pinned</span>');
  }

  const tags = Array.isArray(announcement.tags)
    ? announcement.tags.map((tag) => `<li>#${tag}</li>`).join('')
    : '';

  article.innerHTML = `
    <header class="announcement__header">
      <div>
        <h3 class="announcement__title">${announcement.title}</h3>
        <p class="announcement__meta">
          <span class="announcement__author">${announcement.author}</span>
          <span class="announcement__separator">•</span>
          <time datetime="${announcement.published_at}">${new Date(announcement.published_at).toLocaleString()}</time>
        </p>
      </div>
      <div class="announcement__badges">${badges.join('')}</div>
    </header>
    <p class="announcement__summary">${announcement.summary}</p>
    <div class="announcement__content">${announcement.content.replace(/\n/g, '<br>')}</div>
    ${tags ? `<ul class="announcement__tags">${tags}</ul>` : ''}
    <footer class="announcement__footer">
      <button type="button" data-action="mark-read">Mark as read</button>
      <button type="button" data-action="toggle-pin">Pin locally</button>
    </footer>
  `;

  return article;
};

const updateEmptyState = (container, hasItems) => {
  const empty = qs('.empty', container.closest('[data-announcement-list], .pinned'));
  if (empty) {
    empty.toggleAttribute('hidden', hasItems);
  }
};

const updateMetrics = (metrics, elements) => {
  const totalEl = elements.total;
  const pinnedEl = elements.pinned;
  if (totalEl) {
    totalEl.textContent = String(metrics.total);
  }
  if (pinnedEl) {
    pinnedEl.textContent = String(metrics.pinned);
  }
};

const persistSet = (key, valueSet) => {
  localStorage.setItem(key, JSON.stringify(Array.from(valueSet)));
};

const persistDraft = (form) => {
  const data = new FormData(form);
  const payload = {};
  data.forEach((value, field) => {
    payload[field] = value;
  });
  const pinField = form.elements['is_pinned'];
  if (pinField) {
    payload.is_pinned = pinField.checked;
  }
  localStorage.setItem(storageKeys.draft, JSON.stringify(payload));
};

const restoreDraft = (form) => {
  const draft = localStorage.getItem(storageKeys.draft);
  if (!draft) {
    return false;
  }
  try {
    const payload = JSON.parse(draft);
    Object.entries(payload).forEach(([key, value]) => {
      const field = form.elements[key];
      if (!field) return;
      if (field.type === 'checkbox') {
        field.checked = value === true || value === 'on' || value === 'true';
      } else {
        field.value = value;
      }
    });
    return true;
  } catch (error) {
    console.error('Failed to restore draft', error);
    return false;
  }
};

const clearDraft = () => {
  localStorage.removeItem(storageKeys.draft);
};

const showToast = (toast, message) => {
  if (!toast) return;
  toast.querySelector('.toast__message').textContent = message;
  toast.hidden = false;
  toast.classList.add('is-visible');
  if (toastTimer) {
    clearTimeout(toastTimer);
  }
  toastTimer = setTimeout(() => hideToast(toast), 4000);
};

const hideToast = (toast) => {
  if (!toast) return;
  toast.classList.remove('is-visible');
  toast.hidden = true;
  if (toastTimer) {
    clearTimeout(toastTimer);
    toastTimer = null;
  }
};

const BoardController = () => {
  const board = qs('.board');
  if (!board) {
    return;
  }

  const feedUrl = board.dataset.feedUrl;
  const createUrl = board.dataset.createUrl;
  const list = qs('[data-announcement-list]', board);
  const pinned = qs('[data-pinned-list]', board);
  const searchForm = qs('[data-search-form]', board);
  const filterGroup = qs('[data-filter-group]', board);
  const toggles = qs('[data-toggle]', board) ? qsa('[data-toggle]', board) : [];
  const toast = qs('[data-toast]');
  const metrics = {
    total: qs('[data-metric-value="total"]', board),
    pinned: qs('[data-metric-value="pinned"]', board),
  };
  const form = qs('[data-announcement-form]', board);
  const statusRegion = form ? qs('.form-status', form) : null;
  const draftsModule = qs('[data-drafts]', board);

  const readSet = new Set(JSON.parse(localStorage.getItem(storageKeys.read) || '[]'));
  const localPins = new Set(JSON.parse(localStorage.getItem(storageKeys.pinned) || '[]'));

  const state = {
    announcements: parseJSONScript('initial-announcements'),
    filters: {
      q: '',
      category: '',
      showPinned: true,
      unreadOnly: false,
    },
  };

  const applyFilters = () => {
    return state.announcements.filter((item) => {
      if (state.filters.category && item.category !== state.filters.category) {
        return false;
      }
      if (state.filters.q) {
        const term = state.filters.q.toLowerCase();
        const haystack = [item.title, item.summary, item.content, (item.tags || []).join(' ')].join(' ').toLowerCase();
        if (!haystack.includes(term)) {
          return false;
        }
      }
      if (!state.filters.showPinned && (item.is_pinned || localPins.has(String(item.id)))) {
        return false;
      }
      if (state.filters.unreadOnly && readSet.has(String(item.id))) {
        return false;
      }
      return true;
    });
  };

  const splitAnnouncements = (items) => {
    const pinnedAnnouncements = [];
    const feed = [];
    items.forEach((item) => {
      const isPinned = item.is_pinned || localPins.has(String(item.id));
      if (isPinned) {
        pinnedAnnouncements.push(item);
      }
      if (!item.is_pinned) {
        feed.push(item);
      } else {
        feed.push(item);
      }
    });
    return { pinnedAnnouncements, feed };
  };

  const render = () => {
    if (!list || !pinned) return;
    list.innerHTML = '';
    pinned.querySelectorAll('[data-announcement]').forEach((node) => node.remove());

    const filtered = applyFilters();
    const { pinnedAnnouncements, feed } = splitAnnouncements(filtered);

    feed.forEach((item) => {
      const card = createAnnouncementCard(item);
      if (readSet.has(String(item.id))) {
        card.classList.add('is-read');
      }
      if (localPins.has(String(item.id))) {
        card.classList.add('is-local-pinned');
      }
      list.appendChild(card);
    });

    pinnedAnnouncements.forEach((item) => {
      const card = createAnnouncementCard(item);
      card.classList.add('is-pinned-card');
      if (readSet.has(String(item.id))) {
        card.classList.add('is-read');
      }
      pinned.appendChild(card);
    });

    updateEmptyState(list, list.querySelectorAll('[data-announcement]').length > 0);
    updateEmptyState(pinned, pinned.querySelectorAll('[data-announcement]').length > 0);

    updateMetrics(
      {
        total: state.announcements.length,
        pinned: state.announcements.filter((item) => item.is_pinned || localPins.has(String(item.id))).length,
      },
      metrics,
    );
  };

  const syncAnnouncements = async () => {
    if (!feedUrl) return;
    try {
      const response = await fetch(feedUrl);
      if (!response.ok) throw new Error('Failed to refresh feed');
      const payload = await response.json();
      state.announcements = payload.announcements;
      render();
    } catch (error) {
      console.error(error);
      showToast(toast, 'Unable to refresh announcements.');
    }
  };

  const handleListClick = (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    const article = button.closest('[data-announcement]');
    if (!article) return;
    const id = article.dataset.id;
    if (!id) return;

    if (button.dataset.action === 'mark-read') {
      if (readSet.has(id)) {
        readSet.delete(id);
      } else {
        readSet.add(id);
      }
      persistSet(storageKeys.read, readSet);
      render();
    }

    if (button.dataset.action === 'toggle-pin') {
      if (localPins.has(id)) {
        localPins.delete(id);
        showToast(toast, 'Announcement unpinned locally.');
      } else {
        localPins.add(id);
        showToast(toast, 'Announcement pinned to your console.');
      }
      persistSet(storageKeys.pinned, localPins);
      render();
    }
  };

  const handleFilterClick = (event) => {
    const target = event.target.closest('button[data-category]');
    if (!target) return;
    event.preventDefault();
    state.filters.category = target.dataset.category || '';
    qsa('button[data-category]', filterGroup).forEach((button) => {
      button.classList.toggle('is-active', button === target);
    });
    render();
  };

  const handleSearch = (event) => {
    event.preventDefault();
    const formData = new FormData(searchForm);
    state.filters.q = (formData.get('q') || '').toString();
    render();
  };

  const handleToggleChange = (event) => {
    const checkbox = event.target.closest('input[type="checkbox"][data-toggle]');
    if (!checkbox) return;
    if (checkbox.dataset.toggle === 'pinned') {
      state.filters.showPinned = checkbox.checked;
    }
    if (checkbox.dataset.toggle === 'unread') {
      state.filters.unreadOnly = checkbox.checked;
    }
    render();
  };

  const handleFormSubmit = async (event) => {
    if (!form) return;
    event.preventDefault();
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    const pinField = form.elements['is_pinned'];
    if (pinField) {
      payload.is_pinned = pinField.checked;
    }
    if (statusRegion) {
      statusRegion.textContent = 'Publishing…';
    }
    try {
      const response = await fetch(createUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error('Unable to publish announcement');
      }
      state.announcements.unshift(data.announcement);
      clearDraft();
      form.reset();
      render();
      if (statusRegion) {
        statusRegion.textContent = 'Announcement published!';
      }
      showToast(toast, 'Transmission deployed successfully.');
    } catch (error) {
      console.error(error);
      if (statusRegion) {
        statusRegion.textContent = 'Publishing failed. Check your input and try again.';
      }
      showToast(toast, 'Publishing failed.');
    }
  };

  const attachDraftHandlers = () => {
    if (!form) return;
    form.addEventListener('input', () => persistDraft(form));
    if (!draftsModule) return;
    const restoreButton = qs('[data-action="restore-draft"]', draftsModule);
    const clearButton = qs('[data-action="clear-draft"]', draftsModule);
    if (restoreButton) {
      restoreButton.addEventListener('click', () => {
        if (restoreDraft(form)) {
          showToast(toast, 'Draft restored.');
        } else {
          showToast(toast, 'No draft available.');
        }
      });
    }
    if (clearButton) {
      clearButton.addEventListener('click', () => {
        clearDraft();
        showToast(toast, 'Draft cleared.');
      });
    }
    restoreDraft(form);
  };

  if (list) {
    list.addEventListener('click', handleListClick);
  }
  if (pinned) {
    pinned.addEventListener('click', handleListClick);
  }
  if (filterGroup) {
    filterGroup.addEventListener('click', handleFilterClick);
  }
  if (searchForm) {
    searchForm.addEventListener('submit', handleSearch);
  }
  if (toggles.length) {
    toggles.forEach((toggle) => toggle.addEventListener('change', handleToggleChange));
  }
  if (form) {
    form.addEventListener('submit', handleFormSubmit);
  }
  if (toast) {
    const closeBtn = toast.querySelector('.toast__close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => hideToast(toast));
    }
  }

  attachDraftHandlers();
  render();
  syncAnnouncements();
  setInterval(syncAnnouncements, 60000);
};

document.addEventListener('DOMContentLoaded', BoardController);
