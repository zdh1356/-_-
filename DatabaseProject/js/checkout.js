// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载购物车商品
    loadCartItems();
    // 加载省份数据
    loadProvinces();
    // 加载已保存的地址
    loadSavedAddresses();
    // 绑定事件监听器
    bindEventListeners();
});

// 加载购物车商品
function loadCartItems() {
    // 从localStorage或API获取购物车数据
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartContainer = document.getElementById('cart-items');
    let subtotal = 0;

    cartContainer.innerHTML = cart.map(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;
        return `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${item.image}" alt="${item.title}" style="width: 50px; margin-right: 10px;">
                        <div>
                            <h6 class="mb-0">${item.title}</h6>
                            <small class="text-muted">${item.author}</small>
                        </div>
                    </div>
                </td>
                <td>¥${item.price.toFixed(2)}</td>
                <td>${item.quantity}</td>
                <td>¥${itemTotal.toFixed(2)}</td>
            </tr>
        `;
    }).join('');

    // 更新订单金额
    updateOrderAmount(subtotal);
}

// 更新订单金额
function updateOrderAmount(subtotal) {
    const shipping = 0; // 免运费
    const discount = parseFloat(localStorage.getItem('discount') || '0');
    const total = subtotal - discount;

    document.getElementById('subtotal').textContent = `¥${subtotal.toFixed(2)}`;
    document.getElementById('discount').textContent = `-¥${discount.toFixed(2)}`;
    document.getElementById('total').textContent = `¥${total.toFixed(2)}`;
}

// 加载省份数据
function loadProvinces() {
    const provinces = [
        '北京市', '上海市', '天津市', '重庆市', '河北省', '山西省', '辽宁省', '吉林省',
        '黑龙江省', '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省', '河南省',
        '湖北省', '湖南省', '广东省', '海南省', '四川省', '贵州省', '云南省', '陕西省',
        '甘肃省', '青海省', '台湾省', '内蒙古自治区', '广西壮族自治区', '西藏自治区',
        '宁夏回族自治区', '新疆维吾尔自治区', '香港特别行政区', '澳门特别行政区'
    ];

    const provinceSelect = document.getElementById('province');
    provinces.forEach(province => {
        const option = document.createElement('option');
        option.value = province;
        option.textContent = province;
        provinceSelect.appendChild(option);
    });
}

// 加载已保存的地址
function loadSavedAddresses() {
    // 从localStorage或API获取保存的地址
    const addresses = JSON.parse(localStorage.getItem('saved_addresses')) || [];
    const container = document.getElementById('saved-addresses-container');

    container.innerHTML = addresses.map((address, index) => `
        <div class="col-md-6 mb-3">
            <div class="card">
                <div class="card-body">
                    <div class="custom-control custom-radio">
                        <input type="radio" id="address${index}" name="savedAddress" class="custom-control-input" 
                            ${index === 0 ? 'checked' : ''}>
                        <label class="custom-control-label" for="address${index}">
                            <strong>${address.name}</strong><br>
                            ${address.phone}<br>
                            ${address.province}${address.city}${address.district}<br>
                            ${address.address}
                        </label>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// 绑定事件监听器
function bindEventListeners() {
    // 省份选择改变时加载城市
    document.getElementById('province').addEventListener('change', function(e) {
        loadCities(e.target.value);
    });

    // 城市选择改变时加载区县
    document.getElementById('city').addEventListener('change', function(e) {
        loadDistricts(e.target.value);
    });

    // 发票选择框变化
    document.getElementById('needInvoice').addEventListener('change', function(e) {
        document.getElementById('invoiceForm').style.display = e.target.checked ? 'block' : 'none';
    });

    // 优惠券应用按钮点击
    document.getElementById('couponCode').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyCoupon();
        }
    });
}

// 应用优惠券
function applyCoupon() {
    const couponCode = document.getElementById('couponCode').value.trim();
    if (!couponCode) {
        showToast('请输入优惠码');
        return;
    }

    // 这里应该调用API验证优惠码
    // 示例实现
    if (couponCode === 'BOOK2024') {
        const subtotal = parseFloat(document.getElementById('subtotal').textContent.replace('¥', ''));
        const discount = subtotal * 0.1; // 10%折扣
        localStorage.setItem('discount', discount.toString());
        updateOrderAmount(subtotal);
        showToast('优惠码应用成功！');
    } else {
        showToast('无效的优惠码');
    }
}

// 显示新增地址表单
function showNewAddressForm() {
    // 清空表单
    document.getElementById('shipping-form').reset();
    // 切换到收货信息标签页
    document.querySelector('a[href="#tabs-1-2"]').click();
}

// 提交订单
async function submitOrder() {
    try {
        // 收集表单数据
        const formData = {
            paymentMethod: document.querySelector('input[name="paymentMethod"]:checked').id,
            shipping: {
                name: document.getElementById('forms-3-name').value,
                phone: document.getElementById('form-1-phone').value,
                province: document.getElementById('province').value,
                city: document.getElementById('city').value,
                district: document.getElementById('district').value,
                address: document.getElementById('forms-3-street-address').value
            },
            invoice: document.getElementById('needInvoice').checked ? {
                type: document.getElementById('invoiceType').value,
                title: document.getElementById('invoiceTitle').value
            } : null,
            notes: document.getElementById('orderNotes').value,
            items: JSON.parse(localStorage.getItem('cart')) || [],
            total: parseFloat(document.getElementById('total').textContent.replace('¥', ''))
        };

        // 表单验证
        if (!validateOrderForm(formData)) {
            return;
        }

        // 调用订单创建API
        const response = await createOrder(formData);
        
        // 根据支付方式调用相应的支付接口
        switch(formData.paymentMethod) {
            case 'alipay':
                await handleAlipayPayment(response.orderId);
                break;
            case 'wechat':
                await handleWechatPayment(response.orderId);
                break;
            case 'bankTransfer':
                showBankTransferInfo(response.orderId);
                break;
        }

    } catch (error) {
        console.error('提交订单失败:', error);
        showToast('提交订单失败，请重试');
    }
}

// 表单验证
function validateOrderForm(formData) {
    const { shipping } = formData;
    if (!shipping.name || !shipping.phone || !shipping.address) {
        showToast('请填写完整的收货信息');
        return false;
    }

    if (!/^1[3-9]\d{9}$/.test(shipping.phone)) {
        showToast('请输入正确的手机号码');
        return false;
    }

    if (formData.items.length === 0) {
        showToast('购物车为空，请先添加商品');
        return false;
    }

    return true;
}

// 创建订单
async function createOrder(orderData) {
    const response = await fetch('http://1.94.203.175:5000/api/orders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(orderData)
    });

    if (!response.ok) {
        throw new Error('创建订单失败');
    }

    return response.json();
}

// 处理支付宝支付
async function handleAlipayPayment(orderId) {
    try {
        // 获取支付宝支付参数
        const response = await fetch(`http://1.94.203.175:5000/api/payments/alipay/${orderId}`);
        const { payInfo } = await response.json();
        
        // 调用支付宝SDK
        ap.tradePay({
            tradeNO: payInfo.tradeNo
        }, function(res) {
            if (res.resultCode === "9000") {
                showToast('支付成功');
                clearCartAndRedirect(orderId);
            } else {
                showToast('支付失败，请重试');
            }
        });
    } catch (error) {
        console.error('支付宝支付失败:', error);
        showToast('支付发起失败，请重试');
    }
}

