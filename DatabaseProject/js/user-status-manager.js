/**
 * 华轩书店全局用户状态管理器
 * 统一管理用户登录状态，确保所有页面都能正确显示用户信息
 */

class UserStatusManager {
    constructor() {
        this.apiBase = 'http://1.94.203.175:5000/api';
        this.isInitialized = false;
        this.currentUser = null;
        this.loginCallbacks = [];
        this.logoutCallbacks = [];
        
        // 自动初始化
        this.init();
    }

    /**
     * 初始化用户状态管理器
     */
    init() {
        if (this.isInitialized) return;
        
        console.log('🔧 初始化用户状态管理器');
        
        // 检查当前登录状态
        this.checkLoginStatus();
        
        // 监听存储变化（跨标签页同步）
        window.addEventListener('storage', (e) => {
            if (['authToken', 'userInfo', 'isLoggedIn'].includes(e.key)) {
                console.log('📡 检测到登录状态变化，重新检查');
                this.checkLoginStatus();
            }
        });
        
        this.isInitialized = true;
        console.log('✅ 用户状态管理器初始化完成');
    }

    /**
     * 检查登录状态
     */
    checkLoginStatus() {
        const authToken = localStorage.getItem('authToken') || localStorage.getItem('token');
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        const userInfoStr = localStorage.getItem('userInfo');
        const username = localStorage.getItem('username');

        console.log('🔍 检查登录状态:', {
            authToken: !!authToken,
            isLoggedIn,
            userInfoStr: !!userInfoStr,
            username
        });

        let userInfo = {};
        if (userInfoStr) {
            try {
                userInfo = JSON.parse(userInfoStr);
            } catch (error) {
                console.error('❌ 解析用户信息失败:', error);
                this.clearLoginData();
                return false;
            }
        }

        // 检查是否已登录（多重验证）
        const hasValidLogin = (
            (authToken && authToken !== 'null') &&
            (isLoggedIn === 'true') &&
            (userInfo.username || username)
        );

        if (hasValidLogin) {
            this.currentUser = {
                id: userInfo.id,
                username: userInfo.username || username,
                email: userInfo.email || localStorage.getItem('userEmail'),
                token: authToken,
                ...userInfo
            };
            
            console.log('✅ 用户已登录:', this.currentUser.username);
            this.updateUserDisplay(true);
            this.triggerLoginCallbacks();
            return true;
        } else {
            console.log('❌ 用户未登录');
            this.currentUser = null;
            this.updateUserDisplay(false);
            this.triggerLogoutCallbacks();
            return false;
        }
    }

    /**
     * 更新页面上的用户显示
     */
    updateUserDisplay(isLoggedIn) {
        const userMenu = document.getElementById('userMenu');
        const userDisplayName = document.getElementById('userDisplayName');
        const userDropdown = document.getElementById('userDropdown');

        if (!userMenu || !userDisplayName) {
            console.warn('⚠️ 用户菜单元素未找到，可能页面还未加载完成');
            return;
        }

        if (isLoggedIn && this.currentUser) {
            // 用户已登录
            const displayName = this.currentUser.username || '用户';
            userDisplayName.textContent = displayName;
            userMenu.href = '#';
            
            // 绑定下拉菜单事件
            userMenu.onclick = (e) => {
                e.preventDefault();
                this.toggleUserDropdown();
            };

            // 显示下拉菜单
            if (userDropdown) {
                userDropdown.style.display = 'block';
            }
        } else {
            // 用户未登录
            userDisplayName.textContent = '登录';
            userMenu.href = 'login-page.html';
            userMenu.onclick = null;
            
            // 隐藏下拉菜单
            if (userDropdown) {
                userDropdown.style.display = 'none';
            }
        }

        // 更新购物车计数
        this.updateCartCount();
    }

