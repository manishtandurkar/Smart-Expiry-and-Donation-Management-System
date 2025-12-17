# Deployment Guide

Complete guide for deploying the Smart Expiry and Donation Management System to production.

---

## Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Vercel    │─────▶│    Render    │─────▶│   Railway   │
│  (Frontend) │      │  (Backend)   │      │   (MySQL)   │
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                            │
                     ┌──────▼───────┐
                     │ MongoDB Atlas│
                     │   (NoSQL)    │
                     └──────────────┘
```

---

## Step 1: Deploy MySQL to Railway

### 1.1 Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Create new project

### 1.2 Add MySQL Service
1. Click "New" → "Database" → "MySQL"
2. Wait for provisioning
3. Go to "Variables" tab
4. Note down these credentials:
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`

### 1.3 Import Schema
```bash
# Install MySQL client locally if needed
# Connect to Railway MySQL
mysql -h <MYSQL_HOST> -P <MYSQL_PORT> -u <MYSQL_USER> -p<MYSQL_PASSWORD>

# Create database
CREATE DATABASE expiry_donation_db;
USE expiry_donation_db;

# Copy-paste schema.sql content or:
source database/schema.sql
```

**Alternative:** Use Railway's MySQL client in dashboard

### 1.4 Verify Data
```sql
SHOW TABLES;
SELECT COUNT(*) FROM Category;
SELECT * FROM Item LIMIT 5;
```

---

## Step 2: Deploy MongoDB to Atlas

### 2.1 Create Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up (free tier available)
3. Create cluster (M0 Free tier)

### 2.2 Configure Cluster
1. Choose cloud provider (AWS recommended)
2. Choose region closest to you
3. Cluster name: `expiry-donation-cluster`

### 2.3 Create Database User
1. Security → Database Access → Add New User
2. Username: `admin`
3. Password: Generate strong password
4. Built-in Role: `Read and write to any database`

### 2.4 Whitelist IP
1. Security → Network Access → Add IP Address
2. Option 1: Add your current IP
3. Option 2: Allow access from anywhere (0.0.0.0/0) - for testing only

### 2.5 Get Connection String
1. Click "Connect"
2. Choose "Connect your application"
3. Driver: Python
4. Copy connection string:
   ```
   mongodb+srv://admin:<password>@cluster0.xxxxx.mongodb.net/
   ```
5. Replace `<password>` with actual password
6. Add database name at the end:
   ```
   mongodb+srv://admin:pass123@cluster0.xxxxx.mongodb.net/expiry_donation_db
   ```

---

## Step 3: Deploy Backend to Render

### 3.1 Prepare Backend for Deployment

Create `backend/Procfile` (if using Heroku) or use Render's settings:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Update `backend/requirements.txt` to ensure all dependencies are listed:
```bash
cd backend
pip freeze > requirements.txt
```

### 3.2 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### 3.3 Create Web Service
1. Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `expiry-donation-api`
   - **Region**: Choose closest
   - **Branch**: `main` or `master`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3.4 Add Environment Variables
In Render dashboard, add these environment variables:

```env
MYSQL_HOST=<from Railway>
MYSQL_PORT=<from Railway>
MYSQL_USER=<from Railway>
MYSQL_PASSWORD=<from Railway>
MYSQL_DATABASE=expiry_donation_db

MONGO_URI=<from MongoDB Atlas>
MONGO_DATABASE=expiry_donation_db

APP_NAME=Smart Expiry and Donation Management System
DEBUG=False
EXPIRY_CHECK_DAYS=30
```

### 3.5 Deploy
1. Click "Create Web Service"
2. Wait for build to complete
3. Note your backend URL: `https://expiry-donation-api.onrender.com`

### 3.6 Test Backend
```bash
curl https://expiry-donation-api.onrender.com/health
curl https://expiry-donation-api.onrender.com/api/categories
```

Visit: `https://expiry-donation-api.onrender.com/docs`

---

## Step 4: Deploy Frontend to Vercel

### 4.1 Update API URL
Edit `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://expiry-donation-api.onrender.com';
```

Or create `frontend/.env.production`:
```env
VITE_API_URL=https://expiry-donation-api.onrender.com
```

### 4.2 Update CORS in Backend
Update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app"           # Allow all Vercel preview URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.3 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

### 4.4 Deploy from GitHub
1. Dashboard → Add New → Project
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 4.5 Add Environment Variables (if needed)
```env
VITE_API_URL=https://expiry-donation-api.onrender.com
```

### 4.6 Deploy
1. Click "Deploy"
2. Wait for build
3. Note your frontend URL: `https://your-app.vercel.app`

