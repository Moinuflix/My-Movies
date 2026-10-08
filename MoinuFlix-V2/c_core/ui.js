/**
 * ==========================================================================
 * MoinuFlix V2 — Master UI Shared Controller
 * File: c_core/ui.js
 * Scope: Toast management, modal lifecycle, loading states, navigation helpers.
 * Note: Pure shared UI logic ONLY. Zero API, parser, or storage dependencies.
 * ==========================================================================
 */

(function (global) {
  'use strict';

  var MoinuUI = {
    version: '2.0.0',

    /**
     * Display a temporary toast notification.
     * @param {string} message - Notification text
     * @param {'info'|'success'|'warning'|'danger'} [type='info'] - Status category
     * @param {number} [duration=3500] - Duration in ms before auto-dismiss
     */
    toast: function (message, type, duration) {
      type = type || 'info';
      duration = duration || 3500;

      var container = document.getElementById('moinu-toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'moinu-toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
      }

      var toastEl = document.createElement('div');
      toastEl.className = 'toast toast--' + type;
      toastEl.setAttribute('role', 'alert');
      toastEl.textContent = message;

      container.appendChild(toastEl);

      setTimeout(function () {
        toastEl.style.opacity = '0';
        toastEl.style.transform = 'translateY(8px)';
        toastEl.style.transition = 'opacity 200ms ease, transform 200ms ease';
        setTimeout(function () {
          if (toastEl.parentNode) {
            toastEl.parentNode.removeChild(toastEl);
          }
        }, 200);
      }, duration);
    },

    /**
     * Show or hide loading indicator on an element or button.
     * @param {HTMLElement|string} target - Element reference or ID
     * @param {boolean} isLoading - Active state
     * @param {string} [loadingText] - Optional temporary replacement text
     */
    setLoading: function (target, isLoading, loadingText) {
      var el = typeof target === 'string' ? document.getElementById(target) : target;
      if (!el) return;

      if (isLoading) {
        el.dataset.originalText = el.textContent;
        el.dataset.prevDisabled = el.disabled ? 'true' : 'false';
        el.disabled = true;
        if (loadingText) el.textContent = loadingText;
        el.classList.add('is-loading');
      } else {
        if (el.dataset.originalText) {
          el.textContent = el.dataset.originalText;
          delete el.dataset.originalText;
        }
        if (el.dataset.prevDisabled !== 'true') {
          el.disabled = false;
        }
        delete el.dataset.prevDisabled;
        el.classList.remove('is-loading');
      }
    },

    /**
     * Open a target modal by ID.
     * @param {string} modalId - Target modal DOM ID
     */
    openModal: function (modalId) {
      var modal = document.getElementById(modalId);
      if (!modal) return;
      modal.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    },

    /**
     * Close a target modal by ID.
     * @param {string} modalId - Target modal DOM ID
     */
    closeModal: function (modalId) {
      var modal = document.getElementById(modalId);
      if (!modal) return;
      modal.classList.remove('is-open');
      document.body.style.overflow = '';
    },

    /**
     * Initialize modal closing triggers across all backdrop containers.
     */
    initModals: function () {
      var backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(function (backdrop) {
        backdrop.addEventListener('click', function (e) {
          if (e.target === backdrop) {
            backdrop.classList.remove('is-open');
            document.body.style.overflow = '';
          }
        });

        var closeBtns = backdrop.querySelectorAll('[data-modal-close]');
        closeBtns.forEach(function (btn) {
          btn.addEventListener('click', function () {
            backdrop.classList.remove('is-open');
            document.body.style.overflow = '';
          });
        });
      });
    },

    /**
     * Synchronize and set active navigation links across desktop & mobile.
     * @param {string} activeKey - Identifier corresponding to data-nav attribute
     */
    setActiveNav: function (activeKey) {
      if (!activeKey) return;
      var navItems = document.querySelectorAll('[data-nav]');
      navItems.forEach(function (item) {
        if (item.getAttribute('data-nav') === activeKey) {
          item.classList.add('is-active');
        } else {
          item.classList.remove('is-active');
        }
      });
    }
  };

  // Auto-init generic listeners when DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      MoinuUI.initModals();
    });
  } else {
    MoinuUI.initModals();
  }

  // Export to global scope
  global.MoinuUI = MoinuUI;

})(typeof window !== 'undefined' ? window : this);
