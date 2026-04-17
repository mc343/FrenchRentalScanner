# Deployment Guide

This document provides deployment instructions for the French Rental Scanner application, with a focus on Vercel deployment while acknowledging architectural considerations.

## Prerequisites

Before deploying to Vercel, ensure you have:

1. **Vercel Account**: Create a free account at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install the Vercel CLI globally:
   ```bash
   npm install -g vercel
   ```
   Verify installation: `vercel --version`

3. **GitHub Account**: For seamless deployment integration
4. **Python Environment**: Local Python 3.8+ for testing

## Architecture Considerations

**Important Note**: The French Rental Scanner was originally designed as a Streamlit application. Streamlit is optimized for long-running processes and interactive sessions, which doesn't align perfectly with Vercel's serverless architecture:

- **Timeout Limits**: Vercel's Hobby tier has a 10-second function timeout (Pro tier: 60 seconds)
- **Stateless Design**: Serverless functions are stateless, which conflicts with Streamlit's session-based architecture
- **Cold Starts**: Serverless functions have cold start delays that affect user experience

### Current Implementation

The current implementation includes:
- **WSGI Adapter** (`api/index.py`): Adapts the application for serverless deployment
- **Optimized Core**: Streamlit-independent core functionality in `main.py`
- **Stateless API**: RESTful endpoints for scraping operations

## Environment Variables

Configure these environment variables in your Vercel project settings:

### Required Variables
- `PYTHON_VERSION`: `3.12` (or your target version)
- `SCRAPER_TIMEOUT`: `30` (timeout in seconds for scraping operations)

### Optional Variables
- `LOG_LEVEL`: `INFO` (default logging level)
- `CACHE_ENABLED`: `true` (enable caching for better performance)
- `MAX_CONCURRENT_SCRAPERS`: `3` (limit concurrent operations)

### Setting Environment Variables in Vercel:

1. Go to your project dashboard on Vercel
2. Navigate to **Settings** → **Environment Variables**
3. Add each variable with appropriate value
4. Select applicable environments (Production, Preview, Development)

## Deployment Steps

### Option 1: Deploy via Vercel CLI

1. **Navigate to project directory**:
   ```bash
   cd /path/to/rentalscanner
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy to Vercel**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Set up and deploy? **Y**
   - Which scope? (Select your account)
   - Link to existing project? **N** (for new project)
   - Project name: `french-rental-scanner`
   - In which directory is your code? **.** (current directory)
   - Override settings? **N** (use defaults from vercel.json)

5. **Production Deployment**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard

1. **Import Project**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click **Add New** → **Project**
   - Import from Git (GitHub, GitLab, or Bitbucket)

2. **Configure Project**:
   - Framework Preset: **Python**
   - Root Directory: `./`
   - Build Command: (leave empty for default)
   - Output Directory: (leave empty for default)

3. **Environment Variables**:
   - Add required environment variables (see above)

4. **Deploy**:
   - Click **Deploy**

### Option 3: Continuous Deployment from Git

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect Repository in Vercel**:
   - Follow Option 2 steps to import from Git
   - Vercel will auto-deploy on every push to main branch

## Verification

After deployment, verify your application:

1. **Check Deployment Status**:
   - Visit your Vercel dashboard
   - Ensure deployment shows "Ready" status

2. **Test API Endpoints**:
   ```bash
   # Test health check
   curl https://your-project.vercel.app/api/health

   # Test scraping endpoint
   curl https://your-project.vercel.app/api/scrape
   ```

3. **Monitor Logs**:
   - Vercel Dashboard → Your Project → **Functions** tab
   - Check for any runtime errors or warnings

## Troubleshooting

### Common Issues

#### 1. Timeout Errors
**Problem**: Functions timing out during scraping operations

**Solutions**:
- Upgrade to Vercel Pro plan for 60-second timeout
- Implement background job processing
- Break up large scraping tasks into smaller chunks
- Use Vercel Cron Jobs for scheduled tasks

#### 2. Cold Start Delays
**Problem**: Slow initial response times

**Solutions**:
- Keep function size small (minimize dependencies)
- Use `@vercel/python` edge runtime for faster cold starts
- Implement keep-alive mechanisms
- Consider alternative deployment (see below)

#### 3. Memory Limit Exceeded
**Problem**: Functions running out of memory

**Solutions**:
- Optimize memory usage in scraping code
- Process fewer URLs per request
- Upgrade to Vercel Pro for higher memory limits
- Implement streaming responses

#### 4. Import Errors
**Problem**: Missing dependencies or import failures

**Solutions**:
- Verify `requirements.txt` is up to date
- Test locally with `vercel dev`
- Check Vercel build logs for specific errors
- Ensure Python version compatibility

#### 5. Streamlit Session Issues
**Problem**: Streamlit sessions not persisting

**Solutions**:
- Use the WSGI adapter included in `api/index.py`
- Implement stateless REST API endpoints
- Store session data in external service (Redis, database)
- Consider removing Streamlit dependency for serverless

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Deploy with debug enabled
vercel env add LOG_LEVEL DEBUG
vercel --prod
```