### 4.7 Test Frontend
1. Visit `https://your-app.vercel.app`
2. Check dashboard loads
3. Try adding an item
4. Verify data in Railway MySQL

---

## Step 5: Post-Deployment Configuration

### 5.1 Update Backend CORS
After getting Vercel URL, update backend CORS settings and redeploy

### 5.2 Setup Database Indexes
MongoDB indexes should auto-create, but verify:
```javascript
// Connect via MongoDB Compass or mongosh
db.alerts.getIndexes()
```

### 5.3 Test Full Flow
1. Open frontend
2. Add item with NLP prediction
3. Record donation
4. Run expiry check
5. View alerts
6. Verify data in both databases

---

## Deployment Checklist

- [ ] MySQL deployed to Railway
- [ ] Schema imported with sample data
- [ ] MongoDB Atlas cluster created
- [ ] Database user and network access configured
- [ ] Backend deployed to Render
- [ ] All environment variables set
- [ ] Backend health endpoint responds
- [ ] API documentation accessible
- [ ] Frontend deployed to Vercel
- [ ] Frontend can reach backend API
- [ ] CORS configured correctly
- [ ] All features working end-to-end
- [ ] Error handling tested
- [ ] Performance acceptable

---

## Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl https://your-backend.onrender.com/health

# Database connectivity (add endpoint)
curl https://your-backend.onrender.com/api/stats
```

### Logs
- **Render**: Dashboard → Logs
- **Vercel**: Dashboard → Deployments → View Function Logs
- **Railway**: Dashboard → Deployments → View Logs

### Scaling
- **Render**: Upgrade plan for more resources
- **MongoDB Atlas**: Upgrade cluster tier
- **Railway**: Auto-scales with usage

---

## Cost Estimation

### Free Tier Limits
- **Railway**: $5/month credit (MySQL)
- **MongoDB Atlas**: 512 MB storage (Free tier)
- **Render**: 750 hours/month (Free tier)
- **Vercel**: Unlimited bandwidth (Hobby tier)

**Total Cost**: $0-5/month for small usage

### Upgrade Recommendations
- Railway: Hobby ($5/month) for production MySQL
- MongoDB Atlas: M10 ($0.08/hour) for better performance
- Render: Starter ($7/month) for always-on backend

---

## Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure requirements.txt is up to date
- Check database connectivity

### Frontend can't reach backend
- Verify API_BASE_URL is correct
- Check CORS settings in backend
- Ensure backend is running
- Check browser console for errors

### Database connection fails
- Verify credentials in environment variables
- Check Railway MySQL is running
- Verify MongoDB Atlas IP whitelist
- Test connection locally first

### 502 Bad Gateway
- Backend starting up (wait 30 seconds)
- Check backend logs for errors
- Verify database connections work

---

## Security Best Practices

1. **Never commit `.env` files** - Use .gitignore
2. **Use strong passwords** - For database users
3. **Limit IP access** - MongoDB whitelist specific IPs in production
4. **Enable HTTPS** - Railway, Render, Vercel all provide free SSL
5. **Update dependencies** - Regularly check for security updates
6. **Monitor logs** - Watch for unusual activity
7. **Backup data** - Regular database backups
8. **Environment isolation** - Separate dev/prod databases

---

## Backup Strategy

### Automated Backups
- **Railway**: Built-in backups available
- **MongoDB Atlas**: Point-in-time recovery (paid tiers)

### Manual Backups
```bash
# MySQL (from Railway)
mysqldump -h <host> -P <port> -u <user> -p<password> expiry_donation_db > backup.sql

# MongoDB (to Atlas)
mongodump --uri="mongodb+srv://..." --db=expiry_donation_db
```

---

## Performance Optimization

### Backend
- Enable uvicorn workers in production
- Use connection pooling (already configured)
- Add Redis for caching (optional)

### Frontend
- Vite automatically optimizes build
- Enable compression in Vercel
- Use lazy loading for components

### Database
- Ensure indexes are created (already in schema)
- Monitor query performance
- Consider read replicas for scaling

---

## Success Indicators

✅ All services running and healthy
✅ Frontend accessible via HTTPS
✅ Backend API responding correctly
✅ Data flowing MySQL ↔ Backend ↔ Frontend
✅ MongoDB receiving alert logs
✅ NLP predictions working
✅ No CORS errors
✅ Responsive performance (<2s page loads)

---

**Your app is now live! 🎉**

Frontend: https://your-app.vercel.app
Backend: https://your-backend.onrender.com
API Docs: https://your-backend.onrender.com/docs
