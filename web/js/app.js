// Bot Database Web App
let allBots = [];
let filteredBots = [];
let currentPage = 1;
const botsPerPage = 50;
let sortColumn = null;
let sortDirection = 'asc';

// Category rating badges
const RATING_BADGES = {
    'beneficial': '✅ Beneficial',
    'neutral': '⚪ Neutral',
    'harmful': '❌ Harmful',
    'not_applicable': '➖ N/A'
};

// Emoji-only ratings for compact display
const RATING_EMOJIS = {
    'beneficial': '✅',
    'neutral': '⚪',
    'harmful': '❌',
    'not_applicable': '➖'
};

// Category display names for tooltips
const CATEGORY_NAMES = {
    'ecommerce': 'E-commerce',
    'news': 'News',
    'media': 'Media',
    'blog': 'Blog',
    'saas': 'SaaS',
    'corporate': 'Corporate',
    'documentation': 'Documentation',
    'social': 'Social',
    'portfolio': 'Portfolio',
    'government': 'Government'
};

// Ordered list of categories to display
const CATEGORY_ORDER = ['ecommerce', 'news', 'media', 'blog', 'saas', 'corporate', 'documentation', 'social', 'portfolio', 'government'];

// Load bots from GitHub
async function loadBots() {
    try {
        const response = await fetch('https://raw.githubusercontent.com/philipjewell/central-bot-database/main/data/bots.json');
        const data = await response.json();
        allBots = data.bots;
        filteredBots = allBots;

        populateFilters();
        updateStats();
        renderTable();
    } catch (error) {
        console.error('Error loading bots:', error);
        document.getElementById('botsTableBody').innerHTML = `
            <tr><td colspan="6" class="loading" style="color: #ef4444;">
                Error loading bot database. Please try again later.
            </td></tr>
        `;
    }
}

// Populate filter dropdowns
function populateFilters() {
    const operators = new Set(allBots.map(bot => bot.operator).filter(Boolean));
    const operatorFilter = document.getElementById('operatorFilter');

    Array.from(operators).sort().forEach(operator => {
        const option = document.createElement('option');
        option.value = operator;
        option.textContent = operator;
        operatorFilter.appendChild(option);
    });
}

// Update statistics
function updateStats() {
    document.getElementById('totalBots').textContent = allBots.length;
    document.getElementById('filteredBots').textContent = filteredBots.length;

    const operators = new Set(allBots.map(bot => bot.operator).filter(Boolean));
    document.getElementById('operatorCount').textContent = operators.size;
}

// Filter bots
function filterBots() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const operatorFilter = document.getElementById('operatorFilter').value;
    const sourceFilter = document.getElementById('sourceFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const ratingFilter = document.getElementById('ratingFilter').value;

    filteredBots = allBots.filter(bot => {
        // Search filter
        const searchMatch = !searchTerm ||
            bot.user_agent?.toLowerCase().includes(searchTerm) ||
            bot.operator?.toLowerCase().includes(searchTerm) ||
            bot.purpose?.toLowerCase().includes(searchTerm);

        // Operator filter
        const operatorMatch = !operatorFilter || bot.operator === operatorFilter;

        // Source filter
        const sourceMatch = !sourceFilter || bot.sources?.includes(sourceFilter);

        // Category and rating filter
        let categoryMatch = true;
        if (categoryFilter && ratingFilter) {
            categoryMatch = bot.categories?.[categoryFilter] === ratingFilter;
        }

        return searchMatch && operatorMatch && sourceMatch && categoryMatch;
    });

    currentPage = 1;
    updateStats();
    renderTable();
}

// Sort bots
function sortBots(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }

    filteredBots.sort((a, b) => {
        let aVal = a[column] || '';
        let bVal = b[column] || '';

        // Handle arrays (like sources)
        if (Array.isArray(aVal)) aVal = aVal.join(', ');
        if (Array.isArray(bVal)) bVal = bVal.join(', ');

        // String comparison
        aVal = aVal.toString().toLowerCase();
        bVal = bVal.toString().toLowerCase();

        if (sortDirection === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });

    updateSortIcons();
    renderTable();
}

// Update sort icons
function updateSortIcons() {
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        if (th.dataset.sort === sortColumn) {
            th.classList.add(`sort-${sortDirection}`);
        }
    });
}

