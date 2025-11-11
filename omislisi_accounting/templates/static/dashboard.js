// Dashboard JavaScript

// Global variable to store all monthly data
let allMonthlyData = null;
let currentSelectedMonth = null;

// Initialize expandable sections and month selector
document.addEventListener('DOMContentLoaded', function() {
    // Set up expandable sections
    const expandableHeaders = document.querySelectorAll('.expandable-header');
    expandableHeaders.forEach(header => {
        header.addEventListener('click', function(e) {
            // Prevent event from bubbling if clicked on child elements
            e.stopPropagation();

            // Find the content div - it's the next sibling of the header
            const content = this.nextElementSibling;
            if (!content || !content.classList.contains('expandable-content')) {
                console.warn('Could not find expandable-content for header');
                return;
            }

            const isExpanded = content.classList.contains('expanded');

            if (isExpanded) {
                content.classList.remove('expanded');
                this.classList.add('collapsed');
            } else {
                content.classList.add('expanded');
                this.classList.remove('collapsed');
            }
        });

        // Also make sure child elements (like h2) don't interfere
        const childElements = header.querySelectorAll('*');
        childElements.forEach(child => {
            child.style.pointerEvents = 'none';
        });
    });

    // Initialize month selector
    initializeMonthSelector();

    // Format numbers
    formatNumbers();
});

// Initialize month selector dropdown
function initializeMonthSelector() {
    const monthSelector = document.getElementById('month-selector');
    if (!monthSelector) return;

    const dashboardData = getDashboardData();
    if (!dashboardData || !dashboardData.available_months) return;

    allMonthlyData = dashboardData.all_months || {};
    currentSelectedMonth = dashboardData.default_month || dashboardData.available_months[dashboardData.available_months.length - 1];

    // Populate dropdown
    dashboardData.available_months.forEach(month => {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = formatMonthLabel(month);
        if (month === currentSelectedMonth) {
            option.selected = true;
        }
        monthSelector.appendChild(option);
    });

    // Add change handler
    monthSelector.addEventListener('change', function() {
        currentSelectedMonth = this.value;
        updateMonthView(currentSelectedMonth);
    });
}

// Format month label for display
function formatMonthLabel(monthStr) {
    const [year, month] = monthStr.split('-');
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    return `${monthNames[parseInt(month) - 1]} ${year}`;
}

// Update the view when month changes
function updateMonthView(monthStr) {
    if (!allMonthlyData || !allMonthlyData[monthStr]) return;

    const monthData = allMonthlyData[monthStr];

    // Update all elements with class 'month-income'
    document.querySelectorAll('.month-income').forEach(el => {
        el.textContent = formatCurrency(monthData.summary.total_income);
    });

    // Update all elements with class 'month-expenses'
    document.querySelectorAll('.month-expenses').forEach(el => {
        el.textContent = formatCurrency(monthData.summary.total_expenses);
    });

    // Update all elements with class 'month-net'
    document.querySelectorAll('.month-net').forEach(el => {
        const value = monthData.summary.net;
        el.textContent = formatCurrency(value);
        el.className = 'metric-value month-net ' + (value >= 0 ? 'positive' : 'negative');
    });

    // Update all elements with class 'month-label'
    document.querySelectorAll('.month-label').forEach(el => {
        el.textContent = monthStr;
    });

    // Update comparison values
    document.querySelectorAll('.month-income-change').forEach(el => {
        const change = monthData.comparison.income_change;
        const changePct = monthData.comparison.income_change_pct;
        el.textContent = formatPercentage(changePct);
        el.className = 'metric-change month-income-change ' + (change >= 0 ? 'positive' : 'negative');
    });

    document.querySelectorAll('.month-expense-change').forEach(el => {
        const change = monthData.comparison.expense_change;
        const changePct = monthData.comparison.expense_change_pct;
        el.textContent = formatPercentage(changePct);
        el.className = 'metric-change month-expense-change ' + (change <= 0 ? 'positive' : 'negative');
    });

    document.querySelectorAll('.month-net-change').forEach(el => {
        const change = monthData.comparison.net_change;
        const changePct = monthData.comparison.net_change_pct;
        el.textContent = formatPercentage(changePct);
        el.className = 'metric-change month-net-change ' + (change >= 0 ? 'positive' : 'negative');
    });

    // Update transaction count
    document.querySelectorAll('.month-transactions').forEach(el => {
        el.textContent = monthData.summary.transaction_count;
    });

    // Update comparison table if present
    updateComparisonTable(monthData);

    // Update category breakdown if present
    updateCategoryBreakdown(monthData);

    // Update counterparty table if present
    updateCounterpartyTable(monthData);
}

// Update comparison table
function updateComparisonTable(monthData) {
    const rows = document.querySelectorAll('.comparison-table tbody tr');
    if (rows.length === 0) return;

    // Income row
    if (rows[0]) {
        const cells = rows[0].querySelectorAll('td');
        if (cells.length >= 5) {
            cells[1].textContent = formatCurrency(monthData.summary.total_income);
            cells[1].className = 'text-right month-income';
            const prevIncome = monthData.summary.total_income - monthData.comparison.income_change;
            cells[2].textContent = formatCurrency(prevIncome);
            cells[3].textContent = formatCurrency(monthData.comparison.income_change);
            cells[3].className = 'text-right month-income-change ' + (monthData.comparison.income_change >= 0 ? 'positive' : 'negative');
            cells[4].textContent = formatPercentage(monthData.comparison.income_change_pct);
            cells[4].className = 'text-right month-income-change-pct ' + (monthData.comparison.income_change_pct >= 0 ? 'positive' : 'negative');
        }
    }

    // Expenses row
    if (rows[1]) {
        const cells = rows[1].querySelectorAll('td');
        if (cells.length >= 5) {
            cells[1].textContent = formatCurrency(monthData.summary.total_expenses);
            cells[1].className = 'text-right month-expenses';
            const prevExpenses = monthData.summary.total_expenses - monthData.comparison.expense_change;
            cells[2].textContent = formatCurrency(prevExpenses);
            cells[3].textContent = formatCurrency(monthData.comparison.expense_change);
            cells[3].className = 'text-right month-expense-change ' + (monthData.comparison.expense_change <= 0 ? 'positive' : 'negative');
            cells[4].textContent = formatPercentage(monthData.comparison.expense_change_pct);
            cells[4].className = 'text-right month-expense-change-pct ' + (monthData.comparison.expense_change_pct <= 0 ? 'positive' : 'negative');
        }
    }

    // Net row
    if (rows[2]) {
        const cells = rows[2].querySelectorAll('td');
        if (cells.length >= 5) {
            cells[1].textContent = formatCurrency(monthData.summary.net);
            cells[1].className = 'text-right month-net ' + (monthData.summary.net >= 0 ? 'positive' : 'negative');
            const prevNet = monthData.summary.net - monthData.comparison.net_change;
            cells[2].textContent = formatCurrency(prevNet);
            cells[2].className = 'text-right ' + (prevNet >= 0 ? 'positive' : 'negative');
            cells[3].textContent = formatCurrency(monthData.comparison.net_change);
            cells[3].className = 'text-right month-net-change ' + (monthData.comparison.net_change >= 0 ? 'positive' : 'negative');
            cells[4].textContent = formatPercentage(monthData.comparison.net_change_pct);
            cells[4].className = 'text-right month-net-change-pct ' + (monthData.comparison.net_change_pct >= 0 ? 'positive' : 'negative');
        }
    }
}

// Helper function to escape HTML (if not already defined)
function escapeHtmlForTable(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Update category breakdown table
function updateCategoryBreakdown(monthData) {
    const tbody = document.querySelector('.category-breakdown-table tbody');
    if (!tbody) return;

    // Clear existing rows
    tbody.innerHTML = '';

    // Sort categories by total amount
    const categories = Object.entries(monthData.breakdown || {})
        .sort((a, b) => Math.abs(b[1].total || 0) - Math.abs(a[1].total || 0));

    categories.forEach(([cat, data]) => {
        const row = document.createElement('tr');
        const urlCat = encodeURIComponent(cat);
        row.innerHTML = `
            <td><a href="category_trends.html?category=${urlCat}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cat)}</a></td>
            <td class="text-right">${formatCurrency(data.total || 0)}</td>
            <td class="text-center">${data.count || 0}</td>
        `;
        tbody.appendChild(row);

        // Add tag breakdown if present
        if (data.tags) {
            const tagEntries = Object.entries(data.tags)
                .sort((a, b) => Math.abs(b[1].total || 0) - Math.abs(a[1].total || 0));

            tagEntries.forEach(([tag, tagData]) => {
                const tagRow = document.createElement('tr');
                tagRow.style.backgroundColor = '#f8f9fa';
                const urlTag = encodeURIComponent(tag);
                tagRow.innerHTML = `
                    <td style="padding-left: 2rem;">└─ <a href="category_trends.html?category=${urlCat}&tag=${urlTag}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(tag)}</a></td>
                    <td class="text-right">${formatCurrency(tagData.total || 0)}</td>
                    <td class="text-center">${tagData.count || 0}</td>
                `;
                tbody.appendChild(tagRow);
            });
        }
    });
}

// Update counterparty table
function updateCounterpartyTable(monthData) {
    const tbody = document.querySelector('.counterparty-breakdown-table tbody');
    if (!tbody) return;

    // Clear existing rows
    tbody.innerHTML = '';

    // Get top 10 counterparties
    const counterparties = (monthData.counterparties || []).slice(0, 10);

    counterparties.forEach(cp => {
        const row = document.createElement('tr');
        const urlName = encodeURIComponent(cp.name);
        row.innerHTML = `
            <td><a href="counterparty_trends.html?counterparty=${urlName}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cp.name)}</a></td>
            <td class="text-center">${cp.count}</td>
            <td class="text-right">${formatCurrency(cp.total)}</td>
        `;
        tbody.appendChild(row);
    });
}

// Format numbers with thousand separators
function formatNumbers() {
    document.querySelectorAll('.format-number').forEach(el => {
        const num = parseFloat(el.textContent);
        if (!isNaN(num)) {
            el.textContent = formatCurrency(num);
        }
    });
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Format percentage
function formatPercentage(value) {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
}

// Get data from embedded JSON
function getDashboardData() {
    const scriptTag = document.getElementById('dashboard-data');
    if (scriptTag) {
        return JSON.parse(scriptTag.textContent);
    }
    return null;
}

// Chart helper functions
function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    };

    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    };

    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

function createPieChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'right',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = formatCurrency(context.parsed);
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((context.parsed / total) * 100).toFixed(1);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };

    return new Chart(ctx, {
        type: 'pie',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

function createDoughnutChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'right',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = formatCurrency(context.parsed);
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((context.parsed / total) * 100).toFixed(1);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };

    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

// Data transformation helpers
function prepareMonthlyTrendData(monthlyData) {
    const labels = Object.keys(monthlyData).sort();
    const income = labels.map(m => monthlyData[m].total_income || 0);
    const expenses = labels.map(m => monthlyData[m].total_expenses || 0);
    const net = labels.map(m => monthlyData[m].net || 0);

    return {
        labels: labels,
        datasets: [
            {
                label: 'Income',
                data: income,
                borderColor: 'rgb(39, 174, 96)',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                tension: 0.1
            },
            {
                label: 'Expenses',
                data: expenses,
                borderColor: 'rgb(231, 76, 60)',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.1
            },
            {
                label: 'Net',
                data: net,
                borderColor: 'rgb(52, 152, 219)',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.1
            }
        ]
    };
}

function prepareCategoryData(breakdown) {
    const categories = Object.keys(breakdown);
    const totals = categories.map(cat => Math.abs(breakdown[cat].total || 0));

    return {
        labels: categories,
        datasets: [{
            data: totals,
            backgroundColor: generateColors(categories.length)
        }]
    };
}

function generateColors(count) {
    const colors = [
        'rgb(52, 152, 219)', 'rgb(231, 76, 60)', 'rgb(39, 174, 96)',
        'rgb(241, 196, 15)', 'rgb(155, 89, 182)', 'rgb(230, 126, 34)',
        'rgb(26, 188, 156)', 'rgb(149, 165, 166)', 'rgb(46, 204, 113)',
        'rgb(231, 76, 60)', 'rgb(52, 73, 94)', 'rgb(127, 140, 141)'
    ];

    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

// Searchable Select functionality
function initializeSearchableSelect(inputId, hiddenSelectId, dropdownId, options, onSelect) {
    const input = document.getElementById(inputId);
    const hiddenSelect = document.getElementById(hiddenSelectId);
    const dropdown = document.getElementById(dropdownId);

    if (!input || !hiddenSelect || !dropdown) return;

    let selectedValue = '';
    let selectedText = '';

    // Get all options from hidden select
    const allOptions = Array.from(hiddenSelect.options).map(opt => ({
        value: opt.value,
        text: opt.textContent
    })).filter(opt => opt.value !== ''); // Filter out empty option

    function filterOptions(searchTerm) {
        if (!searchTerm) {
            return allOptions;
        }
        const lowerSearch = searchTerm.toLowerCase();
        return allOptions.filter(opt =>
            opt.text.toLowerCase().includes(lowerSearch) ||
            opt.value.toLowerCase().includes(lowerSearch)
        );
    }

    function renderDropdown(optionsToShow) {
        dropdown.innerHTML = '';

        if (optionsToShow.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'searchable-select-option no-results';
            noResults.textContent = 'No results found';
            dropdown.appendChild(noResults);
        } else {
            optionsToShow.forEach(opt => {
                const optionDiv = document.createElement('div');
                optionDiv.className = 'searchable-select-option';
                optionDiv.textContent = opt.text;
                optionDiv.dataset.value = opt.value;

                if (opt.value === selectedValue) {
                    optionDiv.classList.add('selected');
                }

                optionDiv.addEventListener('click', function() {
                    selectedValue = opt.value;
                    selectedText = opt.text;
                    input.value = opt.text;
                    dropdown.classList.remove('show');
                    hiddenSelect.value = opt.value;
                    if (onSelect) {
                        onSelect(opt.value, opt.text);
                    }
                });

                dropdown.appendChild(optionDiv);
            });
        }
    }

    // Input focus handler
    input.addEventListener('focus', function() {
        const filtered = filterOptions(input.value);
        renderDropdown(filtered);
        dropdown.classList.add('show');
    });

    // Input input handler (typing)
    input.addEventListener('input', function() {
        const filtered = filterOptions(input.value);
        renderDropdown(filtered);
        dropdown.classList.add('show');
    });

    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });

    // Keyboard navigation
    let selectedIndex = -1;
    input.addEventListener('keydown', function(e) {
        const options = dropdown.querySelectorAll('.searchable-select-option:not(.no-results)');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, options.length - 1);
            if (options[selectedIndex]) {
                options[selectedIndex].scrollIntoView({ block: 'nearest' });
                options.forEach((opt, idx) => {
                    opt.classList.toggle('selected', idx === selectedIndex);
                });
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            options.forEach((opt, idx) => {
                opt.classList.toggle('selected', idx === selectedIndex);
            });
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIndex >= 0 && options[selectedIndex]) {
                options[selectedIndex].click();
            } else if (options.length === 1) {
                options[0].click();
            }
        } else if (e.key === 'Escape') {
            dropdown.classList.remove('show');
        }
    });

    // Set initial value if hidden select has one
    if (hiddenSelect.value) {
        const selectedOption = allOptions.find(opt => opt.value === hiddenSelect.value);
        if (selectedOption) {
            input.value = selectedOption.text;
            selectedValue = selectedOption.value;
            selectedText = selectedOption.text;
        }
    }

    return {
        setValue: function(value) {
            const option = allOptions.find(opt => opt.value === value);
            if (option) {
                selectedValue = option.value;
                selectedText = option.text;
                input.value = option.text;
                hiddenSelect.value = option.value;
            }
        },
        getValue: function() {
            return selectedValue;
        }
    };
}

// Multi-select functionality
function initializeMultiSelect(inputId, hiddenSelectId, dropdownId, selectedItemsContainerId, onSelectionChange) {
    const input = document.getElementById(inputId);
    const hiddenSelect = document.getElementById(hiddenSelectId);
    const dropdown = document.getElementById(dropdownId);
    const selectedContainer = document.getElementById(selectedItemsContainerId);

    if (!input || !hiddenSelect || !dropdown || !selectedContainer) return;

    let selectedItems = new Map(); // Map of value -> {value, text}

    // Get all options from hidden select
    const allOptions = Array.from(hiddenSelect.options).map(opt => ({
        value: opt.value,
        text: opt.textContent
    })).filter(opt => opt.value !== ''); // Filter out empty option

    function filterOptions(searchTerm) {
        if (!searchTerm) {
            return allOptions.filter(opt => !selectedItems.has(opt.value));
        }
        const lowerSearch = searchTerm.toLowerCase();
        return allOptions.filter(opt =>
            !selectedItems.has(opt.value) &&
            (opt.text.toLowerCase().includes(lowerSearch) ||
             opt.value.toLowerCase().includes(lowerSearch))
        );
    }

    function renderSelectedItems() {
        selectedContainer.innerHTML = '';
        selectedItems.forEach((item, value) => {
            const chip = document.createElement('div');
            chip.className = 'selected-item';
            chip.innerHTML = `
                <span>${item.text}</span>
                <span class="remove-btn" data-value="${value}">×</span>
            `;
            chip.querySelector('.remove-btn').addEventListener('click', function() {
                removeItem(value);
            });
            selectedContainer.appendChild(chip);
        });
    }

    function addItem(value, text) {
        if (!selectedItems.has(value)) {
            selectedItems.set(value, { value, text });
            renderSelectedItems();
            input.value = '';
            dropdown.classList.remove('show');
            if (onSelectionChange) {
                onSelectionChange(Array.from(selectedItems.values()));
            }
        }
    }

    function removeItem(value) {
        if (selectedItems.has(value)) {
            selectedItems.delete(value);
            renderSelectedItems();
            if (onSelectionChange) {
                onSelectionChange(Array.from(selectedItems.values()));
            }
        }
    }

    function renderDropdown(optionsToShow) {
        dropdown.innerHTML = '';

        if (optionsToShow.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'searchable-select-option no-results';
            noResults.textContent = 'No results found';
            dropdown.appendChild(noResults);
        } else {
            optionsToShow.forEach(opt => {
                const optionDiv = document.createElement('div');
                optionDiv.className = 'searchable-select-option';
                optionDiv.textContent = opt.text;
                optionDiv.dataset.value = opt.value;

                optionDiv.addEventListener('click', function() {
                    addItem(opt.value, opt.text);
                });

                dropdown.appendChild(optionDiv);
            });
        }
    }

    // Input focus handler
    input.addEventListener('focus', function() {
        const filtered = filterOptions(input.value);
        renderDropdown(filtered);
        dropdown.classList.add('show');
    });

    // Input input handler (typing)
    input.addEventListener('input', function() {
        const filtered = filterOptions(input.value);
        renderDropdown(filtered);
        dropdown.classList.add('show');
    });

    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target) && !selectedContainer.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });

    // Keyboard navigation
    let selectedIndex = -1;
    input.addEventListener('keydown', function(e) {
        const options = dropdown.querySelectorAll('.searchable-select-option:not(.no-results)');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, options.length - 1);
            if (options[selectedIndex]) {
                options[selectedIndex].scrollIntoView({ block: 'nearest' });
                options.forEach((opt, idx) => {
                    opt.classList.toggle('selected', idx === selectedIndex);
                });
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            options.forEach((opt, idx) => {
                opt.classList.toggle('selected', idx === selectedIndex);
            });
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIndex >= 0 && options[selectedIndex]) {
                options[selectedIndex].click();
            } else if (options.length === 1) {
                options[0].click();
            }
        } else if (e.key === 'Escape') {
            dropdown.classList.remove('show');
        }
    });

    return {
        getSelectedItems: function() {
            return Array.from(selectedItems.values());
        },
        setSelectedItems: function(items) {
            selectedItems.clear();
            items.forEach(item => {
                selectedItems.set(item.value, item);
            });
            renderSelectedItems();
        },
        clear: function() {
            selectedItems.clear();
            renderSelectedItems();
            if (onSelectionChange) {
                onSelectionChange([]);
            }
        }
    };
}

// Category Trends functionality
let categoryTrendChart = null;
let categoryMultiSelect = null;

function initializeCategoryTrends() {
    const data = getDashboardData();
    if (!data) return;

    // Populate year selector
    const yearSelector = document.getElementById('year-selector');
    if (yearSelector && data.available_months) {
        const years = new Set();
        data.available_months.forEach(month => {
            const year = month.split('-')[0];
            years.add(year);
        });
        Array.from(years).sort().reverse().forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelector.appendChild(option);
        });
    }

    // Initialize multi-select category selector
    categoryMultiSelect = initializeMultiSelect(
        'category-selector',
        'category-selector-hidden',
        'category-selector-dropdown',
        'category-selected-items',
        function(selectedItems) {
            updateCategoryTrendChart(data);
        }
    );

    // Year selector change handler
    if (yearSelector) {
        yearSelector.addEventListener('change', function() {
            updateCategoryTrendChart(data);
            // Also update transactions table
            const selectedCategories = categoryMultiSelect ? categoryMultiSelect.getSelectedItems() : [];
            updateCategoryTransactionsTable(data, selectedCategories, yearSelector.value, null);
        });
    }

    // Group by selector change handler
    const groupBySelector = document.getElementById('group-by-selector');
    if (groupBySelector) {
        groupBySelector.addEventListener('change', function() {
            updateCategoryTrendChart(data);
        });
    }

    // Date range filter handlers
    const dateStartInput = document.getElementById('date-start');
    const dateEndInput = document.getElementById('date-end');
    if (dateStartInput) {
        dateStartInput.addEventListener('change', function() {
            updateCategoryTrendChart(data);
        });
    }
    if (dateEndInput) {
        dateEndInput.addEventListener('change', function() {
            updateCategoryTrendChart(data);
        });
    }

    // Amount range filter handlers
    const amountMinInput = document.getElementById('amount-min');
    const amountMaxInput = document.getElementById('amount-max');
    if (amountMinInput) {
        amountMinInput.addEventListener('input', function() {
            updateCategoryTrendChart(data);
        });
    }
    if (amountMaxInput) {
        amountMaxInput.addEventListener('input', function() {
            updateCategoryTrendChart(data);
        });
    }

    // Cumulative totals toggle
    const cumulativeToggle = document.getElementById('cumulative-toggle');
    if (cumulativeToggle) {
        cumulativeToggle.addEventListener('change', function() {
            updateCategoryTrendChart(data);
        });
    }

    // Check URL parameters for pre-selection
    const urlParams = new URLSearchParams(window.location.search);
    const categoryParam = urlParams.get('category');
    const tagParam = urlParams.get('tag');
    const yearParam = urlParams.get('year');

    // Set year selector from URL parameter, default to "all" if not specified
    if (yearSelector) {
        const yearValue = yearParam || 'all';
        const yearOptions = Array.from(yearSelector.options);
        const yearOption = yearOptions.find(opt => opt.value === yearValue);
        if (yearOption) {
            yearSelector.value = yearValue;
        }
    }

    if (categoryParam && categoryMultiSelect) {
        // Decode URL parameter
        const decodedCategory = decodeURIComponent(categoryParam);
        let value = decodedCategory;
        let displayText = decodedCategory;

        // If tag is provided, combine them as category:tag
        if (tagParam) {
            const decodedTag = decodeURIComponent(tagParam);
            value = `${decodedCategory}:${decodedTag}`;
            displayText = `${decodedCategory}: ${decodedTag}`;
        }

        categoryMultiSelect.setSelectedItems([{ value: value, text: displayText }]);
        updateCategoryTrendChart(data);
    }
}

function updateCategoryTrendChart(data) {
    const selectedCategories = categoryMultiSelect ? categoryMultiSelect.getSelectedItems() : [];
    const yearSelector = document.getElementById('year-selector');
    const groupBySelector = document.getElementById('group-by-selector');

    if (!selectedCategories || selectedCategories.length === 0 || !data.all_months) {
        // Clear chart if no categories selected
        if (categoryTrendChart) {
            categoryTrendChart.destroy();
            categoryTrendChart = null;
        }
        updateTrendSummary(0, 0, 0, 'month');
        return;
    }

    const year = yearSelector ? yearSelector.value : 'all';
    const groupBy = groupBySelector ? groupBySelector.value : 'month';

    // Get date and amount filters
    const dateStartInput = document.getElementById('date-start');
    const dateEndInput = document.getElementById('date-end');
    const amountMinInput = document.getElementById('amount-min');
    const amountMaxInput = document.getElementById('amount-max');

    const startDate = dateStartInput && dateStartInput.value ? dateStartInput.value : null;
    const endDate = dateEndInput && dateEndInput.value ? dateEndInput.value : null;
    const minAmount = amountMinInput && amountMinInput.value ? parseFloat(amountMinInput.value) : null;
    const maxAmount = amountMaxInput && amountMaxInput.value ? parseFloat(amountMaxInput.value) : null;

    // Filter transactions if filters are applied
    let filteredTransactions = data.all_transactions || [];
    let filteredMonths = data.all_months;

    if (startDate || endDate || minAmount !== null || maxAmount !== null) {
        filteredTransactions = filteredTransactions.filter(tx => {
            // Date filter
            if (startDate && tx.date && tx.date < startDate) return false;
            if (endDate && tx.date && tx.date > endDate) return false;

            // Amount filter
            const amount = tx.amount || 0;
            if (minAmount !== null && amount < minAmount) return false;
            if (maxAmount !== null && amount > maxAmount) return false;

            return true;
        });

        // Recalculate monthly breakdowns from filtered transactions
        filteredMonths = recalculateMonthlyBreakdowns(filteredTransactions);
        data = { ...data, all_transactions: filteredTransactions, all_months: filteredMonths };
    }

    // Parse each selected item - could be "category" or "category:tag"
    const allTrendData = selectedCategories.map(item => {
        let category, tag, displayText;

        if (item.value.includes(':')) {
            // Format: "category:tag"
            const parts = item.value.split(':', 2);
            category = parts[0];
            tag = parts[1];
            displayText = item.text || item.value;
        } else {
            // Format: "category" (no tag)
            category = item.value;
            tag = null;
            displayText = item.text || item.value;
        }

        return {
            category: category,
            tag: tag,
            displayText: displayText,
            data: extractCategoryTrendData(filteredMonths, category, tag, year, groupBy)
        };
    });

    // Get common labels (all should have the same labels after grouping)
    const labels = allTrendData.length > 0 ? allTrendData[0].data.labels : [];

    // Create or update chart
    const ctx = document.getElementById('categoryTrendChart');
    if (!ctx) return;

    if (categoryTrendChart) {
        categoryTrendChart.destroy();
    }

    // Generate distinct colors for each category
    const colors = generateDistinctColors(selectedCategories.length);
    const datasets = [];
    let totalTotal = 0;
    let totalCount = 0;

    allTrendData.forEach((trendInfo, index) => {
        const displayText = trendInfo.displayText;
        const trendData = trendInfo.data;
        const color = colors[index];

        totalTotal += trendData.total;
        totalCount += trendData.count;

        // Convert to absolute values and split into expenses and income
        const expenseData = trendData.values.map(val => val < 0 ? Math.abs(val) : null);
        const incomeData = trendData.values.map(val => val >= 0 ? Math.abs(val) : null);

        // Check if there are any non-null values for each type
        const hasIncome = incomeData.some(val => val !== null && val > 0);
        const hasExpense = expenseData.some(val => val !== null && val > 0);

        // Add income dataset only if there are income values
        if (hasIncome) {
            datasets.push({
                label: `${displayText} (Income)`,
                data: incomeData,
                borderColor: color,
                backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                tension: 0.1,
                fill: false,
                spanGaps: true
            });
        }

        // Add expense dataset only if there are expense values
        if (hasExpense) {
            datasets.push({
                label: `${displayText} (Expense)`,
                data: expenseData,
                borderColor: color,
                backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                tension: 0.1,
                fill: false,
                spanGaps: true
            });
        }
    });

    // Check cumulative toggle before creating chart
    const cumulativeToggle = document.getElementById('cumulative-toggle');
    const isCumulative = cumulativeToggle ? cumulativeToggle.checked : false;

    // Apply cumulative transformation if enabled
    if (isCumulative) {
        datasets.forEach(dataset => {
            let runningTotal = 0;
            dataset.data = dataset.data.map(val => {
                if (val === null) return null;
                runningTotal += val;
                return runningTotal;
            });
        });
    }

    categoryTrendChart = createZoomableLineChart(ctx, {
        labels: labels,
        datasets: datasets
    });

    // Update summary with combined totals
    updateTrendSummary(totalTotal, totalCount, labels.length, groupBy);

    // Build monthlyData for projections (combine all selected categories)
    const monthlyData = [];
    labels.forEach((label, index) => {
        let periodTotal = 0;
        allTrendData.forEach(trendInfo => {
            const trendData = trendInfo.data;
            if (trendData.values && trendData.values[index] !== undefined) {
                periodTotal += trendData.values[index] || 0;
            }
        });
        monthlyData.push({
            period: label,
            total: periodTotal
        });
    });

    // Update projections
    const currentYear = data.current_year || new Date().getFullYear();
    updateCategoryProjections(monthlyData, groupBy, currentYear);

    // Update transactions table (with filtered data)
    updateCategoryTransactionsTable(data, selectedCategories, year, filteredTransactions);
}

