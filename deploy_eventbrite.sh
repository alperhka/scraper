#!/bin/bash

echo "🚀 Deploying Eventbrite Sync Function..."

# Deploy the function
supabase functions deploy eventbrite-sync

echo "✅ Deployment requested."
echo "⚠️ Don't forget to set your secrets in Supabase Dashboard or via CLI:"
echo "supabase secrets set EVENTBRITE_TOKEN=your_token"
echo "supabase secrets set EVENTBRITE_ORG_ID=your_org_id"
