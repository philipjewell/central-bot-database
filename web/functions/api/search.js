// API endpoint: Search bots
export async function onRequestGet(context) {
    try {
        const url = new URL(context.request.url);
        const query = url.searchParams.get('q');
        const limit = Math.min(parseInt(url.searchParams.get('limit') || '10'), 100);

        if (!query) {
            return new Response(JSON.stringify({
                error: 'Missing required parameter: q'
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

        // Search bots
        const searchTerm = query.toLowerCase();
        const results = allBots.filter(bot => {
            return (
                bot.user_agent?.toLowerCase().includes(searchTerm) ||
                bot.operator?.toLowerCase().includes(searchTerm) ||
                bot.purpose?.toLowerCase().includes(searchTerm)
            );
        }).slice(0, limit);

        return new Response(JSON.stringify({
            results,
            count: results.length,
            query
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