// Generate distinct colors for multiple datasets
function generateDistinctColors(count) {
    const baseColors = [
        'rgb(52, 152, 219)',   // Blue
        'rgb(231, 76, 60)',     // Red
        'rgb(39, 174, 96)',     // Green
        'rgb(241, 196, 15)',    // Yellow
        'rgb(155, 89, 182)',    // Purple
        'rgb(230, 126, 34)',    // Orange
        'rgb(46, 204, 113)',    // Emerald
        'rgb(26, 188, 156)',    // Turquoise
        'rgb(52, 73, 94)',      // Dark blue-gray
        'rgb(149, 165, 166)'    // Gray
    ];

    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
}

// Helper function to recalculate monthly breakdowns from filtered transactions
function recalculateMonthlyBreakdowns(transactions) {
    const monthlyData = {};

    transactions.forEach(tx => {
        if (!tx.date) return;

        const month = tx.date.substring(0, 7); // YYYY-MM format
        if (!monthlyData[month]) {
            monthlyData[month] = {
                breakdown: {}
            };
        }

        const category = (tx.category || '').trim() || 'Unknown';
        if (!monthlyData[month].breakdown[category]) {
            monthlyData[month].breakdown[category] = {
                total: 0,
                count: 0,
                tags: {}
            };
        }

        const amount = tx.amount || 0;
        monthlyData[month].breakdown[category].total += amount;
        monthlyData[month].breakdown[category].count += 1;

        // Handle tags if present
        if (tx.tag) {
            const tag = tx.tag.trim();
            if (!monthlyData[month].breakdown[category].tags[tag]) {
                monthlyData[month].breakdown[category].tags[tag] = {
                    total: 0,
                    count: 0
                };
            }
            monthlyData[month].breakdown[category].tags[tag].total += amount;
            monthlyData[month].breakdown[category].tags[tag].count += 1;
        }
    });

    return monthlyData;
}

function extractCategoryTrendData(allMonths, category, tag, year, groupBy = 'month') {
    // Filter months by year if specified
    let monthsToProcess = Object.keys(allMonths).sort();
    if (year !== 'all') {
        monthsToProcess = monthsToProcess.filter(m => m.startsWith(year));
    }

    // Extract raw monthly data
    const monthlyData = [];
    monthsToProcess.forEach(month => {
        const monthData = allMonths[month];
        if (!monthData || !monthData.breakdown) {
            monthlyData.push({ month, total: 0, count: 0 });
            return;
        }

        const breakdown = monthData.breakdown[category];
        if (!breakdown) {
            monthlyData.push({ month, total: 0, count: 0 });
            return;
        }

        let monthTotal = 0;
        let monthCount = 0;

        if (tag) {
            // Looking for specific tag
            if (breakdown.tags && breakdown.tags[tag]) {
                monthTotal = breakdown.tags[tag].total || 0;
                monthCount = breakdown.tags[tag].count || 0;
            }
        } else {
            // All tags or base category
            monthTotal = breakdown.total || 0;
            monthCount = breakdown.count || 0;
        }

        monthlyData.push({ month, total: monthTotal, count: monthCount });
    });

    // Group data based on groupBy parameter
    return groupTrendData(monthlyData, groupBy);
}

function groupTrendData(monthlyData, groupBy) {
    const grouped = {};
    let total = 0;
    let count = 0;

    monthlyData.forEach(({ month, total: monthTotal, count: monthCount }) => {
        let groupKey;

        if (groupBy === 'quarter') {
            const [year, monthNum] = month.split('-');
            const quarter = Math.floor((parseInt(monthNum) - 1) / 3) + 1;
            groupKey = `${year}-Q${quarter}`;
        } else if (groupBy === 'year') {
            groupKey = month.split('-')[0];
        } else {
            // month
            groupKey = month;
        }

        if (!grouped[groupKey]) {
            grouped[groupKey] = { total: 0, count: 0 };
        }

        grouped[groupKey].total += monthTotal;
        grouped[groupKey].count += monthCount;
        total += monthTotal;
        count += monthCount;
    });

    // Convert to arrays sorted by key
    const labels = Object.keys(grouped).sort();
    const values = labels.map(key => grouped[key].total);

    return { labels, values, total, count };
}

// Counterparty Trends functionality
let counterpartyTrendChart = null;
let counterpartyMultiSelect = null;

function initializeCounterpartyTrends() {
    const data = getDashboardData();
    if (!data) return;

    // Populate year selector
    const yearSelector = document.getElementById('year-selector');
    if (yearSelector && data.available_months) {
        const years = new Set();
        data.available_months.forEach(month => {
            const year = month.split('-')[0];
            years.add(year);
        });
        Array.from(years).sort().reverse().forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelector.appendChild(option);
        });
    }

    // Initialize multi-select counterparty selector
    counterpartyMultiSelect = initializeMultiSelect(
        'counterparty-selector',
        'counterparty-selector-hidden',
        'counterparty-selector-dropdown',
        'counterparty-selected-items',
        function(selectedItems) {
            updateCounterpartyTrendChart(data);
        }
    );

    // Year selector change handler
    if (yearSelector) {
        yearSelector.addEventListener('change', function() {
            updateCounterpartyTrendChart(data);
            // Also update transactions table
            const selectedCounterparties = counterpartyMultiSelect ? counterpartyMultiSelect.getSelectedItems() : [];
            updateCounterpartyTransactionsTable(data, selectedCounterparties, yearSelector.value, null);
        });
    }

    // Group by selector change handler
    const groupBySelector = document.getElementById('group-by-selector');
    if (groupBySelector) {
        groupBySelector.addEventListener('change', function() {
            updateCounterpartyTrendChart(data);
        });
    }

    // Date range filter handlers
    const dateStartInput = document.getElementById('date-start');
    const dateEndInput = document.getElementById('date-end');
    if (dateStartInput) {
        dateStartInput.addEventListener('change', function() {
            updateCounterpartyTrendChart(data);
        });
    }
    if (dateEndInput) {
        dateEndInput.addEventListener('change', function() {
            updateCounterpartyTrendChart(data);
        });
    }

    // Amount range filter handlers
    const amountMinInput = document.getElementById('amount-min');
    const amountMaxInput = document.getElementById('amount-max');
    if (amountMinInput) {
        amountMinInput.addEventListener('input', function() {
            updateCounterpartyTrendChart(data);
        });
    }
    if (amountMaxInput) {
        amountMaxInput.addEventListener('input', function() {
            updateCounterpartyTrendChart(data);
        });
    }

    // Cumulative totals toggle
    const cumulativeToggle = document.getElementById('cumulative-toggle');
    if (cumulativeToggle) {
        cumulativeToggle.addEventListener('change', function() {
            updateCounterpartyTrendChart(data);
        });
    }

    // Check URL parameters for pre-selection
    const urlParams = new URLSearchParams(window.location.search);
    const counterpartyParam = urlParams.get('counterparty');
    const yearParam = urlParams.get('year');

    // Set year selector from URL parameter, default to "all" if not specified
    if (yearSelector) {
        const yearValue = yearParam || 'all';
        const yearOptions = Array.from(yearSelector.options);
        const yearOption = yearOptions.find(opt => opt.value === yearValue);
        if (yearOption) {
            yearSelector.value = yearValue;
        }
    }

    if (counterpartyParam && counterpartyMultiSelect) {
        // Decode URL parameter
        const decodedCounterparty = decodeURIComponent(counterpartyParam);
        counterpartyMultiSelect.setSelectedItems([{ value: decodedCounterparty, text: decodedCounterparty }]);
        updateCounterpartyTrendChart(data);
    }
}

function updateCounterpartyTrendChart(data) {
    const selectedCounterparties = counterpartyMultiSelect ? counterpartyMultiSelect.getSelectedItems() : [];
    const yearSelector = document.getElementById('year-selector');
    const groupBySelector = document.getElementById('group-by-selector');

    const year = yearSelector ? yearSelector.value : 'all';

    if (!selectedCounterparties || selectedCounterparties.length === 0 || !data.all_months) {
        // Clear chart if no counterparties selected
        if (counterpartyTrendChart) {
            counterpartyTrendChart.destroy();
            counterpartyTrendChart = null;
        }
        updateTrendSummary(0, 0, 0, 'month');
        // Clear transactions table
        updateCounterpartyTransactionsTable(data, [], year, null);
        return;
    }
    const groupBy = groupBySelector ? groupBySelector.value : 'month';

    // Get date and amount filters
    const dateStartInput = document.getElementById('date-start');
    const dateEndInput = document.getElementById('date-end');
    const amountMinInput = document.getElementById('amount-min');
    const amountMaxInput = document.getElementById('amount-max');

    const startDate = dateStartInput && dateStartInput.value ? dateStartInput.value : null;
    const endDate = dateEndInput && dateEndInput.value ? dateEndInput.value : null;
    const minAmount = amountMinInput && amountMinInput.value ? parseFloat(amountMinInput.value) : null;
    const maxAmount = amountMaxInput && amountMaxInput.value ? parseFloat(amountMaxInput.value) : null;

    // Filter transactions if filters are applied
    let filteredTransactions = data.all_transactions || [];
    if (startDate || endDate || minAmount !== null || maxAmount !== null) {
        filteredTransactions = filteredTransactions.filter(tx => {
            // Date filter
            if (startDate && tx.date && tx.date < startDate) return false;
            if (endDate && tx.date && tx.date > endDate) return false;

            // Amount filter
            const amount = tx.amount || 0;
            if (minAmount !== null && amount < minAmount) return false;
            if (maxAmount !== null && amount > maxAmount) return false;

            return true;
        });

        // Pass filtered transactions to extraction function
        data = { ...data, all_transactions: filteredTransactions };
    }

    // Extract trend data for each selected counterparty
    const allTrendData = selectedCounterparties.map(cp => ({
        counterparty: cp.value,
        counterpartyText: cp.text,
        data: extractCounterpartyTrendData(data.all_months, data.all_transactions, cp.value, year, groupBy)
    }));

    // Get common labels (all should have the same labels after grouping)
    const labels = allTrendData.length > 0 ? allTrendData[0].data.labels : [];

    // Create or update chart
    const ctx = document.getElementById('counterpartyTrendChart');
    if (!ctx) return;

    if (counterpartyTrendChart) {
        counterpartyTrendChart.destroy();
    }

    // Generate distinct colors for each counterparty
    const colors = generateDistinctColors(selectedCounterparties.length);
    const datasets = [];
    let totalTotal = 0;
    let totalCount = 0;

    allTrendData.forEach((trendInfo, index) => {
        const counterparty = trendInfo.counterparty;
        const counterpartyText = trendInfo.counterpartyText;
        const trendData = trendInfo.data;
        const color = colors[index];

        totalTotal += trendData.total;
        totalCount += trendData.count;

        // Convert to absolute values and split into expenses and income
        const expenseData = trendData.values.map(val => val < 0 ? Math.abs(val) : null);
        const incomeData = trendData.values.map(val => val >= 0 ? Math.abs(val) : null);

        // Check if there are any non-null values for each type
        const hasIncome = incomeData.some(val => val !== null && val > 0);
        const hasExpense = expenseData.some(val => val !== null && val > 0);

        // Add income dataset only if there are income values
        if (hasIncome) {
            datasets.push({
                label: `${counterpartyText} (Income)`,
                data: incomeData,
                borderColor: color,
                backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                tension: 0.1,
                fill: false,
                spanGaps: true
            });
        }

        // Add expense dataset only if there are expense values
        if (hasExpense) {
            datasets.push({
                label: `${counterpartyText} (Expense)`,
                data: expenseData,
                borderColor: color,
                backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                tension: 0.1,
                fill: false,
                spanGaps: true
            });
        }
    });

    // Check cumulative toggle before creating chart
    const cumulativeToggle = document.getElementById('cumulative-toggle');
    const isCumulative = cumulativeToggle ? cumulativeToggle.checked : false;

    // Apply cumulative transformation if enabled
    if (isCumulative) {
        datasets.forEach(dataset => {
            let runningTotal = 0;
            dataset.data = dataset.data.map(val => {
                if (val === null) return null;
                runningTotal += val;
                return runningTotal;
            });
        });
    }

    counterpartyTrendChart = createZoomableLineChart(ctx, {
        labels: labels,
        datasets: datasets
    });

    // Update summary with combined totals
    updateTrendSummary(totalTotal, totalCount, labels.length, groupBy);

    // Build monthlyData for projections (combine all selected counterparties)
    const monthlyData = [];
    labels.forEach((label, index) => {
        let periodTotal = 0;
        allTrendData.forEach(trendInfo => {
            const trendData = trendInfo.data;
            if (trendData.values && trendData.values[index] !== undefined) {
                periodTotal += trendData.values[index] || 0;
            }
        });
        monthlyData.push({
            period: label,
            total: periodTotal
        });
    });

    // Update projections
    const currentYear = data.current_year || new Date().getFullYear();
    updateCounterpartyProjections(monthlyData, groupBy, currentYear);

    // Update transactions table (with filtered data)
    updateCounterpartyTransactionsTable(data, selectedCounterparties, year, filteredTransactions);
}

function extractCounterpartyTrendData(allMonths, allTransactions, counterpartyName, year, groupBy = 'month') {
    // Normalize counterparty name for matching - same logic as Python get_counterparty_breakdowns
    function normalizeCounterpartyName(name) {
        if (!name) return '';
        let normalized = name.toLowerCase();

        // Unicode normalization (remove accents)
        normalized = normalized.normalize('NFD').replace(/[\u0300-\u036f]/g, '');

        // Normalize company suffixes - handle "d. d." with space
        normalized = normalized.replace(/\bd\.\s*d\.\b/g, 'd.d.');
        normalized = normalized.replace(/\bss\s+d\.o\.o\./g, 'ss d.o.o.');
        normalized = normalized.replace(/\bss\s+d\.o\.o\b/g, 'ss d.o.o.');
        normalized = normalized.replace(/,\s*(d\.o\.o\.?|d\.d\.?|s\.p\.?|z\.b\.o\.?)/g, ' $1');
        // Normalize legal suffixes - ensure consistent format with trailing period
        normalized = normalized.replace(/\bd\.o\.o\.?\b/g, 'd.o.o.');
        normalized = normalized.replace(/\bd\.d\.\.?\b/g, 'd.d.');
        normalized = normalized.replace(/\bs\.p\.\.?\b/g, 's.p.');
        // Fix z.b.o. normalization - handle both with and without trailing period
        normalized = normalized.replace(/\bz\.b\.o\.?\b/g, 'z.b.o.');

        // Clean up multiple dots and spaces
        normalized = normalized.replace(/\.{2,}/g, '.');
        normalized = normalized.replace(/\s+/g, ' ').trim();

        // Special entity aliases - normalize known variations to canonical form
        // CTRP and IN-FIT are the same entity
        if (normalized.includes('ctrp') || normalized.includes('in-fit') || normalized.includes('infit')) {
            normalized = normalized.replace(/.*(ctrp|in-fit|infit).*/, 'in-fit d.o.o.');
        }

        return normalized;
    }

    const normalizedSearch = normalizeCounterpartyName(counterpartyName);

    // Filter transactions directly from all_transactions instead of relying on monthly breakdowns
    // This ensures we match the same transactions that were counted in the YTD breakdown
    let filteredTransactions = [];
    if (allTransactions && Array.isArray(allTransactions)) {
        filteredTransactions = allTransactions.filter(tx => {
            // Filter by year if specified
            if (year !== 'all' && tx.date && !tx.date.startsWith(year)) {
                return false;
            }
            // Check if transaction counterparty matches (using normalization)
            const txCounterparty = normalizeCounterpartyName(tx.counterparty || '');
            return txCounterparty === normalizedSearch;
        });
    }

    // If we don't have all_transactions, fall back to monthly breakdowns
    if (filteredTransactions.length === 0 && allMonths) {
        // Filter months by year if specified
        let monthsToProcess = Object.keys(allMonths).sort();
        if (year !== 'all') {
            monthsToProcess = monthsToProcess.filter(m => m.startsWith(year));
        }

        // Extract raw monthly data from monthly breakdowns
        const monthlyData = [];
        monthsToProcess.forEach(month => {
            const monthData = allMonths[month];
            if (!monthData || !monthData.counterparties) {
                monthlyData.push({ month, total: 0, count: 0 });
                return;
            }

            // Find matching counterparty - match against normalized names
            const matchingCp = monthData.counterparties.find(cp => {
                const normalizedCp = normalizeCounterpartyName(cp.name);
                return normalizedCp === normalizedSearch;
            });

            const monthTotal = matchingCp ? matchingCp.total : 0;
            const monthCount = matchingCp ? matchingCp.count : 0;

            monthlyData.push({ month, total: monthTotal, count: monthCount });
        });

        // Group data based on groupBy parameter
        return groupTrendData(monthlyData, groupBy);
    }

    // Group filtered transactions by month
    const monthlyDataMap = {};
    filteredTransactions.forEach(tx => {
        if (!tx.date) return;
        const month = tx.date.substring(0, 7); // YYYY-MM
        if (!monthlyDataMap[month]) {
            monthlyDataMap[month] = { total: 0, count: 0 };
        }
        monthlyDataMap[month].total += tx.amount || 0;
        monthlyDataMap[month].count += 1;
    });

    // Convert to array format
    const monthlyData = [];
    const monthsToProcess = Object.keys(allMonths || {}).sort();
    monthsToProcess.forEach(month => {
        if (year !== 'all' && !month.startsWith(year)) {
            return;
        }
        const data = monthlyDataMap[month] || { total: 0, count: 0 };
        monthlyData.push({ month, total: data.total, count: data.count });
    });

    // Group data based on groupBy parameter
    return groupTrendData(monthlyData, groupBy);
}

// Create zoomable line chart
function createZoomableLineChart(ctx, data, options = {}) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            },
            zoom: {
                zoom: {
                    wheel: {
                        enabled: false,
                    },
                    pinch: {
                        enabled: true
                    },
                    mode: 'x',
                },
                pan: {
                    enabled: true,
                    mode: 'x',
                }
            }
        },
        scales: {
            x: {
                display: true,
            },
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    };

    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

// Update trend summary
function updateTrendSummary(total, count, periodCount, groupBy = 'month') {
    const totalEl = document.getElementById('trend-total');
    const countEl = document.getElementById('trend-count');
    const avgEl = document.getElementById('trend-avg');
    const avgLabelEl = document.getElementById('trend-avg-label');

    if (totalEl) {
        totalEl.textContent = formatCurrency(total);
        totalEl.className = 'metric-value ' + (total >= 0 ? 'positive' : 'negative');
    }
    if (countEl) {
        countEl.textContent = count;
    }
    if (avgEl && periodCount > 0) {
        const avg = total / periodCount;
        avgEl.textContent = formatCurrency(avg);
        avgEl.className = 'metric-value ' + (avg >= 0 ? 'positive' : 'negative');
    }
    if (avgLabelEl) {
        let labelText = 'Average per Month';
        if (groupBy === 'quarter') {
            labelText = 'Average per Quarter';
        } else if (groupBy === 'year') {
            labelText = 'Average per Year';
        }
        avgLabelEl.textContent = labelText;
    }
}

// Transaction table functionality
let categoryTableSortState = { column: 'date', direction: 'desc' };
let counterpartyTableSortState = { column: 'date', direction: 'desc' };
let counterpartiesTableSortState = { column: 'total', direction: 'desc' }; // For counterparties.html page

function updateCategoryTransactionsTable(data, selectedCategories, year, preFilteredTransactions = null) {
    const tbody = document.getElementById('category-transactions-tbody');
    const transactionsToUse = preFilteredTransactions || data.all_transactions;
    if (!tbody || !transactionsToUse) return;

    if (!selectedCategories || selectedCategories.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #7f8c8d;">Select categories or subcategories to view transactions</td></tr>';
        return;
    }

    // Filter transactions based on selected categories and year
    let filteredTransactions = transactionsToUse.filter(tx => {
        // Filter by year if specified
        if (year !== 'all' && tx.date && !tx.date.startsWith(year)) {
            return false;
        }

        // Check if transaction matches any selected category
        const txCategory = tx.category || '';
        return selectedCategories.some(selected => {
            if (selected.value.includes(':')) {
                // Selected is a category:tag combination
                return txCategory === selected.value;
            } else {
                // Selected is a base category - match if transaction category starts with it
                if (txCategory.includes(':')) {
                    const [baseCat] = txCategory.split(':', 1);
                    return baseCat === selected.value;
                } else {
                    return txCategory === selected.value;
                }
            }
        });
    });

    // Sort transactions
    filteredTransactions = sortTransactions(filteredTransactions, categoryTableSortState.column, categoryTableSortState.direction);

    // Render table
    renderTransactionsTable(tbody, filteredTransactions, 'category');
}

function updateCounterpartyTransactionsTable(data, selectedCounterparties, year, preFilteredTransactions = null) {
    const tbody = document.getElementById('counterparty-transactions-tbody');
    const transactionsToUse = preFilteredTransactions || data.all_transactions;
    if (!tbody || !transactionsToUse) return;

    if (!selectedCounterparties || selectedCounterparties.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #7f8c8d;">Select counterparties to view transactions</td></tr>';
        return;
    }

    // Normalize counterparty names for matching
    function normalizeCounterpartyName(name) {
        if (!name) return '';
        let normalized = name.toLowerCase();
        normalized = normalized.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        normalized = normalized.replace(/\bd\.\s*d\.\b/g, 'd.d.');
        normalized = normalized.replace(/\bss\s+d\.o\.o\./g, 'ss d.o.o.');
        normalized = normalized.replace(/\bss\s+d\.o\.o\b/g, 'ss d.o.o.');
        normalized = normalized.replace(/,\s*(d\.o\.o\.?|d\.d\.?|s\.p\.?|z\.b\.o\.?)/g, ' $1');
        normalized = normalized.replace(/\bd\.o\.o\.?\b/g, 'd.o.o.');
        normalized = normalized.replace(/\bd\.d\.\.?\b/g, 'd.d.');
        normalized = normalized.replace(/\bs\.p\.\.?\b/g, 's.p.');
        normalized = normalized.replace(/\bz\.b\.o\.?\b/g, 'z.b.o.');
        normalized = normalized.replace(/\.{2,}/g, '.');
        normalized = normalized.replace(/\s+/g, ' ').trim();
        if (normalized.includes('ctrp') || normalized.includes('in-fit') || normalized.includes('infit')) {
            normalized = normalized.replace(/.*(ctrp|in-fit|infit).*/, 'in-fit d.o.o.');
        }
        return normalized;
    }

    // Filter transactions based on selected counterparties and year
    const selectedNormalized = selectedCounterparties.map(cp => normalizeCounterpartyName(cp.value));

    let filteredTransactions = transactionsToUse.filter(tx => {
        // Filter by year if specified
        if (year !== 'all' && tx.date && !tx.date.startsWith(year)) {
            return false;
        }

        // Check if transaction counterparty matches any selected counterparty
        const txCounterparty = normalizeCounterpartyName(tx.counterparty || '');
        return selectedNormalized.some(selected => txCounterparty === selected);
    });

    // Sort transactions
    filteredTransactions = sortTransactions(filteredTransactions, counterpartyTableSortState.column, counterpartyTableSortState.direction);

    // Render table
    renderTransactionsTable(tbody, filteredTransactions, 'counterparty');
}

function sortTransactions(transactions, column, direction) {
    const sorted = [...transactions];
    sorted.sort((a, b) => {
        let aVal, bVal;

        switch(column) {
            case 'date':
                aVal = a.date || '';
                bVal = b.date || '';
                break;
            case 'description':
                aVal = (a.description || '').toLowerCase();
                bVal = (b.description || '').toLowerCase();
                break;
            case 'counterparty':
                aVal = (a.counterparty || '').toLowerCase();
                bVal = (b.counterparty || '').toLowerCase();
                break;
            case 'category':
                aVal = (a.category || '').toLowerCase();
                bVal = (b.category || '').toLowerCase();
                break;
            case 'amount':
                aVal = Math.abs(a.amount || 0);
                bVal = Math.abs(b.amount || 0);
                break;
            case 'type':
                aVal = (a.type || '').toLowerCase();
                bVal = (b.type || '').toLowerCase();
                break;
            case 'source_file':
                aVal = (a.source_file || '').toLowerCase();
                bVal = (b.source_file || '').toLowerCase();
                break;
            default:
                return 0;
        }

        if (column === 'date' || column === 'amount') {
            // Numeric/date comparison
            if (direction === 'asc') {
                return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            } else {
                return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
            }
        } else {
            // String comparison
            if (direction === 'asc') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal.localeCompare(aVal);
            }
        }
    });

    return sorted;
}

function renderTransactionsTable(tbody, transactions, tableType) {
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: #7f8c8d;">No transactions found</td></tr>';
        return;
    }

    tbody.innerHTML = transactions.map(tx => {
        const date = tx.date ? tx.date.substring(0, 10) : 'N/A';
        const description = (tx.description || '').substring(0, 50);
        const counterparty = (tx.counterparty || '').substring(0, 40);
        const category = tx.category || '';
        const amount = tx.amount || 0;
        const type = tx.type || 'unknown';
        const amountClass = 'text-right';
        const amountColor = amount >= 0 ? '#27ae60' : '#e74c3c';

        // Generate Google Drive link for PDF
        const sourceFile = tx.source_file || '';
        const pdfFilename = tx.pdf_filename || sourceFile.replace('.zip', '.pdf').replace('.csv', '.pdf');
        let sourceCell = '<td>-</td>';

        if (sourceFile && pdfFilename) {
            // Encode filename for URL
            const encodedFilename = encodeURIComponent(pdfFilename);
            // Google Drive search URL - searches for the PDF file
            // This will open Google Drive and search for the file
            const googleDriveUrl = `https://drive.google.com/drive/search?q=${encodedFilename}`;
            // Display PDF filename instead of original zip/csv filename
            sourceCell = `<td><a href="${googleDriveUrl}" target="_blank" style="color: #3498db; text-decoration: none;" title="Open PDF in Google Drive">${escapeHtml(pdfFilename)}</a></td>`;
        }

        // Generate counterparty cell - link if on category trends page
        let counterpartyCell = escapeHtml(counterparty);
        if (tableType === 'category' && counterparty) {
            const urlCounterparty = encodeURIComponent(counterparty);
            counterpartyCell = `<a href="counterparty_trends.html?counterparty=${urlCounterparty}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtml(counterparty)}</a>`;
        }

        // Generate category cell - link if on counterparty trends page
        let categoryCell = escapeHtml(category);
        if (tableType === 'counterparty' && category) {
            // Handle category tags (category:tag format)
            let urlCategory, urlTag;
            if (category.includes(':')) {
                const [baseCategory, tag] = category.split(':', 2);
                urlCategory = encodeURIComponent(baseCategory);
                urlTag = encodeURIComponent(tag);
                categoryCell = `<a href="category_trends.html?category=${urlCategory}&tag=${urlTag}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtml(category)}</a>`;
            } else {
                urlCategory = encodeURIComponent(category);
                categoryCell = `<a href="category_trends.html?category=${urlCategory}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtml(category)}</a>`;
            }
        }

        return `
            <tr>
                <td>${date}</td>
                <td>${escapeHtml(description)}</td>
                <td>${counterpartyCell}</td>
                <td>${categoryCell}</td>
                <td class="${amountClass}" style="color: ${amountColor}; font-weight: 600;">€${amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}</td>
                <td class="text-center">${type}</td>
                ${sourceCell}
            </tr>
        `;
    }).join('');

    // Initialize sorting for this table
    const tableId = tableType === 'category' ? 'category-transactions-table' : 'counterparty-transactions-table';
    const sortState = tableType === 'category' ? categoryTableSortState : counterpartyTableSortState;
    initializeTableSorting(tableId, sortState, tableType);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function initializeTableSorting(tableId, sortState, tableType) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const headers = table.querySelectorAll('th.sortable');
    headers.forEach(header => {
        // Remove existing sort indicators
        header.classList.remove('sorted-asc', 'sorted-desc');

        // Set current sort indicator
        if (header.dataset.sort === sortState.column) {
            header.classList.add(sortState.direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }

        // Remove existing listeners by cloning
        const newHeader = header.cloneNode(true);
        header.parentNode.replaceChild(newHeader, header);

        newHeader.addEventListener('click', function() {
            const column = newHeader.dataset.sort;
            const currentDirection = (sortState.column === column && sortState.direction === 'asc') ? 'desc' : 'asc';

            // Update sort state
            sortState.column = column;
            sortState.direction = currentDirection;

            // Update visual indicators
            const allHeaders = table.querySelectorAll('th.sortable');
            allHeaders.forEach(h => {
                h.classList.remove('sorted-asc', 'sorted-desc');
                if (h.dataset.sort === column) {
                    h.classList.add(currentDirection === 'asc' ? 'sorted-asc' : 'sorted-desc');
                }
            });

            // Re-render table with new sort
            const data = getDashboardData();
            if (tableType === 'category') {
                const selectedCategories = categoryMultiSelect ? categoryMultiSelect.getSelectedItems() : [];
                const yearSelector = document.getElementById('year-selector');
                const year = yearSelector ? yearSelector.value : 'all';
                updateCategoryTransactionsTable(data, selectedCategories, year, null);
            } else {
                const selectedCounterparties = counterpartyMultiSelect ? counterpartyMultiSelect.getSelectedItems() : [];
                const yearSelector = document.getElementById('year-selector');
                const year = yearSelector ? yearSelector.value : 'all';
                updateCounterpartyTransactionsTable(data, selectedCounterparties, year, null);
            }
        });
    });
}