// Render table
function renderTable() {
    const tbody = document.getElementById('botsTableBody');
    const start = (currentPage - 1) * botsPerPage;
    const end = start + botsPerPage;
    const pageItems = filteredBots.slice(start, end);

    if (pageItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No bots found matching your filters.</td></tr>';
        updatePagination();
        return;
    }

    tbody.innerHTML = pageItems.map(bot => {
        const categoryRatings = getCategoryRatings(bot);
        const sources = (bot.sources || []).map(s =>
            `<span class="source-tag">${s}</span>`
        ).join('');

        return `
            <tr>
                <td><strong>${escapeHtml(bot.user_agent || 'Unknown')}</strong></td>
                <td>${escapeHtml(bot.operator || 'Unknown')}</td>
                <td>${truncate(escapeHtml(bot.purpose || 'No description'), 100)}</td>
                <td>${categoryRatings}</td>
                <td>${sources}</td>
                <td>
                    <button class="view-details" onclick="showBotDetails('${escapeHtml(bot.user_agent)}')">
                        View
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    updatePagination();
}

// Get category ratings for display
function getCategoryRatings(bot) {
    if (!bot.categories) return '-';

    // Show all 10 categories in order, emoji-only for compact display
    return CATEGORY_ORDER.map(category => {
        const rating = bot.categories[category] || 'not_applicable';
        const emoji = RATING_EMOJIS[rating] || '❓';
        const categoryName = CATEGORY_NAMES[category];
        const ratingName = RATING_BADGES[rating]?.split(' ')[1] || rating;

        return `<span class="category-emoji" title="${categoryName}: ${ratingName}">${emoji}</span>`;
    }).join(' ');
}

// Show bot details modal
function showBotDetails(userAgent) {
    const bot = allBots.find(b => b.user_agent === userAgent);
    if (!bot) return;

    const modal = document.getElementById('botModal');
    const details = document.getElementById('botDetails');

    // Format raw data
    const rawData = bot.raw_data || {};
    const technicalDetails = [];

    if (rawData.ip_ranges?.length) {
        technicalDetails.push(`IP Ranges: ${rawData.ip_ranges.join(', ')}`);
    }
    if (rawData.asn) {
        technicalDetails.push(`ASN: ${rawData.asn}`);
    }
    if (rawData.cf_traffic_percentage) {
        technicalDetails.push(`CF Traffic: ${(parseFloat(rawData.cf_traffic_percentage) * 100).toFixed(2)}%`);
    }
    if (rawData.verification_method) {
        technicalDetails.push(`Verification: ${rawData.verification_method}`);
    }

    details.innerHTML = `
        <h2>${escapeHtml(bot.user_agent)}</h2>

        <div class="detail-section">
            <div class="detail-label">Operator</div>
            <div class="detail-value"><strong>${escapeHtml(bot.operator || 'Unknown')}</strong></div>
        </div>

        <div class="detail-section">
            <div class="detail-label">Purpose</div>
            <div class="detail-value">${escapeHtml(bot.purpose || 'No description available')}</div>
        </div>

        <div class="detail-section">
            <div class="detail-label">Impact of Blocking</div>
            <div class="detail-value">${escapeHtml(bot.impact_of_blocking || 'Unknown')}</div>
        </div>

        ${bot.website ? `
        <div class="detail-section">
            <div class="detail-label">Website</div>
            <div class="detail-value">
                <a href="${escapeHtml(bot.website)}" target="_blank">${escapeHtml(bot.website)}</a>
            </div>
        </div>
        ` : ''}

        ${technicalDetails.length > 0 ? `
        <div class="detail-section">
            <div class="detail-label">Technical Details</div>
            <div class="detail-value">${technicalDetails.join(' | ')}</div>
        </div>
        ` : ''}

        <div class="detail-section">
            <div class="detail-label">Sources</div>
            <div class="detail-value">
                ${(bot.sources || []).map(s => `<span class="source-tag">${s}</span>`).join(' ')}
            </div>
        </div>

        ${bot.categories ? `
        <div class="detail-section">
            <div class="detail-label">Recommendations by Site Type</div>
            <div class="category-grid">
                ${Object.entries(bot.categories).map(([category, rating]) => `
                    <div class="category-item">
                        <div class="category-name">${category}</div>
                        <span class="badge badge-${rating}">${RATING_BADGES[rating] || rating}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}

        ${bot.last_updated ? `
        <div class="detail-section" style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
            <div class="detail-value" style="color: #6b7280; font-size: 0.9rem;">
                Last updated: ${new Date(bot.last_updated).toLocaleDateString()}
            </div>
        </div>
        ` : ''}
    `;

    modal.style.display = 'block';
}

// Update pagination
function updatePagination() {
    const totalPages = Math.ceil(filteredBots.length / botsPerPage);
    document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages;
}

// Utility functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadBots();

    // Search and filters
    document.getElementById('searchInput').addEventListener('input', filterBots);
    document.getElementById('operatorFilter').addEventListener('change', filterBots);
    document.getElementById('sourceFilter').addEventListener('change', filterBots);
    document.getElementById('categoryFilter').addEventListener('change', filterBots);
    document.getElementById('ratingFilter').addEventListener('change', filterBots);

    // Reset filters
    document.getElementById('resetFilters').addEventListener('click', () => {
        document.getElementById('searchInput').value = '';
        document.getElementById('operatorFilter').value = '';
        document.getElementById('sourceFilter').value = '';
        document.getElementById('categoryFilter').value = '';
        document.getElementById('ratingFilter').value = '';
        filterBots();
    });

    // Sorting
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => sortBots(th.dataset.sort));
    });

    // Pagination
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        const totalPages = Math.ceil(filteredBots.length / botsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
        }
    });

    // Modal
    const modal = document.getElementById('botModal');
    const closeBtn = document.querySelector('.close');

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Make showBotDetails globally accessible
window.showBotDetails = showBotDetails;
