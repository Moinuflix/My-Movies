/**
 * MOINUFLIX V5 - MASTER UI SYSTEM JAVASCRIPT
 * File: c_core/ui.js
 * Strictly Presentation & Common UI Helpers.
 */

(function (window) {
  'use strict';

  const MoinuUI = {};

  /**
   * HTML escape utility
   */
  MoinuUI.escapeHtml = function (str) {
    if (typeof str !== 'string') return str;
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  /**
   * Laser Toast Notification Engine
   */
  MoinuUI.showLaserToast = function (message, type = 'info', duration = 3500) {
    let container = document.getElementById('laser-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'laser-toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Icon generation based on status
    let iconSvg = '';
    if (type === 'success') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
    } else if (type === 'error') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
    } else if (type === 'warning') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';
    } else {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
    }

    toast.innerHTML = `
      <span class="toast-icon">${iconSvg}</span>
      <span class="toast-msg">${MoinuUI.escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => toast.remove(), 250);
    }, duration);
  };

  /**
   * Modal Controls
   */
  MoinuUI.showModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  };

  MoinuUI.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  };

  /**
   * State Management (Button / Container Spinners)
   */
  MoinuUI.setLoading = function (element, isLoading, text = '') {
    if (!element) return;
    if (isLoading) {
      element.dataset.prevHtml = element.innerHTML;
      element.disabled = true;
      element.innerHTML = `<span class="loading-spinner"></span> ${text ? MoinuUI.escapeHtml(text) : ''}`;
    } else {
      element.disabled = false;
      if (element.dataset.prevHtml) {
        element.innerHTML = element.dataset.prevHtml;
        delete element.dataset.prevHtml;
      }
    }
  };

  /**
   * Universal Navigation Sync (Desktop Sidebar + Mobile Bottom Bar)
   */
  MoinuUI.setActiveNavigation = function (pageKey) {
    // Desktop sidebar links
    document.querySelectorAll('.desktop-sidebar .nav-btn').forEach(btn => {
      if (btn.dataset.nav === pageKey) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Mobile bottom navigation links
    document.querySelectorAll('.mobile-bottom-bar .m-nav-item').forEach(item => {
      if (item.dataset.nav === pageKey) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  };

  window.MoinuUI = MoinuUI;
})(window);
