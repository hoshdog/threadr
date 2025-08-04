'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/hooks/useAuth';

export default function AnalyticsPage() {
  const { user } = useAuth();

  // Mock analytics data
  const stats = {
    totalThreads: 42,
    totalViews: 1240,
    avgEngagement: 8.5,
    topThread: 'How to Build a SaaS in 2024'
  };

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="border-b border-x-border pb-6">
        <h1 className="text-2xl font-bold text-white mb-2">Analytics Dashboard</h1>
        <p className="text-x-gray">
          Track your thread performance and engagement metrics.
        </p>
      </div>

      {!user?.isPremium ? (
        <Card className="border-accent bg-x-dark">
          <CardHeader>
            <CardTitle className="text-white">Premium Feature</CardTitle>
            <CardDescription className="text-x-gray">
              Analytics are available for Premium subscribers only.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-x-gray mb-4">
              Upgrade to Premium to access detailed analytics including:
            </p>
            <ul className="list-disc list-inside text-sm text-x-gray space-y-1 mb-6">
              <li>Thread performance metrics</li>
              <li>Engagement tracking</li>
              <li>Audience insights</li>
              <li>Historical data trends</li>
            </ul>
            <Button className="bg-x-blue hover:bg-x-blue/90">
              Upgrade to Premium
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-x-dark border-x-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-x-gray">Total Threads</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{stats.totalThreads}</div>
                <p className="text-xs text-x-gray">+12% from last month</p>
              </CardContent>
            </Card>

            <Card className="bg-x-dark border-x-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-x-gray">Total Views</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{stats.totalViews.toLocaleString()}</div>
                <p className="text-xs text-x-gray">+8% from last month</p>
              </CardContent>
            </Card>

            <Card className="bg-x-dark border-x-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-x-gray">Avg Engagement</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{stats.avgEngagement}%</div>
                <p className="text-xs text-x-gray">+2.1% from last month</p>
              </CardContent>
            </Card>

            <Card className="bg-x-dark border-x-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-x-gray">Top Performer</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm font-bold truncate text-white">{stats.topThread}</div>
                <p className="text-xs text-x-gray">245 views</p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card className="bg-x-dark border-x-border">
            <CardHeader>
              <CardTitle className="text-white">Recent Thread Performance</CardTitle>
              <CardDescription className="text-x-gray">Your latest threads and their metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-x-gray">
                <div className="text-4xl mb-4">📊</div>
                <p className="font-medium">Thread analytics data will appear here</p>
                <p className="text-sm">Create more threads to see detailed analytics</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}