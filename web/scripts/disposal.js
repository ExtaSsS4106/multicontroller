class WriteoffPage {
    constructor() {
        this.selectedProducts = new Map(); // groupId -> { group, selectedQuantity, productIds }
        this.groupedProducts = []; // Сгруппированные товары из API
        this.allProducts = []; // Плоский список всех товаров для поиска по ID
        this.init();
    }

    async init() {
        await this.loadProducts();
        this.setupEventListeners();
        this.updateUI();
    }

    async loadProducts() {
        try {
            // Запрос к API
            const response = await eel.select_active_with_ids()();
            
            console.log('Ответ от сервера:', response); // Для отладки
            
            // Проверяем структуру ответа
            if (response && !response.error) {
                // Если данные приходят напрямую, без обертки
                if (response.grouped_data) {
                    this.groupedProducts = response.grouped_data;
                } 
                // Если данные в response.data
                else if (response.data && response.data.grouped_data) {
                    this.groupedProducts = response.data.grouped_data;
                }
                // Если данные в response.data.data
                else if (response.data && response.data.data && response.data.data.grouped_data) {
                    this.groupedProducts = response.data.data.grouped_data;
                }
                else {
                    console.error('Неверный формат данных:', response);
                    return;
                }
                
                // Создаем плоский список всех товаров для удобства
                this.allProducts = [];
                this.groupedProducts.forEach(group => {
                    if (group.product_ids && Array.isArray(group.product_ids)) {
                        group.product_ids.forEach(id => {
                            this.allProducts.push({
                                id: id,
                                name: group.name,
                                manufacturer: group.manufacturer,
                                category: group.category,
                                animal_type: group.animal_type,
                                expiry_date: group.expiry_date,
                                total_quantity: group.total_quantity,
                                status: group.status,
                                groupId: `${group.name}-${group.manufacturer}-${group.expiry_date}`
                            });
                        });
                    }
                });
                
                this.renderProducts();
            } else {
                console.error('Ошибка загрузки данных:', response?.message || 'Неизвестная ошибка');
            }
        } catch (error) {
            console.error('Ошибка загрузки товаров:', error);
        }
    }

    setupEventListeners() {
        console.log('Настройка обработчиков событий');
        
        // Поиск
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterProducts(e.target.value);
            });
        }

        // Фильтр по статусу
        const filterSelect = document.getElementById('filterSelect');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.filterByStatus(e.target.value);
            });
        }

        // Кнопка списания
        const writeoffBtn = document.getElementById('writeoffBtn');
        if (writeoffBtn) {
            writeoffBtn.addEventListener('click', () => {
                this.submitWriteoff();
            });
        }

        // Кнопка очистки
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearSelection();
            });
        }
    }

    renderProducts() {
        const grid = document.getElementById('productsGrid');
        if (!grid) {
            console.error('Элемент productsGrid не найден');
            return;
        }
        
        grid.innerHTML = '';

        this.groupedProducts.forEach(group => {
            this.renderProductGroup(grid, group);
        });
    }

    renderProductGroup(grid, group) {
        // Используем первый ID группы как идентификатор для выбора всей группы
        const groupId = group.product_ids[0].toString(); // Приводим к строке
        
        const item = document.createElement('div');
        item.className = `product-item ${this.selectedProducts.has(groupId) ? 'selected' : ''}`;
        item.dataset.groupId = groupId;
        item.dataset.status = group.status;

        // Определяем иконку для типа животного
        let animalIcon = '🐾';
        const animalType = String(group.animal_type || '').toLowerCase();
        if (animalType.includes('кош') || animalType.includes('cat')) {
            animalIcon = '🐱';
        } else if (animalType.includes('соб') || animalType.includes('dog')) {
            animalIcon = '🐶';
        }

        item.innerHTML = `
            <div class="product-checkbox"></div>
            <div class="product-info">
                <div class="product-name">
                    ${group.name}
                    <span class="product-quantity">${group.total_quantity} шт</span>
                </div>
                <div class="product-details">
                    <span class="product-detail">🏭 ${group.manufacturer}</span>
                    <span class="product-detail">📦 ${group.category}</span>
                    <span class="product-detail">${animalIcon} ${group.animal_type}</span>
                    <span class="product-detail">📅 до ${group.expiry_date}</span>
                    <span class="product-status">${group.status}</span>
                </div>
            </div>
        `;

        item.addEventListener('click', (e) => {
            e.preventDefault();
            if (!e.target.classList.contains('quantity-btn') && !e.target.classList.contains('quantity-input') && !e.target.classList.contains('remove-selected')) {
                this.toggleProductGroup(group, groupId);
            }
        });

        grid.appendChild(item);
    }

    toggleProductGroup(group, groupId) {
        if (this.selectedProducts.has(groupId)) {
            this.selectedProducts.delete(groupId);
        } else {
            this.selectedProducts.set(groupId, {
                ...group,
                selectedQuantity: group.total_quantity,
                productIds: [...group.product_ids] // копируем массив ID
            });
        }

        this.updateUI();
        this.updateProductSelection(groupId);
    }

    updateProductSelection(groupId) {
        const item = document.querySelector(`.product-item[data-groupId="${groupId}"]`);
        if (item) {
            if (this.selectedProducts.has(groupId)) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        }
    }

    updateQuantity(groupId, delta) {
        const selected = this.selectedProducts.get(groupId);
        if (!selected) return;

        const newQuantity = selected.selectedQuantity + delta;
        if (newQuantity >= 1 && newQuantity <= selected.total_quantity) {
            selected.selectedQuantity = newQuantity;
            this.selectedProducts.set(groupId, selected);
            this.updateUI();
        }
    }

    handleQuantityInput(groupId, value) {
        const selected = this.selectedProducts.get(groupId);
        if (!selected) return;

        let newQuantity = parseInt(value);
        if (isNaN(newQuantity) || newQuantity < 1) {
            newQuantity = 1;
        } else if (newQuantity > selected.total_quantity) {
            newQuantity = selected.total_quantity;
        }

        selected.selectedQuantity = newQuantity;
        this.selectedProducts.set(groupId, selected);
        this.updateUI();
    }

    updateUI() {
        // Обновить счетчик
        const count = this.selectedProducts.size;
        const selectedCountEl = document.getElementById('selectedCount');
        if (selectedCountEl) {
            selectedCountEl.textContent = count;
        }
        
        // Обновить кнопку списания
        const writeoffBtn = document.getElementById('writeoffBtn');
        if (writeoffBtn) {
            writeoffBtn.disabled = count === 0;
        }

        // Обновить список выбранных
        this.renderSelectedItems();

        // Обновить сводку
        this.updateSummary();

        // Обновить выделение всех карточек
        this.updateAllSelections();
    }

    updateAllSelections() {
        this.groupedProducts.forEach(group => {
            const groupId = group.product_ids[0].toString();
            this.updateProductSelection(groupId);
        });
    }

    renderSelectedItems() {
        const container = document.getElementById('selectedItems');
        if (!container) return;
        
        container.innerHTML = '';

        this.selectedProducts.forEach((group, groupId) => {
            const item = document.createElement('div');
            item.className = 'selected-item';
            item.dataset.groupId = groupId;
            item.innerHTML = `
                <div class="selected-item-info">
                    <span class="selected-item-name">${group.name}</span>
                    <span class="selected-item-details">
                        🏭 ${group.manufacturer} | 📅 до ${group.expiry_date}
                    </span>
                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <div class="quantity-control">
                            <button class="quantity-btn" data-group="${groupId}" data-delta="-1" ${group.selectedQuantity <= 1 ? 'disabled' : ''}>−</button>
                            <input type="text" class="quantity-input" data-group="${groupId}" value="${group.selectedQuantity}" 
                                onkeypress="return (event.charCode >= 48 && event.charCode <= 57)">
                            <button class="quantity-btn" data-group="${groupId}" data-delta="1" ${group.selectedQuantity >= group.total_quantity ? 'disabled' : ''}>+</button>
                        </div>
                        <span class="quantity-max">макс: ${group.total_quantity} шт</span>
                    </div>
                </div>
                <button class="remove-selected" data-group="${groupId}">✕</button>
            `;

            // Добавляем обработчики событий
            const minusBtn = item.querySelector('.quantity-btn[data-delta="-1"]');
            const plusBtn = item.querySelector('.quantity-btn[data-delta="1"]');
            const input = item.querySelector('.quantity-input');
            const removeBtn = item.querySelector('.remove-selected');

            minusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.updateQuantity(groupId, -1);
            });

            plusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.updateQuantity(groupId, 1);
            });

            input.addEventListener('change', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleQuantityInput(groupId, e.target.value);
            });

            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleQuantityInput(groupId, e.target.value);
                }
            });

            removeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.removeSelected(groupId);
            });

            container.appendChild(item);
        });
    }

    removeSelected(groupId) {
        this.selectedProducts.delete(groupId);
        this.updateUI();
    }

    clearSelection() {
        const groupIds = Array.from(this.selectedProducts.keys());
        this.selectedProducts.clear();
        this.updateUI();
    }

    updateSummary() {
        const itemsCount = this.selectedProducts.size;
        const totalQuantity = Array.from(this.selectedProducts.values())
            .reduce((sum, group) => sum + group.selectedQuantity, 0);

        const summaryItems = document.getElementById('summaryItems');
        const summaryQuantity = document.getElementById('summaryQuantity');
        
        if (summaryItems) summaryItems.textContent = itemsCount;
        if (summaryQuantity) summaryQuantity.textContent = totalQuantity + ' шт';
    }

    generateWriteoffData() {
        const products = [];
        
        this.selectedProducts.forEach((group) => {
            // Берем первые N ID из массива product_ids, где N = selectedQuantity
            const selectedIds = group.productIds.slice(0, group.selectedQuantity);
            
            selectedIds.forEach(id => {
                products.push({
                    id: id,
                    status: "deleted"
                });
            });
        });

        return {
            products: products
        };
    }

    async submitWriteoff() {
        try {
            const writeoffData = this.generateWriteoffData();
            
            console.log('Данные для списания:', writeoffData);
            
            // Здесь будет отправка на сервер
            const result = await eel.change_status(writeoffData)();
            
            // Показываем уведомление об успехе
            alert(`Товары успешно списаны! (${writeoffData.products.length} единиц)`);
            
            // Очищаем выбранное
            this.clearSelection();
            
            // Перезагружаем список товаров
            await this.loadProducts();
            
        } catch (error) {
            console.error('Ошибка при списании:', error);
            alert('Произошла ошибка при списании товаров');
        }
    }

    filterProducts(searchText) {
        const items = document.querySelectorAll('.product-item');
        const searchLower = searchText.toLowerCase();

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchLower)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    filterByStatus(status) {
        const items = document.querySelectorAll('.product-item');
        
        items.forEach(item => {
            if (status === 'all') {
                item.style.display = 'flex';
            } else {
                const itemStatus = item.dataset.status;
                item.style.display = itemStatus === status ? 'flex' : 'none';
            }
        });
    }
}
