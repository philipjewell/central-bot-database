// API endpoint: Get bot details
export async function onRequestGet(context) {
    try {
        const url = new URL(context.request.url);
        const botQuery = url.searchParams.get('bot');

        if (!botQuery) {
            return new Response(JSON.stringify({
                error: 'Missing required parameter: bot'
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

        // Find bot (case-insensitive)
        const searchTerm = botQuery.toLowerCase();
        const bot = allBots.find(b =>
            b.user_agent?.toLowerCase() === searchTerm ||
            b.user_agent?.toLowerCase().includes(searchTerm)
        );

        if (!bot) {
            return new Response(JSON.stringify({
                error: 'Bot not found',
                query: botQuery
            }), {
                status: 404,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        return new Response(JSON.stringify(bot), {
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
