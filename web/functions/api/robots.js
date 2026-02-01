// API endpoint: Generate robots.txt
export async function onRequestGet(context) {
    try {
        const url = new URL(context.request.url);
        const category = url.searchParams.get('category');
        const blockLevel = url.searchParams.get('block') || 'harmful';

        const validCategories = ['ecommerce', 'news', 'media', 'blog', 'saas', 'corporate', 'documentation', 'social', 'portfolio', 'government'];

        if (!category || !validCategories.includes(category)) {
            return new Response(JSON.stringify({
                error: 'Invalid or missing category parameter',
                valid_categories: validCategories
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

        // Determine which ratings to block
        const ratingsToBlock = blockLevel === 'harmful+neutral'
            ? ['harmful', 'neutral']
            : ['harmful'];

        // Filter bots to block
        const botsToBlock = allBots.filter(bot => {
            if (!bot.categories || !bot.categories[category]) {
                return false;
            }
            return ratingsToBlock.includes(bot.categories[category]);
        });

        // Generate robots.txt
        const lines = [
            `# Generated robots.txt for ${category} sites`,
            `# Blocking: ${ratingsToBlock.join(', ')} bots`,
            `# Generated: ${new Date().toISOString()}`,
            `# Total bots blocked: ${botsToBlock.length}`,
            '',
            '# Allow all beneficial bots',
            'User-agent: *',
            'Allow: /',
            ''
        ];

        // Add blocked bots
        if (botsToBlock.length > 0) {
            lines.push('# Blocked bots');
            botsToBlock.forEach(bot => {
                lines.push(`User-agent: ${bot.user_agent}`);
                lines.push('Disallow: /');
                lines.push('');
            });
        }

        const robotsTxt = lines.join('\n');

        return new Response(robotsTxt, {
            headers: {
                'Content-Type': 'text/plain',
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