### Local Testing with Vercel Dev

Test your deployment locally before pushing:

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Start local development server
vercel dev

# Test your endpoints
curl http://localhost:3000/api/health
```

## Alternative Deployment Options

Given the architectural constraints of serverless platforms, consider these alternatives:

### Streamlit Cloud (Recommended for Original Application)
- **Best for**: Streamlit applications
- **Advantages**: Designed for Streamlit, free tier available, easy deployment
- **Link**: [streamlit.io/cloud](https://streamlit.io/cloud)
- **Deployment**: Connect your GitHub repository and deploy

### Railway
- **Best for**: Full-stack applications with background workers
- **Advantages**: Longer timeouts, persistent storage, background jobs
- **Link**: [railway.app](https://railway.app)
- **Deployment**: `railway up` from project directory

### Render
- **Best for**: Web services and APIs
- **Advantages**: Free tier, persistent storage, cron jobs
- **Link**: [render.com](https://render.com)
- **Deployment**: Connect repository and configure

### Fly.io
- **Best for**: Near-global deployment
- **Advantages**: Edge deployment, persistent storage, Docker support
- **Link**: [fly.io](https://fly.io)
- **Deployment**: `fly launch` from project directory

### AWS Lambda + API Gateway
- **Best for**: Enterprise serverless deployments
- **Advantages**: Longer timeouts (15 minutes), more control, AWS ecosystem
- **Deployment**: Use AWS SAM or Serverless Framework

## Monitoring and Maintenance

### Vercel Analytics
- Enable analytics in project settings
- Monitor function invocations and duration
- Track error rates and performance

### Logging
- Check Vercel function logs regularly
- Set up log exports to external services
- Monitor for scraping failures or performance issues

### Performance Optimization
- Review function execution times
- Optimize expensive operations
- Implement caching where appropriate
- Consider CDN for static assets

## Cost Considerations

### Vercel Pricing (as of 2025)
- **Hobby Tier**: Free
  - 10-second timeout
  - 100GB bandwidth
  - Limited functions
  
- **Pro Tier**: $20/month
  - 60-second timeout
  - 1TB bandwidth
  - Unlimited functions
  - Team collaboration

### When to Upgrade
- Need longer timeouts
- Exceed bandwidth limits
- Require team features
- Need advanced analytics

## Support and Resources

### Documentation
- [Vercel Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [Environment Variables](https://vercel.com/docs/projects/environment-variables)

### Community
- [Vercel Discord](https://vercel.com/discord)
- [Vercel GitHub](https://github.com/vercel/vercel)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/vercel)

## Conclusion

While Vercel deployment is possible with the current implementation, be mindful of the architectural constraints. For the best experience with Streamlit applications, consider Streamlit Cloud or other platforms designed for long-running processes. The included WSGI adapter and optimized core provide flexibility for various deployment scenarios.

For questions or issues, please refer to the main project README or open an issue on GitHub.
