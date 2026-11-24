/* ==========================================================================
   Chegoland Dairy Farm — Frontend behaviour
   ========================================================================== */
(function () {
  'use strict';

  var apiBase = '/api/v1/cart';
  var toastEl = null;

  /* ------------------------------------------------------------------ */
  /* Toast notifications                                                */
  /* ------------------------------------------------------------------ */
  function showToast(message, type) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className =
        'fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg shadow-medium text-sm font-semibold' +
        (type === 'error' ? ' bg-red-100 text-red-800 border border-red-200' : ' bg-green-100 text-green-800 border border-green-200');
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = message;
    toastEl.className = toastEl.className.replace(/opacity-0|translate-y-\d+/g, '');
    toastEl.style.opacity = '1';
    toastEl.style.transform = 'translateY(0)';
    clearTimeout(toastEl._timer);
    toastEl._timer = setTimeout(function () {
      toastEl.style.opacity = '0';
      toastEl.style.transform = 'translateY(20px)';
    }, 3500);
  }

  /* ------------------------------------------------------------------ */
  /* Cart badge                                                         */
  /* ------------------------------------------------------------------ */
  function updateCartBadge(count) {
    var badge = document.querySelector('.cart-badge');
    var cartLinks = document.querySelectorAll('.cart-link, #mobile-menu .mobile-list a[href="/cart"]');
    if (!badge && count <= 0) {
      return;
    }
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'cart-badge';
      cartLinks.forEach(function (link) {
        link.style.position = 'relative';
        link.appendChild(badge.cloneNode(false));
      });
      badge = document.querySelector('.cart-badge');
    }
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  }

  function refreshCartBadge() {
    fetch(apiBase, { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        updateCartBadge(data && typeof data.count === 'number' ? data.count : 0);
      })
      .catch(function () { /* ignore; badge stays as-is */ });
  }
  /* ------------------------------------------------------------------ */
  /* Add to cart                                                        */
  /* ------------------------------------------------------------------ */
  window.cgh = window.cgh || {};
  window.cgh.addToCart = function (productId, name, price, unit, quantity) {
    if (quantity === undefined) {
      quantity = 1;
    }
    fetch(apiBase + '/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ product_id: productId, quantity: parseInt(quantity, 10) || 1 })
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.success) {
          showToast((name || 'Item') + ' added to cart');
          updateCartBadge(data.count);
          var event = new CustomEvent('cg:cart-changed', { detail: { count: data.count } });
          document.dispatchEvent(event);
        } else {
          showToast(data.detail || 'Could not add to cart', 'error');
        }
      })
      .catch(function () {
        showToast('Could not add to cart', 'error');
      });
  };

  /* ------------------------------------------------------------------ */
  /* Update cart item quantity (cart page)                              */
  /* ------------------------------------------------------------------ */
  window.cgh.updateCartQty = function (productId, quantity) {
    quantity = parseInt(quantity, 10);
    if (quantity < 1) {
      window.cgh.removeFromCart(productId);
      return;
    }
    var btn = document.querySelector('[data-update-qty="' + productId + '"]');
    var orig = btn ? btn.textContent : '';
    if (btn) {
      btn.textContent = '…';
      btn.disabled = true;
    }
    fetch(apiBase + '/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ product_id: productId, quantity: quantity })
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.success) {
          updateCartBadge(data.count);
          document.dispatchEvent(new CustomEvent('cg:cart-changed', { detail: { count: data.count } }));
          location.reload();
        } else {
          showToast(data.detail || 'Update failed', 'error');
          if (btn) {
            btn.textContent = orig;
            btn.disabled = false;
          }
        }
      })
      .catch(function () {
        showToast('Update failed', 'error');
        if (btn) {
          btn.textContent = orig;
          btn.disabled = false;
        }
      });
  };

  /* ------------------------------------------------------------------ */
  /* Remove from cart                                                   */
  /* ------------------------------------------------------------------ */
  window.cgh.removeFromCart = function (productId) {
    var btn = document.querySelector('[data-remove="' + productId + '"]');
    var orig = btn ? btn.textContent : '';
    if (btn) {
      btn.textContent = '…';
      btn.disabled = true;
    }
    fetch(apiBase + '/remove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ product_id: productId })
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.success) {
          updateCartBadge(data.count);
          document.dispatchEvent(new CustomEvent('cg:cart-changed', { detail: { count: data.count } }));
          location.reload();
        } else {
          showToast(data.detail || 'Remove failed', 'error');
          if (btn) {
            btn.textContent = orig;
            btn.disabled = false;
          }
        }
      })
      .catch(function () {
        showToast('Remove failed', 'error');
        if (btn) {
          btn.textContent = orig;
          btn.disabled = false;
        }
      });
  };
  /* ------------------------------------------------------------------ */
  /* Mobile menu                                                        */
  /* ------------------------------------------------------------------ */
  window.toggleMobileMenu = function () {
    var menu = document.getElementById('mobile-menu');
    var btn = document.getElementById('mobile-menu-btn');
    if (!menu) {
      return;
    }
    var open = menu.classList.toggle('open');
    if (btn) {
      btn.setAttribute('aria-expanded', open);
      var icon = btn.querySelector('i');
      if (icon) {
        icon.className = open ? 'fas fa-times text-xl' : 'fas fa-bars text-xl';
      }
    }
  };

  /* Close mobile menu when a link is clicked */
  document.addEventListener('click', function (e) {
    var menu = document.getElementById('mobile-menu');
    var btn = document.getElementById('mobile-menu-btn');
    if (!menu || !menu.classList.contains('open')) {
      return;
    }
    if (e.target.closest('#mobile-menu a')) {
      menu.classList.remove('open');
      if (btn) {
        btn.setAttribute('aria-expanded', 'false');
        var icon = btn.querySelector('i');
        if (icon) {
          icon.className = 'fas fa-bars text-xl';
        }
      }
    }
  });
  /* ------------------------------------------------------------------ */
  /* Form validation helpers                                            */
  /* ------------------------------------------------------------------ */
  function setFieldError(input, message) {
    input.classList.add('error');
    var wrapper = input.parentElement;
    var existing = wrapper.querySelector('.field-error');
    if (existing) {
      existing.remove();
    }
    if (message) {
      var err = document.createElement('p');
      err.className = 'field-error';
      err.textContent = message;
      wrapper.appendChild(err);
    }
  }

  function clearFieldError(input) {
    input.classList.remove('error');
    var wrapper = input.parentElement;
    var existing = wrapper.querySelector('.field-error');
    if (existing) {
      existing.remove();
    }
  }

  function validateEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  function validatePhone(value) {
    // Accepts Kenyan formats: 07XXXXXXXX, +2547XXXXXXXX, 2547XXXXXXXX
    return /^(\+254|254|0)?[17]\d{8}$/.test(value.replace(/\s/g, ''));
  }

  /* ------------------------------------------------------------------ */
  /* Checkout form                                                      */
  /* ------------------------------------------------------------------ */
  function initCheckoutForm() {
    var form = document.getElementById('checkoutForm');
    if (!form) {
      return;
    }
    var fields = {
      customer_name: function (v) { return v.trim() !== '' || 'Full name is required'; },
      customer_phone: function (v) { return validatePhone(v) || 'Enter a valid phone number (e.g. 0712345678)'; },
      customer_email: function (v) { return v.trim() === '' || validateEmail(v) || 'Enter a valid email address'; },
      delivery_address: function (v) { return v.trim() !== '' || 'Delivery address is required'; },
      delivery_date: function (v) {
        if (v.trim() === '') {
          return 'Please choose a delivery date';
        }
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        var chosen = new Date(v);
        return chosen >= today || 'Delivery date cannot be in the past';
      },
      delivery_time_slot: function (v) { return v !== '' || 'Please choose a delivery time slot'; },
      payment_method: function (v) { return v !== '' || 'Please choose a payment method'; }
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var hasError = false;
      var formData = new FormData(form);
      var data = {};
      formData.forEach(function (value, key) {
        data[key] = value;
        var input = form.elements[key];
        if (input) {
          clearFieldError(input);
          var msg = fields[key] ? fields[key](value) : null;
          if (msg) {
            setFieldError(input, msg);
            hasError = true;
          }
        }
      });
      if (hasError) {
        showToast('Please fix the highlighted fields', 'error');
        var firstErr = form.querySelector('.error');
        if (firstErr) {
          firstErr.focus();
        }
        return;
      }

      var submitBtn = form.querySelector('button[type="submit"]');
      var origBtnText = submitBtn ? submitBtn.textContent : '';
      if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
      }

      fetch('/api/v1/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json(); })
        .then(function (result) {
          if (submitBtn) {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            submitBtn.textContent = origBtnText;
          }
          if (result.success) {
            window.location.href = result.redirect || '/order-confirmation/' + (result.order_id || '');
          } else {
            showToast(result.detail || 'Checkout failed', 'error');
          }
        })
        .catch(function () {
          if (submitBtn) {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            submitBtn.textContent = origBtnText;
          }
          showToast('Checkout failed. Please try again.', 'error');
        });
    });

    // Real-time clearing of errors on input
    Object.keys(fields).forEach(function (key) {
      var input = form.elements[key];
      if (input) {
        input.addEventListener('input', function () {
          clearFieldError(input);
        });
        input.addEventListener('change', function () {
          clearFieldError(input);
        });
      }
    });

    // Min delivery date = today
    var dateInput = form.elements.delivery_date;
    if (dateInput) {
      var today = new Date();
      var iso = today.toISOString().slice(0, 10);
      dateInput.setAttribute('min', iso);
    }
  }
  /* ------------------------------------------------------------------ */
  /* Contact form success highlight                                     */
  /* ------------------------------------------------------------------ */
  function initContactForm() {
    var form = document.querySelector('form[action="/contact"]') || document.getElementById('contactForm');
    if (!form) {
      return;
    }
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
      }
    });
  }

  /* ------------------------------------------------------------------ */
  /* Quantity selectors on product cards                                */
  /* ------------------------------------------------------------------ */
  function initQtySelectors() {
    document.querySelectorAll('.qty-selector').forEach(function (qty) {
      var input = qty.querySelector('input');
      qty.querySelectorAll('button').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var step = btn.dataset.step === '-' ? -1 : 1;
          var val = parseInt(input.value, 10) || 1;
          var max = parseInt(input.getAttribute('max') || '99', 10);
          var next = Math.min(Math.max(val + step, 1), max);
          input.value = next;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
      });
      input.addEventListener('change', function () {
        var val = parseInt(input.value, 10) || 1;
        var max = parseInt(input.getAttribute('max') || '99', 10);
        if (val < 1) {
          val = 1;
        }
        if (val > max) {
          val = max;
        }
        input.value = val;
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Lazy loading fallback for browsers without native support          */
  /* ------------------------------------------------------------------ */
  function initLazyLoad() {
    if ('loading' in HTMLImageElement.prototype) {
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          observer.unobserve(img);
        }
      });
    });
    document.querySelectorAll('img[data-src]').forEach(function (img) {
      observer.observe(img);
    });
  }

  /* ------------------------------------------------------------------ */
  /* Init                                                               */
  /* ------------------------------------------------------------------ */
  document.addEventListener('DOMContentLoaded', function () {
    refreshCartBadge();
    initCheckoutForm();
    initContactForm();
    initQtySelectors();
    initLazyLoad();
  });
})();