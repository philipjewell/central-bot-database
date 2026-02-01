// API endpoint: Get database statistics
export async function onRequestGet(context) {
    try {
        // Fetch bots data from GitHub
        const botsResponse = await fetch(
            'https://raw.githubusercontent.com/philipjewell/central-bot-database/main/data/bots.json'
        );
        const data = await botsResponse.json();
        const allBots = data.bots;

        // Calculate statistics
        const operators = new Set(allBots.map(bot => bot.operator).filter(Boolean));

        const sourceStats = {};
        allBots.forEach(bot => {
            (bot.sources || []).forEach(source => {
                sourceStats[source] = (sourceStats[source] || 0) + 1;
            });
        });

        const categoryStats = {};
        const categories = ['ecommerce', 'news', 'media', 'blog', 'saas', 'corporate', 'documentation', 'social', 'portfolio', 'government'];
        categories.forEach(category => {
            categoryStats[category] = {
                beneficial: 0,
                neutral: 0,
                harmful: 0,
                not_applicable: 0
            };
        });

        allBots.forEach(bot => {
            if (bot.categories) {
                Object.entries(bot.categories).forEach(([category, rating]) => {
                    if (categoryStats[category]) {
                        categoryStats[category][rating] = (categoryStats[category][rating] || 0) + 1;
                    }
                });
            }
        });

        // Find most recent update
        const lastUpdated = allBots
            .map(bot => bot.last_updated)
            .filter(Boolean)
            .sort()
            .reverse()[0] || null;

        return new Response(JSON.stringify({
            total_bots: allBots.length,
            operators: operators.size,
            sources: sourceStats,
            categories: categoryStats,
            last_updated: lastUpdated,
            generated_at: data.meta?.generated_at || null
        }), {
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'public, max-age=3600' // Cache for 1 hour
            }
        });
    } catch (error) {
        return new Response(JSON.stringify({
            error: 'Internal server error',
            message: error.message
        }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
