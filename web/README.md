# Central Bot Database - Web Application

A modern web interface for browsing and querying the Central Bot Database with a RESTful API powered by Cloudflare Pages and Workers.

## Features

- 🔍 **Searchable Table** - Search and filter bots by name, operator, purpose, and more
- 📊 **Advanced Filtering** - Filter by operator, source, site category, and rating
- ↕️ **Sortable Columns** - Click column headers to sort
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🚀 **Fast API** - RESTful API endpoints for programmatic access
- 🌐 **Static Hosting** - Deploys to Cloudflare Pages (no server required)
- 🔄 **Auto-Updates** - Pulls latest data directly from GitHub

## Quick Start (Local Development)

1. **Serve the web directory:**
   ```bash
   # Using Python
   cd web
   python -m http.server 8000

   # Or using Node.js
   npx serve web
   ```

2. **Open in browser:**
   ```
   http://localhost:8000
   ```

## Deploy to Cloudflare Pages

### Option 1: Using Cloudflare Dashboard (Recommended)

1. **Sign in to Cloudflare**
   - Go to https://dash.cloudflare.com
   - Navigate to **Pages** in the sidebar

2. **Create a new Pages project**
   - Click **Create a project**
   - Connect your GitHub account
   - Select your forked `central-bot-database` repository

3. **Configure build settings**
   - **Build command:** (leave empty - static site)
   - **Build output directory:** `/web`
   - **Root directory:** `/web`

4. **Deploy**
   - Click **Save and Deploy**
   - Your site will be live at `https://your-project.pages.dev`

### Option 2: Using Wrangler CLI

1. **Install Wrangler**
   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare**
   ```bash
   wrangler login
   ```

3. **Deploy from the web directory**
   ```bash
   cd web
   wrangler pages deploy . --project-name=central-bot-database
   ```

4. **Your site is now live!**
   ```
   https://central-bot-database.pages.dev
   ```

## Custom Domain

1. In Cloudflare Pages dashboard, go to your project
2. Click **Custom domains**
3. Add your domain (e.g., `bots.yourdomain.com`)
4. Follow the DNS setup instructions

## API Endpoints

All API endpoints are serverless Cloudflare Workers that run on the edge.

### Base URL
```
https://your-deployment.pages.dev/api
```

### Available Endpoints

#### 1. Search Bots
```bash
GET /api/search?q=googlebot&limit=10
```

#### 2. Get Recommendations
```bash
GET /api/recommend?category=ecommerce&rating=beneficial
```

#### 3. Get Bot Details
```bash
GET /api/details?bot=Googlebot
```

#### 4. Generate robots.txt
```bash
GET /api/robots?category=ecommerce&block=harmful
```

#### 5. Get Statistics
```bash
GET /api/stats
```

See the [API Documentation](https://your-deployment.pages.dev/api.html) for full details.

## Configuration

### Update Data Source

By default, the app pulls data from:
```
https://raw.githubusercontent.com/philipjewell/central-bot-database/main/data/bots.json
```

To use your own fork:

1. Edit `web/js/app.js` and update the fetch URL (line 17):
   ```javascript
   const response = await fetch('https://raw.githubusercontent.com/YOUR-USERNAME/central-bot-database/main/data/bots.json');
   ```

2. Edit all API function files in `web/functions/api/*.js` and update the fetch URLs

### Customize Styling

Edit `web/css/styles.css` to customize colors, fonts, and layout:
```css
:root {
    --primary-color: #3b82f6;  /* Change to your brand color */
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... more variables ... */
}
```

## Architecture

```
web/
├── index.html              # Main browsing interface
├── api.html               # API documentation page
├── css/
│   └── styles.css         # Global styles
├── js/
│   └── app.js            # Main application logic
├── functions/            # Cloudflare Workers API
│   └── api/
│       ├── search.js     # Search endpoint
│       ├── recommend.js  # Recommendations endpoint
│       ├── details.js    # Bot details endpoint
│       ├── robots.js     # robots.txt generator
│       └── stats.js      # Statistics endpoint
├── _headers              # HTTP headers configuration
└── README.md            # This file
```

## How It Works

1. **Static Frontend**: HTML/CSS/JS hosted on Cloudflare Pages CDN
2. **Serverless API**: Cloudflare Workers functions handle API requests
3. **Data Source**: Fetches fresh data from GitHub raw content on each request
4. **Edge Computing**: Everything runs on Cloudflare's global network

## Performance

- **Global CDN**: Static assets served from Cloudflare's edge network
- **Fast API**: Workers execute in ~10ms on the edge
- **Smart Caching**: API responses cached for 1 hour
- **Client-side Filtering**: Table filtering/sorting happens in browser (instant)

## Browser Support

- ✅ Chrome/Edge (latest 2 versions)
- ✅ Firefox (latest 2 versions)
- ✅ Safari (latest 2 versions)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### API returns 404
- Make sure you've deployed with the `functions/` directory included
- Check that your Cloudflare Pages build output directory is set to `/web`

### Data not loading
- Check browser console for errors
- Verify the GitHub raw URL is accessible
- Make sure CORS is enabled (handled by `_headers` file)

### Custom domain not working
- Verify DNS records are correct
- Allow 24-48 hours for DNS propagation
- Check SSL/TLS settings in Cloudflare dashboard

## Contributing

To contribute improvements to the web app:

1. Fork the repository
2. Make changes in the `web/` directory
3. Test locally
4. Submit a pull request

## License

MIT License - Same as the main Central Bot Database project

## Support

- 📖 [Main Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/philipjewell/central-bot-database/issues)
- 💬 [Discussions](https://github.com/philipjewell/central-bot-database/discussions)

---

Built with ❤️ using Cloudflare Pages and Workers
