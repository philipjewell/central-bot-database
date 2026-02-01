// API endpoint: Get recommendations by category
export async function onRequestGet(context) {
    try {
        const url = new URL(context.request.url);
        const category = url.searchParams.get('category');
        const rating = url.searchParams.get('rating');

        const validCategories = ['ecommerce', 'news', 'media', 'blog', 'saas', 'corporate', 'documentation', 'social', 'portfolio', 'government'];
        const validRatings = ['beneficial', 'neutral', 'harmful', 'not_applicable'];

        if (!category || !validCategories.includes(category)) {
            return new Response(JSON.stringify({
                error: 'Invalid or missing category parameter',
                valid_categories: validCategories
            }), {
                status: 400,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        if (rating && !validRatings.includes(rating)) {
            return new Response(JSON.stringify({
                error: 'Invalid rating parameter',
                valid_ratings: validRatings
            }), {
                status: 400,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // Fetch bots data from GitHub
        const botsResponse = await fetch(
            'https://raw.githubusercontent.com/philipjewell/central-bot-database/main/data/bots.json'
        );
        const data = await botsResponse.json();
        const allBots = data.bots;

        // Filter bots by category and rating
        const filtered = allBots.filter(bot => {
            if (!bot.categories || !bot.categories[category]) {
                return false;
            }
            if (rating) {
                return bot.categories[category] === rating;
            }
            return true;
        });

        return new Response(JSON.stringify({
            category,
            rating: rating || 'all',
            bots: filtered,
            count: filtered.length
        }), {
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
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