// Counterparties table sorting functionality (for counterparties.html page)
function sortCounterparties(counterparties, column, direction) {
    const sorted = [...counterparties];
    sorted.sort((a, b) => {
        let aVal, bVal;

        switch(column) {
            case 'name':
                aVal = (a.name || '').toLowerCase();
                bVal = (b.name || '').toLowerCase();
                break;
            case 'count':
                aVal = a.count || 0;
                bVal = b.count || 0;
                break;
            case 'total':
                aVal = Math.abs(a.total || 0);
                bVal = Math.abs(b.total || 0);
                break;
            case 'percentage':
                // Percentage is proportional to total, so sort by absolute total
                aVal = Math.abs(a.total || 0);
                bVal = Math.abs(b.total || 0);
                break;
            default:
                return 0;
        }

        if (column === 'count' || column === 'total' || column === 'percentage') {
            // Numeric comparison
            if (direction === 'asc') {
                return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            } else {
                return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
            }
        } else {
            // String comparison
            if (direction === 'asc') {
                return aVal.localeCompare(bVal);
            } else {
                return bVal.localeCompare(aVal);
            }
        }
    });

    return sorted;
}

function renderCounterpartiesTable(tbody, counterparties, comparisonData = null, data = null, period = null) {
    const compareEnabled = comparisonData !== null;
    const colSpan = compareEnabled ? 12 : 9; // Updated for new columns: Counterparty, Total, % of Total, % of Income, % of Expenses, Count, Avg Amount, Avg/Month, Trend (+ 3 comparison columns)

    // Check if we're on the counterparties.html page (has pagination controls)
    const paginationControls = document.getElementById('counterparty-pagination-controls');
    const isCounterpartiesPage = paginationControls !== null;

    // Store full filtered/sorted data for pagination if on counterparties page
    // This should be the complete list (before pagination)
    if (isCounterpartiesPage) {
        counterpartiesPageData = [...counterparties]; // Store full list
    }

    if (counterparties.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${colSpan}" style="text-align: center; padding: 2rem; color: #7f8c8d;">No counterparties found</td></tr>`;
        if (isCounterpartiesPage) {
            updateCounterpartiesPaginationInfo(0);
        }
        return;
    }

    // Apply pagination if on counterparties page
    let displayCounterparties = counterparties;
    if (isCounterpartiesPage) {
        // Use the stored full list for pagination (should be set above)
        const fullList = counterpartiesPageData || counterparties;
        const startIdx = (counterpartiesPage - 1) * itemsPerPage;
        const endIdx = Math.min(startIdx + itemsPerPage, fullList.length);
        displayCounterparties = fullList.slice(startIdx, endIdx);
        updateCounterpartiesPaginationInfo(fullList.length, startIdx, endIdx);
    } else {
        // Not on counterparties page, show all
        displayCounterparties = counterparties;
    }

    // Calculate totals for percentage calculations
    // Use full list for percentage calculation, not just displayed items
    const totalAbsolute = counterparties.reduce((sum, cp) => sum + Math.abs(cp.total || 0), 0);
    const totalIncome = counterparties.filter(cp => cp.total > 0).reduce((sum, cp) => sum + cp.total, 0);
    const totalExpenses = Math.abs(counterparties.filter(cp => cp.total < 0).reduce((sum, cp) => sum + cp.total, 0));

    // Calculate number of months in period for average per month
    let numMonths = 1;
    if (period && data && data.all_months) {
        if (period.startsWith('ytd')) {
            // Count months in current year that have data
            const currentYear = data.current_year || new Date().getFullYear();
            numMonths = Object.keys(data.all_months).filter(month => {
                const [year] = month.split('-');
                return parseInt(year) === currentYear;
            }).length;
        } else if (period.startsWith('year:')) {
            numMonths = 12;
        } else if (period.startsWith('quarter:')) {
            numMonths = 3;
        } else if (period.startsWith('month:')) {
            numMonths = 1;
        }
    }

    // Create comparison map for quick lookup
    const comparisonMap = {};
    if (comparisonData) {
        comparisonData.forEach(cp => {
            comparisonMap[cp.name] = cp;
        });
    }

    tbody.innerHTML = displayCounterparties.map(cp => {
        const totalAmount = cp.total || 0;
        const isNegative = totalAmount < 0;
        const sign = isNegative ? '-' : '+';
        const absAmount = Math.abs(totalAmount);
        const formattedAmount = `€${sign}${absAmount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        // Percentage calculations
        const percentage = totalAbsolute > 0 ? ((absAmount / totalAbsolute) * 100) : 0;
        const formattedPercentage = `${percentage.toFixed(1)}%`;

        // Percentage of income/expenses
        const pctOfIncome = totalAmount > 0 && totalIncome > 0 ? ((totalAmount / totalIncome) * 100) : 0;
        const formattedPctOfIncome = totalAmount > 0 ? `${pctOfIncome.toFixed(1)}%` : '-';
        const pctOfExpenses = totalAmount < 0 && totalExpenses > 0 ? ((absAmount / totalExpenses) * 100) : 0;
        const formattedPctOfExpenses = totalAmount < 0 ? `${pctOfExpenses.toFixed(1)}%` : '-';

        // Average transaction amount
        const avgAmount = cp.count > 0 ? (totalAmount / cp.count) : 0;
        const avgSign = avgAmount >= 0 ? '+' : '-';
        const formattedAvgAmount = `€${avgSign}${Math.abs(avgAmount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        // Average per month
        const avgPerMonth = numMonths > 0 ? (totalAmount / numMonths) : totalAmount;
        const avgMonthSign = avgPerMonth >= 0 ? '+' : '-';
        const formattedAvgPerMonth = `€${avgMonthSign}${Math.abs(avgPerMonth).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        const urlName = encodeURIComponent(cp.name || '');
        // Use red for negative (expenses), green for positive (income)
        const amountColor = isNegative ? '#e74c3c' : '#27ae60';

        // Get comparison data
        let comparisonHtml = '';
        if (compareEnabled) {
            const compCp = comparisonMap[cp.name];
            const prevTotal = compCp ? compCp.total : 0;
            const prevIsNegative = prevTotal < 0;
            const prevSign = prevIsNegative ? '-' : '+';
            const prevAbsAmount = Math.abs(prevTotal);
            const formattedPrevAmount = `€${prevSign}${prevAbsAmount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
            const prevAmountColor = prevIsNegative ? '#e74c3c' : '#27ae60';

            const change = totalAmount - prevTotal;
            const changeIsNegative = change < 0;
            const changeSign = changeIsNegative ? '-' : '+';
            const changeAbsAmount = Math.abs(change);
            const formattedChange = `€${changeSign}${changeAbsAmount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
            const changeColor = changeIsNegative ? '#e74c3c' : '#27ae60';

            const changePct = prevTotal !== 0 ? ((change / Math.abs(prevTotal)) * 100) : (change !== 0 ? (change > 0 ? 100 : -100) : 0);
            const formattedChangePct = `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%`;

            comparisonHtml = `
                <td class="text-right" style="color: ${prevAmountColor};">${formattedPrevAmount}</td>
                <td class="text-right" style="color: ${changeColor}; font-weight: 600;">${formattedChange}</td>
                <td class="text-right" style="color: ${changeColor}; font-weight: 600;">${formattedChangePct}</td>
            `;
        }

        // Generate sparkline data for this counterparty
        const sparklineData = getCounterpartySparklineData(cp.name, data, totalAmount);
        const sparklineHtml = sparklineData ? `<canvas class="sparkline" data-sparkline="${btoa(JSON.stringify(sparklineData))}" width="100" height="20" style="max-width: 100px;"></canvas>` : '<span style="color: #bdc3c7;">-</span>';

        return `
            <tr class="drill-down-row" data-counterparty="${escapeHtmlForTable(cp.name || '')}" data-type="counterparty">
                <td class="expand-icon" style="cursor: pointer; text-align: center; user-select: none;">▶</td>
                <td><a href="counterparty_trends.html?counterparty=${urlName}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cp.name || '')}</a></td>
                <td class="text-right" style="color: ${amountColor}; font-weight: 600;">${formattedAmount}</td>
                <td class="text-right" style="color: #7f8c8d;">${formattedPercentage}</td>
                <td class="text-right" style="color: ${totalAmount > 0 ? '#27ae60' : '#bdc3c7'}; font-size: 0.9rem;">${formattedPctOfIncome}</td>
                <td class="text-right" style="color: ${totalAmount < 0 ? '#e74c3c' : '#bdc3c7'}; font-size: 0.9rem;">${formattedPctOfExpenses}</td>
                <td class="text-center">${cp.count || 0}</td>
                <td class="text-right" style="color: ${amountColor}; font-size: 0.9rem;">${formattedAvgAmount}</td>
                <td class="text-right" style="color: ${amountColor}; font-size: 0.9rem;">${formattedAvgPerMonth}</td>
                <td class="text-center">${sparklineHtml}</td>
                ${comparisonHtml}
            </tr>
            <tr class="drill-down-detail" data-parent="${escapeHtmlForTable(cp.name || '')}" style="display: none;">
                <td colspan="${colSpan + 1}" style="padding: 1rem; background: #f8f9fa; border-top: 2px solid #3498db;">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; color: #34495e;">Categories for "${escapeHtmlForTable(cp.name || '')}":</div>
                    <div class="drill-down-content" style="min-height: 50px; color: #7f8c8d;">Loading...</div>
                </td>
            </tr>
        `;
    }).join('');

    // Render sparklines after a short delay
    setTimeout(renderSparklines, 100);

    // Re-initialize drill-down handlers after rendering
    if (data) {
        initializeDrillDownHandlers(data);
    }

    // Add pagination handlers if on counterparties page
    if (isCounterpartiesPage) {
        setupCounterpartiesPaginationHandlers();
    }
}

function updateCounterpartiesPaginationInfo(totalCount, startIdx = 0, endIdx = 0) {
    const paginationInfoEl = document.getElementById('counterparty-pagination-info');
    const totalCountEl = document.getElementById('counterparty-total-count');
    const prevBtn = document.getElementById('counterparty-prev-btn');
    const nextBtn = document.getElementById('counterparty-next-btn');

    if (totalCountEl) {
        totalCountEl.textContent = totalCount;
    }

    if (paginationInfoEl && totalCount > 0) {
        paginationInfoEl.innerHTML = `Showing ${startIdx + 1}-${endIdx} of <span id="counterparty-total-count">${totalCount}</span>`;
    } else if (paginationInfoEl) {
        paginationInfoEl.innerHTML = `Showing 0-0 of <span id="counterparty-total-count">0</span>`;
    }

    if (prevBtn) {
        prevBtn.disabled = counterpartiesPage === 1;
    }

    if (nextBtn && counterpartiesPageData) {
        const totalPages = Math.ceil(counterpartiesPageData.length / itemsPerPage);
        nextBtn.disabled = counterpartiesPage >= totalPages;
    }
}

function setupCounterpartiesPaginationHandlers() {
    const prevBtn = document.getElementById('counterparty-prev-btn');
    const nextBtn = document.getElementById('counterparty-next-btn');

    // Remove existing handlers and add new ones
    if (prevBtn) {
        prevBtn.onclick = () => {
            if (counterpartiesPage > 1) {
                counterpartiesPage--;
                renderCounterpartiesTableWithPagination();
            }
        };
    }

    if (nextBtn) {
        nextBtn.onclick = () => {
            if (counterpartiesPageData) {
                const totalPages = Math.ceil(counterpartiesPageData.length / itemsPerPage);
                if (counterpartiesPage < totalPages) {
                    counterpartiesPage++;
                    renderCounterpartiesTableWithPagination();
                }
            }
        };
    }
}

function renderCounterpartiesTableWithPagination() {
    const tbody = document.getElementById('counterparties-tbody');
    if (!tbody) return;

    // Get the full unfiltered/unsorted data from currentCounterpartiesData
    // This is the source of truth that was set when updateCounterpartiesChartsAndTable was called
    const allCounterparties = currentCounterpartiesData || counterpartiesPageData || [];
    if (allCounterparties.length === 0) return;

    // Get current filter and sort state
    const selectedFilter = document.querySelector('input[name="type-filter"]:checked');
    const filterType = selectedFilter ? selectedFilter.value : 'both';

    // Apply filter
    let filteredCounterparties = [...allCounterparties];
    if (filterType === 'income') {
        filteredCounterparties = filteredCounterparties.filter(cp => cp.total > 0);
    } else if (filterType === 'expense') {
        filteredCounterparties = filteredCounterparties.filter(cp => cp.total < 0);
    }

    // Apply sorting
    const sortedCounterparties = sortCounterparties(filteredCounterparties, counterpartiesTableSortState.column, counterpartiesTableSortState.direction);

    // Update stored data with sorted/filtered version for pagination
    counterpartiesPageData = sortedCounterparties;

    // Get comparison data if enabled
    const compareToggle = document.getElementById('compare-toggle');
    const compareEnabled = compareToggle ? compareToggle.checked : false;
    let comparisonData = null;

    if (compareEnabled && window.counterpartiesComparisonData) {
        // Apply same filter to comparison data
        let filteredComparison = [...window.counterpartiesComparisonData];
        if (filterType === 'income') {
            filteredComparison = filteredComparison.filter(cp => cp.total > 0);
        } else if (filterType === 'expense') {
            filteredComparison = filteredComparison.filter(cp => cp.total < 0);
        }
        comparisonData = filteredComparison;
    }

    // Re-render with pagination
    const period = window.counterpartiesPeriod || null;
    renderCounterpartiesTable(tbody, sortedCounterparties, comparisonData, window.counterpartiesFullData, period);

    // Re-initialize drill-down handlers after re-rendering
    if (window.counterpartiesFullData) {
        initializeDrillDownHandlers(window.counterpartiesFullData);
    }
}

function initializeCounterpartiesTableSorting(data) {
    const table = document.getElementById('counterparties-table');
    if (!table) return;

    // Store initial counterparties data (will be updated when table is rendered)
    if (data.counterparties) {
        currentCounterpartiesData = data.counterparties;
    }

    // Initial render with default sort (will be handled by updateCounterpartiesView)
    // Just set up the click handlers

    // Set initial sort indicator
    const headers = table.querySelectorAll('th.sortable');
    headers.forEach(header => {
        if (header.dataset.sort === counterpartiesTableSortState.column) {
            header.classList.add(counterpartiesTableSortState.direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }
    });

    // Add click handlers
    headers.forEach(header => {
        header.addEventListener('click', function() {
            const column = header.dataset.sort;
            const currentDirection = (counterpartiesTableSortState.column === column && counterpartiesTableSortState.direction === 'asc') ? 'desc' : 'asc';

            // Update sort state
            counterpartiesTableSortState.column = column;
            counterpartiesTableSortState.direction = currentDirection;

            // Update visual indicators
            headers.forEach(h => {
                h.classList.remove('sorted-asc', 'sorted-desc');
                if (h.dataset.sort === column) {
                    h.classList.add(currentDirection === 'asc' ? 'sorted-asc' : 'sorted-desc');
                }
            });

            // Reset pagination when sorting changes
            const paginationControls = document.getElementById('counterparty-pagination-controls');
            if (paginationControls) {
                counterpartiesPage = 1;
            }

            // Re-render table with new sort
            // Use currentCounterpartiesData if available, otherwise fall back to stored data
            const allCounterparties = currentCounterpartiesData || counterpartiesPageData || [];
            if (allCounterparties.length === 0) {
                console.warn('No counterparties data available for sorting');
                return;
            }

            // Apply filter before sorting (respect the current filter selection)
            const selectedFilter = document.querySelector('input[name="type-filter"]:checked');
            const filterType = selectedFilter ? selectedFilter.value : 'both';

            let filteredCounterparties = [...allCounterparties];
            if (filterType === 'income') {
                filteredCounterparties = filteredCounterparties.filter(cp => cp.total > 0);
            } else if (filterType === 'expense') {
                filteredCounterparties = filteredCounterparties.filter(cp => cp.total < 0);
            }

            const sortedCounterparties = sortCounterparties(filteredCounterparties, column, currentDirection);

            // Update stored data for pagination
            if (paginationControls) {
                counterpartiesPageData = sortedCounterparties;
            }

            const tbody = document.getElementById('counterparties-tbody');
            if (tbody) {
                // Get comparison data if enabled
                const compareToggle = document.getElementById('compare-toggle');
                const compareEnabled = compareToggle ? compareToggle.checked : false;
                let comparisonData = null;
                if (compareEnabled && window.counterpartiesComparisonData) {
                    // Apply same filter to comparison data
                    let filteredComparison = [...window.counterpartiesComparisonData];
                    if (filterType === 'income') {
                        filteredComparison = filteredComparison.filter(cp => cp.total > 0);
                    } else if (filterType === 'expense') {
                        filteredComparison = filteredComparison.filter(cp => cp.total < 0);
                    }
                    comparisonData = filteredComparison;
                }
                const period = window.counterpartiesPeriod || null;
                renderCounterpartiesTable(tbody, sortedCounterparties, comparisonData, window.counterpartiesFullData || data, period);

                // Re-initialize drill-down handlers after re-rendering
                initializeDrillDownHandlers(window.counterpartiesFullData || data);
            }
        });
    });
}

// Counterparties period selector functionality
let incomeChart = null;
let expenseChart = null;
let currentCounterpartiesData = null; // Store current counterparties for sorting

function normalizeCounterpartyNameForGrouping(name) {
    if (!name) return '';
    let normalized = name.toLowerCase();
    normalized = normalized.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    normalized = normalized.replace(/\bd\.\s*d\.\b/g, 'd.d.');
    normalized = normalized.replace(/\bss\s+d\.o\.o\./g, 'ss d.o.o.');
    normalized = normalized.replace(/\bss\s+d\.o\.o\b/g, 'ss d.o.o.');
    normalized = normalized.replace(/,\s*(d\.o\.o\.?|d\.d\.?|s\.p\.?|z\.b\.o\.?)/g, ' $1');
    normalized = normalized.replace(/\bd\.o\.o\.?\b/g, 'd.o.o.');
    normalized = normalized.replace(/\bd\.d\.\.?\b/g, 'd.d.');
    normalized = normalized.replace(/\bs\.p\.\.?\b/g, 's.p.');
    normalized = normalized.replace(/\bz\.b\.o\.?\b/g, 'z.b.o.');
    normalized = normalized.replace(/\.{2,}/g, '.');
    normalized = normalized.replace(/\s+/g, ' ').trim();
    if (normalized.includes('ctrp') || normalized.includes('in-fit') || normalized.includes('infit')) {
        normalized = normalized.replace(/.*(ctrp|in-fit|infit).*/, 'in-fit d.o.o.');
    }
    return normalized;
}

function getCounterpartyBreakdowns(transactions, limit = 10000) {
    const counterpartyStats = {};
    const groupKeys = {};

    transactions.forEach(tx => {
        const counterparty = (tx.counterparty || '').trim() || 'Unknown';
        const normalizedName = normalizeCounterpartyNameForGrouping(counterparty);
        const groupKey = `name:${normalizedName}`;
        const amount = tx.amount || 0;

        if (!groupKeys[groupKey]) {
            groupKeys[groupKey] = {
                primaryName: counterparty,
                nameVariants: new Set([counterparty])
            };
        } else {
            groupKeys[groupKey].nameVariants.add(counterparty);
        }

        if (!counterpartyStats[groupKey]) {
            counterpartyStats[groupKey] = {
                count: 0,
                total: 0,
                transactions: [],
                nameVariants: new Set()
            };
        }

        counterpartyStats[groupKey].count += 1;
        counterpartyStats[groupKey].total += amount;
        counterpartyStats[groupKey].transactions.push(tx);
        counterpartyStats[groupKey].nameVariants.add(counterparty);
    });

    const result = [];
    Object.keys(counterpartyStats).forEach(groupKey => {
        const stats = counterpartyStats[groupKey];
        const groupInfo = groupKeys[groupKey];
        const nameVariants = Array.from(stats.nameVariants);
        const mostCommonName = nameVariants.reduce((a, b) => {
            const aCount = stats.transactions.filter(tx => (tx.counterparty || '').trim() === a).length;
            const bCount = stats.transactions.filter(tx => (tx.counterparty || '').trim() === b).length;
            return aCount > bCount ? a : b;
        });

        result.push({
            name: mostCommonName,
            count: stats.count,
            total: stats.total
        });
    });

    result.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
    return result.slice(0, limit);
}

// Helper function to calculate comparison period
function calculateComparisonPeriod(period, currentYear) {
    if (period === 'ytd') {
        // Compare with previous year YTD
        const lastYear = currentYear - 1;
        return `ytd:${lastYear}`;
    } else if (period.startsWith('year:')) {
        const year = parseInt(period.split(':')[1]);
        return `year:${year - 1}`;
    } else if (period.startsWith('quarter:')) {
        const [year, quarter] = period.split(':')[1].split('-Q');
        const yearNum = parseInt(year);
        const quarterNum = parseInt(quarter);
        if (quarterNum === 1) {
            return `quarter:${yearNum - 1}-Q4`;
        } else {
            return `quarter:${yearNum}-Q${quarterNum - 1}`;
        }
    } else if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        const [year, monthNum] = month.split('-');
        const yearNum = parseInt(year);
        const monthNumInt = parseInt(monthNum);
        if (monthNumInt === 1) {
            return `month:${yearNum - 1}-12`;
        } else {
            return `month:${yearNum}-${String(monthNumInt - 1).padStart(2, '0')}`;
        }
    }
    return null;
}

// Helper function to format comparison period label
function formatComparisonPeriodLabel(comparisonPeriod) {
    if (!comparisonPeriod) return 'Previous Period';
    if (comparisonPeriod.startsWith('ytd:')) {
        const year = comparisonPeriod.split(':')[1];
        return `YTD ${year}`;
    } else if (comparisonPeriod.startsWith('year:')) {
        return comparisonPeriod.split(':')[1];
    } else if (comparisonPeriod.startsWith('quarter:')) {
        const [year, quarter] = comparisonPeriod.split(':')[1].split('-Q');
        return `Q${quarter} ${year}`;
    } else if (comparisonPeriod.startsWith('month:')) {
        const month = comparisonPeriod.split(':')[1];
        const [year, monthNum] = month.split('-');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${monthNames[parseInt(monthNum) - 1]} ${year}`;
    }
    return 'Previous Period';
}

function filterTransactionsByPeriod(transactions, period, currentYear) {
    if (period === 'ytd') {
        const currentDate = new Date();
        const year = currentYear || currentDate.getFullYear();
        return transactions.filter(tx => {
            if (!tx.date) return false;
            const txYear = parseInt(tx.date.substring(0, 4));
            const txDate = new Date(tx.date);
            return txYear === year && txDate <= currentDate;
        });
    } else if (period === 'alltime') {
        // Return all transactions
        return transactions.filter(tx => tx.date);
    } else if (period.startsWith('custom:')) {
        // Handle custom range: format is "custom:YYYY-MM-DD:YYYY-MM-DD"
        const parts = period.split(':');
        if (parts.length === 3) {
            const startDate = new Date(parts[1]);
            const endDate = new Date(parts[2]);
            // Set end date to end of day
            endDate.setHours(23, 59, 59, 999);
            return transactions.filter(tx => {
                if (!tx.date) return false;
                const txDate = new Date(tx.date);
                return txDate >= startDate && txDate <= endDate;
            });
        }
        return transactions;
    } else if (period.startsWith('year:')) {
        const year = period.split(':')[1];
        return transactions.filter(tx => tx.date && tx.date.startsWith(year));
    } else if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        return transactions.filter(tx => tx.date && tx.date.startsWith(month));
    } else if (period.startsWith('quarter:')) {
        const [year, quarter] = period.split(':')[1].split('-Q');
        const startMonth = (parseInt(quarter) - 1) * 3 + 1;
        const endMonth = startMonth + 2;
        return transactions.filter(tx => {
            if (!tx.date) return false;
            const txYear = tx.date.substring(0, 4);
            const txMonth = parseInt(tx.date.substring(5, 7));
            return txYear === year && txMonth >= startMonth && txMonth <= endMonth;
        });
    } else if (period.startsWith('ytd:')) {
        // Handle YTD comparison - get same months from previous year
        const compareYear = parseInt(period.split(':')[1]);
        const currentYearNum = currentYear || new Date().getFullYear();

        // Find which months actually exist in the current year
        const currentYearMonths = new Set();
        transactions.forEach(tx => {
            if (tx.date) {
                const txYear = parseInt(tx.date.substring(0, 4));
                if (txYear === currentYearNum) {
                    const txMonth = tx.date.substring(5, 7);
                    currentYearMonths.add(txMonth);
                }
            }
        });

        // Get transactions for same months from previous year
        return transactions.filter(tx => {
            if (!tx.date) return false;
            const txYear = parseInt(tx.date.substring(0, 4));
            const txMonth = tx.date.substring(5, 7);
            return txYear === compareYear && currentYearMonths.has(txMonth);
        });
    }
    return transactions;
}

function initializeCounterpartiesPeriodSelector(data) {
    const periodSelector = document.getElementById('period-selector');
    if (!periodSelector) return;

    // Clear existing options
    periodSelector.innerHTML = '';

    // Add Year-to-Date option (no group, always first)
    const ytdOption = document.createElement('option');
    ytdOption.value = 'ytd';
    ytdOption.textContent = '📊 Year-to-Date';
    ytdOption.selected = true;
    periodSelector.appendChild(ytdOption);

    // Add separator
    const separator1 = document.createElement('option');
    separator1.disabled = true;
    separator1.textContent = '─────────────────';
    periodSelector.appendChild(separator1);

    // Get available years
    const years = new Set();
    if (data.available_months) {
        data.available_months.forEach(month => {
            const year = month.split('-')[0];
            years.add(year);
        });
    }

    const sortedYears = Array.from(years).sort().reverse();
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Group options by year - create a year group for each year
    sortedYears.forEach((year, yearIndex) => {
        // Create a year group
        const yearGroup = document.createElement('optgroup');
        yearGroup.label = `📅 ${year}`;

        // Add full year option to the group
        const yearOption = document.createElement('option');
        yearOption.value = `year:${year}`;
        yearOption.textContent = `Full Year ${year}`;
        yearGroup.appendChild(yearOption);

        // Add quarters to the group
        for (let q = 1; q <= 4; q++) {
            const option = document.createElement('option');
            option.value = `quarter:${year}-Q${q}`;
            option.textContent = `Q${q} ${year}`;
            yearGroup.appendChild(option);
        }

        // Add months to the group (newest first)
        const yearMonths = data.available_months
            ? data.available_months.filter(m => m.startsWith(year)).sort().reverse()
            : [];
        yearMonths.forEach(month => {
            const [, monthNum] = month.split('-');
            const option = document.createElement('option');
            option.value = `month:${month}`;
            option.textContent = `${monthNames[parseInt(monthNum) - 1]} ${year}`;
            yearGroup.appendChild(option);
        });

        periodSelector.appendChild(yearGroup);
    });

    // Add change handler for period selector
    periodSelector.addEventListener('change', function() {
        updateCounterpartiesView(data, this.value);
    });

    // Add comparison toggle handler
    const compareToggle = document.getElementById('compare-toggle');
    if (compareToggle) {
        compareToggle.addEventListener('change', function() {
            updateCounterpartiesView(data, periodSelector.value);
        });
    }

    // Add change handlers for type filter radio buttons
    const typeFilters = document.querySelectorAll('input[name="type-filter"]');
    typeFilters.forEach(radio => {
        radio.addEventListener('change', function() {
            updateCounterpartiesView(data, periodSelector.value);
        });
    });

    // Add search filter handler
    const searchInput = document.getElementById('counterparty-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            applyCounterpartyFilters(data, periodSelector.value);
        });
    }

    // Add amount range filter handlers
    const amountMinInput = document.getElementById('counterparty-amount-min');
    const amountMaxInput = document.getElementById('counterparty-amount-max');
    if (amountMinInput) {
        amountMinInput.addEventListener('input', function() {
            applyCounterpartyFilters(data, periodSelector.value);
        });
    }
    if (amountMaxInput) {
        amountMaxInput.addEventListener('input', function() {
            applyCounterpartyFilters(data, periodSelector.value);
        });
    }

    // Add table search handler
    const tableSearchInput = document.getElementById('counterparty-table-search');
    if (tableSearchInput) {
        tableSearchInput.addEventListener('input', function() {
            filterCounterpartyTable();
        });
    }
}

function updateCounterpartiesView(data, period) {
    if (!data.all_transactions) {
        // Fallback to pre-calculated data if all_transactions not available
        if (period === 'ytd' && data.counterparties) {
            updateCounterpartiesChartsAndTable(data.counterparties, data, period);
            return;
        }
        return;
    }

    const currentYear = data.current_year || new Date().getFullYear();
    const filteredTransactions = filterTransactionsByPeriod(data.all_transactions, period, currentYear);
    const counterparties = getCounterpartyBreakdowns(filteredTransactions, 10000);

    updateCounterpartiesChartsAndTable(counterparties, data, period);
}

function updateCounterpartiesChartsAndTable(counterparties, data, period) {
    // Store current counterparties for sorting
    currentCounterpartiesData = counterparties;

    // Reset pagination when data changes
    const paginationControls = document.getElementById('counterparty-pagination-controls');
    if (paginationControls) {
        counterpartiesPage = 1;
    }

    // Check if comparison is enabled
    const compareToggle = document.getElementById('compare-toggle');
    const compareEnabled = compareToggle ? compareToggle.checked : false;

    // Calculate comparison data if enabled
    let comparisonData = null;
    let comparisonPeriod = null;
    if (compareEnabled && data && data.all_transactions) {
        comparisonPeriod = calculateComparisonPeriod(period, data.current_year || new Date().getFullYear());
        if (comparisonPeriod) {
            const currentYear = data.current_year || new Date().getFullYear();
            const comparisonTransactions = filterTransactionsByPeriod(data.all_transactions, comparisonPeriod, currentYear);
            const comparisonCounterparties = getCounterpartyBreakdowns(comparisonTransactions, 10000);
            comparisonData = comparisonCounterparties;
            // Store comparison data globally for pagination
            window.counterpartiesComparisonData = comparisonData;
        }
    } else {
        window.counterpartiesComparisonData = null;
    }

    // Store full data object and period for pagination
    window.counterpartiesFullData = data;
    window.counterpartiesPeriod = period;

    // Update comparison summary
    updateCounterpartyComparisonSummary(counterparties, comparisonData, comparisonPeriod, data, period);

    // Show/hide comparison columns
    const comparisonColumns = document.querySelectorAll('.comparison-column');
    comparisonColumns.forEach(col => {
        col.style.display = compareEnabled ? '' : 'none';
    });

    // Get selected filter type
    const selectedFilter = document.querySelector('input[name="type-filter"]:checked');
    const filterType = selectedFilter ? selectedFilter.value : 'both';

    // Separate into income and expenses
    const incomeCounterparties = counterparties.filter(cp => cp.total > 0);
    const expenseCounterparties = counterparties.filter(cp => cp.total < 0);

    // Sort by absolute amount
    incomeCounterparties.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
    expenseCounterparties.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));

    // Take top 10 for each chart
    const topIncome = incomeCounterparties.slice(0, 10);
    const topExpenses = expenseCounterparties.slice(0, 10);

    // Get chart containers for showing/hiding
    const incomeChartContainer = document.querySelector('.counterparty-charts-grid > div:first-child');
    const expenseChartContainer = document.querySelector('.counterparty-charts-grid > div:last-child');

    // Show/hide charts based on filter
    if (filterType === 'income') {
        if (incomeChartContainer) incomeChartContainer.style.display = 'block';
        if (expenseChartContainer) expenseChartContainer.style.display = 'none';
    } else if (filterType === 'expense') {
        if (incomeChartContainer) incomeChartContainer.style.display = 'none';
        if (expenseChartContainer) expenseChartContainer.style.display = 'block';
    } else {
        // both
        if (incomeChartContainer) incomeChartContainer.style.display = 'block';
        if (expenseChartContainer) expenseChartContainer.style.display = 'block';
    }

    // Update income chart
    const incomeCtx = document.getElementById('incomeChart');
    if (incomeCtx && (filterType === 'both' || filterType === 'income')) {
        if (incomeChart) {
            incomeChart.destroy();
        }
        if (topIncome.length > 0) {
            incomeChart = createDoughnutChart('incomeChart', {
                labels: topIncome.map(cp => cp.name),
                datasets: [{
                    data: topIncome.map(cp => cp.total),
                    backgroundColor: generateColors(topIncome.length)
                }]
            });
        } else {
            // Clear chart if no data
            if (incomeChart) {
                incomeChart.destroy();
                incomeChart = null;
            }
        }
    } else if (incomeCtx && filterType === 'expense') {
        // Destroy chart if not showing
        if (incomeChart) {
            incomeChart.destroy();
            incomeChart = null;
        }
    }

    // Update expense chart
    const expenseCtx = document.getElementById('expenseChart');
    if (expenseCtx && (filterType === 'both' || filterType === 'expense')) {
        if (expenseChart) {
            expenseChart.destroy();
        }
        if (topExpenses.length > 0) {
            expenseChart = createDoughnutChart('expenseChart', {
                labels: topExpenses.map(cp => cp.name),
                datasets: [{
                    data: topExpenses.map(cp => Math.abs(cp.total)),
                    backgroundColor: generateColors(topExpenses.length)
                }]
            });
        } else {
            // Clear chart if no data
            if (expenseChart) {
                expenseChart.destroy();
                expenseChart = null;
            }
        }
    } else if (expenseCtx && filterType === 'income') {
        // Destroy chart if not showing
        if (expenseChart) {
            expenseChart.destroy();
            expenseChart = null;
        }
    }

    // Update table with filtered data
    let filteredCounterparties = counterparties;
    if (filterType === 'income') {
        filteredCounterparties = incomeCounterparties;
    } else if (filterType === 'expense') {
        filteredCounterparties = expenseCounterparties;
    }

    const sortedCounterparties = sortCounterparties(filteredCounterparties, counterpartiesTableSortState.column, counterpartiesTableSortState.direction);
    const tbody = document.getElementById('counterparties-tbody');
    if (tbody) {
        renderCounterpartiesTable(tbody, sortedCounterparties, comparisonData, data, period);

        // Re-initialize drill-down handlers after re-rendering
        if (data) {
            initializeDrillDownHandlers(data);
        }
    }
}

