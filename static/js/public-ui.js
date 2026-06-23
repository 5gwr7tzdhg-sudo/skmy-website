(() => {
  const language = document.documentElement.lang;
  const uiText = {
    ru: {
      closeTemplate: 'Закрыть шаблон',
      copiedTemplate: 'Скопирован финский шаблон для отправки в организацию.',
      copiedValue: '✓ Шаблон скопирован',
      copyError: 'Не удалось скопировать',
    },
    fi: {
      closeTemplate: 'Sulje viestipohja',
      copiedTemplate: '✓ Viestipohja kopioitu',
      copiedValue: '✓ Numero kopioitu',
      copyError: 'Kopiointi epäonnistui',
    },
    en: {
      closeTemplate: 'Close template',
      copiedTemplate: '✓ Template copied',
      copiedValue: '✓ Number copied',
      copyError: 'Could not copy',
    },
  }[language] || {};
  const elements = document.querySelectorAll('.reveal');
  if (!elements.length || !('IntersectionObserver' in window)) {
    elements.forEach((element) => element.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -24px' });

  // The guide topics form a short, intentional sequence rather than appearing
  // as one block. Direction remains in CSS, so the effect stays responsive.
  document.querySelectorAll('.home-guide-card.reveal').forEach((card, index) => {
    card.style.transitionDelay = `${index * 90}ms`;
  });

  elements.forEach((element) => observer.observe(element));

  const copyText = async (text) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const input = document.createElement('textarea');
    input.value = text;
    input.style.position = 'fixed';
    input.style.opacity = '0';
    document.body.append(input);
    input.select();
    document.execCommand('copy');
    input.remove();
  };

  const closeTemplateCard = (card) => {
    window.clearTimeout(Number(card.dataset.closeTimer));
    card.classList.remove('is-open');
    card.style.height = '';
    card.querySelector('[data-template-toggle]')?.setAttribute('aria-expanded', 'false');
  };

  document.querySelectorAll('.interpreter-template-card__back').forEach((back) => {
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.dataset.templateClose = '';
    closeButton.textContent = uiText.closeTemplate;
    back.append(closeButton);
  });

  document.querySelectorAll('[data-template-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const card = button.closest('.interpreter-template-card');
      window.clearTimeout(Number(card.dataset.closeTimer));
      const isOpen = card.classList.toggle('is-open');
      const back = card.querySelector('.interpreter-template-card__back');
      card.style.height = isOpen ? `${back.scrollHeight}px` : '';
      button.setAttribute('aria-expanded', String(isOpen));
      if (isOpen) {
        card.dataset.closeTimer = String(window.setTimeout(() => closeTemplateCard(card), 15000));
      }
    });
  });

  document.querySelectorAll('[data-template-close]').forEach((button) => {
    button.addEventListener('click', () => closeTemplateCard(button.closest('.interpreter-template-card')));
  });

  document.querySelectorAll('[data-copy-template], [data-copy-value]').forEach((button) => {
    button.addEventListener('click', async () => {
      const template = button.dataset.copyTemplate && document.getElementById(button.dataset.copyTemplate);
      const text = template ? template.content.textContent.trim() : button.dataset.copyValue;
      if (!text) return;
      const originalText = button.textContent;
      try {
        await copyText(text);
        button.textContent = button.dataset.copyTemplate
          ? uiText.copiedTemplate
          : uiText.copiedValue;
        window.setTimeout(() => {
          button.textContent = originalText;
          const card = button.closest('.interpreter-template-card');
          if (!card) return;
          closeTemplateCard(card);
        }, 2300);
      } catch (_) {
        button.textContent = uiText.copyError;
        window.setTimeout(() => { button.textContent = originalText; }, 1800);
      }
    });
  });
})();
