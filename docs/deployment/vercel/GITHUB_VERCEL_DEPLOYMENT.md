# Deploy Threadr Frontend via GitHub + Vercel (Easiest Method)

## Why This Method?
This approach bypasses CLI authentication issues and sets up automatic deployments.

## Step 1: Push to GitHub
1. Make sure your code is committed and pushed to GitHub
2. Your repository should have the `frontend/` directory with all files

## Step 2: Connect to Vercel via Web Interface
1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub (or your preferred method)
3. Click "New Project"
4. Import your GitHub repository
5. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: Leave empty (static site)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

## Step 3: Environment Variables (Optional)
Add this environment variable in Vercel:
- **Name**: `THREADR_API_URL`
- **Value**: `https://threadr-production.up.railway.app`

## Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Get your deployment URL (e.g., `https://threadr-abc123.vercel.app`)

## Step 5: Test
1. Visit your deployment URL
2. Test thread generation
3. Verify backend connectivity

## Benefits of This Approach
- ✅ No CLI authentication needed
- ✅ Automatic deployments on push
- ✅ Easy to manage via web interface
- ✅ Built-in rollback capabilities
- ✅ Custom domain setup via dashboard

## After Deployment
Your frontend will be live and the 404 error will be resolved!

The app will automatically:
- Detect it's in production
- Use the Railway backend URL
- Handle CORS properly
- Show the email capture modal after first use