// Categories period selector functionality
let categoryIncomeChart = null;
let categoryExpenseChart = null;
let counterpartiesPage = 1; // Pagination for counterparties.html page (separate from overview page)
let counterpartiesPageData = null; // Store full sorted counterparty data for pagination
let currentCategoriesData = null; // Store current categories for rendering
const itemsPerPage = 50; // Items per page for pagination (used by both categories and counterparties pages)

function getCategoryBreakdowns(transactions, limit = 10000) {
    const categoryStats = {};

    transactions.forEach(tx => {
        const category = (tx.category || '').trim() || 'Unknown';
        const amount = tx.amount || 0;

        if (!categoryStats[category]) {
            categoryStats[category] = {
                count: 0,
                total: 0,
                transactions: []
            };
        }

        categoryStats[category].count += 1;
        categoryStats[category].total += amount;
        categoryStats[category].transactions.push(tx);
    });

    const result = [];
    Object.keys(categoryStats).forEach(category => {
        const stats = categoryStats[category];
        result.push({
            name: category,
            count: stats.count,
            total: stats.total
        });
    });

    result.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
    return result.slice(0, limit);
}

function initializeCategoriesPeriodSelector(data) {
    const periodSelector = document.getElementById('period-selector');
    if (!periodSelector) return;

    // Clear existing options
    periodSelector.innerHTML = '';

    // Add Year-to-Date option (no group, always first)
    const ytdOption = document.createElement('option');
    ytdOption.value = 'ytd';
    ytdOption.textContent = '📊 Year-to-Date';
    ytdOption.selected = true;
    periodSelector.appendChild(ytdOption);

    // Add separator
    const separator1 = document.createElement('option');
    separator1.disabled = true;
    separator1.textContent = '─────────────────';
    periodSelector.appendChild(separator1);

    // Get available years
    const years = new Set();
    if (data.available_months) {
        data.available_months.forEach(month => {
            const year = month.split('-')[0];
            years.add(year);
        });
    }

    const sortedYears = Array.from(years).sort().reverse();
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Group options by year - create a year group for each year
    sortedYears.forEach((year, yearIndex) => {
        // Create a year group
        const yearGroup = document.createElement('optgroup');
        yearGroup.label = `📅 ${year}`;

        // Add full year option to the group
        const yearOption = document.createElement('option');
        yearOption.value = `year:${year}`;
        yearOption.textContent = `Full Year ${year}`;
        yearGroup.appendChild(yearOption);

        // Add quarters to the group
        for (let q = 1; q <= 4; q++) {
            const option = document.createElement('option');
            option.value = `quarter:${year}-Q${q}`;
            option.textContent = `Q${q} ${year}`;
            yearGroup.appendChild(option);
        }

        // Add months to the group (newest first)
        const yearMonths = data.available_months
            ? data.available_months.filter(m => m.startsWith(year)).sort().reverse()
            : [];
        yearMonths.forEach(month => {
            const [, monthNum] = month.split('-');
            const option = document.createElement('option');
            option.value = `month:${month}`;
            option.textContent = `${monthNames[parseInt(monthNum) - 1]} ${year}`;
            yearGroup.appendChild(option);
        });

        periodSelector.appendChild(yearGroup);
    });

    // Add change handler for period selector
    periodSelector.addEventListener('change', function() {
        updateCategoriesView(data, this.value);
    });

    // Add change handlers for type filter radio buttons
    const typeFilters = document.querySelectorAll('input[name="type-filter"]');
    typeFilters.forEach(radio => {
        radio.addEventListener('change', function() {
            updateCategoriesView(data, periodSelector.value);
        });
    });

    // Add comparison toggle handler
    const compareToggle = document.getElementById('compare-toggle');
    if (compareToggle) {
        compareToggle.addEventListener('change', function() {
            updateCategoriesView(data, periodSelector.value);
        });
    }

    // Add search filter handler
    const searchInput = document.getElementById('category-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            applyCategoryFilters(data, periodSelector.value);
        });
    }

    // Add amount range filter handlers
    const amountMinInput = document.getElementById('category-amount-min');
    const amountMaxInput = document.getElementById('category-amount-max');
    if (amountMinInput) {
        amountMinInput.addEventListener('input', function() {
            applyCategoryFilters(data, periodSelector.value);
        });
    }
    if (amountMaxInput) {
        amountMaxInput.addEventListener('input', function() {
            applyCategoryFilters(data, periodSelector.value);
        });
    }

    // Add table search handler
    const tableSearchInput = document.getElementById('category-table-search');
    if (tableSearchInput) {
        tableSearchInput.addEventListener('input', function() {
            filterCategoryTable();
        });
    }
}

function updateCategoriesView(data, period) {
    if (!data.all_transactions) {
        // Fallback to pre-calculated data if all_transactions not available
        if (period === 'ytd' && data.all_months) {
            // Use YTD breakdown from all_months
            const ytdBreakdown = {};
            Object.values(data.all_months).forEach(monthData => {
                if (monthData.breakdown) {
                    Object.entries(monthData.breakdown).forEach(([cat, catData]) => {
                        if (!ytdBreakdown[cat]) {
                            ytdBreakdown[cat] = { total: 0, count: 0, tags: {} };
                        }
                        ytdBreakdown[cat].total += catData.total || 0;
                        ytdBreakdown[cat].count += catData.count || 0;
                    });
                }
            });
            const categories = Object.entries(ytdBreakdown).map(([name, data]) => ({
                name: name,
                count: data.count,
                total: data.total
            }));
            updateCategoriesChartsAndTable(categories, data, period);
            return;
        }
        return;
    }

    const currentYear = data.current_year || new Date().getFullYear();
    const filteredTransactions = filterTransactionsByPeriod(data.all_transactions, period, currentYear);
    const categories = getCategoryBreakdowns(filteredTransactions, 10000);

    updateCategoriesChartsAndTable(categories, data, period);
}

function updateCategoriesChartsAndTable(categories, data, period) {
    // Store current categories for rendering
    currentCategoriesData = categories;

    // Check if comparison is enabled
    const compareToggle = document.getElementById('compare-toggle');
    const compareEnabled = compareToggle ? compareToggle.checked : false;

    // Calculate comparison data if enabled
    let comparisonData = null;
    let comparisonPeriod = null;
    if (compareEnabled && data && data.all_transactions) {
        comparisonPeriod = calculateComparisonPeriod(period, data.current_year || new Date().getFullYear());
        if (comparisonPeriod) {
            const currentYear = data.current_year || new Date().getFullYear();
            const comparisonTransactions = filterTransactionsByPeriod(data.all_transactions, comparisonPeriod, currentYear);
            const comparisonCategories = getCategoryBreakdowns(comparisonTransactions, 10000);
            comparisonData = comparisonCategories;
        }
    }

    // Update comparison summary
    updateCategoryComparisonSummary(categories, comparisonData, comparisonPeriod, data, period);

    // Show/hide comparison columns
    const comparisonColumns = document.querySelectorAll('.comparison-column');
    comparisonColumns.forEach(col => {
        col.style.display = compareEnabled ? '' : 'none';
    });

    // Get selected filter type
    const selectedFilter = document.querySelector('input[name="type-filter"]:checked');
    const filterType = selectedFilter ? selectedFilter.value : 'both';

    // Separate into income and expenses
    const incomeCategories = categories.filter(cat => cat.total > 0);
    const expenseCategories = categories.filter(cat => cat.total < 0);

    // Sort by absolute amount
    incomeCategories.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
    expenseCategories.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));

    // Take top 10 for each chart
    const topIncome = incomeCategories.slice(0, 10);
    const topExpenses = expenseCategories.slice(0, 10);

    // Get chart containers for showing/hiding
    const incomeChartContainer = document.querySelector('.counterparty-charts-grid > div:first-child');
    const expenseChartContainer = document.querySelector('.counterparty-charts-grid > div:last-child');

    // Show/hide charts based on filter
    if (filterType === 'income') {
        if (incomeChartContainer) incomeChartContainer.style.display = 'block';
        if (expenseChartContainer) expenseChartContainer.style.display = 'none';
    } else if (filterType === 'expense') {
        if (incomeChartContainer) incomeChartContainer.style.display = 'none';
        if (expenseChartContainer) expenseChartContainer.style.display = 'block';
    } else {
        // both
        if (incomeChartContainer) incomeChartContainer.style.display = 'block';
        if (expenseChartContainer) expenseChartContainer.style.display = 'block';
    }

    // Update income chart
    const incomeCtx = document.getElementById('incomeChart');
    if (incomeCtx && (filterType === 'both' || filterType === 'income')) {
        if (categoryIncomeChart) {
            categoryIncomeChart.destroy();
        }
        if (topIncome.length > 0) {
            categoryIncomeChart = createDoughnutChart('incomeChart', {
                labels: topIncome.map(cat => cat.name),
                datasets: [{
                    data: topIncome.map(cat => cat.total),
                    backgroundColor: generateColors(topIncome.length)
                }]
            });
        } else {
            // Clear chart if no data
            if (categoryIncomeChart) {
                categoryIncomeChart.destroy();
                categoryIncomeChart = null;
            }
        }
    } else if (incomeCtx && filterType === 'expense') {
        // Destroy chart if not showing
        if (categoryIncomeChart) {
            categoryIncomeChart.destroy();
            categoryIncomeChart = null;
        }
    }

    // Update expense chart
    const expenseCtx = document.getElementById('expenseChart');
    if (expenseCtx && (filterType === 'both' || filterType === 'expense')) {
        if (categoryExpenseChart) {
            categoryExpenseChart.destroy();
        }
        if (topExpenses.length > 0) {
            categoryExpenseChart = createDoughnutChart('expenseChart', {
                labels: topExpenses.map(cat => cat.name),
                datasets: [{
                    data: topExpenses.map(cat => Math.abs(cat.total)),
                    backgroundColor: generateColors(topExpenses.length)
                }]
            });
        } else {
            // Clear chart if no data
            if (categoryExpenseChart) {
                categoryExpenseChart.destroy();
                categoryExpenseChart = null;
            }
        }
    } else if (expenseCtx && filterType === 'income') {
        // Destroy chart if not showing
        if (categoryExpenseChart) {
            categoryExpenseChart.destroy();
            categoryExpenseChart = null;
        }
    }

    // Update table with filtered data
    const tbody = document.getElementById('categories-tbody');
    if (tbody) {
        let filteredCategories = categories;
        if (filterType === 'income') {
            filteredCategories = incomeCategories;
        } else if (filterType === 'expense') {
            filteredCategories = expenseCategories;
        }
        renderCategoriesTable(tbody, filteredCategories, comparisonData, data, period);
    }
}

