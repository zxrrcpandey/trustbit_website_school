/**
 * Trustbit Website School - Frontend JavaScript
 * Handles search, cart, and UI interactions
 */

const TrustbitWebshop = {
    // Configuration
    config: {
        debounceDelay: 500,
        searchMinChars: 2,
        notificationDuration: 3000,
    },

    // State
    state: {
        searchQuery: '',
        searchTimer: null,
        isSearching: false,
        cart: [],
    },

    // ================================
    // INITIALIZATION
    // ================================

    init() {
        this.initSearch();
        this.initCart();
        this.initNotifications();
        this.bindEvents();
        console.log('Trustbit Website School initialized');
    },

    bindEvents() {
        // Bundle add to cart
        $(document).on('click', '.kgs-add-bundle-btn', (e) => {
            const itemCode = $(e.currentTarget).data('item-code');
            this.addBundleToCart(itemCode);
        });

        // Single item add to cart
        $(document).on('click', '.kgs-add-item-btn', (e) => {
            const itemCode = $(e.currentTarget).data('item-code');
            this.addItemToCart(itemCode);
        });

        // Bundle preview
        $(document).on('click', '.kgs-preview-bundle-btn', (e) => {
            const itemCode = $(e.currentTarget).data('item-code');
            this.showBundlePreview(itemCode);
        });

        // Close modal
        $(document).on('click', '.kgs-modal-overlay, .kgs-modal-close', () => {
            this.closeModal();
        });

        // Category click
        $(document).on('click', '.kgs-category-card', (e) => {
            const category = $(e.currentTarget).data('category');
            window.location.href = `/shop/category/${encodeURIComponent(category)}`;
        });

        // Product card click (on image or title) - add to cart
        $(document).on('click', '.kgs-product-card .kgs-product-image, .kgs-product-card h4', (e) => {
            e.stopPropagation();
            const $card = $(e.currentTarget).closest('.kgs-product-card');
            const $btn = $card.find('.kgs-add-item-btn');
            const itemCode = $btn.data('item-code');
            if (itemCode && !$btn.prop('disabled')) {
                this.addItemToCart(itemCode);
            }
        });
    },

    // ================================
    // SEARCH FUNCTIONALITY
    // ================================

    initSearch() {
        const $searchInput = $('#kgs-search-input');
        const $searchDropdown = $('#kgs-search-dropdown');

        if (!$searchInput.length) return;

        // Input handler with debounce
        $searchInput.on('input', (e) => {
            const query = e.target.value;
            this.state.searchQuery = query;

            // Clear existing timer
            if (this.state.searchTimer) {
                clearTimeout(this.state.searchTimer);
            }

            // Show typing indicator
            this.showSearchTyping();

            // Set new timer
            this.state.searchTimer = setTimeout(() => {
                this.performSearch(query);
            }, this.config.debounceDelay);
        });

        // Focus handler
        $searchInput.on('focus', () => {
            if (this.state.searchQuery.length >= this.config.searchMinChars) {
                $searchDropdown.show();
            } else {
                this.showRecentSearches();
            }
        });

        // Click outside to close
        $(document).on('click', (e) => {
            if (!$(e.target).closest('.kgs-search-container').length) {
                $searchDropdown.hide();
            }
        });

        // Keyboard navigation
        $searchInput.on('keydown', (e) => {
            this.handleSearchKeyboard(e);
        });
    },

    async performSearch(query) {
        if (query.length < this.config.searchMinChars) {
            this.showRecentSearches();
            return;
        }

        this.state.isSearching = true;
        this.showSearchLoading();

        try {
            const response = await frappe.call({
                method: 'trustbit_website_school.api.webshop.search_items',
                args: {
                    query: query,
                    filters: this.getSearchFilters(),
                    limit: 10
                }
            });

            this.renderSearchResults(response.message || []);
        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError();
        } finally {
            this.state.isSearching = false;
        }
    },

    getSearchFilters() {
        const filters = {};
        const $typeFilter = $('#kgs-search-type');
        const $schoolFilter = $('#kgs-search-school');
        const $classFilter = $('#kgs-search-class');

        if ($typeFilter.val()) filters.type = $typeFilter.val();
        if ($schoolFilter.val()) filters.school = $schoolFilter.val();
        if ($classFilter.val()) filters.class = $classFilter.val();

        return filters;
    },

    renderSearchResults(results) {
        const $dropdown = $('#kgs-search-dropdown');

        if (results.length === 0) {
            $dropdown.html(`
                <div class="kgs-search-empty">
                    <span style="font-size: 40px;">🔍</span>
                    <p>No results found for "${this.state.searchQuery}"</p>
                </div>
            `);
        } else {
            let html = `
                <div class="kgs-search-header">
                    🔍 ${results.length} results found
                </div>
            `;

            results.forEach((item, idx) => {
                const isBundle = item.type === 'bundle';
                html += `
                    <div class="kgs-search-result ${idx === 0 ? 'selected' : ''}" 
                         data-item-code="${item.item_code}"
                         data-type="${item.type}">
                        <div class="kgs-search-result-image" style="
                            background: ${isBundle ? 'linear-gradient(135deg, #7c3aed, #a855f7)' : '#f0f9ff'};
                        ">
                            ${item.image ? `<img src="${item.image}" alt="">` : (isBundle ? '📦' : '📖')}
                        </div>
                        <div class="kgs-search-result-info">
                            <div class="kgs-search-result-badges">
                                <span class="kgs-type-badge ${isBundle ? 'bundle' : 'item'}">
                                    ${isBundle ? '📦 BUNDLE' : '📖 ITEM'}
                                </span>
                                <span class="kgs-item-code">${item.item_code}</span>
                            </div>
                            <div class="kgs-search-result-name">${item.item_name}</div>
                            <div class="kgs-search-result-meta">
                                ${isBundle 
                                    ? `${item.item_count || 0} items` 
                                    : `Stock: ${item.stock || 0}`
                                }
                            </div>
                        </div>
                        <div class="kgs-search-result-price">
                            <div class="price">₹${(item.price || 0).toLocaleString()}</div>
                            <span class="kgs-action-badge ${isBundle ? 'bundle' : 'item'}">
                                ${isBundle ? 'View Bundle' : '+ Add'}
                            </span>
                        </div>
                    </div>
                `;
            });

            $dropdown.html(html);
        }

        $dropdown.show();

        // Click handler for results
        $dropdown.find('.kgs-search-result').on('click', (e) => {
            const $result = $(e.currentTarget);
            const itemCode = $result.data('item-code');
            const type = $result.data('type');

            if (type === 'bundle') {
                window.location.href = `/shop/bundles/${itemCode}`;
            } else {
                this.addItemToCart(itemCode);
            }

            $dropdown.hide();
            $('#kgs-search-input').val('');
        });
    },

    showSearchTyping() {
        $('#kgs-search-dropdown').html(`
            <div class="kgs-search-typing">
                <span style="font-size: 32px;">✍️</span>
                <p>Keep typing...</p>
                <small>Search will start when you stop</small>
            </div>
        `).show();
    },

    showSearchLoading() {
        $('#kgs-search-dropdown').html(`
            <div class="kgs-search-loading">
                <span style="font-size: 32px;">⏳</span>
                <p>Searching...</p>
            </div>
        `).show();
    },

    showSearchError() {
        $('#kgs-search-dropdown').html(`
            <div class="kgs-search-error">
                <span style="font-size: 32px;">❌</span>
                <p>Search failed. Please try again.</p>
            </div>
        `).show();
    },

    showRecentSearches() {
        // TODO: Implement recent searches from localStorage
        $('#kgs-search-dropdown').hide();
    },

    handleSearchKeyboard(e) {
        const $dropdown = $('#kgs-search-dropdown');
        const $results = $dropdown.find('.kgs-search-result');
        const $selected = $results.filter('.selected');
        let idx = $results.index($selected);

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                idx = Math.min(idx + 1, $results.length - 1);
                $results.removeClass('selected').eq(idx).addClass('selected');
                break;
            case 'ArrowUp':
                e.preventDefault();
                idx = Math.max(idx - 1, 0);
                $results.removeClass('selected').eq(idx).addClass('selected');
                break;
            case 'Enter':
                e.preventDefault();
                $selected.click();
                break;
            case 'Escape':
                $dropdown.hide();
                break;
        }
    },

    // ================================
    // CART FUNCTIONALITY
    // ================================

    initCart() {
        this.loadCart();
    },

    loadCart() {
        // Only load cart for logged in users
        if (!frappe.session.user || frappe.session.user === 'Guest') {
            return;
        }
        frappe.call({
            method: 'webshop.webshop.shopping_cart.cart.get_cart_quotation',
            callback: (r) => {
                if (r.message && r.message.doc) {
                    this.updateCartUI(r.message.doc.items || []);
                }
            },
            error: () => {
                // Silently ignore errors
            }
        });
    },

    async addBundleToCart(itemCode) {
        // Check if user is logged in
        if (frappe.session.user === 'Guest') {
            this.showNotification('🔐 Please login to add items to cart', 'warning');
            setTimeout(() => {
                window.location.href = '/login?redirect-to=' + encodeURIComponent(window.location.pathname);
            }, 1500);
            return;
        }

        this.showNotification('⏳ Adding bundle items...', 'info');

        try {
            const response = await frappe.call({
                method: 'trustbit_website_school.api.webshop.add_bundle_to_cart',
                args: { item_code: itemCode }
            });

            const result = response.message;

            if (result && result.success) {
                this.showNotification(
                    `✅ ${result.message}`,
                    result.skipped.length > 0 ? 'warning' : 'success'
                );
                this.loadCart();
            } else {
                this.showNotification('❌ Failed to add bundle', 'error');
            }
        } catch (error) {
            console.error('Add bundle error:', error);
            if (error.message && error.message.includes('Not permitted')) {
                this.showNotification('🔐 Please login to add items to cart', 'warning');
            } else {
                this.showNotification('❌ Error adding bundle to cart', 'error');
            }
        }
    },

    async addItemToCart(itemCode) {
        // Check if user is logged in
        if (frappe.session.user === 'Guest') {
            this.showNotification('🔐 Please login to add items to cart', 'warning');
            setTimeout(() => {
                window.location.href = '/login?redirect-to=' + encodeURIComponent(window.location.pathname);
            }, 1500);
            return;
        }

        try {
            await frappe.call({
                method: 'webshop.webshop.shopping_cart.cart.add_to_cart',
                args: { item_code: itemCode }
            });

            this.showNotification('✅ Item added to cart', 'success');
            this.loadCart();
        } catch (error) {
            console.error('Add item error:', error);
            if (error.message && error.message.includes('Not permitted')) {
                this.showNotification('🔐 Please login to add items to cart', 'warning');
            } else {
                this.showNotification('❌ Error adding item to cart', 'error');
            }
        }
    },

    updateCartUI(items) {
        const count = items.reduce((sum, item) => sum + item.qty, 0);
        const $cartBtn = $('.kgs-cart-btn');
        const $cartCount = $cartBtn.find('.kgs-cart-count');

        if (count > 0) {
            $cartBtn.addClass('has-items');
            if ($cartCount.length) {
                $cartCount.text(count);
            } else {
                $cartBtn.append(`<span class="kgs-cart-count">${count}</span>`);
            }
        } else {
            $cartBtn.removeClass('has-items');
            $cartCount.remove();
        }
    },

    // ================================
    // BUNDLE PREVIEW MODAL
    // ================================

    async showBundlePreview(itemCode) {
        try {
            const response = await frappe.call({
                method: 'trustbit_website_school.api.webshop.get_bundle_detail',
                args: { item_code: itemCode }
            });

            const bundle = response.message;
            this.renderBundleModal(bundle);
        } catch (error) {
            console.error('Bundle preview error:', error);
            this.showNotification('❌ Error loading bundle', 'error');
        }
    },

    renderBundleModal(bundle) {
        const itemsHtml = bundle.items.map((item, idx) => `
            <div class="kgs-modal-item ${item.stock <= 0 ? 'out-of-stock' : ''}">
                <span class="kgs-modal-item-image">${item.image || '📦'}</span>
                <div class="kgs-modal-item-info">
                    <div class="kgs-modal-item-name">${item.item_name}</div>
                    <div class="kgs-modal-item-meta">
                        Qty: ${item.qty} ${item.uom} • 
                        <span class="${item.stock > 0 ? 'in-stock' : 'no-stock'}">
                            ${item.stock > 0 ? `${item.stock} available` : 'Out of Stock'}
                        </span>
                    </div>
                </div>
                <div class="kgs-modal-item-price">₹${item.rate}</div>
            </div>
        `).join('');

        const modalHtml = `
            <div class="kgs-modal-overlay">
                <div class="kgs-modal kgs-glass">
                    <div class="kgs-modal-header">
                        <div>
                            <small>📦 PRODUCT BUNDLE • ${bundle.items.length} Items</small>
                            <h2>${bundle.item_name}</h2>
                            <p>${bundle.school || ''} ${bundle.class ? '• ' + bundle.class : ''}</p>
                        </div>
                        <button class="kgs-modal-close">✕</button>
                    </div>
                    <div class="kgs-modal-body">
                        ${itemsHtml}
                    </div>
                    <div class="kgs-modal-footer">
                        <div class="kgs-modal-total">
                            <span>Total Bundle Value</span>
                            <strong>₹${bundle.total_price.toLocaleString()}</strong>
                        </div>
                        <div class="kgs-modal-actions">
                            <button class="kgs-btn kgs-btn-outline kgs-modal-close">Cancel</button>
                            <button class="kgs-btn kgs-btn-secondary kgs-add-bundle-btn" 
                                    data-item-code="${bundle.item_code}">
                                🛒 Add All Items to Cart
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modalHtml);
    },

    closeModal() {
        $('.kgs-modal-overlay').remove();
    },

    // ================================
    // NOTIFICATIONS
    // ================================

    initNotifications() {
        // Create notification container if not exists
        if (!$('#kgs-notifications').length) {
            $('body').append('<div id="kgs-notifications"></div>');
        }
    },

    showNotification(message, type = 'success') {
        const id = 'notif-' + Date.now();
        const $notification = $(`
            <div id="${id}" class="kgs-notification ${type}">
                ${message}
            </div>
        `);

        $('#kgs-notifications').append($notification);

        // Auto remove
        setTimeout(() => {
            $notification.fadeOut(300, function() {
                $(this).remove();
            });
        }, this.config.notificationDuration);
    },

    // ================================
    // UTILITY FUNCTIONS
    // ================================

    formatCurrency(amount) {
        return '₹' + parseFloat(amount).toLocaleString('en-IN');
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialize on DOM ready
$(document).ready(() => {
    TrustbitWebshop.init();
});

// Export for global access
window.TrustbitWebshop = TrustbitWebshop;
