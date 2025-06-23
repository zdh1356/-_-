/**
 * 页面适配器 - 将现有页面快速接入实时数据系统
 * 替换localStorage调用，实现数据库实时连接
 */

class PageAdapters {
    constructor() {
        this.dataManager = window.dataManager;
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    init() {
        console.log('🔧 PageAdapters初始化:', {
            currentPage: this.currentPage,
            dataManager: !!this.dataManager,
            pathname: window.location.pathname
        });

        if (!this.dataManager) {
            console.error('❌ DataManager未初始化');
            return;
        }

        // 根据页面类型初始化对应适配器
        switch (this.currentPage) {
            case 'login':
                this.initLoginPage();
                break;
            case 'register':
                this.initRegisterPage();
                break;
            case 'change-password':
                this.initChangePasswordPage();
                break;
            case 'user-profile':
                this.initUserProfilePage();
                break;
            case 'shopping-cart':
                this.initShoppingCartPage();
                break;
            case 'checkout':
                this.initCheckoutPage();
                break;
            case 'order-history':
                this.initOrderHistoryPage();
                break;
            case 'browsing-history':
                this.initBrowsingHistoryPage();
                break;
            case 'user-preferences':
                this.initUserPreferencesPage();
                break;
            case 'book-detail':
                this.initBookDetailPage();
                break;
            case 'search-results':
                this.initSearchResultsPage();
                break;
            case 'category':
                this.initCategoryPage();
                break;
            default:
                this.initCommonFeatures();
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop().split('.')[0];

        // 处理特殊页面名称映射
        const pageMap = {
            'login-page': 'login',
            'registration-page': 'register',
            'change-password': 'change-password',
            'user-profile': 'user-profile',
            'shopping-cart': 'shopping-cart',
            'order-history': 'order-history',
            'browsing-history': 'browsing-history',
            'user-preferences': 'user-preferences',
            'book-detail': 'book-detail',
            'search-results': 'search-results',
            'category': 'category'
        };

        return pageMap[filename] || filename || 'index';
    }

    // ==================== 登录页面适配器 ====================
    
    initLoginPage() {
        console.log('🔑 初始化登录页面');

        const loginForm = document.getElementById('loginForm');
        if (!loginForm) {
            console.error('❌ 未找到登录表单 #loginForm');
            return;
        }

        console.log('✅ 找到登录表单，绑定事件');

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('📝 登录表单提交');

            const emailEl = document.getElementById('forms-login-email');
            const passwordEl = document.getElementById('forms-login-password');
            const rememberEl = document.querySelector('input[name="remember"]');

            if (!emailEl || !passwordEl) {
                console.error('❌ 未找到邮箱或密码输入框');
                this.showMessage('页面元素错误，请刷新重试', 'error');
                return;
            }

            const email = emailEl.value;
            const password = passwordEl.value;
            const remember = rememberEl ? rememberEl.checked : false;

            console.log('📧 登录信息:', { email, password: '***', remember });

            if (!email || !password) {
                this.showMessage('请填写邮箱和密码', 'error');
                return;
            }

            try {
                this.showMessage('正在登录...', 'info');
                const result = await this.dataManager.login(email, password, remember);
                console.log('🔄 登录结果:', result);

                if (result.success) {
                    this.showMessage('登录成功！正在跳转...', 'success');
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1000);
                } else {
                    this.showMessage(result.error || '登录失败', 'error');
                }
            } catch (error) {
                console.error('❌ 登录异常:', error);
                this.showMessage('登录失败: ' + error.message, 'error');
            }
        });
    }

    // ==================== 注册页面适配器 ====================
    
    initRegisterPage() {
        const registerForm = document.getElementById('registerForm');
        if (!registerForm) return;

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(registerForm);
            const userData = Object.fromEntries(formData.entries());

            const result = await this.dataManager.register(userData);
            
            if (result.success) {
                this.showMessage('注册成功！请登录', 'success');
                setTimeout(() => {
                    window.location.href = 'login-page.html';
                }, 2000);
            } else {
                this.showMessage(result.error, 'error');
            }
        });
    }

    // ==================== 修改密码页面适配器 ====================
    
    initChangePasswordPage() {
        // 检查登录状态
        this.checkAuthRequired();

        const changePasswordForm = document.getElementById('changePasswordForm');
        if (!changePasswordForm) return;

        changePasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const currentPassword = document.getElementById('forms-current-password').value;
            const newPassword = document.getElementById('forms-new-password').value;
            const confirmPassword = document.getElementById('forms-confirm-new-password').value;

            // 前端验证
            if (newPassword !== confirmPassword) {
                this.showMessage('两次输入的新密码不一致', 'error');
                return;
            }

            if (newPassword.length < 6) {
                this.showMessage('新密码长度至少为6位', 'error');
                return;
            }

            const result = await this.dataManager.changePassword(currentPassword, newPassword);
            
            if (result.success) {
                this.showMessage('密码修改成功！', 'success');
                changePasswordForm.reset();
                setTimeout(() => {
                    window.location.href = 'user-profile.html';
                }, 2000);
            } else {
                this.showMessage(result.error, 'error');
            }
        });
    }

    // ==================== 用户资料页面适配器 ====================
    
    initUserProfilePage() {
        this.checkAuthRequired();
        this.loadUserProfile();

        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(profileForm);
                const userData = Object.fromEntries(formData.entries());

                const result = await this.dataManager.updateUserInfo(userData);
                
                if (result.success) {
                    this.showMessage('资料更新成功！', 'success');
                } else {
                    this.showMessage(result.error, 'error');
                }
            });
        }
    }

    async loadUserProfile() {
        const userInfo = await this.dataManager.getUserInfo();
        if (!userInfo) return;

        // 填充表单字段
        const fields = ['username', 'email', 'phone', 'realName', 'gender', 'birthDate', 'address'];
        fields.forEach(field => {
            const element = document.getElementById(field) || document.querySelector(`[name="${field}"]`);
            if (element && userInfo[field]) {
                element.value = userInfo[field];
            }
        });
    }

    // ==================== 购物车页面适配器 ====================
    
    async initShoppingCartPage() {
        console.log('🛒 初始化购物车页面');

        // 检查认证状态
        const isAuthenticated = await this.checkAuthRequired();
        if (!isAuthenticated) {
            return;
        }

        // 初始化通用功能
        this.initCommonFeatures();

        // 加载购物车数据
        this.loadShoppingCart();
        this.bindCartEvents();
    }

    async loadShoppingCart() {
        console.log('🛒 开始加载购物车数据');

        try {
            const cartData = await this.dataManager.getCartData(true); // 强制刷新
            console.log('🛒 购物车数据获取结果:', cartData);

            this.renderCartItems(cartData);
        } catch (error) {
            console.error('❌ 加载购物车数据失败:', error);
            this.renderCartItems([]);
        }
    }

    renderCartItems(cartData) {
        const container = document.getElementById('cartItems');
        console.log('🎨 渲染购物车数据:', {
            container: !!container,
            cartData: cartData,
            dataLength: cartData ? cartData.length : 0
        });

        if (!container) {
            console.error('❌ 购物车容器元素未找到');
            return;
        }

        if (!cartData || cartData.length === 0) {
            console.log('📭 购物车为空，显示空状态');
            container.innerHTML = '<tr><td colspan="6" class="text-center" style="padding: 40px;">购物车为空，<a href="index.html">去首页看看</a></td></tr>';

            // 更新总计显示
            const totalAmountEl = document.getElementById('totalPrice');
            const selectedCountEl = document.getElementById('selectedCount');
            if (totalAmountEl) totalAmountEl.textContent = '0.00';
            if (selectedCountEl) selectedCountEl.textContent = '0';

            return;
        }

        container.innerHTML = cartData.map(item => {
            // 确保价格是数字
            const price = parseFloat(item.currentPrice) || parseFloat(item.price) || 0;
            const quantity = parseInt(item.quantity) || 1;
            const subtotal = price * quantity;

            console.log(`🛒 渲染商品 ${item.bookId}:`, {
                title: item.title,
                author: item.author,
                price: price,
                quantity: quantity,
                subtotal: subtotal
            });

            return `
                <tr data-book-id="${item.bookId}">
                    <td>
                        <div class="checkbox-inline">
                            <label>
                                <input type="checkbox" class="cart-item-checkbox" data-id="${item.bookId}" checked>
                                <span class="checkbox-inline__box"></span>
                            </label>
                        </div>
                    </td>
                    <td>
                        <div class="d-flex align-items-center">
                            <img src="${item.coverImageUrl || 'images/default-book.svg'}" alt="${item.title}" style="width: 60px; margin-right: 15px;" onerror="this.src='images/default-book.svg'">
                            <div>
                                <h6 class="mb-1">${item.title || '未知商品'}</h6>
                                <small class="text-muted">${item.author || '未知作者'}</small>
                            </div>
                        </div>
                    </td>
                    <td class="price-cell">¥${price.toFixed(2)}</td>
                    <td>
                        <div class="quantity-controls">
                            <button class="quantity-minus" data-book-id="${item.bookId}" data-id="${item.bookId}">-</button>
                            <span class="quantity-value">${quantity}</span>
                            <button class="quantity-plus" data-book-id="${item.bookId}" data-id="${item.bookId}">+</button>
                        </div>
                    </td>
                    <td class="subtotal-cell">¥${subtotal.toFixed(2)}</td>
                    <td>
                        <button class="button button-sm button-default remove-item" data-id="${item.bookId}">删除</button>
                    </td>
                </tr>
            `;
        }).join('');

        this.updateCartSummary(cartData);
    }

    bindCartEvents() {
        const container = document.getElementById('cartItems');
        if (!container) return;

        // 数量增减
        container.addEventListener('click', async (e) => {
            const bookId = e.target.dataset.bookId || e.target.dataset.id;
            if (!bookId) return;

            console.log('🔢 购物车操作:', {
                action: e.target.className,
                bookId: bookId,
                element: e.target.tagName
            });

            if (e.target.classList.contains('quantity-plus')) {
                const quantitySpan = e.target.previousElementSibling;
                const currentQty = parseInt(quantitySpan.textContent) || 1;
                const newQty = currentQty + 1;

                // 立即更新显示
                this.updateQuantityDisplay(bookId, newQty);

                // 后台更新数据
                try {
                    await this.dataManager.updateCartItem(bookId, newQty);
                } catch (error) {
                    console.error('更新购物车数量失败:', error);
                    // 如果更新失败，恢复原来的数量
                    this.updateQuantityDisplay(bookId, currentQty);
                }

            } else if (e.target.classList.contains('quantity-minus')) {
                const quantitySpan = e.target.nextElementSibling;
                const currentQty = parseInt(quantitySpan.textContent) || 1;

                if (currentQty > 1) {
                    const newQty = currentQty - 1;

                    // 立即更新显示
                    this.updateQuantityDisplay(bookId, newQty);

                    // 后台更新数据
                    try {
                        await this.dataManager.updateCartItem(bookId, newQty);
                    } catch (error) {
                        console.error('更新购物车数量失败:', error);
                        // 如果更新失败，恢复原来的数量
                        this.updateQuantityDisplay(bookId, currentQty);
                    }
                }

            } else if (e.target.classList.contains('remove-item')) {
                if (confirm('确定要移除这个商品吗？')) {
                    await this.dataManager.removeFromCart(bookId);
                    this.loadShoppingCart();
                }
            }
        });

        // 全选功能
        const selectAllCheckbox = document.getElementById('selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.cart-item-checkbox');
                checkboxes.forEach(cb => cb.checked = e.target.checked);
                this.updateCartSummary();
            });
        }

        // 清空购物车
        const clearCartBtn = document.getElementById('clearCart');
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', async () => {
                if (confirm('确定要清空购物车吗？')) {
                    await this.dataManager.clearCart();
                    this.loadShoppingCart();
                }
            });
        }

        // 结算
        const checkoutBtn = document.getElementById('checkout');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => {
                const selectedItems = Array.from(document.querySelectorAll('.cart-item-checkbox:checked'))
                    .map(cb => cb.dataset.id);
                
                if (selectedItems.length === 0) {
                    this.showMessage('请选择要结算的商品', 'error');
                    return;
                }
                
                window.location.href = `checkout.html?items=${selectedItems.join(',')}`;
            });
        }
    }

    updateCartSummary(cartData) {
        console.log('📊 更新购物车统计:', cartData);

        const selectedCheckboxes = document.querySelectorAll('.cart-item-checkbox:checked');
        const selectedIds = Array.from(selectedCheckboxes).map(cb => cb.dataset.id);

        console.log('选中的商品ID:', selectedIds);

        let totalAmount = 0;
        let selectedCount = 0;

        // 如果没有传入cartData，从页面读取
        if (!cartData) {
            selectedCheckboxes.forEach(checkbox => {
                const row = checkbox.closest('tr');
                if (row) {
                    const priceCell = row.querySelector('.price-cell');
                    const quantitySpan = row.querySelector('.quantity-value');

                    if (priceCell && quantitySpan) {
                        const price = parseFloat(priceCell.textContent.replace('¥', '')) || 0;
                        const quantity = parseInt(quantitySpan.textContent) || 1;

                        totalAmount += price * quantity;
                        selectedCount += quantity;
                    }
                }
            });
        } else {
            // 使用传入的cartData
            cartData.forEach(item => {
                if (selectedIds.includes(item.bookId.toString())) {
                    const price = parseFloat(item.currentPrice) || parseFloat(item.price) || 0;
                    const quantity = parseInt(item.quantity) || 1;

                    totalAmount += price * quantity;
                    selectedCount += quantity;
                }
            });
        }

        console.log('统计结果:', { totalAmount, selectedCount });

        // 更新显示
        const totalAmountEl = document.getElementById('totalAmount') || document.getElementById('totalPrice');
        const selectedCountEl = document.getElementById('selectedCount');

        if (totalAmountEl) totalAmountEl.textContent = totalAmount.toFixed(2);
        if (selectedCountEl) selectedCountEl.textContent = selectedCount;

        // 绑定选中框事件（如果还没绑定）
        this.bindCheckboxEvents();
    }

    bindCheckboxEvents() {
        const checkboxes = document.querySelectorAll('.cart-item-checkbox');
        checkboxes.forEach(checkbox => {
            // 移除旧的事件监听器
            checkbox.removeEventListener('change', this.handleCheckboxChange);
            // 添加新的事件监听器
            checkbox.addEventListener('change', this.handleCheckboxChange.bind(this));
        });
    }

    handleCheckboxChange() {
        console.log('☑️ 选中状态改变');
        this.updateCartSummary();
    }

    // 更新数量显示
    updateQuantityDisplay(bookId, newQuantity) {
        const row = document.querySelector(`tr[data-book-id="${bookId}"]`);
        if (!row) {
            console.error('找不到商品行:', bookId);
            return;
        }

        const quantitySpan = row.querySelector('.quantity-value');
        const priceCell = row.querySelector('.price-cell');
        const subtotalCell = row.querySelector('.subtotal-cell');

        if (quantitySpan) {
            quantitySpan.textContent = newQuantity;
        }

        // 更新小计
        if (priceCell && subtotalCell) {
            const price = parseFloat(priceCell.textContent.replace('¥', '')) || 0;
            const subtotal = price * newQuantity;
            subtotalCell.textContent = `¥${subtotal.toFixed(2)}`;
        }

        // 更新总计
        this.updateCartSummary();

        console.log(`✅ 已更新商品${bookId}数量为${newQuantity}`);
    }

    // ==================== 通用功能 ====================
    
    async checkAuthRequired() {
        const userInfo = await this.dataManager.getUserInfo();
        console.log('🔐 检查认证状态:', { userInfo: !!userInfo, currentPage: this.currentPage });

        if (!userInfo || !userInfo.id) {
            console.log('❌ 认证失败，跳转到登录页面');
            window.location.href = 'login-page.html';
            return false;
        }

        console.log('✅ 认证通过');
        return true;
    }

    initCommonFeatures() {
        // 初始化通用功能：用户菜单、购物车计数等
        this.initUserMenu();

        // 只在非登录页面初始化购物车计数
        if (this.currentPage !== 'login' && this.currentPage !== 'register') {
            this.initCartCount();
        }

        this.bindGlobalEvents();
    }

    initUserMenu() {
        const userMenu = document.getElementById('userMenu');
        const userDropdown = document.getElementById('userDropdown');
        
        if (userMenu && userDropdown) {
            userMenu.addEventListener('click', (e) => {
                e.preventDefault();
                userDropdown.style.display = userDropdown.style.display === 'none' ? 'block' : 'none';
            });

            // 点击其他地方关闭菜单
            document.addEventListener('click', (e) => {
                if (!userMenu.contains(e.target)) {
                    userDropdown.style.display = 'none';
                }
            });
        }

        // 绑定登出功能
        const logoutBtns = document.querySelectorAll('[onclick="logout()"], .logout-btn');
        logoutBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm('确定要退出登录吗？')) {
                    this.dataManager.logout();
                }
            });
        });
    }

    async initCartCount() {
        const cartData = await this.dataManager.getCartData();
        this.dataManager.updateCartDisplay(cartData);
    }

    bindGlobalEvents() {
        // 监听购物车更新事件
        window.addEventListener('cartUpdated', (e) => {
            console.log('购物车已更新:', e.detail);
        });

        // 添加到购物车按钮（仅在非首页绑定，避免重复绑定）
        if (this.currentPage !== 'index') {
            document.addEventListener('click', async (e) => {
                if (e.target.classList.contains('add-to-cart-btn')) {
                    e.preventDefault();
                    e.stopPropagation();

                    // 防止重复点击
                    if (e.target.disabled) return;

                    const bookId = e.target.dataset.bookId;
                    const quantity = parseInt(e.target.dataset.quantity) || 1;

                    if (bookId) {
                        // 显示加载状态
                        const originalText = e.target.textContent;
                        e.target.textContent = '添加中...';
                        e.target.disabled = true;

                        try {
                            await this.dataManager.addToCart(bookId, quantity);
                        } finally {
                            // 恢复按钮状态
                            setTimeout(() => {
                                e.target.textContent = originalText;
                                e.target.disabled = false;
                            }, 1000);
                        }
                    }
                }
            });
        }
    }

    showMessage(message, type = 'info') {
        this.dataManager.showMessage(message, type);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 页面DOM加载完成，准备初始化PageAdapters');

    // 等待DataManager初始化完成
    function initPageAdapters() {
        if (window.dataManager) {
            console.log('✅ DataManager已就绪，初始化PageAdapters');
            new PageAdapters();
        } else {
            console.log('⏳ DataManager未就绪，等待中...');
            return false;
        }
        return true;
    }

    // 立即尝试初始化
    if (!initPageAdapters()) {
        // 如果DataManager还未初始化，等待一下
        let attempts = 0;
        const maxAttempts = 10;

        const checkInterval = setInterval(() => {
            attempts++;
            console.log(`🔄 第${attempts}次尝试初始化PageAdapters`);

            if (initPageAdapters() || attempts >= maxAttempts) {
                clearInterval(checkInterval);
                if (attempts >= maxAttempts) {
                    console.error('❌ DataManager初始化超时，PageAdapters初始化失败');
                }
            }
        }, 500);
    }
});

// 导出供其他脚本使用
window.PageAdapters = PageAdapters;