function renderCategoriesTable(tbody, categories, comparisonData = null, data = null, period = null) {
    const compareEnabled = comparisonData !== null;
    const colSpan = compareEnabled ? 12 : 9; // Updated for new columns: Category, Total, % of Total, % of Income, % of Expenses, Count, Avg Amount, Avg/Month, Trend (+ 3 comparison columns)

    if (categories.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${colSpan}" style="text-align: center; padding: 2rem; color: #7f8c8d;">No categories found</td></tr>`;
        return;
    }

    // Group categories by base category and tags FIRST
    const categoryMap = {};
    const tagMap = {};

    categories.forEach(cat => {
        const categoryName = cat.name || '';
        if (categoryName.includes(':')) {
            // This is a tag (category:tag)
            const [baseCat, tag] = categoryName.split(':', 2);
            if (!tagMap[baseCat]) {
                tagMap[baseCat] = [];
            }
            tagMap[baseCat].push({ tag: tag, total: cat.total, count: cat.count });
        } else {
            // This is a base category
            categoryMap[categoryName] = { total: cat.total, count: cat.count };
        }
    });

    // Calculate totals for percentage calculations
    // Use the original categories array (before grouping) to ensure we calculate
    // percentages from the exact same filtered data that will be displayed in the table.
    // This ensures percentages sum to 100% (within rounding).
    let totalAbsolute = 0;
    let totalIncome = 0;
    let totalExpenses = 0;

    categories.forEach(cat => {
        const catTotal = cat.total || 0;
        totalAbsolute += Math.abs(catTotal);
        if (catTotal > 0) {
            totalIncome += catTotal;
        } else if (catTotal < 0) {
            totalExpenses += Math.abs(catTotal);
        }
    });

    // Calculate number of months in period for average per month
    let numMonths = 1;
    if (period && data && data.all_months) {
        if (period.startsWith('ytd')) {
            // Count months in current year that have data
            const currentYear = data.current_year || new Date().getFullYear();
            numMonths = Object.keys(data.all_months).filter(month => {
                const [year] = month.split('-');
                return parseInt(year) === currentYear;
            }).length;
        } else if (period.startsWith('year:')) {
            numMonths = 12;
        } else if (period.startsWith('quarter:')) {
            numMonths = 3;
        } else if (period.startsWith('month:')) {
            numMonths = 1;
        }
    }

    // Create comparison map for quick lookup
    const comparisonMap = {};
    if (comparisonData) {
        comparisonData.forEach(cat => {
            comparisonMap[cat.name] = cat;
        });
    }

    // Handle base categories with tags (subcategories)
    // Always sum tag totals into base category totals, regardless of whether base category has direct transactions
    // This ensures parent category totals include the sum of all their subcategories
    Object.keys(tagMap).forEach(baseCatName => {
        const tagTotals = tagMap[baseCatName].reduce((sum, tagData) => sum + tagData.total, 0);
        const tagCounts = tagMap[baseCatName].reduce((sum, tagData) => sum + tagData.count, 0);

        if (!categoryMap[baseCatName]) {
            // Base category only exists as tags, create entry with sum of tag totals
            categoryMap[baseCatName] = { total: tagTotals, count: tagCounts };
        } else {
            // Base category exists - add tag totals to existing total (may have both direct transactions and tags)
            categoryMap[baseCatName].total += tagTotals;
            categoryMap[baseCatName].count += tagCounts;
        }
    });

    // Sort categories by absolute total
    const sortedCategories = Object.entries(categoryMap)
        .map(([name, data]) => ({ name, ...data }))
        .sort((a, b) => Math.abs(b.total) - Math.abs(a.total));

    // Build HTML with running totals
    let html = '';
    let runningTotal = 0;
    sortedCategories.forEach(cat => {
        const amountColor = cat.total >= 0 ? '#27ae60' : '#e74c3c';
        const sign = cat.total >= 0 ? '+' : '';
        const formattedAmount = `€${sign}${Math.abs(cat.total).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        // Percentage calculations
        const percentage = totalAbsolute > 0 ? ((Math.abs(cat.total) / totalAbsolute) * 100) : 0;
        const formattedPercentage = `${percentage.toFixed(1)}%`;

        // Percentage of income/expenses
        const pctOfIncome = cat.total > 0 && totalIncome > 0 ? ((cat.total / totalIncome) * 100) : 0;
        const formattedPctOfIncome = cat.total > 0 ? `${pctOfIncome.toFixed(1)}%` : '-';
        const pctOfExpenses = cat.total < 0 && totalExpenses > 0 ? ((Math.abs(cat.total) / totalExpenses) * 100) : 0;
        const formattedPctOfExpenses = cat.total < 0 ? `${pctOfExpenses.toFixed(1)}%` : '-';

        // Average transaction amount
        const avgAmount = cat.count > 0 ? (cat.total / cat.count) : 0;
        const avgSign = avgAmount >= 0 ? '+' : '';
        const formattedAvgAmount = `€${avgSign}${Math.abs(avgAmount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        // Average per month
        const avgPerMonth = numMonths > 0 ? (cat.total / numMonths) : cat.total;
        const avgMonthSign = avgPerMonth >= 0 ? '+' : '';
        const formattedAvgPerMonth = `€${avgMonthSign}${Math.abs(avgPerMonth).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        // Running total (cumulative)
        runningTotal += cat.total;
        const runningSign = runningTotal >= 0 ? '+' : '';
        const formattedRunningTotal = `€${runningSign}${Math.abs(runningTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        const urlCat = encodeURIComponent(cat.name);

        // Get comparison data
        const compCat = comparisonMap[cat.name];
        let comparisonHtml = '';
        if (compareEnabled) {
            const prevTotal = compCat ? compCat.total : 0;
            const prevAmountColor = prevTotal >= 0 ? '#27ae60' : '#e74c3c';
            const prevSign = prevTotal >= 0 ? '+' : '';
            const formattedPrevAmount = `€${prevSign}${Math.abs(prevTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

            const change = cat.total - prevTotal;
            const changeColor = change >= 0 ? '#27ae60' : '#e74c3c';
            const changeSign = change >= 0 ? '+' : '';
            const formattedChange = `€${changeSign}${Math.abs(change).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

            const changePct = prevTotal !== 0 ? ((change / Math.abs(prevTotal)) * 100) : (change !== 0 ? (change > 0 ? 100 : -100) : 0);
            const formattedChangePct = `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%`;

            comparisonHtml = `
                <td class="text-right" style="color: ${prevAmountColor};">${formattedPrevAmount}</td>
                <td class="text-right" style="color: ${changeColor}; font-weight: 600;">${formattedChange}</td>
                <td class="text-right" style="color: ${changeColor}; font-weight: 600;">${formattedChangePct}</td>
            `;
        }

        // Generate sparkline data for this category
        const sparklineData = getCategorySparklineData(cat.name, data, cat.total);
        const sparklineHtml = sparklineData ? `<canvas class="sparkline" data-sparkline="${btoa(JSON.stringify(sparklineData))}" width="100" height="20" style="max-width: 100px;"></canvas>` : '<span style="color: #bdc3c7;">-</span>';

        html += `
            <tr class="drill-down-row" data-category="${escapeHtmlForTable(cat.name)}" data-type="category">
                <td class="expand-icon" style="cursor: pointer; text-align: center; user-select: none;">▶</td>
                <td><a href="category_trends.html?category=${urlCat}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cat.name)}</a></td>
                <td class="text-right" style="color: ${amountColor}; font-weight: 600;">${formattedAmount}</td>
                <td class="text-right" style="color: #7f8c8d;">${formattedPercentage}</td>
                <td class="text-right" style="color: ${cat.total > 0 ? '#27ae60' : '#bdc3c7'}; font-size: 0.9rem;">${formattedPctOfIncome}</td>
                <td class="text-right" style="color: ${cat.total < 0 ? '#e74c3c' : '#bdc3c7'}; font-size: 0.9rem;">${formattedPctOfExpenses}</td>
                <td class="text-center">${cat.count || 0}</td>
                <td class="text-right" style="color: ${amountColor}; font-size: 0.9rem;">${formattedAvgAmount}</td>
                <td class="text-right" style="color: ${amountColor}; font-size: 0.9rem;">${formattedAvgPerMonth}</td>
                <td class="text-center">${sparklineHtml}</td>
                ${comparisonHtml}
            </tr>
            <tr class="drill-down-detail" data-parent="${escapeHtmlForTable(cat.name)}" style="display: none;">
                <td colspan="${colSpan + 1}" style="padding: 1rem; background: #f8f9fa; border-top: 2px solid #3498db;">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; color: #34495e;">Counterparties for "${escapeHtmlForTable(cat.name)}":</div>
                    <div class="drill-down-content" style="min-height: 50px; color: #7f8c8d;">Loading...</div>
                </td>
            </tr>
        `;

        // Add tags if present
        if (tagMap[cat.name]) {
            const sortedTags = tagMap[cat.name].sort((a, b) => Math.abs(b.total) - Math.abs(a.total));
            sortedTags.forEach(tagData => {
                const tagAmountColor = tagData.total >= 0 ? '#27ae60' : '#e74c3c';
                const tagSign = tagData.total >= 0 ? '+' : '';
                const formattedTagAmount = `€${tagSign}${Math.abs(tagData.total).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
                const tagPercentage = totalAbsolute > 0 ? ((Math.abs(tagData.total) / totalAbsolute) * 100) : 0;
                const formattedTagPercentage = `${tagPercentage.toFixed(1)}%`;

                // Percentage of income/expenses for tag
                const tagPctOfIncome = tagData.total > 0 && totalIncome > 0 ? ((tagData.total / totalIncome) * 100) : 0;
                const formattedTagPctOfIncome = tagData.total > 0 ? `${tagPctOfIncome.toFixed(1)}%` : '-';
                const tagPctOfExpenses = tagData.total < 0 && totalExpenses > 0 ? ((Math.abs(tagData.total) / totalExpenses) * 100) : 0;
                const formattedTagPctOfExpenses = tagData.total < 0 ? `${tagPctOfExpenses.toFixed(1)}%` : '-';

                // Average transaction amount for tag
                const tagAvgAmount = tagData.count > 0 ? (tagData.total / tagData.count) : 0;
                const tagAvgSign = tagAvgAmount >= 0 ? '+' : '';
                const formattedTagAvgAmount = `€${tagAvgSign}${Math.abs(tagAvgAmount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

                // Average per month for tag
                const tagAvgPerMonth = numMonths > 0 ? (tagData.total / numMonths) : tagData.total;
                const tagAvgMonthSign = tagAvgPerMonth >= 0 ? '+' : '';
                const formattedTagAvgPerMonth = `€${tagAvgMonthSign}${Math.abs(tagAvgPerMonth).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

                const urlTag = encodeURIComponent(tagData.tag);
                const fullCategoryTag = `${cat.name}:${tagData.tag}`;

                // Get comparison data for tag
                let tagComparisonHtml = '';
                if (compareEnabled) {
                    const compTag = comparisonMap[fullCategoryTag];
                    const prevTagTotal = compTag ? compTag.total : 0;
                    const prevTagAmountColor = prevTagTotal >= 0 ? '#27ae60' : '#e74c3c';
                    const prevTagSign = prevTagTotal >= 0 ? '+' : '';
                    const formattedPrevTagAmount = `€${prevTagSign}${Math.abs(prevTagTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

                    const tagChange = tagData.total - prevTagTotal;
                    const tagChangeColor = tagChange >= 0 ? '#27ae60' : '#e74c3c';
                    const tagChangeSign = tagChange >= 0 ? '+' : '';
                    const formattedTagChange = `€${tagChangeSign}${Math.abs(tagChange).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

                    const tagChangePct = prevTagTotal !== 0 ? ((tagChange / Math.abs(prevTagTotal)) * 100) : (tagChange !== 0 ? (tagChange > 0 ? 100 : -100) : 0);
                    const formattedTagChangePct = `${tagChangePct >= 0 ? '+' : ''}${tagChangePct.toFixed(1)}%`;

                    tagComparisonHtml = `
                        <td class="text-right" style="color: ${prevTagAmountColor};">${formattedPrevTagAmount}</td>
                        <td class="text-right" style="color: ${tagChangeColor}; font-weight: 600;">${formattedTagChange}</td>
                        <td class="text-right" style="color: ${tagChangeColor}; font-weight: 600;">${formattedTagChangePct}</td>
                    `;
                }

                // Generate sparkline for tag
                const tagSparklineData = getCategorySparklineData(fullCategoryTag, data, tagData.total);
                const tagSparklineHtml = tagSparklineData ? `<canvas class="sparkline" data-sparkline="${btoa(JSON.stringify(tagSparklineData))}" width="100" height="20" style="max-width: 100px;"></canvas>` : '<span style="color: #bdc3c7;">-</span>';

                html += `
                    <tr style="background-color: #f8f9fa;">
                        <td></td>
                        <td style="padding-left: 2rem;">└─ <a href="category_trends.html?category=${urlCat}&tag=${urlTag}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(tagData.tag)}</a></td>
                        <td class="text-right" style="color: ${tagAmountColor}; font-weight: 600;">${formattedTagAmount}</td>
                        <td class="text-right" style="color: #7f8c8d;">${formattedTagPercentage}</td>
                        <td class="text-right" style="color: ${tagData.total > 0 ? '#27ae60' : '#bdc3c7'}; font-size: 0.9rem;">${formattedTagPctOfIncome}</td>
                        <td class="text-right" style="color: ${tagData.total < 0 ? '#e74c3c' : '#bdc3c7'}; font-size: 0.9rem;">${formattedTagPctOfExpenses}</td>
                        <td class="text-center">${tagData.count || 0}</td>
                        <td class="text-right" style="color: ${tagAmountColor}; font-size: 0.9rem;">${formattedTagAvgAmount}</td>
                        <td class="text-right" style="color: ${tagAmountColor}; font-size: 0.9rem;">${formattedTagAvgPerMonth}</td>
                        <td class="text-center">${tagSparklineHtml}</td>
                        ${tagComparisonHtml}
                    </tr>
                `;
            });
        }
    });

    tbody.innerHTML = html;

    // Render sparklines after a short delay to ensure DOM is updated
    setTimeout(renderSparklines, 100);

    // Initialize drill-down handlers
    initializeDrillDownHandlers(data);
}

// Comparison summary functions
function updateCategoryComparisonSummary(categories, comparisonData, comparisonPeriod, data = null, period = null) {
    const summaryContainer = document.getElementById('category-comparison-summary');
    if (!summaryContainer) return;

    const compareToggle = document.getElementById('compare-toggle');
    const compareEnabled = compareToggle ? compareToggle.checked : false;

    if (!compareEnabled || !comparisonData) {
        summaryContainer.style.display = 'none';
        // Hide insights container
        const insightsContainer = document.getElementById('category-insights-container');
        if (insightsContainer) insightsContainer.style.display = 'none';
        return;
    }

    summaryContainer.style.display = 'block';

    // Calculate totals
    const currentTotal = categories.reduce((sum, cat) => sum + (cat.total || 0), 0);
    const comparisonTotal = comparisonData.reduce((sum, cat) => sum + (cat.total || 0), 0);
    const change = currentTotal - comparisonTotal;
    const changePct = comparisonTotal !== 0 ? ((change / Math.abs(comparisonTotal)) * 100) : (change !== 0 ? (change > 0 ? 100 : -100) : 0);

    // Update summary cards
    const currentEl = document.getElementById('category-current-total');
    const comparisonEl = document.getElementById('category-comparison-total');
    const changeEl = document.getElementById('category-change-total');
    const changePctEl = document.getElementById('category-change-pct');
    const labelEl = document.getElementById('category-comparison-label');

    if (currentEl) {
        const sign = currentTotal >= 0 ? '+' : '-';
        currentEl.textContent = `€${sign}${Math.abs(currentTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        currentEl.className = 'metric-value ' + (currentTotal >= 0 ? 'positive' : 'negative');
    }

    if (comparisonEl) {
        const sign = comparisonTotal >= 0 ? '+' : '-';
        comparisonEl.textContent = `€${sign}${Math.abs(comparisonTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        comparisonEl.className = 'metric-value ' + (comparisonTotal >= 0 ? 'positive' : 'negative');
    }

    if (changeEl) {
        const sign = change >= 0 ? '+' : '-';
        changeEl.textContent = `€${sign}${Math.abs(change).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        changeEl.className = 'metric-value ' + (change >= 0 ? 'positive' : 'negative');
    }

    if (changePctEl) {
        changePctEl.textContent = `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%`;
        changePctEl.className = 'metric-value ' + (changePct >= 0 ? 'positive' : 'negative');
    }

    if (labelEl) {
        labelEl.textContent = formatComparisonPeriodLabel(comparisonPeriod);
    }

    // Update insights
    if (data && period) {
        updateCategoryInsights(categories, comparisonData, data, period);
    }
}

function updateCounterpartyComparisonSummary(counterparties, comparisonData, comparisonPeriod, data = null, period = null) {
    const summaryContainer = document.getElementById('counterparty-comparison-summary');
    if (!summaryContainer) return;

    const compareToggle = document.getElementById('compare-toggle');
    const compareEnabled = compareToggle ? compareToggle.checked : false;

    if (!compareEnabled || !comparisonData) {
        summaryContainer.style.display = 'none';
        // Hide insights container
        const insightsContainer = document.getElementById('counterparty-insights-container');
        if (insightsContainer) insightsContainer.style.display = 'none';
        return;
    }

    summaryContainer.style.display = 'block';

    // Calculate totals
    const currentTotal = counterparties.reduce((sum, cp) => sum + (cp.total || 0), 0);
    const comparisonTotal = comparisonData.reduce((sum, cp) => sum + (cp.total || 0), 0);
    const change = currentTotal - comparisonTotal;
    const changePct = comparisonTotal !== 0 ? ((change / Math.abs(comparisonTotal)) * 100) : (change !== 0 ? (change > 0 ? 100 : -100) : 0);

    // Update summary cards
    const currentEl = document.getElementById('counterparty-current-total');
    const comparisonEl = document.getElementById('counterparty-comparison-total');
    const changeEl = document.getElementById('counterparty-change-total');
    const changePctEl = document.getElementById('counterparty-change-pct');
    const labelEl = document.getElementById('counterparty-comparison-label');

    if (currentEl) {
        const sign = currentTotal >= 0 ? '+' : '-';
        currentEl.textContent = `€${sign}${Math.abs(currentTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        currentEl.className = 'metric-value ' + (currentTotal >= 0 ? 'positive' : 'negative');
    }

    if (comparisonEl) {
        const sign = comparisonTotal >= 0 ? '+' : '-';
        comparisonEl.textContent = `€${sign}${Math.abs(comparisonTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        comparisonEl.className = 'metric-value ' + (comparisonTotal >= 0 ? 'positive' : 'negative');
    }

    if (changeEl) {
        const sign = change >= 0 ? '+' : '-';
        changeEl.textContent = `€${sign}${Math.abs(change).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        changeEl.className = 'metric-value ' + (change >= 0 ? 'positive' : 'negative');
    }

    if (changePctEl) {
        changePctEl.textContent = `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%`;
        changePctEl.className = 'metric-value ' + (changePct >= 0 ? 'positive' : 'negative');
    }

    if (labelEl) {
        labelEl.textContent = formatComparisonPeriodLabel(comparisonPeriod);
    }

    // Update comparison chart
    updateCounterpartyComparisonChart(counterparties, comparisonData, comparisonPeriod);

    // Update insights
    if (data && period) {
        updateCounterpartyInsights(counterparties, comparisonData, data, period);
    }
}

function updateCategoryComparisonChart(categories, comparisonData, comparisonPeriod) {
    const chartEl = document.getElementById('categoryComparisonChart');
    if (!chartEl) return;

    const compareToggle = document.getElementById('compare-toggle');
    const compareEnabled = compareToggle ? compareToggle.checked : false;

    if (!compareEnabled || !comparisonData) {
        if (window.categoryComparisonChart) {
            window.categoryComparisonChart.destroy();
            window.categoryComparisonChart = null;
        }
        return;
    }

    // Get top 10 categories for comparison
    const topCategories = [...categories]
        .sort((a, b) => Math.abs(b.total) - Math.abs(a.total))
        .slice(0, 10);

    const labels = topCategories.map(cat => cat.name);
    const currentValues = topCategories.map(cat => cat.total || 0);
    const comparisonValues = topCategories.map(cat => {
        const compCat = comparisonData.find(c => c.name === cat.name);
        return compCat ? compCat.total : 0;
    });

    if (window.categoryComparisonChart) {
        window.categoryComparisonChart.destroy();
    }

    window.categoryComparisonChart = new Chart(chartEl, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Current Period',
                    data: currentValues,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgb(52, 152, 219)',
                    borderWidth: 1
                },
                {
                    label: formatComparisonPeriodLabel(comparisonPeriod),
                    data: comparisonValues,
                    backgroundColor: 'rgba(149, 165, 166, 0.7)',
                    borderColor: 'rgb(149, 165, 166)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

function updateCounterpartyComparisonChart(counterparties, comparisonData, comparisonPeriod) {
    const chartEl = document.getElementById('counterpartyComparisonChart');
    if (!chartEl) return;

    const compareToggle = document.getElementById('compare-toggle');
    const compareEnabled = compareToggle ? compareToggle.checked : false;

    if (!compareEnabled || !comparisonData) {
        if (window.counterpartyComparisonChart) {
            window.counterpartyComparisonChart.destroy();
            window.counterpartyComparisonChart = null;
        }
        return;
    }

    // Get top 10 counterparties for comparison
    const topCounterparties = [...counterparties]
        .sort((a, b) => Math.abs(b.total) - Math.abs(a.total))
        .slice(0, 10);

    const labels = topCounterparties.map(cp => cp.name);
    const currentValues = topCounterparties.map(cp => cp.total || 0);
    const comparisonValues = topCounterparties.map(cp => {
        const compCp = comparisonData.find(c => c.name === cp.name);
        return compCp ? compCp.total : 0;
    });

    if (window.counterpartyComparisonChart) {
        window.counterpartyComparisonChart.destroy();
    }

    window.counterpartyComparisonChart = new Chart(chartEl, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Current Period',
                    data: currentValues,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgb(52, 152, 219)',
                    borderWidth: 1
                },
                {
                    label: formatComparisonPeriodLabel(comparisonPeriod),
                    data: comparisonValues,
                    backgroundColor: 'rgba(149, 165, 166, 0.7)',
                    borderColor: 'rgb(149, 165, 166)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// Sparkline helper functions
function getCategorySparklineData(categoryName, data, totalAmount = null) {
    if (!data || !data.all_months) return null;

    const months = Object.keys(data.all_months).sort();
    const last12Months = months.slice(-12); // Last 12 months

    // Check if this is a tag (format: "category:tag")
    const isTag = categoryName.includes(':');
    let baseCategory = categoryName;
    let tag = null;

    if (isTag) {
        [baseCategory, tag] = categoryName.split(':', 2);
    }

    const values = last12Months.map(month => {
        const monthData = data.all_months[month];
        if (!monthData || !monthData.breakdown) return 0;

        const categoryData = monthData.breakdown[baseCategory];
        if (!categoryData) return 0;

        // If this is a tag, look in the tags structure
        if (isTag && tag && categoryData.tags && categoryData.tags[tag]) {
            const tagData = categoryData.tags[tag];
            return Math.abs(tagData.total || 0);
        } else if (!isTag) {
            // Base category - use the category total
            return Math.abs(categoryData.total || 0);
        }

        return 0;
    });

    // Determine if this is primarily an expense category
    // If totalAmount is provided, use it; otherwise check the last value's original sign
    let lastValue = 0;
    if (last12Months.length > 0) {
        const lastMonth = data.all_months[last12Months[last12Months.length - 1]];
        if (lastMonth && lastMonth.breakdown) {
            const categoryData = lastMonth.breakdown[baseCategory];
            if (categoryData) {
                if (isTag && tag && categoryData.tags && categoryData.tags[tag]) {
                    lastValue = categoryData.tags[tag].total || 0;
                } else if (!isTag) {
                    lastValue = categoryData.total || 0;
                }
            }
        }
    }

    const isExpense = totalAmount !== null ? totalAmount < 0 : lastValue < 0;

    return { values, labels: last12Months, isExpense };
}

function getCounterpartySparklineData(counterpartyName, data, totalAmount = null) {
    if (!data || !data.all_months || !data.all_transactions) return null;

    const months = Object.keys(data.all_months).sort();
    const last12Months = months.slice(-12);

    const values = last12Months.map(month => {
        const monthTransactions = data.all_transactions.filter(tx =>
            tx.date && tx.date.startsWith(month)
        );

        const counterpartyTransactions = monthTransactions.filter(tx => {
            const txCounterparty = normalizeCounterpartyNameForGrouping(tx.counterparty || '');
            const cpName = normalizeCounterpartyNameForGrouping(counterpartyName);
            return txCounterparty === cpName;
        });

        const total = counterpartyTransactions.reduce((sum, tx) => sum + (tx.amount || 0), 0);
        // Use absolute values to match trend chart behavior (expenses go upward)
        return Math.abs(total);
    });

    // Determine if this is primarily an expense counterparty
    // If totalAmount is provided, use it; otherwise check the last month's total
    let isExpense = false;
    if (totalAmount !== null) {
        isExpense = totalAmount < 0;
    } else {
        const lastMonth = last12Months[last12Months.length - 1];
        const monthTransactions = data.all_transactions.filter(tx =>
            tx.date && tx.date.startsWith(lastMonth)
        );
        const counterpartyTransactions = monthTransactions.filter(tx => {
            const txCounterparty = normalizeCounterpartyNameForGrouping(tx.counterparty || '');
            const cpName = normalizeCounterpartyNameForGrouping(counterpartyName);
            return txCounterparty === cpName;
        });
        const lastMonthTotal = counterpartyTransactions.reduce((sum, tx) => sum + (tx.amount || 0), 0);
        isExpense = lastMonthTotal < 0;
    }

    return { values, labels: last12Months, isExpense };
}

// Render sparklines after table is rendered
function renderSparklines() {
    const sparklines = document.querySelectorAll('.sparkline');
    sparklines.forEach(canvas => {
        try {
            const dataStr = canvas.getAttribute('data-sparkline');
            if (!dataStr) return;

            const sparklineData = JSON.parse(atob(dataStr));
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;

            ctx.clearRect(0, 0, width, height);

            if (!sparklineData.values || sparklineData.values.length === 0) return;

            const values = sparklineData.values;
            const min = Math.min(...values);
            const max = Math.max(...values);
            const range = max - min || 1;

            // Use isExpense flag if available, otherwise fall back to checking last value
            // Since we now use absolute values, we need the isExpense flag to determine color
            const isExpense = sparklineData.isExpense !== undefined ? sparklineData.isExpense : false;
            ctx.strokeStyle = isExpense ? '#e74c3c' : '#27ae60';
            ctx.lineWidth = 1;
            ctx.beginPath();

            values.forEach((val, idx) => {
                const x = (idx / (values.length - 1)) * width;
                const y = height - ((val - min) / range) * height;

                if (idx === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });

            ctx.stroke();
        } catch (e) {
            console.error('Error rendering sparkline:', e);
        }
    });
}

// Insights functions for categories and counterparties
function calculateCategoryInsights(categories, comparisonData, data, period) {
    const insights = [];
    if (!comparisonData || categories.length === 0) return insights;

    // Create comparison map
    const comparisonMap = {};
    comparisonData.forEach(cat => {
        comparisonMap[cat.name] = cat;
    });

    // Calculate total for percentage
    const totalAbsolute = categories.reduce((sum, cat) => sum + Math.abs(cat.total || 0), 0);
    const comparisonTotalAbsolute = comparisonData.reduce((sum, cat) => sum + Math.abs(cat.total || 0), 0);

    // Find anomalies (significant changes >50%)
    categories.forEach(cat => {
        const compCat = comparisonMap[cat.name];
        if (!compCat) return;

        const prevTotal = Math.abs(compCat.total || 0);
        const currentTotal = Math.abs(cat.total || 0);

        if (prevTotal > 0) {
            const changePct = ((currentTotal - prevTotal) / prevTotal) * 100;
            if (Math.abs(changePct) >= 50) {
                insights.push({
                    type: changePct > 0 ? 'warning' : 'positive',
                    message: `${escapeHtmlForTable(cat.name)} ${changePct > 0 ? 'increased' : 'decreased'} by ${Math.abs(changePct).toFixed(0)}%`,
                    icon: changePct > 0 ? '⚠️' : '✅'
                });
            }
        }
    });

    // Find major contributors (>20% of total)
    categories.forEach(cat => {
        const percentage = totalAbsolute > 0 ? ((Math.abs(cat.total) / totalAbsolute) * 100) : 0;
        if (percentage >= 20) {
            insights.push({
                type: 'info',
                message: `${escapeHtmlForTable(cat.name)} represents ${percentage.toFixed(1)}% of total`,
                icon: '📊'
            });
        }
    });

    // Find growth trends (accelerating/decelerating)
    // This requires historical data - simplified version
    if (data && data.all_months) {
        const months = Object.keys(data.all_months).sort();
        const recentMonths = months.slice(-3); // Last 3 months

        if (recentMonths.length >= 2) {
            categories.slice(0, 5).forEach(cat => { // Check top 5 categories
                const values = recentMonths.map(month => {
                    const monthData = data.all_months[month];
                    if (!monthData || !monthData.breakdown) return 0;
                    const catData = monthData.breakdown[cat.name];
                    return catData ? Math.abs(catData.total || 0) : 0;
                });

                if (values.length >= 2 && values[0] > 0) {
                    const growth1 = values[1] > 0 ? ((values[1] - values[0]) / values[0]) * 100 : 0;
                    const growth2 = values[2] > 0 && values[1] > 0 ? ((values[2] - values[1]) / values[1]) * 100 : 0;

                    if (Math.abs(growth1) > 10 && Math.abs(growth2) > 10) {
                        const isAccelerating = (growth2 > growth1 && growth2 > 0) || (growth2 < growth1 && growth2 < 0);
                        if (isAccelerating) {
                            insights.push({
                                type: 'warning',
                                message: `${escapeHtmlForTable(cat.name)} shows ${growth2 > 0 ? 'accelerating' : 'decelerating'} growth trend`,
                                icon: growth2 > 0 ? '📈' : '📉'
                            });
                        }
                    }
                }
            });
        }
    }

    return insights.slice(0, 5); // Limit to 5 insights
}

function updateCategoryInsights(categories, comparisonData, data, period) {
    const insightsContainer = document.getElementById('category-insights-container');
    const insightsContent = document.getElementById('category-insights-content');
    if (!insightsContainer || !insightsContent) return;

    const insights = calculateCategoryInsights(categories, comparisonData, data, period);

    if (insights.length === 0) {
        insightsContainer.style.display = 'none';
        return;
    }

    insightsContainer.style.display = 'block';
    insightsContent.innerHTML = insights.map(insight => {
        const bgColor = insight.type === 'positive' ? '#d5f4e6' : insight.type === 'negative' ? '#fadbd8' : insight.type === 'warning' ? '#fff3cd' : '#d1ecf1';
        const textColor = insight.type === 'positive' ? '#27ae60' : insight.type === 'negative' ? '#e74c3c' : insight.type === 'warning' ? '#856404' : '#0c5460';
        const borderColor = insight.type === 'positive' ? '#27ae60' : insight.type === 'negative' ? '#e74c3c' : insight.type === 'warning' ? '#ffc107' : '#17a2b8';

        return `
            <span style="padding: 0.5rem 0.75rem; background-color: ${bgColor}; border-left: 3px solid ${borderColor}; border-radius: 4px; display: inline-flex; align-items: center; gap: 0.5rem; white-space: nowrap;">
                <span style="font-size: 1.1rem;">${insight.icon}</span>
                <span style="color: ${textColor}; font-size: 0.9rem;">${insight.message}</span>
            </span>
        `;
    }).join('');
}

function calculateCounterpartyInsights(counterparties, comparisonData, data, period) {
    const insights = [];
    if (!comparisonData || counterparties.length === 0) return insights;

    // Create comparison map
    const comparisonMap = {};
    comparisonData.forEach(cp => {
        comparisonMap[cp.name] = cp;
    });

    // Calculate total for percentage
    const totalAbsolute = counterparties.reduce((sum, cp) => sum + Math.abs(cp.total || 0), 0);
    const comparisonTotalAbsolute = comparisonData.reduce((sum, cp) => sum + Math.abs(cp.total || 0), 0);

    // Find anomalies (significant changes >50%)
    counterparties.forEach(cp => {
        const compCp = comparisonMap[cp.name];
        if (!compCp) return;

        const prevTotal = Math.abs(compCp.total || 0);
        const currentTotal = Math.abs(cp.total || 0);

        if (prevTotal > 0) {
            const changePct = ((currentTotal - prevTotal) / prevTotal) * 100;
            if (Math.abs(changePct) >= 50) {
                insights.push({
                    type: changePct > 0 ? 'warning' : 'positive',
                    message: `${escapeHtmlForTable(cp.name)} ${changePct > 0 ? 'increased' : 'decreased'} by ${Math.abs(changePct).toFixed(0)}%`,
                    icon: changePct > 0 ? '⚠️' : '✅'
                });
            }
        }
    });

    // Find major contributors (>20% of total)
    counterparties.forEach(cp => {
        const percentage = totalAbsolute > 0 ? ((Math.abs(cp.total) / totalAbsolute) * 100) : 0;
        if (percentage >= 20) {
            insights.push({
                type: 'info',
                message: `${escapeHtmlForTable(cp.name)} represents ${percentage.toFixed(1)}% of total`,
                icon: '📊'
            });
        }
    });

    return insights.slice(0, 5); // Limit to 5 insights
}

function updateCounterpartyInsights(counterparties, comparisonData, data, period) {
    const insightsContainer = document.getElementById('counterparty-insights-container');
    const insightsContent = document.getElementById('counterparty-insights-content');
    if (!insightsContainer || !insightsContent) return;

    const insights = calculateCounterpartyInsights(counterparties, comparisonData, data, period);

    if (insights.length === 0) {
        insightsContainer.style.display = 'none';
        return;
    }

    insightsContainer.style.display = 'block';
    insightsContent.innerHTML = insights.map(insight => {
        const bgColor = insight.type === 'positive' ? '#d5f4e6' : insight.type === 'negative' ? '#fadbd8' : insight.type === 'warning' ? '#fff3cd' : '#d1ecf1';
        const textColor = insight.type === 'positive' ? '#27ae60' : insight.type === 'negative' ? '#e74c3c' : insight.type === 'warning' ? '#856404' : '#0c5460';
        const borderColor = insight.type === 'positive' ? '#27ae60' : insight.type === 'negative' ? '#e74c3c' : insight.type === 'warning' ? '#ffc107' : '#17a2b8';

        return `
            <span style="padding: 0.5rem 0.75rem; background-color: ${bgColor}; border-left: 3px solid ${borderColor}; border-radius: 4px; display: inline-flex; align-items: center; gap: 0.5rem; white-space: nowrap;">
                <span style="font-size: 1.1rem;">${insight.icon}</span>
                <span style="color: ${textColor}; font-size: 0.9rem;">${insight.message}</span>
            </span>
        `;
    }).join('');
}

// Filtering functions for categories and counterparties
function applyCategoryFilters(data, period) {
    if (!data.all_transactions) {
        updateCategoriesView(data, period);
        return;
    }

    const currentYear = data.current_year || new Date().getFullYear();
    let filteredTransactions = filterTransactionsByPeriod(data.all_transactions, period, currentYear);

    // Apply search filter
    const searchInput = document.getElementById('category-search');
    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
    if (searchTerm) {
        filteredTransactions = filteredTransactions.filter(tx => {
            const category = (tx.category || '').toLowerCase();
            return category.includes(searchTerm);
        });
    }

    // Apply amount range filter
    const amountMinInput = document.getElementById('category-amount-min');
    const amountMaxInput = document.getElementById('category-amount-max');
    const minAmount = amountMinInput && amountMinInput.value ? parseFloat(amountMinInput.value) : null;
    const maxAmount = amountMaxInput && amountMaxInput.value ? parseFloat(amountMaxInput.value) : null;

    if (minAmount !== null || maxAmount !== null) {
        filteredTransactions = filteredTransactions.filter(tx => {
            const amount = tx.amount || 0;
            if (minAmount !== null && amount < minAmount) return false;
            if (maxAmount !== null && amount > maxAmount) return false;
            return true;
        });
    }

    const categories = getCategoryBreakdowns(filteredTransactions, 10000);
    updateCategoriesChartsAndTable(categories, data, period);
}

function applyCounterpartyFilters(data, period) {
    if (!data.all_transactions) {
        updateCounterpartiesView(data, period);
        return;
    }

    const currentYear = data.current_year || new Date().getFullYear();
    let filteredTransactions = filterTransactionsByPeriod(data.all_transactions, period, currentYear);

    // Apply search filter
    const searchInput = document.getElementById('counterparty-search');
    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
    if (searchTerm) {
        filteredTransactions = filteredTransactions.filter(tx => {
            const counterparty = (tx.counterparty || '').toLowerCase();
            return counterparty.includes(searchTerm);
        });
    }

    // Apply amount range filter
    const amountMinInput = document.getElementById('counterparty-amount-min');
    const amountMaxInput = document.getElementById('counterparty-amount-max');
    const minAmount = amountMinInput && amountMinInput.value ? parseFloat(amountMinInput.value) : null;
    const maxAmount = amountMaxInput && amountMaxInput.value ? parseFloat(amountMaxInput.value) : null;

    if (minAmount !== null || maxAmount !== null) {
        filteredTransactions = filteredTransactions.filter(tx => {
            const amount = tx.amount || 0;
            if (minAmount !== null && amount < minAmount) return false;
            if (maxAmount !== null && amount > maxAmount) return false;
            return true;
        });
    }

    const counterparties = getCounterpartyBreakdowns(filteredTransactions, 10000);
    updateCounterpartiesChartsAndTable(counterparties, data, period);
}

function filterCategoryTable() {
    const searchInput = document.getElementById('category-table-search');
    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const tbody = document.getElementById('categories-tbody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (searchTerm === '' || text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function filterCounterpartyTable() {
    const searchInput = document.getElementById('counterparty-table-search');
    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const tbody = document.getElementById('counterparties-tbody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (searchTerm === '' || text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Overview period selector functionality
let overviewChart = null;

function initializeOverviewPeriodSelector(data) {
    const periodSelector = document.getElementById('overview-period-selector');
    if (!periodSelector) return;

    // Add change handler
    periodSelector.addEventListener('change', function() {
        updateOverviewView(data, this.value);
    });
}

function updateOverviewView(data, viewType) {
    // Hide all views first
    document.getElementById('overview-month-view').style.display = 'none';
    document.getElementById('overview-ytd-view').style.display = 'none';
    document.getElementById('overview-12m-view').style.display = 'none';
    document.getElementById('overview-month-comparison').style.display = 'none';
    document.getElementById('overview-month-categories').style.display = 'none';
    document.getElementById('overview-month-counterparties').style.display = 'none';
    document.getElementById('overview-12m-table').style.display = 'none';

    const chartTitle = document.getElementById('overview-chart-title');

    if (viewType === 'month') {
        // Show month view
        document.getElementById('overview-month-view').style.display = 'block';
        document.getElementById('overview-month-comparison').style.display = 'block';
        document.getElementById('overview-month-categories').style.display = 'block';
        document.getElementById('overview-month-counterparties').style.display = 'block';

        if (chartTitle) chartTitle.textContent = 'Monthly Trends';

        // Update chart with current month data (will be updated by month selector)
        updateOverviewMonthChart(data);
        updateOverviewMonthTables(data);

        // Initialize month selector if not already done
        if (!allMonthlyData) {
            initializeMonthSelector();
        }
    } else if (viewType === 'ytd') {
        // Show YTD view
        document.getElementById('overview-ytd-view').style.display = 'block';

        if (chartTitle) chartTitle.textContent = 'Year-to-Date Monthly Progression';

        // Update chart with YTD data
        updateOverviewYTDChart(data);
    } else if (viewType === '12m') {
        // Show 12M view
        document.getElementById('overview-12m-view').style.display = 'block';
        document.getElementById('overview-12m-table').style.display = 'block';

        if (chartTitle) chartTitle.textContent = 'Last 12 Months Trends';

        // Update chart with 12M data
        updateOverview12MChart(data);
        updateOverview12MTable(data);
    }
}

function updateOverviewMonthChart(data) {
    // This will be called by updateMonthView when month selector changes
    // Show recent trends (last 6 months)
    const ctx = document.getElementById('overviewChart');
    if (!ctx || !data.all_months) return;

    if (overviewChart) {
        overviewChart.destroy();
    }

    // Show last 6 months trend
    const allMonths = Object.keys(data.all_months).sort();
    const recentMonths = allMonths.slice(-6);

    // Prepare data in format expected by prepareMonthlyTrendData
    const monthlyTrendsData = {};
    recentMonths.forEach(month => {
        const monthData = data.all_months[month];
        if (monthData && monthData.summary) {
            monthlyTrendsData[month] = {
                total_income: monthData.summary.total_income || 0,
                total_expenses: monthData.summary.total_expenses || 0,
                net: monthData.summary.net || 0
            };
        }
    });

    const trendData = prepareMonthlyTrendData(monthlyTrendsData);
    overviewChart = createLineChart('overviewChart', trendData);
}

function updateOverviewYTDChart(data) {
    const ctx = document.getElementById('overviewChart');
    if (!ctx || !data.ytd) return;

    if (overviewChart) {
        overviewChart.destroy();
    }

    overviewChart = createLineChart('overviewChart', {
        labels: data.ytd.monthly_labels,
        datasets: [
            {
                label: 'Income',
                data: data.ytd.monthly_income,
                borderColor: 'rgb(39, 174, 96)',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                tension: 0.1
            },
            {
                label: 'Expenses',
                data: data.ytd.monthly_expenses,
                borderColor: 'rgb(231, 76, 60)',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.1
            },
            {
                label: 'Net',
                data: data.ytd.monthly_net,
                borderColor: 'rgb(52, 152, 219)',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.1
            }
        ]
    });
}

function updateOverview12MChart(data) {
    const ctx = document.getElementById('overviewChart');
    if (!ctx || !data.trends_12m) return;

    if (overviewChart) {
        overviewChart.destroy();
    }

    overviewChart = createLineChart('overviewChart', {
        labels: data.trends_12m.monthly_labels,
        datasets: [
            {
                label: 'Income',
                data: data.trends_12m.monthly_income,
                borderColor: 'rgb(39, 174, 96)',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                tension: 0.1
            },
            {
                label: 'Expenses',
                data: data.trends_12m.monthly_expenses,
                borderColor: 'rgb(231, 76, 60)',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.1
            },
            {
                label: 'Net',
                data: data.trends_12m.monthly_net,
                borderColor: 'rgb(52, 152, 219)',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.1
            }
        ]
    });
}

function updateOverviewMonthTables(data) {
    if (!data.all_months) return;

    const currentMonth = currentSelectedMonth || data.default_month;
    const monthData = data.all_months[currentMonth];

    if (!monthData || !monthData.breakdown) return;

    // Update category breakdown
    const categoryTbody = document.getElementById('overview-category-tbody');
    if (categoryTbody) {
        categoryTbody.innerHTML = '';

        const categories = Object.entries(monthData.breakdown || {})
            .sort((a, b) => Math.abs(b[1].total || 0) - Math.abs(a[1].total || 0));

        categories.forEach(([cat, catData]) => {
            const row = document.createElement('tr');
            const urlCat = encodeURIComponent(cat);
            const total = catData.total || 0;
            const amountColor = total >= 0 ? '#27ae60' : '#e74c3c';
            const sign = total >= 0 ? '+' : '';
            const formattedTotal = `€${sign}${Math.abs(total).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

            row.innerHTML = `
                <td><a href="category_trends.html?category=${urlCat}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cat)}</a></td>
                <td class="text-right" style="color: ${amountColor}; font-weight: 600;">${formattedTotal}</td>
                <td class="text-center">${catData.count || 0}</td>
            `;
            categoryTbody.appendChild(row);

            // Add tag breakdown if present
            if (catData.tags) {
                const tagEntries = Object.entries(catData.tags)
                    .sort((a, b) => Math.abs(b[1].total || 0) - Math.abs(a[1].total || 0));

                tagEntries.forEach(([tag, tagData]) => {
                    const tagRow = document.createElement('tr');
                    tagRow.style.backgroundColor = '#f8f9fa';
                    const urlTag = encodeURIComponent(tag);
                    const tagTotal = tagData.total || 0;
                    const tagAmountColor = tagTotal >= 0 ? '#27ae60' : '#e74c3c';
                    const tagSign = tagTotal >= 0 ? '+' : '';
                    const formattedTagTotal = `€${tagSign}${Math.abs(tagTotal).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

                    tagRow.innerHTML = `
                        <td style="padding-left: 2rem;">└─ <a href="category_trends.html?category=${urlCat}&tag=${urlTag}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(tag)}</a></td>
                        <td class="text-right" style="color: ${tagAmountColor}; font-weight: 600;">${formattedTagTotal}</td>
                        <td class="text-center">${tagData.count || 0}</td>
                    `;
                    categoryTbody.appendChild(tagRow);
                });
            }
        });
    }

    // Update counterparty breakdown
    const counterpartyTbody = document.getElementById('overview-counterparty-tbody');
    if (counterpartyTbody && monthData.counterparties) {
        counterpartyTbody.innerHTML = '';

        const counterparties = (monthData.counterparties || []).slice(0, 10);

        counterparties.forEach(cp => {
            const row = document.createElement('tr');
            const urlName = encodeURIComponent(cp.name);
            const totalAmount = cp.total || 0;
            const isNegative = totalAmount < 0;
            const sign = isNegative ? '-' : '+';
            const absAmount = Math.abs(totalAmount);
            const formattedAmount = `€${sign}${absAmount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
            const amountColor = isNegative ? '#e74c3c' : '#27ae60';

            row.innerHTML = `
                <td><a href="counterparty_trends.html?counterparty=${urlName}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cp.name)}</a></td>
                <td class="text-center">${cp.count}</td>
                <td class="text-right" style="color: ${amountColor}; font-weight: 600;">${formattedAmount}</td>
            `;
            counterpartyTbody.appendChild(row);
        });
    }
}

function updateOverview12MTable(data) {
    const tbody = document.getElementById('overview-12m-tbody');
    if (!tbody || !data.trends_12m || !data.trends_12m.monthly_data) return;

    const monthlyData = data.trends_12m.monthly_data;
    const monthlyLabels = data.trends_12m.monthly_labels;

    let html = '';
    let prevNet = null;

    monthlyLabels.forEach(month => {
        const summary = monthlyData[month].summary;
        let changeStr = '';

        if (prevNet !== null) {
            const netChange = summary.net - prevNet;
            const changePct = prevNet !== 0 ? (netChange / Math.abs(prevNet) * 100) : 0;
            changeStr = `€${netChange.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')} (${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%)`;
        } else {
            changeStr = '-';
        }

        html += `
            <tr>
                <td>${month}</td>
                <td class="text-right">${formatCurrency(summary.total_income)}</td>
                <td class="text-right">${formatCurrency(summary.total_expenses)}</td>
                <td class="text-right ${summary.net >= 0 ? 'positive' : 'negative'}" style="font-weight: 600;">${formatCurrency(summary.net)}</td>
                <td class="text-right">${changeStr}</td>
                <td class="text-center">${summary.transaction_count}</td>
            </tr>
        `;

        prevNet = summary.net;
    });

    tbody.innerHTML = html;
}

// Override updateMonthView to also update overview chart if on overview page
const originalUpdateMonthView = updateMonthView;
updateMonthView = function(monthStr) {
    originalUpdateMonthView(monthStr);

    // If on overview page, update the overview chart
    const overviewPeriodSelector = document.getElementById('overview-period-selector');
    if (overviewPeriodSelector && overviewPeriodSelector.value === 'month') {
        const data = getDashboardData();
        if (data) {
            updateOverviewMonthChart(data);
            updateOverviewMonthTables(data);
        }
    }
};

// Overview period selector functionality (for index page)
function initializeOverviewPeriodSelector(data) {
    const periodSelector = document.getElementById('period-selector');
    if (!periodSelector) return;

    // Clear existing options
    periodSelector.innerHTML = '';

    // Add Year-to-Date option (no group, always first)
    const ytdOption = document.createElement('option');
    ytdOption.value = 'ytd';
    ytdOption.textContent = '📊 Year-to-Date';
    ytdOption.selected = true;
    periodSelector.appendChild(ytdOption);

    // Add All Time option
    const allTimeOption = document.createElement('option');
    allTimeOption.value = 'alltime';
    allTimeOption.textContent = '🕐 All Time';
    periodSelector.appendChild(allTimeOption);

    // Add Custom Range option
    const customRangeOption = document.createElement('option');
    customRangeOption.value = 'custom';
    customRangeOption.textContent = '📅 Custom Range';
    periodSelector.appendChild(customRangeOption);

    // Add separator
    const separator1 = document.createElement('option');
    separator1.disabled = true;
    separator1.textContent = '─────────────────';
    periodSelector.appendChild(separator1);

    // Get available years
    const years = new Set();
    if (data.available_months) {
        data.available_months.forEach(month => {
            const year = month.split('-')[0];
            years.add(year);
        });
    }

    const sortedYears = Array.from(years).sort().reverse();
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Group options by year
    sortedYears.forEach((year) => {
        const yearGroup = document.createElement('optgroup');
        yearGroup.label = `📅 ${year}`;

        // Add full year option
        const yearOption = document.createElement('option');
        yearOption.value = `year:${year}`;
        yearOption.textContent = `Full Year ${year}`;
        yearGroup.appendChild(yearOption);

        // Add quarters
        for (let q = 1; q <= 4; q++) {
            const option = document.createElement('option');
            option.value = `quarter:${year}-Q${q}`;
            option.textContent = `Q${q} ${year}`;
            yearGroup.appendChild(option);
        }

        // Add months (newest first)
        const yearMonths = data.available_months
            ? data.available_months.filter(m => m.startsWith(year)).sort().reverse()
            : [];
        yearMonths.forEach(month => {
            const [, monthNum] = month.split('-');
            const option = document.createElement('option');
            option.value = `month:${month}`;
            option.textContent = `${monthNames[parseInt(monthNum) - 1]} ${year}`;
            yearGroup.appendChild(option);
        });

        periodSelector.appendChild(yearGroup);
    });

    // Add change handler
    periodSelector.addEventListener('change', function() {
        categoryPage = 1;
        counterpartyPage = 1;

        // Show/hide custom range container
        const customRangeContainer = document.getElementById('custom-range-container');
        if (customRangeContainer) {
            if (this.value === 'custom') {
                customRangeContainer.style.display = 'flex';
                // Don't update view yet - wait for user to select dates
                return;
            } else {
                customRangeContainer.style.display = 'none';
            }
        }

        updateOverviewPeriodView(data, this.value);
    });

    // Setup custom range date inputs and apply button
    const customRangeContainer = document.getElementById('custom-range-container');
    const customRangeStart = document.getElementById('custom-range-start');
    const customRangeEnd = document.getElementById('custom-range-end');
    const applyCustomRangeBtn = document.getElementById('apply-custom-range');

    if (customRangeContainer && customRangeStart && customRangeEnd && applyCustomRangeBtn) {
        // Set default dates (first transaction date to today)
        if (data.all_transactions && data.all_transactions.length > 0) {
            const dates = data.all_transactions
                .map(tx => tx.date)
                .filter(d => d)
                .sort();
            if (dates.length > 0) {
                customRangeStart.value = dates[0];
            }
        }
        if (!customRangeEnd.value) {
            const today = new Date();
            customRangeEnd.value = today.toISOString().split('T')[0];
        }

        // Apply button handler
        applyCustomRangeBtn.addEventListener('click', function() {
            const startDate = customRangeStart.value;
            const endDate = customRangeEnd.value;

            if (!startDate || !endDate) {
                alert('Please select both start and end dates');
                return;
            }

            if (new Date(startDate) > new Date(endDate)) {
                alert('Start date must be before end date');
                return;
            }

            const customPeriod = `custom:${startDate}:${endDate}`;
            categoryPage = 1;
            counterpartyPage = 1;
            updateOverviewPeriodView(data, customPeriod);
        });

        // Allow Enter key to apply
        customRangeStart.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyCustomRangeBtn.click();
            }
        });
        customRangeEnd.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyCustomRangeBtn.click();
            }
        });
    }
}

function updateOverviewPeriodView(data, period) {
    if (!data.all_transactions) return;

    const currentYear = data.current_year || new Date().getFullYear();
    const filteredTransactions = filterTransactionsByPeriod(data.all_transactions, period, currentYear);

    // Calculate summary
    const summary = calculatePeriodSummary(filteredTransactions);

    // Calculate comparison (previous period or same period last year)
    const comparison = calculatePeriodComparison(data.all_transactions, period, currentYear, summary);

    // Update metrics
    updatePeriodMetrics(summary);

    // Update comparison table
    updatePeriodComparison(comparison, summary);

    // Update year progress indicator
    updateYearProgress(period, currentYear);

    // Update health indicators
    updateHealthIndicators(summary);

    // Update monthly breakdown chart
    updateMonthlyBreakdownChart(data, period, filteredTransactions);

    // Update recent trends chart (show last 6 months)
    updateOverviewTrendsChart(data, period);

    // Update top categories and counterparties
    updateOverviewTopItems(filteredTransactions, summary);

    // Update insights
    updateOverviewInsights(summary, comparison, period);

    // Update net comparison chart
    updateNetComparisonChart(data, period, filteredTransactions, comparison, currentYear);

    // Update category breakdown with pagination
    updatePeriodCategoryBreakdown(filteredTransactions);

    // Update counterparty breakdown with pagination
    updatePeriodCounterpartyBreakdown(filteredTransactions);
}

function updateOverviewTrendsChart(data, period) {
    const ctx = document.getElementById('recentTrendsChart');
    if (!ctx || !data.all_months) return;

    // Determine which months to show based on period
    let monthsToShow = [];

    if (period === 'ytd') {
        const currentYear = data.current_year || new Date().getFullYear();
        const allMonths = Object.keys(data.all_months).sort();
        monthsToShow = allMonths
            .filter(m => m.startsWith(String(currentYear)))
            .slice(-6);
    } else if (period === 'alltime') {
        // Show last 12 months for all time view
        const allMonths = Object.keys(data.all_months).sort();
        monthsToShow = allMonths.slice(-12);
    } else if (period.startsWith('custom:')) {
        // For custom range, show months within the range
        const parts = period.split(':');
        if (parts.length === 3) {
            const startDate = new Date(parts[1]);
            const endDate = new Date(parts[2]);
            const allMonths = Object.keys(data.all_months).sort();
            monthsToShow = allMonths.filter(m => {
                const monthDate = new Date(m + '-01');
                return monthDate >= startDate && monthDate <= endDate;
            });
            // Limit to last 12 months if range is very large
            if (monthsToShow.length > 12) {
                monthsToShow = monthsToShow.slice(-12);
            }
        }
    } else if (period.startsWith('year:')) {
        const year = period.split(':')[1];
        const allMonths = Object.keys(data.all_months).sort();
        monthsToShow = allMonths
            .filter(m => m.startsWith(year))
            .slice(-6);
    } else if (period.startsWith('quarter:')) {
        const [year, quarter] = period.split(':')[1].split('-Q');
        const startMonth = (parseInt(quarter) - 1) * 3 + 1;
        const endMonth = startMonth + 2;
        const allMonths = Object.keys(data.all_months).sort();
        monthsToShow = allMonths.filter(m => {
            const mYear = m.split('-')[0];
            const mMonth = parseInt(m.split('-')[1]);
            return mYear === year && mMonth >= startMonth && mMonth <= endMonth;
        });
    } else if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        const allMonths = Object.keys(data.all_months).sort();
        const monthIndex = allMonths.indexOf(month);
        monthsToShow = allMonths.slice(Math.max(0, monthIndex - 5), monthIndex + 1);
    }

    // Prepare trend data
    const monthlyTrendsData = {};
    monthsToShow.forEach(month => {
        const monthData = data.all_months[month];
        if (monthData && monthData.summary) {
            monthlyTrendsData[month] = {
                total_income: monthData.summary.total_income || 0,
                total_expenses: monthData.summary.total_expenses || 0,
                net: monthData.summary.net || 0
            };
        }
    });

    const trendData = prepareMonthlyTrendData(monthlyTrendsData);

    // Destroy existing chart if it exists
    const existingChart = Chart.getChart('recentTrendsChart');
    if (existingChart) {
        existingChart.destroy();
    }

    // Create new chart
    createLineChart('recentTrendsChart', trendData);
}

// Year Progress Indicator
function updateYearProgress(period, currentYear) {
    const progressContainer = document.getElementById('year-progress-container');
    const progressBar = document.getElementById('year-progress-bar');
    const progressText = document.getElementById('year-progress-text');

    if (!progressContainer || !progressBar || !progressText) return;

    if (period === 'ytd') {
        const currentDate = new Date();
        const currentMonth = currentDate.getMonth() + 1; // 1-12
        const progress = (currentMonth / 12) * 100;

        progressContainer.style.display = 'block';
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${currentMonth}/12 months (${progress.toFixed(1)}%)`;
    } else if (period === 'alltime' || period.startsWith('custom:')) {
        // Hide progress bar for all time and custom range
        progressContainer.style.display = 'none';
    } else {
        progressContainer.style.display = 'none';
    }
}

// Financial Health Indicators
function calculateHealthIndicators(summary) {
    const income = summary.total_income || 0;
    const expenses = Math.abs(summary.total_expenses || 0);
    const net = summary.net || 0;
    const transactionCount = summary.transaction_count || 0;
    const totalAmount = income + expenses;

    let savingsRate = 0;
    if (income > 0) {
        savingsRate = (net / income) * 100;
    }

    let expenseRatio = 0;
    if (income > 0) {
        expenseRatio = (expenses / income) * 100;
    }

    let avgTransaction = 0;
    if (transactionCount > 0) {
        avgTransaction = totalAmount / transactionCount;
    }

    let incomeExpenseRatio = 0;
    if (expenses > 0) {
        incomeExpenseRatio = income / expenses;
    }

    return {
        savingsRate,
        expenseRatio,
        avgTransaction,
        incomeExpenseRatio
    };
}

function updateHealthIndicators(summary) {
    const indicators = calculateHealthIndicators(summary);

    // Savings Rate
    const savingsRateEl = document.querySelector('.health-savings-rate');
    if (savingsRateEl) {
        const value = indicators.savingsRate;
        savingsRateEl.textContent = value.toFixed(1) + '%';
        savingsRateEl.className = 'metric-value health-savings-rate ' + (value >= 0 ? 'positive' : 'negative');
    }

    // Expense Ratio
    const expenseRatioEl = document.querySelector('.health-expense-ratio');
    if (expenseRatioEl) {
        const value = indicators.expenseRatio;
        expenseRatioEl.textContent = value.toFixed(1) + '%';
        expenseRatioEl.className = 'metric-value health-expense-ratio ' + (value <= 100 ? 'positive' : 'negative');
    }

    // Average Transaction
    const avgTransactionEl = document.querySelector('.health-avg-transaction');
    if (avgTransactionEl) {
        const value = indicators.avgTransaction;
        avgTransactionEl.textContent = '€' + value.toFixed(2);
        avgTransactionEl.className = 'metric-value health-avg-transaction';
    }

    // Income/Expense Ratio
    const incomeExpenseRatioEl = document.querySelector('.health-income-expense-ratio');
    if (incomeExpenseRatioEl) {
        const value = indicators.incomeExpenseRatio;
        incomeExpenseRatioEl.textContent = value.toFixed(2);
        incomeExpenseRatioEl.className = 'metric-value health-income-expense-ratio ' + (value >= 1 ? 'positive' : 'negative');
    }
}

// Monthly Breakdown Chart
function updateMonthlyBreakdownChart(data, period, filteredTransactions) {
    const ctx = document.getElementById('monthlyBreakdownChart');
    if (!ctx) return;

    // Determine which months to show based on period
    let monthsToShow = [];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    if (period === 'ytd') {
        const currentYear = data.current_year || new Date().getFullYear();
        const allMonths = Object.keys(data.all_months || {}).sort();
        monthsToShow = allMonths.filter(m => m.startsWith(String(currentYear)));
    } else if (period.startsWith('year:')) {
        const year = period.split(':')[1];
        const allMonths = Object.keys(data.all_months || {}).sort();
        monthsToShow = allMonths.filter(m => m.startsWith(year));
    } else if (period.startsWith('quarter:')) {
        const [year, quarter] = period.split(':')[1].split('-Q');
        const startMonth = (parseInt(quarter) - 1) * 3 + 1;
        const endMonth = startMonth + 2;
        const allMonths = Object.keys(data.all_months || {}).sort();
        monthsToShow = allMonths.filter(m => {
            const mYear = m.split('-')[0];
            const mMonth = parseInt(m.split('-')[1]);
            return mYear === year && mMonth >= startMonth && mMonth <= endMonth;
        });
    } else if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        const allMonths = Object.keys(data.all_months || {}).sort();
        const monthIndex = allMonths.indexOf(month);
        monthsToShow = allMonths.slice(Math.max(0, monthIndex - 5), monthIndex + 1);
    }

    // Calculate monthly data
    const monthlyData = {};
    filteredTransactions.forEach(tx => {
        if (!tx.date) return;
        const monthKey = tx.date.substring(0, 7); // YYYY-MM
        if (!monthsToShow.includes(monthKey)) return;

        if (!monthlyData[monthKey]) {
            monthlyData[monthKey] = { income: 0, expenses: 0 };
        }

        const amount = tx.amount || 0;
        if (amount > 0) {
            monthlyData[monthKey].income += amount;
        } else {
            monthlyData[monthKey].expenses += Math.abs(amount);
        }
    });

    // Prepare chart data
    const labels = monthsToShow.map(m => {
        const [year, month] = m.split('-');
        return `${monthNames[parseInt(month) - 1]} ${year}`;
    });

    const incomeData = monthsToShow.map(m => monthlyData[m]?.income || 0);
    const expenseData = monthsToShow.map(m => monthlyData[m]?.expenses || 0);

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: 'Income',
                data: incomeData,
                backgroundColor: 'rgba(39, 174, 96, 0.6)',
                borderColor: 'rgba(39, 174, 96, 1)',
                borderWidth: 1
            },
            {
                label: 'Expenses',
                data: expenseData,
                backgroundColor: 'rgba(231, 76, 60, 0.6)',
                borderColor: 'rgba(231, 76, 60, 1)',
                borderWidth: 1
            }
        ]
    };

    // Destroy existing chart if it exists
    const existingChart = Chart.getChart('monthlyBreakdownChart');
    if (existingChart) {
        existingChart.destroy();
    }

    // Create new chart
    createBarChart('monthlyBreakdownChart', chartData, {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    });
}

// Top Categories and Counterparties
function updateOverviewTopItems(transactions, summary) {
    // Get categories and counterparties
    const categories = getCategoryBreakdowns(transactions, 100);
    const counterparties = getCounterpartyBreakdowns(transactions, 100);

    // Separate income and expenses, get top 10
    const incomeCategories = categories.filter(cat => cat.total > 0).sort((a, b) => Math.abs(b.total) - Math.abs(a.total)).slice(0, 10);
    const expenseCategories = categories.filter(cat => cat.total < 0).sort((a, b) => Math.abs(b.total) - Math.abs(a.total)).slice(0, 10);
    const incomeCounterparties = counterparties.filter(cp => cp.total > 0).sort((a, b) => Math.abs(b.total) - Math.abs(a.total)).slice(0, 10);
    const expenseCounterparties = counterparties.filter(cp => cp.total < 0).sort((a, b) => Math.abs(b.total) - Math.abs(a.total)).slice(0, 10);

    const totalIncome = summary.total_income || 0;
    const totalExpenses = Math.abs(summary.total_expenses || 0);

    // Helper function to format currency with commas
    function formatCurrencyWithCommas(value) {
        return value.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    // Helper function to build category link
    function buildCategoryLink(categoryName) {
        const parts = categoryName.split(':');
        if (parts.length === 2) {
            // Has tag (e.g., "salary:founders")
            const category = encodeURIComponent(parts[0]);
            const tag = encodeURIComponent(parts[1]);
            return `category_trends.html?category=${category}&tag=${tag}&year=all`;
        } else {
            // No tag
            const category = encodeURIComponent(categoryName);
            return `category_trends.html?category=${category}&year=all`;
        }
    }

    // Render top income categories
    const topIncomeCategoriesEl = document.getElementById('top-income-categories');
    if (topIncomeCategoriesEl) {
        if (incomeCategories.length === 0) {
            topIncomeCategoriesEl.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 1rem;">No income categories</p>';
        } else {
            topIncomeCategoriesEl.innerHTML = incomeCategories.map(cat => {
                const percentage = totalIncome > 0 ? (cat.total / totalIncome * 100).toFixed(1) : 0;
                const url = buildCategoryLink(cat.name);
                const formattedAmount = formatCurrencyWithCommas(cat.total);
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #ecf0f1;">
                        <a href="${url}" style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #3498db; text-decoration: none; cursor: pointer;" title="View trends for ${escapeHtmlForTable(cat.name)}">${escapeHtmlForTable(cat.name)}</a>
                        <span style="font-weight: 600; color: #27ae60; margin-left: 1rem; white-space: nowrap;">€${formattedAmount}</span>
                        <span style="color: #7f8c8d; margin-left: 0.5rem; font-size: 0.9rem; white-space: nowrap;">${percentage}%</span>
                    </div>
                `;
            }).join('');
        }
    }

    // Render top expense categories
    const topExpenseCategoriesEl = document.getElementById('top-expense-categories');
    if (topExpenseCategoriesEl) {
        if (expenseCategories.length === 0) {
            topExpenseCategoriesEl.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 1rem;">No expense categories</p>';
        } else {
            topExpenseCategoriesEl.innerHTML = expenseCategories.map(cat => {
                const percentage = totalExpenses > 0 ? (Math.abs(cat.total) / totalExpenses * 100).toFixed(1) : 0;
                const url = buildCategoryLink(cat.name);
                const formattedAmount = formatCurrencyWithCommas(Math.abs(cat.total));
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #ecf0f1;">
                        <a href="${url}" style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #3498db; text-decoration: none; cursor: pointer;" title="View trends for ${escapeHtmlForTable(cat.name)}">${escapeHtmlForTable(cat.name)}</a>
                        <span style="font-weight: 600; color: #e74c3c; margin-left: 1rem; white-space: nowrap;">€${formattedAmount}</span>
                        <span style="color: #7f8c8d; margin-left: 0.5rem; font-size: 0.9rem; white-space: nowrap;">${percentage}%</span>
                    </div>
                `;
            }).join('');
        }
    }

    // Render top income counterparties
    const topIncomeCounterpartiesEl = document.getElementById('top-income-counterparties');
    if (topIncomeCounterpartiesEl) {
        if (incomeCounterparties.length === 0) {
            topIncomeCounterpartiesEl.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 1rem;">No income counterparties</p>';
        } else {
            topIncomeCounterpartiesEl.innerHTML = incomeCounterparties.map(cp => {
                const percentage = totalIncome > 0 ? (cp.total / totalIncome * 100).toFixed(1) : 0;
                const urlName = encodeURIComponent(cp.name || '');
                const url = `counterparty_trends.html?counterparty=${urlName}&year=all`;
                const formattedAmount = formatCurrencyWithCommas(cp.total);
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #ecf0f1;">
                        <a href="${url}" style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #3498db; text-decoration: none; cursor: pointer;" title="View trends for ${escapeHtmlForTable(cp.name)}">${escapeHtmlForTable(cp.name)}</a>
                        <span style="font-weight: 600; color: #27ae60; margin-left: 1rem; white-space: nowrap;">€${formattedAmount}</span>
                        <span style="color: #7f8c8d; margin-left: 0.5rem; font-size: 0.9rem; white-space: nowrap;">${percentage}%</span>
                    </div>
                `;
            }).join('');
        }
    }

    // Render top expense counterparties
    const topExpenseCounterpartiesEl = document.getElementById('top-expense-counterparties');
    if (topExpenseCounterpartiesEl) {
        if (expenseCounterparties.length === 0) {
            topExpenseCounterpartiesEl.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 1rem;">No expense counterparties</p>';
        } else {
            topExpenseCounterpartiesEl.innerHTML = expenseCounterparties.map(cp => {
                const percentage = totalExpenses > 0 ? (Math.abs(cp.total) / totalExpenses * 100).toFixed(1) : 0;
                const urlName = encodeURIComponent(cp.name || '');
                const url = `counterparty_trends.html?counterparty=${urlName}&year=all`;
                const formattedAmount = formatCurrencyWithCommas(Math.abs(cp.total));
                return `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #ecf0f1;">
                        <a href="${url}" style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #3498db; text-decoration: none; cursor: pointer;" title="View trends for ${escapeHtmlForTable(cp.name)}">${escapeHtmlForTable(cp.name)}</a>
                        <span style="font-weight: 600; color: #e74c3c; margin-left: 1rem; white-space: nowrap;">€${formattedAmount}</span>
                        <span style="color: #7f8c8d; margin-left: 0.5rem; font-size: 0.9rem; white-space: nowrap;">${percentage}%</span>
                    </div>
                `;
            }).join('');
        }
    }
}

// Key Insights/Alerts
function calculateInsights(summary, comparison, period) {
    const insights = [];

    if (!comparison || !comparison.summary) {
        return insights;
    }

    // Helper function to format currency with commas
    function formatCurrencyWithCommas(value) {
        return value.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    const income = summary.total_income || 0;
    const expenses = Math.abs(summary.total_expenses || 0);
    const net = summary.net || 0;
    const prevIncome = comparison.summary.total_income || 0;
    const prevExpenses = Math.abs(comparison.summary.total_expenses || 0);
    const prevNet = comparison.summary.net || 0;

    // Check for significant percentage changes (>20%)
    if (prevIncome > 0) {
        const incomeChangePct = ((income - prevIncome) / prevIncome) * 100;
        if (Math.abs(incomeChangePct) >= 20) {
            insights.push({
                type: incomeChangePct > 0 ? 'positive' : 'negative',
                message: `Income ${incomeChangePct > 0 ? 'increased' : 'decreased'} by ${Math.abs(incomeChangePct).toFixed(1)}% compared to previous period`,
                icon: incomeChangePct > 0 ? '📈' : '📉'
            });
        }
    }

    if (prevExpenses > 0) {
        const expenseChangePct = ((expenses - prevExpenses) / prevExpenses) * 100;
        if (Math.abs(expenseChangePct) >= 20) {
            insights.push({
                type: expenseChangePct < 0 ? 'positive' : 'negative',
                message: `Expenses ${expenseChangePct > 0 ? 'increased' : 'decreased'} by ${Math.abs(expenseChangePct).toFixed(1)}% compared to previous period`,
                icon: expenseChangePct < 0 ? '✅' : '⚠️'
            });
        }
    }

    // Check for unusual patterns
    if (expenses > income && income > 0) {
        const excess = expenses - income;
        insights.push({
            type: 'warning',
            message: `Expenses exceed income by €${formatCurrencyWithCommas(excess)}`,
            icon: '⚠️'
        });
    }

    if (net > 0 && prevNet <= 0) {
        insights.push({
            type: 'positive',
            message: 'Net income is positive for the first time in this comparison period',
            icon: '🎉'
        });
    }

    if (net < 0 && prevNet >= 0) {
        insights.push({
            type: 'negative',
            message: 'Net income turned negative compared to previous period',
            icon: '📉'
        });
    }

    // Check for significant net change
    if (prevNet !== 0) {
        const netChangePct = ((net - prevNet) / Math.abs(prevNet)) * 100;
        if (Math.abs(netChangePct) >= 50) {
            insights.push({
                type: netChangePct > 0 ? 'positive' : 'negative',
                message: `Net income ${netChangePct > 0 ? 'improved' : 'worsened'} by ${Math.abs(netChangePct).toFixed(1)}%`,
                icon: netChangePct > 0 ? '📈' : '📉'
            });
        }
    }

    return insights;
}

function updateOverviewInsights(summary, comparison, period) {
    const insightsContainer = document.getElementById('insights-container');
    if (!insightsContainer) return;

    const insights = calculateInsights(summary, comparison, period);

    if (insights.length === 0) {
        insightsContainer.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 0.5rem;">No significant insights for this period.</p>';
        return;
    }

    insightsContainer.innerHTML = '<div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">' + insights.map(insight => {
        const bgColor = insight.type === 'positive' ? '#d5f4e6' : insight.type === 'negative' ? '#fadbd8' : '#fff3cd';
        const textColor = insight.type === 'positive' ? '#27ae60' : insight.type === 'negative' ? '#e74c3c' : '#856404';
        const borderColor = insight.type === 'positive' ? '#27ae60' : insight.type === 'negative' ? '#e74c3c' : '#ffc107';

        return `
            <span style="padding: 0.5rem 0.75rem; background-color: ${bgColor}; border-left: 3px solid ${borderColor}; border-radius: 4px; display: inline-flex; align-items: center; gap: 0.5rem; white-space: nowrap;">
                <span style="font-size: 1.1rem;">${insight.icon}</span>
                <span style="color: ${textColor}; font-size: 0.9rem;">${insight.message}</span>
            </span>
        `;
    }).join('') + '</div>';
}

// Net Comparison Chart
function updateNetComparisonChart(data, period, currentTransactions, comparison, currentYear) {
    const ctx = document.getElementById('netComparisonChart');
    if (!ctx || !data.all_transactions) return;

    // Determine which months to show based on period
    let monthsToShow = [];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    if (period === 'ytd') {
        const currentYearNum = currentYear || new Date().getFullYear();
        const allMonths = Object.keys(data.all_months || {}).sort();
        monthsToShow = allMonths.filter(m => m.startsWith(String(currentYearNum)));
    } else if (period.startsWith('year:')) {
        const year = period.split(':')[1];
        const allMonths = Object.keys(data.all_months || {}).sort();
        monthsToShow = allMonths.filter(m => m.startsWith(year));
    } else if (period.startsWith('quarter:')) {
        const [year, quarter] = period.split(':')[1].split('-Q');
        const startMonth = (parseInt(quarter) - 1) * 3 + 1;
        const endMonth = startMonth + 2;
        const allMonths = Object.keys(data.all_months || {}).sort();
        monthsToShow = allMonths.filter(m => {
            const mYear = m.split('-')[0];
            const mMonth = parseInt(m.split('-')[1]);
            return mYear === year && mMonth >= startMonth && mMonth <= endMonth;
        });
    } else if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        monthsToShow = [month];
    }

    if (monthsToShow.length === 0) {
        // Hide chart if no months
        const existingChart = Chart.getChart('netComparisonChart');
        if (existingChart) {
            existingChart.destroy();
        }
        return;
    }

    // Calculate monthly net for current period
    const currentMonthlyNet = {};
    currentTransactions.forEach(tx => {
        if (!tx.date) return;
        const monthKey = tx.date.substring(0, 7); // YYYY-MM
        if (!monthsToShow.includes(monthKey)) return;

        if (!currentMonthlyNet[monthKey]) {
            currentMonthlyNet[monthKey] = 0;
        }
        currentMonthlyNet[monthKey] += (tx.amount || 0);
    });

    // Determine comparison period and get comparison transactions
    let comparisonPeriod = null;
    if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        const [year, monthNum] = month.split('-');
        let prevYear = parseInt(year);
        let prevMonth = parseInt(monthNum) - 1;
        if (prevMonth === 0) {
            prevMonth = 12;
            prevYear -= 1;
        }
        const prevMonthStr = `${prevYear}-${String(prevMonth).padStart(2, '0')}`;
        const prevMonthTransactions = data.all_transactions.filter(tx =>
            tx.date && tx.date.startsWith(prevMonthStr)
        );
        if (prevMonthTransactions.length > 0) {
            comparisonPeriod = `month:${prevMonthStr}`;
        } else {
            comparisonPeriod = `month:${parseInt(year) - 1}-${monthNum}`;
        }
    } else if (period.startsWith('quarter:')) {
        const quarterInfo = period.split(':')[1];
        const [year, quarter] = quarterInfo.split('-Q');
        let prevYear = parseInt(year);
        let prevQuarter = parseInt(quarter) - 1;
        if (prevQuarter === 0) {
            prevQuarter = 4;
            prevYear -= 1;
        }
        comparisonPeriod = `quarter:${prevYear}-Q${prevQuarter}`;
    } else if (period === 'ytd') {
        const currentYearNum = currentYear || new Date().getFullYear();
        comparisonPeriod = `ytd:${currentYearNum - 1}`;
    } else if (period.startsWith('year:')) {
        const year = period.split(':')[1];
        comparisonPeriod = `year:${parseInt(year) - 1}`;
    }

    // Get comparison transactions
    let comparisonTransactions = [];
    if (comparisonPeriod) {
        if (comparisonPeriod.startsWith('ytd:')) {
            const compareYear = parseInt(comparisonPeriod.split(':')[1]);
            const currentYearNum = currentYear || new Date().getFullYear();
            const currentYearMonths = new Set();
            data.all_transactions.forEach(tx => {
                if (tx.date) {
                    const txYear = parseInt(tx.date.substring(0, 4));
                    if (txYear === currentYearNum) {
                        const txMonth = tx.date.substring(5, 7);
                        currentYearMonths.add(txMonth);
                    }
                }
            });
            comparisonTransactions = data.all_transactions.filter(tx => {
                if (!tx.date) return false;
                const txYear = parseInt(tx.date.substring(0, 4));
                const txMonth = tx.date.substring(5, 7);
                return txYear === compareYear && currentYearMonths.has(txMonth);
            });
        } else {
            comparisonTransactions = filterTransactionsByPeriod(data.all_transactions, comparisonPeriod, currentYear);
        }
    }

    // Calculate monthly net for comparison period
    const comparisonMonthlyNet = {};
    let comparisonMonthsToShow = [];

    if (comparisonPeriod && comparisonPeriod.startsWith('ytd:')) {
        // For YTD comparison, use same months as current period but from previous year
        const compareYear = parseInt(comparisonPeriod.split(':')[1]);
        comparisonMonthsToShow = monthsToShow.map(m => {
            const [year, month] = m.split('-');
            return `${compareYear}-${month}`;
        });
    } else if (comparisonPeriod && comparisonPeriod.startsWith('month:')) {
        const month = comparisonPeriod.split(':')[1];
        comparisonMonthsToShow = [month];
    } else if (comparisonPeriod && comparisonPeriod.startsWith('quarter:')) {
        const [year, quarter] = comparisonPeriod.split(':')[1].split('-Q');
        const startMonth = (parseInt(quarter) - 1) * 3 + 1;
        const endMonth = startMonth + 2;
        const allMonths = Object.keys(data.all_months || {}).sort();
        comparisonMonthsToShow = allMonths.filter(m => {
            const mYear = m.split('-')[0];
            const mMonth = parseInt(m.split('-')[1]);
            return mYear === year && mMonth >= startMonth && mMonth <= endMonth;
        });
    } else if (comparisonPeriod && comparisonPeriod.startsWith('year:')) {
        const year = comparisonPeriod.split(':')[1];
        const allMonths = Object.keys(data.all_months || {}).sort();
        comparisonMonthsToShow = allMonths.filter(m => m.startsWith(year));
    }

    comparisonTransactions.forEach(tx => {
        if (!tx.date) return;
        const monthKey = tx.date.substring(0, 7);
        if (!comparisonMonthsToShow.includes(monthKey)) return;

        if (!comparisonMonthlyNet[monthKey]) {
            comparisonMonthlyNet[monthKey] = 0;
        }
        comparisonMonthlyNet[monthKey] += (tx.amount || 0);
    });

    // Prepare chart data - align months
    const labels = monthsToShow.map(m => {
        const [year, month] = m.split('-');
        return `${monthNames[parseInt(month) - 1]} ${year}`;
    });

    const currentValues = monthsToShow.map(m => currentMonthlyNet[m] || 0);
    const comparisonValues = monthsToShow.map(m => {
        if (comparisonPeriod && comparisonPeriod.startsWith('ytd:')) {
            // For YTD, match by month number
            const compareYear = parseInt(comparisonPeriod.split(':')[1]);
            const [, month] = m.split('-');
            const compareMonth = `${compareYear}-${month}`;
            return comparisonMonthlyNet[compareMonth] || 0;
        } else {
            // For other comparisons, try to match by position or find corresponding month
            const index = monthsToShow.indexOf(m);
            if (index < comparisonMonthsToShow.length) {
                const compareMonth = comparisonMonthsToShow[index];
                return comparisonMonthlyNet[compareMonth] || 0;
            }
            return 0;
        }
    });

    // Get labels for comparison period
    let currentLabel = period === 'ytd' ? `YTD ${currentYear}` : period;
    let comparisonLabel = comparison.label || 'Previous Period';

    // Simplify labels
    if (period.startsWith('year:')) {
        currentLabel = period.split(':')[1];
    } else if (period.startsWith('quarter:')) {
        const [year, quarter] = period.split(':')[1].split('-Q');
        currentLabel = `Q${quarter} ${year}`;
    } else if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        const [year, monthNum] = month.split('-');
        currentLabel = `${monthNames[parseInt(monthNum) - 1]} ${year}`;
    }

    if (comparisonPeriod) {
        if (comparisonPeriod.startsWith('ytd:')) {
            comparisonLabel = `YTD ${comparisonPeriod.split(':')[1]}`;
        } else if (comparisonPeriod.startsWith('year:')) {
            comparisonLabel = comparisonPeriod.split(':')[1];
        } else if (comparisonPeriod.startsWith('quarter:')) {
            const [year, quarter] = comparisonPeriod.split(':')[1].split('-Q');
            comparisonLabel = `Q${quarter} ${year}`;
        } else if (comparisonPeriod.startsWith('month:')) {
            const month = comparisonPeriod.split(':')[1];
            const [year, monthNum] = month.split('-');
            comparisonLabel = `${monthNames[parseInt(monthNum) - 1]} ${year}`;
        }
    }

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: currentLabel,
                data: currentValues,
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgb(52, 152, 219)',
                borderWidth: 1
            },
            {
                label: comparisonLabel,
                data: comparisonValues,
                backgroundColor: 'rgba(149, 165, 166, 0.7)',
                borderColor: 'rgb(149, 165, 166)',
                borderWidth: 1
            }
        ]
    };

    // Destroy existing chart if it exists
    const existingChart = Chart.getChart('netComparisonChart');
    if (existingChart) {
        existingChart.destroy();
    }

    // Create new chart
    createBarChart('netComparisonChart', chartData, {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: false
            }
        }
    });
}

// Period View functionality (for current_month page)
let categoryPage = 1;
let counterpartyPage = 1;
// itemsPerPage is defined above with other pagination variables
let periodCounterpartyTableSortState = { column: 'total', direction: 'desc' }; // For overview page counterparty table

function initializePeriodViewSelector(data) {
    const periodSelector = document.getElementById('period-selector');
    if (!periodSelector) return;

    // Clear existing options
    periodSelector.innerHTML = '';

    // Get available years
    const years = new Set();
    if (data.available_months) {
        data.available_months.forEach(month => {
            const year = month.split('-')[0];
            years.add(year);
        });
    }

    const sortedYears = Array.from(years).sort().reverse();
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Group options by year
    sortedYears.forEach((year) => {
        const yearGroup = document.createElement('optgroup');
        yearGroup.label = `📅 ${year}`;

        // Add full year option
        const yearOption = document.createElement('option');
        yearOption.value = `year:${year}`;
        yearOption.textContent = `Full Year ${year}`;
        yearGroup.appendChild(yearOption);

        // Add quarters
        for (let q = 1; q <= 4; q++) {
            const option = document.createElement('option');
            option.value = `quarter:${year}-Q${q}`;
            option.textContent = `Q${q} ${year}`;
            yearGroup.appendChild(option);
        }

        // Add months (newest first)
        const yearMonths = data.available_months
            ? data.available_months.filter(m => m.startsWith(year)).sort().reverse()
            : [];
        yearMonths.forEach(month => {
            const [, monthNum] = month.split('-');
            const option = document.createElement('option');
            option.value = `month:${month}`;
            option.textContent = `${monthNames[parseInt(monthNum) - 1]} ${year}`;
            if (month === data.default_month) {
                option.selected = true;
            }
            yearGroup.appendChild(option);
        });

        periodSelector.appendChild(yearGroup);
    });

    // Add change handler
    periodSelector.addEventListener('change', function() {
        categoryPage = 1;
        counterpartyPage = 1;
        updatePeriodView(data, this.value);
    });
}

function updatePeriodView(data, period) {
    if (!data.all_transactions) return;

    const currentYear = data.current_year || new Date().getFullYear();
    const filteredTransactions = filterTransactionsByPeriod(data.all_transactions, period, currentYear);

    // Calculate summary
    const summary = calculatePeriodSummary(filteredTransactions);

    // Calculate comparison (previous period or same period last year)
    const comparison = calculatePeriodComparison(data.all_transactions, period, currentYear, summary);

    // Update metrics
    updatePeriodMetrics(summary);

    // Update comparison table
    updatePeriodComparison(comparison, summary);

    // Update category breakdown with pagination
    updatePeriodCategoryBreakdown(filteredTransactions);

    // Update counterparty breakdown with pagination
    updatePeriodCounterpartyBreakdown(filteredTransactions);
}

function calculatePeriodSummary(transactions) {
    let totalIncome = 0;
    let totalExpenses = 0;
    let transactionCount = transactions.length;

    transactions.forEach(tx => {
        const amount = tx.amount || 0;
        if (amount > 0) {
            totalIncome += amount;
        } else {
            totalExpenses += Math.abs(amount);
        }
    });

    return {
        total_income: totalIncome,
        total_expenses: totalExpenses,
        net: totalIncome - totalExpenses,
        transaction_count: transactionCount
    };
}

function calculatePeriodComparison(allTransactions, period, currentYear, currentSummary) {
    // Determine comparison period: previous period or same period last year
    let comparisonPeriod = null;
    let comparisonLabel = '';

    if (period.startsWith('month:')) {
        const month = period.split(':')[1];
        const [year, monthNum] = month.split('-');

        // Try previous month first
        let prevYear = parseInt(year);
        let prevMonth = parseInt(monthNum) - 1;
        if (prevMonth === 0) {
            prevMonth = 12;
            prevYear -= 1;
        }
        const prevMonthStr = `${prevYear}-${String(prevMonth).padStart(2, '0')}`;

        // Check if previous month has data
        const prevMonthTransactions = allTransactions.filter(tx =>
            tx.date && tx.date.startsWith(prevMonthStr)
        );

        if (prevMonthTransactions.length > 0) {
            comparisonPeriod = `month:${prevMonthStr}`;
            comparisonLabel = `Previous Month (${prevMonthStr})`;
        } else {
            // Use same month last year
            const lastYear = parseInt(year) - 1;
            const lastYearMonthStr = `${lastYear}-${monthNum}`;
            comparisonPeriod = `month:${lastYearMonthStr}`;
            comparisonLabel = `Same Month Last Year (${lastYearMonthStr})`;
        }
    } else if (period.startsWith('quarter:')) {
        const quarterInfo = period.split(':')[1];
        const [year, quarter] = quarterInfo.split('-Q');

        // Try previous quarter
        let prevYear = parseInt(year);
        let prevQuarter = parseInt(quarter) - 1;
        if (prevQuarter === 0) {
            prevQuarter = 4;
            prevYear -= 1;
        }
        const prevQuarterStr = `quarter:${prevYear}-Q${prevQuarter}`;

        const prevQuarterTransactions = filterTransactionsByPeriod(allTransactions, prevQuarterStr, currentYear);

        if (prevQuarterTransactions.length > 0) {
            comparisonPeriod = prevQuarterStr;
            comparisonLabel = `Previous Quarter (Q${prevQuarter} ${prevYear})`;
        } else {
            // Use same quarter last year
            const lastYear = parseInt(year) - 1;
            const lastYearQuarterStr = `quarter:${lastYear}-Q${quarter}`;
            comparisonPeriod = lastYearQuarterStr;
            comparisonLabel = `Same Quarter Last Year (Q${quarter} ${lastYear})`;
        }
    } else if (period === 'ytd') {
        // For YTD, compare with previous year's YTD (same months)
        // Find which months actually exist in the current year (not just up to current date)
        const currentYearNum = currentYear || new Date().getFullYear();
        const lastYear = currentYearNum - 1;

        // Find actual months that exist in current year
        const currentYearMonths = new Set();
        allTransactions.forEach(tx => {
            if (tx.date) {
                const txYear = parseInt(tx.date.substring(0, 4));
                if (txYear === currentYearNum) {
                    const txMonth = tx.date.substring(5, 7); // MM
                    currentYearMonths.add(txMonth);
                }
            }
        });

        const sortedMonths = Array.from(currentYearMonths).sort();

        // Get transactions for same months from previous year
        const lastYearTransactions = allTransactions.filter(tx => {
            if (!tx.date) return false;
            const txYear = parseInt(tx.date.substring(0, 4));
            const txMonth = tx.date.substring(5, 7);
            return txYear === lastYear && sortedMonths.includes(txMonth);
        });

        if (lastYearTransactions.length > 0) {
            comparisonPeriod = `ytd:${lastYear}`;
            comparisonLabel = `Same Period Last Year (YTD ${lastYear})`;
        } else {
            // Fallback: try full previous year
            const prevYearFull = allTransactions.filter(tx =>
                tx.date && tx.date.startsWith(String(lastYear))
            );
            if (prevYearFull.length > 0) {
                comparisonPeriod = `year:${lastYear}`;
                comparisonLabel = `Previous Year (${lastYear})`;
            }
        }
    } else if (period.startsWith('year:')) {
        const year = period.split(':')[1];
        const lastYear = parseInt(year) - 1;
        comparisonPeriod = `year:${lastYear}`;
        comparisonLabel = `Previous Year (${lastYear})`;
    }

    // Calculate comparison summary
    let comparisonSummary = { total_income: 0, total_expenses: 0, net: 0, transaction_count: 0 };

    if (comparisonPeriod) {
        if (comparisonPeriod.startsWith('ytd:')) {
            // Handle YTD comparison - compare same months from previous year
            const compareYear = parseInt(comparisonPeriod.split(':')[1]);
            const currentYearNum = currentYear || new Date().getFullYear();

            // Find which months actually exist in the current year
            const currentYearMonths = new Set();
            allTransactions.forEach(tx => {
                if (tx.date) {
                    const txYear = parseInt(tx.date.substring(0, 4));
                    if (txYear === currentYearNum) {
                        const txMonth = tx.date.substring(5, 7); // MM
                        currentYearMonths.add(txMonth);
                    }
                }
            });

            // Get transactions for same months from previous year
            const comparisonTransactions = allTransactions.filter(tx => {
                if (!tx.date) return false;
                const txYear = parseInt(tx.date.substring(0, 4));
                const txMonth = tx.date.substring(5, 7);
                return txYear === compareYear && currentYearMonths.has(txMonth);
            });
            comparisonSummary = calculatePeriodSummary(comparisonTransactions);
        } else {
            const comparisonTransactions = filterTransactionsByPeriod(allTransactions, comparisonPeriod, currentYear);
            comparisonSummary = calculatePeriodSummary(comparisonTransactions);
        }
    }

    // Calculate changes
    const incomeChange = currentSummary.total_income - comparisonSummary.total_income;
    const expenseChange = currentSummary.total_expenses - comparisonSummary.total_expenses;
    const netChange = currentSummary.net - comparisonSummary.net;

    const incomeChangePct = comparisonSummary.total_income !== 0
        ? (incomeChange / comparisonSummary.total_income * 100) : 0;
    const expenseChangePct = comparisonSummary.total_expenses !== 0
        ? (expenseChange / comparisonSummary.total_expenses * 100) : 0;
    const netChangePct = comparisonSummary.net !== 0
        ? (netChange / Math.abs(comparisonSummary.net) * 100) : 0;

    return {
        summary: comparisonSummary,
        label: comparisonLabel,
        income_change: incomeChange,
        income_change_pct: incomeChangePct,
        expense_change: expenseChange,
        expense_change_pct: expenseChangePct,
        net_change: netChange,
        net_change_pct: netChangePct
    };
}

function updatePeriodMetrics(summary) {
    document.querySelectorAll('.period-income').forEach(el => {
        el.textContent = formatCurrency(summary.total_income);
        el.className = 'metric-value period-income positive';
    });

    document.querySelectorAll('.period-expenses').forEach(el => {
        el.textContent = formatCurrency(summary.total_expenses);
        el.className = 'metric-value period-expenses negative';
    });

    document.querySelectorAll('.period-net').forEach(el => {
        el.textContent = formatCurrency(summary.net);
        el.className = 'metric-value period-net ' + (summary.net >= 0 ? 'positive' : 'negative');
    });

    document.querySelectorAll('.period-transactions').forEach(el => {
        el.textContent = summary.transaction_count;
    });
}

function updatePeriodComparison(comparison, currentSummary) {
    const labelEl = document.getElementById('comparison-period-label');
    if (labelEl) {
        labelEl.textContent = comparison.label || 'Previous Period';
    }

    const tbody = document.getElementById('comparison-tbody');
    if (!tbody) return;

    tbody.innerHTML = `
        <tr>
            <td>Income</td>
            <td class="text-right period-income">${formatCurrency(currentSummary.total_income)}</td>
            <td class="text-right comparison-income">${formatCurrency(comparison.summary.total_income)}</td>
            <td class="text-right period-income-change ${comparison.income_change >= 0 ? 'positive' : 'negative'}">
                ${formatCurrency(comparison.income_change)}
            </td>
            <td class="text-right period-income-change-pct ${comparison.income_change_pct >= 0 ? 'positive' : 'negative'}">
                ${formatPercentage(comparison.income_change_pct)}
            </td>
        </tr>
        <tr>
            <td>Expenses</td>
            <td class="text-right period-expenses">${formatCurrency(currentSummary.total_expenses)}</td>
            <td class="text-right comparison-expenses">${formatCurrency(comparison.summary.total_expenses)}</td>
            <td class="text-right period-expense-change ${comparison.expense_change <= 0 ? 'positive' : 'negative'}">
                ${formatCurrency(comparison.expense_change)}
            </td>
            <td class="text-right period-expense-change-pct ${comparison.expense_change_pct <= 0 ? 'positive' : 'negative'}">
                ${formatPercentage(comparison.expense_change_pct)}
            </td>
        </tr>
        <tr>
            <td>Net</td>
            <td class="text-right period-net ${currentSummary.net >= 0 ? 'positive' : 'negative'}">
                ${formatCurrency(currentSummary.net)}
            </td>
            <td class="text-right comparison-net">${formatCurrency(comparison.summary.net)}</td>
            <td class="text-right period-net-change ${comparison.net_change >= 0 ? 'positive' : 'negative'}">
                ${formatCurrency(comparison.net_change)}
            </td>
            <td class="text-right period-net-change-pct ${comparison.net_change_pct >= 0 ? 'positive' : 'negative'}">
                ${formatPercentage(comparison.net_change_pct)}
            </td>
        </tr>
    `;
}

function updatePeriodCategoryBreakdown(transactions) {
    // Calculate category breakdown
    const categoryStats = {};

    transactions.forEach(tx => {
        const category = (tx.category || '').trim() || 'Unknown';
        const amount = tx.amount || 0;

        if (!categoryStats[category]) {
            categoryStats[category] = { total: 0, count: 0, tags: {} };
        }

        categoryStats[category].total += amount;
        categoryStats[category].count += 1;

        // Handle tags if category has ':'
        if (category.includes(':')) {
            const [baseCat, tag] = category.split(':', 2);
            if (!categoryStats[baseCat]) {
                categoryStats[baseCat] = { total: 0, count: 0, tags: {} };
            }
            // Add to base category total (so parent includes sum of all subcategories)
            categoryStats[baseCat].total += amount;
            categoryStats[baseCat].count += 1;
            // Also track in tags for subcategory breakdown
            if (!categoryStats[baseCat].tags[tag]) {
                categoryStats[baseCat].tags[tag] = { total: 0, count: 0 };
            }
            categoryStats[baseCat].tags[tag].total += amount;
            categoryStats[baseCat].tags[tag].count += 1;
        }
    });

    // Convert to array and sort
    const allCategories = [];
    Object.entries(categoryStats).forEach(([cat, data]) => {
        if (!cat.includes(':')) {  // Only base categories
            allCategories.push({
                name: cat,
                total: data.total,
                count: data.count,
                tags: data.tags
            });
        }
    });

    allCategories.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));

    // Store for pagination
    window.periodCategoryData = allCategories;

    // Render with pagination
    renderPeriodCategoryTable();
}

function renderPeriodCategoryTable() {
    const tbody = document.getElementById('category-breakdown-tbody');
    const totalCountEl = document.getElementById('category-total-count');
    const paginationInfoEl = document.getElementById('category-pagination-info');
    const prevBtn = document.getElementById('category-prev-btn');
    const nextBtn = document.getElementById('category-next-btn');

    if (!tbody || !window.periodCategoryData) return;

    const totalCount = window.periodCategoryData.length;
    if (totalCountEl) totalCountEl.textContent = totalCount;

    const startIdx = (categoryPage - 1) * itemsPerPage;
    const endIdx = Math.min(startIdx + itemsPerPage, totalCount);
    const pageData = window.periodCategoryData.slice(startIdx, endIdx);

    if (paginationInfoEl) {
        paginationInfoEl.innerHTML = `Showing ${startIdx + 1}-${endIdx} of <span id="category-total-count">${totalCount}</span>`;
    }

    if (prevBtn) prevBtn.disabled = categoryPage === 1;
    if (nextBtn) nextBtn.disabled = endIdx >= totalCount;

    let html = '';
    pageData.forEach(cat => {
        const amountColor = cat.total >= 0 ? '#27ae60' : '#e74c3c';
        const sign = cat.total >= 0 ? '+' : '';
        const formattedTotal = `€${sign}${Math.abs(cat.total).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        const urlCat = encodeURIComponent(cat.name);

        html += `
            <tr>
                <td><a href="category_trends.html?category=${urlCat}" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cat.name)}</a></td>
                <td class="text-right" style="color: ${amountColor}; font-weight: 600;">${formattedTotal}</td>
                <td class="text-center">${cat.count || 0}</td>
            </tr>
        `;

        // Add tags if present
        if (cat.tags && Object.keys(cat.tags).length > 0) {
            const sortedTags = Object.entries(cat.tags)
                .sort((a, b) => Math.abs(b[1].total || 0) - Math.abs(a[1].total || 0));

            sortedTags.forEach(([tag, tagData]) => {
                const tagAmountColor = tagData.total >= 0 ? '#27ae60' : '#e74c3c';
                const tagSign = tagData.total >= 0 ? '+' : '';
                const formattedTagTotal = `€${tagSign}${Math.abs(tagData.total).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
                const urlTag = encodeURIComponent(tag);

                html += `
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding-left: 2rem;">└─ <a href="category_trends.html?category=${urlCat}&tag=${urlTag}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(tag)}</a></td>
                        <td class="text-right" style="color: ${tagAmountColor}; font-weight: 600;">${formattedTagTotal}</td>
                        <td class="text-center">${tagData.count || 0}</td>
                    </tr>
                `;
            });
        }
    });

    tbody.innerHTML = html || '<tr><td colspan="3" style="text-align: center; padding: 2rem; color: #7f8c8d;">No categories found</td></tr>';

    // Add pagination handlers
    if (prevBtn) {
        prevBtn.onclick = () => {
            if (categoryPage > 1) {
                categoryPage--;
                renderPeriodCategoryTable();
            }
        };
    }

    if (nextBtn) {
        nextBtn.onclick = () => {
            const totalPages = Math.ceil((window.periodCategoryData?.length || 0) / itemsPerPage);
            if (categoryPage < totalPages) {
                categoryPage++;
                renderPeriodCategoryTable();
            }
        };
    }
}