    /**
     * 切换用户下拉菜单
     */
    toggleUserDropdown() {
        const userDropdown = document.getElementById('userDropdown');
        if (userDropdown) {
            const isHidden = userDropdown.style.display === 'none' || !userDropdown.style.display;
            userDropdown.style.display = isHidden ? 'block' : 'none';
        }
    }

    /**
     * 更新购物车计数
     */
    async updateCartCount() {
        const cartCount = document.getElementById('cartCount');
        if (!cartCount) return;

        if (!this.isLoggedIn()) {
            cartCount.textContent = '0';
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/order/cart`, {
                headers: {
                    'Authorization': `Bearer ${this.currentUser.token}`
                }
            });

            if (response.ok) {
                const result = await response.json();
                const items = result.data?.items || [];
                const totalCount = items.reduce((sum, item) => sum + (item.quantity || 0), 0);
                cartCount.textContent = totalCount.toString();
            } else {
                cartCount.textContent = '0';
            }
        } catch (error) {
            console.error('❌ 更新购物车计数失败:', error);
            cartCount.textContent = '0';
        }
    }

    /**
     * 登录用户
     */
    login(token, userInfo) {
        console.log('🔐 用户登录:', userInfo.username);
        
        // 保存登录信息
        localStorage.setItem('authToken', token);
        localStorage.setItem('token', token); // 兼容性
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('username', userInfo.username);
        localStorage.setItem('userEmail', userInfo.email);

        // 更新当前状态
        this.checkLoginStatus();
    }

    /**
     * 退出登录
     */
    logout() {
        console.log('🚪 用户退出登录');
        
        this.clearLoginData();
        this.currentUser = null;
        this.updateUserDisplay(false);
        this.triggerLogoutCallbacks();
        
        // 跳转到首页
        if (window.location.pathname !== '/index.html' && !window.location.pathname.endsWith('index.html')) {
            window.location.href = 'index.html';
        }
    }

    /**
     * 清除登录数据
     */
    clearLoginData() {
        const keys = ['authToken', 'token', 'isLoggedIn', 'userInfo', 'username', 'userEmail'];
        keys.forEach(key => localStorage.removeItem(key));
    }

    /**
     * 检查是否已登录
     */
    isLoggedIn() {
        return !!this.currentUser;
    }

    /**
     * 获取当前用户信息
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * 添加登录回调
     */
    onLogin(callback) {
        this.loginCallbacks.push(callback);
    }

    /**
     * 添加退出回调
     */
    onLogout(callback) {
        this.logoutCallbacks.push(callback);
    }

    /**
     * 触发登录回调
     */
    triggerLoginCallbacks() {
        this.loginCallbacks.forEach(callback => {
            try {
                callback(this.currentUser);
            } catch (error) {
                console.error('❌ 登录回调执行失败:', error);
            }
        });
    }

    /**
     * 触发退出回调
     */
    triggerLogoutCallbacks() {
        this.logoutCallbacks.forEach(callback => {
            try {
                callback();
            } catch (error) {
                console.error('❌ 退出回调执行失败:', error);
            }
        });
    }

    /**
     * 强制刷新用户状态
     */
    refresh() {
        console.log('🔄 强制刷新用户状态');
        this.checkLoginStatus();
    }
}

// 创建全局实例
window.userStatusManager = new UserStatusManager();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 页面DOM加载完成，初始化用户状态');
    window.userStatusManager.refresh();
    
    // 延迟再次检查，确保所有元素都已加载
    setTimeout(() => {
        window.userStatusManager.refresh();
    }, 1000);
});

// 页面完全加载后再次检查
window.addEventListener('load', function() {
    console.log('🌐 页面完全加载，再次检查用户状态');
    window.userStatusManager.refresh();
});

// 导出全局函数供其他脚本使用
window.checkUserStatus = function() {
    return window.userStatusManager.checkLoginStatus();
};

window.logout = function() {
    if (confirm('确定要退出登录吗？')) {
        window.userStatusManager.logout();
    }
};

console.log('📚 华轩书店用户状态管理器已加载');
