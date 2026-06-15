# Deployment Guide: Multi-LLM Assistant

This document outlines the steps required to take this application from a local development environment to a production cloud deployment. 

The application consists of three main parts:
1. **Next.js Frontend** (Deployed to Vercel)
2. **FastAPI Backend** (Deployed to Render, Railway, or Google Cloud Run)
3. **Postgres pgvector Database** (Hosted on Supabase or Neon)

*(Note: The codebase has already been fully prepared for production. Environment variables and Dockerfiles are already configured!)*

---

## 1. Provision the Database

You need a managed Postgres database that supports the `pgvector` extension. **Supabase** or **Neon** are excellent free choices.

1. Create a new project/database on Supabase or Neon.
2. In their SQL editor, run this command to enable the vector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy the database connection string they provide (it will look like `postgresql://user:password@host:5432/dbname`).
4. **Important**: Change `postgresql://` to `postgresql+psycopg://` in the URL to ensure compatibility with your SQLAlchemy driver.

---

## 2. Deploy the Backend

You can easily deploy the backend via Docker using a service like **Render** or **Railway**.

1. Create an account on Render (render.com).
2. Create a new "Web Service" and connect your GitHub repository.
3. Set the Root Directory to `backend`.
4. Render will automatically detect the Dockerfile.
5. Add the following **Environment Variables**:
   * `DATABASE_URL`: Your Supabase/Neon connection string (with the `+psycopg` modification).
   * `GROQ_API_KEY`: Your Groq API key.
6. Deploy! Once finished, copy the backend URL (e.g., `https://my-backend.onrender.com`).

*(Note: Don't forget to run `python ingest.py` against your production database at least once by setting the `DATABASE_URL` environment variable locally, so your cloud database gets populated with your PDFs!)*

---

## 3. Deploy the Frontend

**Vercel** is the easiest way to deploy Next.js apps.

1. Go to Vercel (vercel.com) and import your GitHub repository.
2. Set the Root Directory to `frontend`.
3. In the Environment Variables section, add:
   * Key: `NEXT_PUBLIC_API_URL`
   * Value: Your new backend URL (e.g., `https://my-backend.onrender.com`)
4. Click Deploy.

---

🎉 **You're Done!**
Your frontend is now live on Vercel, talking to your FastAPI backend on Render, which is querying your Postgres vector database on Supabase!