function updatePeriodCounterpartyBreakdown(transactions) {
    // Calculate counterparty breakdown using same logic as getCounterpartyBreakdowns
    const counterpartyStats = {};
    const groupKeys = {};

    transactions.forEach(tx => {
        const counterparty = (tx.counterparty || '').trim() || 'Unknown';
        const normalizedName = normalizeCounterpartyNameForGrouping(counterparty);
        const groupKey = `name:${normalizedName}`;
        const amount = tx.amount || 0;

        if (!groupKeys[groupKey]) {
            groupKeys[groupKey] = {
                primaryName: counterparty,
                nameVariants: new Set([counterparty])
            };
        } else {
            groupKeys[groupKey].nameVariants.add(counterparty);
        }

        if (!counterpartyStats[groupKey]) {
            counterpartyStats[groupKey] = {
                count: 0,
                total: 0,
                transactions: [],
                nameVariants: new Set()
            };
        }

        counterpartyStats[groupKey].count += 1;
        counterpartyStats[groupKey].total += amount;
        counterpartyStats[groupKey].transactions.push(tx);
        counterpartyStats[groupKey].nameVariants.add(counterparty);
    });

    const allCounterparties = [];
    Object.keys(counterpartyStats).forEach(groupKey => {
        const stats = counterpartyStats[groupKey];
        const groupInfo = groupKeys[groupKey];
        const nameVariants = Array.from(stats.nameVariants);
        const mostCommonName = nameVariants.reduce((a, b) => {
            const aCount = stats.transactions.filter(tx => (tx.counterparty || '').trim() === a).length;
            const bCount = stats.transactions.filter(tx => (tx.counterparty || '').trim() === b).length;
            return aCount > bCount ? a : b;
        });

        allCounterparties.push({
            name: mostCommonName,
            count: stats.count,
            total: stats.total
        });
    });

    allCounterparties.sort((a, b) => Math.abs(b.total) - Math.abs(a.total));

    // Store for pagination
    window.periodCounterpartyData = allCounterparties;

    // Render with pagination
    renderPeriodCounterpartyTable();
}