// 处理微信支付
async function handleWechatPayment(orderId) {
    try {
        // 获取微信支付参数
        const response = await fetch(`/api/payments/wechat/${orderId}`);
        const { payInfo } = await response.json();
        
        // 调用微信SDK
        WeixinJSBridge.invoke('getBrandWCPayRequest', payInfo, function(res) {
            if (res.err_msg === "get_brand_wcpay_request:ok") {
                showToast('支付成功');
                clearCartAndRedirect(orderId);
            } else {
                showToast('支付失败，请重试');
            }
        });
    } catch (error) {
        console.error('微信支付失败:', error);
        showToast('支付发起失败，请重试');
    }
}

// 显示银行转账信息
function showBankTransferInfo(orderId) {
    // 显示银行账户信息的模态框
    const bankInfo = `
        <h5>银行转账信息</h5>
        <p>请将订单金额转账至以下账户：</p>
        <p>银行：中国工商银行</p>
        <p>账号：1234 5678 9012 3456</p>
        <p>户名：网上书店</p>
        <p>订单号：${orderId}</p>
        <p class="text-danger">请在转账备注中注明订单号</p>
    `;
    
    // 使用Bootstrap模态框显示
    const modal = new bootstrap.Modal(document.getElementById('bankTransferModal'));
    document.querySelector('#bankTransferModal .modal-body').innerHTML = bankInfo;
    modal.show();
}

// 清空购物车并跳转
async function clearCartAndRedirect(orderId) {
    try {
        // 发送订单确认邮件
        await sendOrderConfirmationEmail(orderId);

        localStorage.removeItem('cart');
        localStorage.removeItem('discount');
        window.location.href = `/order-success.html?orderId=${orderId}&emailSent=true`;
    } catch (error) {
        console.error('发送订单确认邮件失败:', error);
        // 即使邮件发送失败，也要跳转到成功页面
        localStorage.removeItem('cart');
        localStorage.removeItem('discount');
        window.location.href = `/order-success.html?orderId=${orderId}&emailSent=false`;
    }
}

// 发送订单确认邮件
async function sendOrderConfirmationEmail(orderId) {
    try {
        // 获取订单详情
        const orderResponse = await fetch(`/api/orders/${orderId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!orderResponse.ok) {
            throw new Error('获取订单详情失败');
        }

        const orderData = await orderResponse.json();

        // 获取用户信息
        const userEmail = orderData.customerEmail || localStorage.getItem('userEmail');
        const username = orderData.customerName || localStorage.getItem('username') || '尊敬的用户';

        if (!userEmail) {
            throw new Error('用户邮箱信息缺失');
        }

        // 发送邮件
        const emailResponse = await fetch('http://127.0.0.1:5000/api/email/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: userEmail,
                email_type: 'order_confirm',
                username: username,
                user_id: orderData.userId,
                order_data: {
                    orderId: orderData.orderId,
                    orderDate: orderData.createTime,
                    total: orderData.total,
                    paymentMethod: orderData.paymentMethod,
                    items: orderData.items,
                    shipping: orderData.shipping,
                    username: username
                }
            })
        });

        const emailResult = await emailResponse.json();

        if (!emailResponse.ok) {
            throw new Error(emailResult.error || '邮件发送失败');
        }

        console.log('✅ 订单确认邮件发送成功');
        return emailResult;

    } catch (error) {
        console.error('❌ 发送订单确认邮件时出错:', error);
        throw error;
    }
}

// 显示提示消息
function showToast(message) {
    // 使用Bootstrap的Toast组件
    const toast = new bootstrap.Toast(document.getElementById('toast'));
    document.querySelector('#toast .toast-body').textContent = message;
    toast.show();
}