function renderPeriodCounterpartyTable() {
    const tbody = document.getElementById('counterparty-breakdown-tbody');
    const totalCountEl = document.getElementById('counterparty-total-count');
    const paginationInfoEl = document.getElementById('counterparty-pagination-info');
    const prevBtn = document.getElementById('counterparty-prev-btn');
    const nextBtn = document.getElementById('counterparty-next-btn');

    if (!tbody || !window.periodCounterpartyData) return;

    // Sort the data before pagination
    const sortedData = sortCounterparties([...window.periodCounterpartyData], periodCounterpartyTableSortState.column, periodCounterpartyTableSortState.direction);

    const totalCount = sortedData.length;
    if (totalCountEl) totalCountEl.textContent = totalCount;

    const startIdx = (counterpartyPage - 1) * itemsPerPage;
    const endIdx = Math.min(startIdx + itemsPerPage, totalCount);
    const pageData = sortedData.slice(startIdx, endIdx);

    if (paginationInfoEl) {
        paginationInfoEl.innerHTML = `Showing ${startIdx + 1}-${endIdx} of <span id="counterparty-total-count">${totalCount}</span>`;
    }

    if (prevBtn) prevBtn.disabled = counterpartyPage === 1;
    if (nextBtn) nextBtn.disabled = endIdx >= totalCount;

    let html = '';
    pageData.forEach(cp => {
        const totalAmount = cp.total || 0;
        const isNegative = totalAmount < 0;
        const sign = isNegative ? '-' : '+';
        const absAmount = Math.abs(totalAmount);
        const formattedAmount = `€${sign}${absAmount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        const amountColor = isNegative ? '#e74c3c' : '#27ae60';
        const urlName = encodeURIComponent(cp.name);

        html += `
            <tr>
                <td><a href="counterparty_trends.html?counterparty=${urlName}&year=all" style="color: #3498db; text-decoration: none; cursor: pointer;">${escapeHtmlForTable(cp.name)}</a></td>
                <td class="text-center">${cp.count || 0}</td>
                <td class="text-right" style="color: ${amountColor}; font-weight: 600;">${formattedAmount}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html || '<tr><td colspan="3" style="text-align: center; padding: 2rem; color: #7f8c8d;">No counterparties found</td></tr>';

    // Update sort indicators
    const table = tbody.closest('table');
    if (table) {
        const headers = table.querySelectorAll('th.sortable');
        headers.forEach(header => {
            header.classList.remove('sorted-asc', 'sorted-desc');
            if (header.dataset.sort === periodCounterpartyTableSortState.column) {
                header.classList.add(periodCounterpartyTableSortState.direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
            }
        });
    }

    // Add pagination handlers
    if (prevBtn) {
        prevBtn.onclick = () => {
            if (counterpartyPage > 1) {
                counterpartyPage--;
                renderPeriodCounterpartyTable();
            }
        };
    }

    if (nextBtn) {
        nextBtn.onclick = () => {
            const totalPages = Math.ceil((window.periodCounterpartyData?.length || 0) / itemsPerPage);
            if (counterpartyPage < totalPages) {
                counterpartyPage++;
                renderPeriodCounterpartyTable();
            }
        };
    }

    // Add sort handlers
    if (table) {
        const headers = table.querySelectorAll('th.sortable');
        headers.forEach(header => {
            // Remove existing listeners by cloning and replacing
            const newHeader = header.cloneNode(true);
            header.parentNode.replaceChild(newHeader, header);

            newHeader.addEventListener('click', function() {
                const column = this.dataset.sort;
                const currentDirection = (periodCounterpartyTableSortState.column === column && periodCounterpartyTableSortState.direction === 'asc') ? 'desc' : 'asc';

                // Update sort state
                periodCounterpartyTableSortState.column = column;
                periodCounterpartyTableSortState.direction = currentDirection;

                // Reset to first page when sorting changes
                counterpartyPage = 1;

                // Re-render table with new sort
                renderPeriodCounterpartyTable();
            });
        });
    }
}

// ============================================================================
// Phase 6: Export & Sharing Functions
// ============================================================================

// CSV Export Functions
function exportTableToCSV(tableSelector, filename, includeHeader = true) {
    // tableSelector can be an ID (for tbody) or a table element
    let table, thead, tbody;

    if (typeof tableSelector === 'string') {
        // If it's an ID, try to find the tbody first, then find its parent table
        tbody = document.getElementById(tableSelector);
        if (tbody) {
            table = tbody.closest('table');
            if (table) {
                thead = table.querySelector('thead');
            }
        } else {
            // Try to find table directly
            table = document.querySelector(`table`);
            if (table) {
                thead = table.querySelector('thead');
                tbody = table.querySelector('tbody');
            }
        }
    } else {
        table = tableSelector;
        thead = table ? table.querySelector('thead') : null;
        tbody = table ? table.querySelector('tbody') : null;
    }

    if (!tbody && !table) {
        console.error(`Table or tbody not found`);
        return;
    }

    // Build CSV content
    let csv = [];

    // Add header row if requested and available
    if (includeHeader && thead) {
        const headerRow = thead.querySelector('tr');
        if (headerRow) {
            const headerCells = headerRow.querySelectorAll('th');
            const headerData = [];
            headerCells.forEach(cell => {
                let text = cell.textContent.trim();
                // Skip sort indicators
                text = text.replace(/↕/g, '').trim();
                if (text.includes(',') || text.includes('"')) {
                    text = '"' + text.replace(/"/g, '""') + '"';
                }
                headerData.push(text);
            });
            csv.push(headerData.join(','));
        }
    }

    // Get all rows from tbody (or table if no tbody)
    const rows = tbody ? tbody.querySelectorAll('tr') : (table ? table.querySelectorAll('tbody tr') : []);
    if (rows.length === 0) {
        alert('No data to export');
        return;
    }

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = [];
        cells.forEach(cell => {
            // Skip sparkline canvas cells
            if (cell.querySelector('.sparkline')) {
                rowData.push('');
            } else {
                // Get text content, remove extra whitespace, and handle commas/quotes
                let text = cell.textContent.trim();
                // Remove currency symbols but keep numbers formatted
                text = text.replace(/€/g, '').trim();
                // Escape quotes and wrap in quotes if contains comma or quote
                if (text.includes(',') || text.includes('"') || text.includes('\n')) {
                    text = '"' + text.replace(/"/g, '""') + '"';
                }
                rowData.push(text);
            }
        });
        csv.push(rowData.join(','));
    });

    // Create download
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename || 'export.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Chart Export Functions
function exportChartToPNG(chartId, filename) {
    const canvas = document.getElementById(chartId);
    if (!canvas) {
        console.error(`Chart canvas with id "${chartId}" not found`);
        alert('Chart not found. Please ensure the chart is displayed.');
        return;
    }

    // Get chart instance if available
    let chart = null;
    if (window.categoryTrendChart && chartId === 'categoryTrendChart') {
        chart = window.categoryTrendChart;
    } else if (window.counterpartyTrendChart && chartId === 'counterpartyTrendChart') {
        chart = window.counterpartyTrendChart;
    } else if (window[chartId + 'Chart']) {
        chart = window[chartId + 'Chart'];
    }

    // Use chart's canvas if available, otherwise use the element directly
    const chartCanvas = chart && chart.canvas ? chart.canvas : canvas;

    if (!chartCanvas || typeof chartCanvas.toBlob !== 'function') {
        console.error('Chart canvas is not available or does not support toBlob');
        alert('Chart export is not available. Please ensure the chart is fully loaded.');
        return;
    }

    // Convert canvas to blob and download
    chartCanvas.toBlob(function(blob) {
        if (!blob) {
            alert('Failed to export chart. Please try again.');
            return;
        }
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', filename || 'chart.png');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }, 'image/png');
}

// Shareable URL Functions
function generateShareableURL(page, filters = {}) {
    const baseUrl = window.location.origin + window.location.pathname;
    const params = new URLSearchParams();

    // Add filters to URL
    Object.keys(filters).forEach(key => {
        if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
            if (Array.isArray(filters[key])) {
                filters[key].forEach(item => params.append(key, item));
            } else {
                params.set(key, filters[key]);
            }
        }
    });

    const queryString = params.toString();
    return queryString ? `${baseUrl}?${queryString}` : baseUrl;
}

function copyToClipboard(text, buttonElement) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            // Show temporary feedback
            if (buttonElement) {
                const originalText = buttonElement.textContent;
                buttonElement.textContent = '✓ Copied!';
                buttonElement.style.background = '#27ae60';
                buttonElement.style.color = 'white';
                setTimeout(() => {
                    buttonElement.textContent = originalText;
                    buttonElement.style.background = '';
                    buttonElement.style.color = '';
                }, 2000);
            }
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard');
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            if (buttonElement) {
                const originalText = buttonElement.textContent;
                buttonElement.textContent = '✓ Copied!';
                setTimeout(() => {
                    buttonElement.textContent = originalText;
                }, 2000);
            }
        } catch (err) {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard');
        }
        document.body.removeChild(textarea);
    }
}

// Initialize export and sharing handlers
function initializeExportAndSharing() {
    // Categories page CSV export
    const exportCategoriesCSV = document.getElementById('export-categories-csv');
    if (exportCategoriesCSV) {
        exportCategoriesCSV.addEventListener('click', function() {
            const periodSelector = document.getElementById('period-selector');
            const period = periodSelector ? periodSelector.value : 'ytd';
            const date = new Date().toISOString().split('T')[0];
            // Export the full table including header
            const tbody = document.getElementById('categories-tbody');
            const table = tbody ? tbody.closest('table') : null;
            if (table) {
                exportTableToCSV(table, `categories-${period}-${date}.csv`, true);
            } else if (tbody) {
                // Fallback to tbody only
                exportTableToCSV('categories-tbody', `categories-${period}-${date}.csv`, false);
            }
        });
    }

    // Categories page copy link
    const copyCategoriesLink = document.getElementById('copy-categories-link');
    if (copyCategoriesLink) {
        copyCategoriesLink.addEventListener('click', function(e) {
            const periodSelector = document.getElementById('period-selector');
            const typeFilter = document.querySelector('input[name="type-filter"]:checked');
            const compareToggle = document.getElementById('compare-toggle');
            const searchInput = document.getElementById('category-search');
            const amountMin = document.getElementById('category-amount-min');
            const amountMax = document.getElementById('category-amount-max');

            const filters = {
                period: periodSelector ? periodSelector.value : 'ytd',
                type: typeFilter ? typeFilter.value : 'both',
                compare: compareToggle && compareToggle.checked ? 'true' : null,
                search: searchInput && searchInput.value ? searchInput.value : null,
                amountMin: amountMin && amountMin.value ? amountMin.value : null,
                amountMax: amountMax && amountMax.value ? amountMax.value : null
            };

            const url = generateShareableURL('categories.html', filters);
            copyToClipboard(url, e.target);
        });
    }

    // Counterparties page CSV export
    const exportCounterpartiesCSV = document.getElementById('export-counterparties-csv');
    if (exportCounterpartiesCSV) {
        exportCounterpartiesCSV.addEventListener('click', function() {
            const periodSelector = document.getElementById('period-selector');
            const period = periodSelector ? periodSelector.value : 'ytd';
            const date = new Date().toISOString().split('T')[0];
            // Export the full table including header
            const table = document.getElementById('counterparties-table');
            if (table) {
                exportTableToCSV(table, `counterparties-${period}-${date}.csv`, true);
            }
        });
    }

    // Counterparties page copy link
    const copyCounterpartiesLink = document.getElementById('copy-counterparties-link');
    if (copyCounterpartiesLink) {
        copyCounterpartiesLink.addEventListener('click', function(e) {
            const periodSelector = document.getElementById('period-selector');
            const typeFilter = document.querySelector('input[name="type-filter"]:checked');
            const compareToggle = document.getElementById('compare-toggle');
            const searchInput = document.getElementById('counterparty-search');
            const amountMin = document.getElementById('counterparty-amount-min');
            const amountMax = document.getElementById('counterparty-amount-max');

            const filters = {
                period: periodSelector ? periodSelector.value : 'ytd',
                type: typeFilter ? typeFilter.value : 'both',
                compare: compareToggle && compareToggle.checked ? 'true' : null,
                search: searchInput && searchInput.value ? searchInput.value : null,
                amountMin: amountMin && amountMin.value ? amountMin.value : null,
                amountMax: amountMax && amountMax.value ? amountMax.value : null
            };

            const url = generateShareableURL('counterparties.html', filters);
            copyToClipboard(url, e.target);
        });
    }

    // Category trends chart export
    const exportCategoryChartPNG = document.getElementById('export-category-chart-png');
    if (exportCategoryChartPNG) {
        exportCategoryChartPNG.addEventListener('click', function() {
            exportChartToPNG('categoryTrendChart', 'category-trends.png');
        });
    }

    // Category trends copy link
    const copyCategoryTrendsLink = document.getElementById('copy-category-trends-link');
    if (copyCategoryTrendsLink) {
        copyCategoryTrendsLink.addEventListener('click', function(e) {
            const categoryMultiSelect = window.categoryMultiSelect;
            const yearSelector = document.getElementById('year-selector');
            const groupBySelector = document.getElementById('group-by-selector');
            const dateStart = document.getElementById('date-start');
            const dateEnd = document.getElementById('date-end');
            const amountMin = document.getElementById('amount-min');
            const amountMax = document.getElementById('amount-max');
            const cumulativeToggle = document.getElementById('cumulative-toggle');

            const selectedCategories = categoryMultiSelect ? categoryMultiSelect.getSelectedItems() : [];
            const filters = {
                category: selectedCategories.length === 1 ? selectedCategories[0] : null,
                categories: selectedCategories.length > 1 ? selectedCategories : null,
                year: yearSelector ? yearSelector.value : 'all',
                groupBy: groupBySelector ? groupBySelector.value : 'month',
                dateStart: dateStart && dateStart.value ? dateStart.value : null,
                dateEnd: dateEnd && dateEnd.value ? dateEnd.value : null,
                amountMin: amountMin && amountMin.value ? amountMin.value : null,
                amountMax: amountMax && amountMax.value ? amountMax.value : null,
                cumulative: cumulativeToggle && cumulativeToggle.checked ? 'true' : null
            };

            const url = generateShareableURL('category_trends.html', filters);
            copyToClipboard(url, e.target);
        });
    }

    // Counterparty trends chart export
    const exportCounterpartyChartPNG = document.getElementById('export-counterparty-chart-png');
    if (exportCounterpartyChartPNG) {
        exportCounterpartyChartPNG.addEventListener('click', function() {
            exportChartToPNG('counterpartyTrendChart', 'counterparty-trends.png');
        });
    }

    // Counterparty trends copy link
    const copyCounterpartyTrendsLink = document.getElementById('copy-counterparty-trends-link');
    if (copyCounterpartyTrendsLink) {
        copyCounterpartyTrendsLink.addEventListener('click', function(e) {
            const counterpartyMultiSelect = window.counterpartyMultiSelect;
            const yearSelector = document.getElementById('year-selector');
            const groupBySelector = document.getElementById('group-by-selector');
            const dateStart = document.getElementById('date-start');
            const dateEnd = document.getElementById('date-end');
            const amountMin = document.getElementById('amount-min');
            const amountMax = document.getElementById('amount-max');
            const cumulativeToggle = document.getElementById('cumulative-toggle');

            const selectedCounterparties = counterpartyMultiSelect ? counterpartyMultiSelect.getSelectedItems() : [];
            const filters = {
                counterparty: selectedCounterparties.length === 1 ? selectedCounterparties[0] : null,
                counterparties: selectedCounterparties.length > 1 ? selectedCounterparties : null,
                year: yearSelector ? yearSelector.value : 'all',
                groupBy: groupBySelector ? groupBySelector.value : 'month',
                dateStart: dateStart && dateStart.value ? dateStart.value : null,
                dateEnd: dateEnd && dateEnd.value ? dateEnd.value : null,
                amountMin: amountMin && amountMin.value ? amountMin.value : null,
                amountMax: amountMax && amountMax.value ? amountMax.value : null,
                cumulative: cumulativeToggle && cumulativeToggle.checked ? 'true' : null
            };

            const url = generateShareableURL('counterparty_trends.html', filters);
            copyToClipboard(url, e.target);
        });
    }
}

// Initialize export and sharing when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeExportAndSharing();
});

// ============================================================================
// Phase 7: Drill-Down Functions
// ============================================================================

function initializeDrillDownHandlers(data) {
    if (!data) return;

    // Remove existing event listeners by cloning and replacing elements
    document.querySelectorAll('.drill-down-row').forEach(row => {
        const expandIcon = row.querySelector('.expand-icon');
        if (expandIcon) {
            // Remove any existing click handlers by cloning the element
            const newExpandIcon = expandIcon.cloneNode(true);
            expandIcon.parentNode.replaceChild(newExpandIcon, expandIcon);

            newExpandIcon.addEventListener('click', function(e) {
                e.stopPropagation();
                e.preventDefault();
                const detailRow = row.nextElementSibling;
                if (detailRow && detailRow.classList.contains('drill-down-detail')) {
                    const isExpanded = detailRow.style.display !== 'none' && detailRow.style.display !== '';
                    if (isExpanded) {
                        detailRow.style.display = 'none';
                        newExpandIcon.textContent = '▶';
                    } else {
                        detailRow.style.display = 'table-row';
                        newExpandIcon.textContent = '▼';

                        // Load drill-down data if not already loaded
                        const contentDiv = detailRow.querySelector('.drill-down-content');
                        if (contentDiv && contentDiv.textContent.trim() === 'Loading...') {
                            const type = row.dataset.type;
                            if (type === 'category') {
                                const categoryName = row.dataset.category;
                                loadCategoryDrillDown(categoryName, contentDiv, data);
                            } else if (type === 'counterparty') {
                                const counterpartyName = row.dataset.counterparty;
                                loadCounterpartyDrillDown(counterpartyName, contentDiv, data);
                            }
                        }
                    }
                }
            });
        }
    });
}

function loadCategoryDrillDown(categoryName, container, data) {
    if (!data || !data.all_transactions) {
        container.innerHTML = '<span style="color: #e74c3c;">No data available</span>';
        return;
    }

    // Filter transactions for this category
    const categoryTransactions = data.all_transactions.filter(tx => {
        const txCategory = (tx.category || '').trim();
        return txCategory === categoryName || txCategory.startsWith(categoryName + ':');
    });

    if (categoryTransactions.length === 0) {
        container.innerHTML = '<span style="color: #7f8c8d;">No transactions found</span>';
        return;
    }

    // Group by counterparty
    const counterpartyMap = {};
    categoryTransactions.forEach(tx => {
        const cpName = normalizeCounterpartyNameForGrouping(tx.counterparty || 'Unknown');
        if (!counterpartyMap[cpName]) {
            counterpartyMap[cpName] = { total: 0, count: 0 };
        }
        counterpartyMap[cpName].total += tx.amount || 0;
        counterpartyMap[cpName].count += 1;
    });

    // Convert to array and sort
    const counterparties = Object.keys(counterpartyMap).map(name => ({
        name: name,
        total: counterpartyMap[name].total,
        count: counterpartyMap[name].count
    })).sort((a, b) => Math.abs(b.total) - Math.abs(a.total));

    // Render counterparties list
    const html = counterparties.map(cp => {
        const amountColor = cp.total >= 0 ? '#27ae60' : '#e74c3c';
        const sign = cp.total >= 0 ? '+' : '';
        const formattedAmount = `€${sign}${Math.abs(cp.total).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        const urlName = encodeURIComponent(cp.name);
        return `
            <div style="padding: 0.5rem; border-bottom: 1px solid #ecf0f1; display: flex; justify-content: space-between; align-items: center;">
                <a href="counterparty_trends.html?counterparty=${urlName}&year=all" style="color: #3498db; text-decoration: none;">${escapeHtmlForTable(cp.name)}</a>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span style="color: #7f8c8d; font-size: 0.9rem;">${cp.count} transaction${cp.count !== 1 ? 's' : ''}</span>
                    <span style="color: ${amountColor}; font-weight: 600;">${formattedAmount}</span>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `<div style="max-height: 300px; overflow-y: auto;">${html}</div>`;
}

function loadCounterpartyDrillDown(counterpartyName, container, data) {
    if (!data || !data.all_transactions) {
        container.innerHTML = '<span style="color: #e74c3c;">No data available</span>';
        return;
    }

    // Filter transactions for this counterparty
    const normalizedName = normalizeCounterpartyNameForGrouping(counterpartyName);
    const counterpartyTransactions = data.all_transactions.filter(tx => {
        const txCounterparty = normalizeCounterpartyNameForGrouping(tx.counterparty || 'Unknown');
        return txCounterparty === normalizedName;
    });

    if (counterpartyTransactions.length === 0) {
        container.innerHTML = '<span style="color: #7f8c8d;">No transactions found</span>';
        return;
    }

    // Group by category
    const categoryMap = {};
    counterpartyTransactions.forEach(tx => {
        const catName = (tx.category || '').trim() || 'Unknown';
        if (!categoryMap[catName]) {
            categoryMap[catName] = { total: 0, count: 0 };
        }
        categoryMap[catName].total += tx.amount || 0;
        categoryMap[catName].count += 1;
    });

    // Convert to array and sort
    const categories = Object.keys(categoryMap).map(name => ({
        name: name,
        total: categoryMap[name].total,
        count: categoryMap[name].count
    })).sort((a, b) => Math.abs(b.total) - Math.abs(a.total));

    // Render categories list
    const html = categories.map(cat => {
        const amountColor = cat.total >= 0 ? '#27ae60' : '#e74c3c';
        const sign = cat.total >= 0 ? '+' : '';
        const formattedAmount = `€${sign}${Math.abs(cat.total).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

        // Handle category tags
        let urlCategory, urlTag;
        if (cat.name.includes(':')) {
            const [baseCategory, tag] = cat.name.split(':', 2);
            urlCategory = encodeURIComponent(baseCategory);
            urlTag = encodeURIComponent(tag);
        } else {
            urlCategory = encodeURIComponent(cat.name);
            urlTag = null;
        }

        const categoryUrl = urlTag
            ? `category_trends.html?category=${urlCategory}&tag=${urlTag}&year=all`
            : `category_trends.html?category=${urlCategory}&year=all`;

        return `
            <div style="padding: 0.5rem; border-bottom: 1px solid #ecf0f1; display: flex; justify-content: space-between; align-items: center;">
                <a href="${categoryUrl}" style="color: #3498db; text-decoration: none;">${escapeHtmlForTable(cat.name)}</a>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span style="color: #7f8c8d; font-size: 0.9rem;">${cat.count} transaction${cat.count !== 1 ? 's' : ''}</span>
                    <span style="color: ${amountColor}; font-weight: 600;">${formattedAmount}</span>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `<div style="max-height: 300px; overflow-y: auto;">${html}</div>`;
}

// ============================================================================
// Phase 8: Forecasting & Projections Functions
// ============================================================================

function calculateProjections(monthlyData, groupBy, currentYear) {
    if (!monthlyData || monthlyData.length === 0) {
        return {
            nextPeriod: 0,
            annual: 0,
            confidenceNext: 'Low',
            confidenceAnnual: 'Low',
            trendDirection: 'Unknown',
            trendStrength: 'Unknown'
        };
    }

    // Extract values from monthly data
    const values = monthlyData.map(item => item.total || 0);

    if (values.length < 2) {
        return {
            nextPeriod: values[0] || 0,
            annual: values[0] || 0,
            confidenceNext: 'Very Low',
            confidenceAnnual: 'Very Low',
            trendDirection: 'Insufficient Data',
            trendStrength: 'Insufficient Data'
        };
    }

    // Calculate trend (simple linear regression)
    const n = values.length;
    let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
    values.forEach((y, i) => {
        const x = i + 1;
        sumX += x;
        sumY += y;
        sumXY += x * y;
        sumX2 += x * x;
    });

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    // Calculate average for simple projection
    const avg = sumY / n;
    const recentAvg = values.slice(-3).reduce((a, b) => a + b, 0) / Math.min(3, values.length);

    // Next period projection (use trend if strong, otherwise use recent average)
    const trendProjection = slope * (n + 1) + intercept;
    const nextPeriod = Math.abs(slope) > Math.abs(avg) * 0.1 ? trendProjection : recentAvg;

    // Annual projection (for YTD)
    const currentMonth = new Date().getMonth() + 1;
    let annualProjection = 0;
    let confidenceAnnual = 'Low';

    if (currentMonth > 0 && currentMonth <= 12) {
        const ytdTotal = values.reduce((a, b) => a + b, 0);
        const avgMonthly = ytdTotal / currentMonth;
        annualProjection = avgMonthly * 12;

        // Confidence based on number of months and variance
        const variance = values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / values.length;
        const coefficientOfVariation = Math.sqrt(variance) / Math.abs(avg || 1);

        if (currentMonth >= 6 && coefficientOfVariation < 0.3) {
            confidenceAnnual = 'High';
        } else if (currentMonth >= 3 && coefficientOfVariation < 0.5) {
            confidenceAnnual = 'Medium';
        } else {
            confidenceAnnual = 'Low';
        }
    }

    // Confidence for next period
    let confidenceNext = 'Low';
    const recentVariance = values.slice(-3).reduce((sum, val) => {
        return sum + Math.pow(val - recentAvg, 2);
    }, 0) / Math.min(3, values.length);
    const recentCV = Math.sqrt(recentVariance) / Math.abs(recentAvg || 1);

    if (recentCV < 0.2 && values.length >= 6) {
        confidenceNext = 'High';
    } else if (recentCV < 0.4 && values.length >= 3) {
        confidenceNext = 'Medium';
    } else {
        confidenceNext = 'Low';
    }

    // Trend direction and strength
    let trendDirection = 'Stable';
    let trendStrength = 'Weak';

    if (Math.abs(slope) > Math.abs(avg) * 0.05) {
        trendDirection = slope > 0 ? 'Increasing' : 'Decreasing';
        const trendRatio = Math.abs(slope) / Math.abs(avg || 1);
        if (trendRatio > 0.15) {
            trendStrength = 'Strong';
        } else if (trendRatio > 0.08) {
            trendStrength = 'Moderate';
        } else {
            trendStrength = 'Weak';
        }
    }

    return {
        nextPeriod: nextPeriod,
        annual: annualProjection,
        confidenceNext: confidenceNext,
        confidenceAnnual: confidenceAnnual,
        trendDirection: trendDirection,
        trendStrength: trendStrength
    };
}

function updateCategoryProjections(monthlyData, groupBy, currentYear) {
    const projections = calculateProjections(monthlyData, groupBy, currentYear);

    const nextEl = document.getElementById('category-projection-next');
    const annualEl = document.getElementById('category-projection-annual');
    const confidenceNextEl = document.getElementById('category-projection-confidence-next');
    const confidenceAnnualEl = document.getElementById('category-projection-confidence-annual');
    const directionEl = document.getElementById('category-trend-direction');
    const strengthEl = document.getElementById('category-trend-strength');

    if (nextEl) {
        const sign = projections.nextPeriod >= 0 ? '+' : '';
        nextEl.textContent = `€${sign}${Math.abs(projections.nextPeriod).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        nextEl.style.color = projections.nextPeriod >= 0 ? '#27ae60' : '#e74c3c';
    }
    if (annualEl) {
        const sign = projections.annual >= 0 ? '+' : '';
        annualEl.textContent = `€${sign}${Math.abs(projections.annual).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        annualEl.style.color = projections.annual >= 0 ? '#27ae60' : '#e74c3c';
    }
    if (confidenceNextEl) {
        const confidenceColor = projections.confidenceNext === 'High' ? '#27ae60' :
                               projections.confidenceNext === 'Medium' ? '#f39c12' : '#e74c3c';
        confidenceNextEl.textContent = `Confidence: ${projections.confidenceNext}`;
        confidenceNextEl.style.color = confidenceColor;
    }
    if (confidenceAnnualEl) {
        const confidenceColor = projections.confidenceAnnual === 'High' ? '#27ae60' :
                               projections.confidenceAnnual === 'Medium' ? '#f39c12' : '#e74c3c';
        confidenceAnnualEl.textContent = `Confidence: ${projections.confidenceAnnual}`;
        confidenceAnnualEl.style.color = confidenceColor;
    }
    if (directionEl) {
        directionEl.textContent = projections.trendDirection;
        directionEl.style.color = projections.trendDirection === 'Increasing' ? '#27ae60' :
                                  projections.trendDirection === 'Decreasing' ? '#e74c3c' : '#7f8c8d';
    }
    if (strengthEl) {
        strengthEl.textContent = `Strength: ${projections.trendStrength}`;
    }
}

function updateCounterpartyProjections(monthlyData, groupBy, currentYear) {
    const projections = calculateProjections(monthlyData, groupBy, currentYear);

    const nextEl = document.getElementById('counterparty-projection-next');
    const annualEl = document.getElementById('counterparty-projection-annual');
    const confidenceNextEl = document.getElementById('counterparty-projection-confidence-next');
    const confidenceAnnualEl = document.getElementById('counterparty-projection-confidence-annual');
    const directionEl = document.getElementById('counterparty-trend-direction');
    const strengthEl = document.getElementById('counterparty-trend-strength');

    if (nextEl) {
        const sign = projections.nextPeriod >= 0 ? '+' : '';
        nextEl.textContent = `€${sign}${Math.abs(projections.nextPeriod).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        nextEl.style.color = projections.nextPeriod >= 0 ? '#27ae60' : '#e74c3c';
    }
    if (annualEl) {
        const sign = projections.annual >= 0 ? '+' : '';
        annualEl.textContent = `€${sign}${Math.abs(projections.annual).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        annualEl.style.color = projections.annual >= 0 ? '#27ae60' : '#e74c3c';
    }
    if (confidenceNextEl) {
        const confidenceColor = projections.confidenceNext === 'High' ? '#27ae60' :
                               projections.confidenceNext === 'Medium' ? '#f39c12' : '#e74c3c';
        confidenceNextEl.textContent = `Confidence: ${projections.confidenceNext}`;
        confidenceNextEl.style.color = confidenceColor;
    }
    if (confidenceAnnualEl) {
        const confidenceColor = projections.confidenceAnnual === 'High' ? '#27ae60' :
                               projections.confidenceAnnual === 'Medium' ? '#f39c12' : '#e74c3c';
        confidenceAnnualEl.textContent = `Confidence: ${projections.confidenceAnnual}`;
        confidenceAnnualEl.style.color = confidenceColor;
    }
    if (directionEl) {
        directionEl.textContent = projections.trendDirection;
        directionEl.style.color = projections.trendDirection === 'Increasing' ? '#27ae60' :
                                  projections.trendDirection === 'Decreasing' ? '#e74c3c' : '#7f8c8d';
    }
    if (strengthEl) {
        strengthEl.textContent = `Strength: ${projections.trendStrength}`;
    }
}
