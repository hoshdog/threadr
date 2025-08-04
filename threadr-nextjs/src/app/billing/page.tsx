'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/hooks/useAuth';

export default function BillingPage() {
  const { user } = useAuth();

  // Mock billing data
  const billingHistory = [
    {
      id: '1',
      date: '2024-01-15',
      description: 'Premium Plan - 30 days',
      amount: '$4.99',
      status: 'Paid'
    },
    {
      id: '2',
      date: '2023-12-15',
      description: 'Premium Plan - 30 days',
      amount: '$4.99',
      status: 'Paid'
    }
  ];

  const usageStats = {
    threadsThisMonth: 15,
    threadsLimit: user?.isPremium ? 'Unlimited' : 20,
    dailyThreads: 3,
    dailyLimit: user?.isPremium ? 'Unlimited' : 5
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Billing & Usage</h1>
            <p className="text-muted-foreground mt-2">
              Manage your subscription and view usage statistics.
            </p>
          </div>

          <div className="grid gap-6">
            {/* Current Plan */}
            <Card>
              <CardHeader>
                <CardTitle>Current Plan</CardTitle>
                <CardDescription>Your active subscription details</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">
                      {user?.isPremium ? '✨ Premium Plan' : '🆓 Free Plan'}
                    </h3>
                    <p className="text-muted-foreground">
                      {user?.isPremium 
                        ? `$4.99/month • Expires ${user.premiumExpiresAt ? new Date(user.premiumExpiresAt).toLocaleDateString() : 'Never'}`
                        : 'Limited features with usage caps'
                      }
                    </p>
                  </div>
                  <div className="text-right">
                    {user?.isPremium ? (
                      <Button variant="secondary">Manage Subscription</Button>
                    ) : (
                      <Button>Upgrade to Premium</Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Usage Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>Usage Statistics</CardTitle>
                <CardDescription>Your current usage and limits</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Monthly Threads</h4>
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold">{usageStats.threadsThisMonth}</span>
                      <span className="text-sm text-muted-foreground">
                        / {usageStats.threadsLimit}
                      </span>
                    </div>
                    {!user?.isPremium && (
                      <div className="w-full bg-muted rounded-full h-2 mt-2">
                        <div 
                          className="bg-accent h-2 rounded-full" 
                          style={{ width: `${(usageStats.threadsThisMonth / 20) * 100}%` }}
                        />
                      </div>
                    )}
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Daily Threads</h4>
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold">{usageStats.dailyThreads}</span>
                      <span className="text-sm text-muted-foreground">
                        / {usageStats.dailyLimit}
                      </span>
                    </div>
                    {!user?.isPremium && (
                      <div className="w-full bg-muted rounded-full h-2 mt-2">
                        <div 
                          className="bg-accent h-2 rounded-full" 
                          style={{ width: `${(usageStats.dailyThreads / 5) * 100}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Billing History */}
            <Card>
              <CardHeader>
                <CardTitle>Billing History</CardTitle>
                <CardDescription>Your payment history and invoices</CardDescription>
              </CardHeader>
              <CardContent>
                {user?.isPremium ? (
                  <div className="space-y-4">
                    {billingHistory.map((invoice) => (
                      <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <p className="font-medium">{invoice.description}</p>
                          <p className="text-sm text-muted-foreground">{invoice.date}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{invoice.amount}</p>
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                            {invoice.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No billing history available</p>
                    <p className="text-sm">Upgrade to Premium to see your payment history</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Upgrade Options */}
            {!user?.isPremium && (
              <Card className="border-accent">
                <CardHeader>
                  <CardTitle>Upgrade to Premium</CardTitle>
                  <CardDescription>Unlock unlimited threads and advanced features</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-2">Premium Features:</h4>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        <li>• Unlimited thread generation</li>
                        <li>• Priority processing</li>
                        <li>• Advanced templates</li>
                        <li>• Thread analytics</li>
                        <li>• Priority support</li>
                      </ul>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2">$4.99</div>
                      <div className="text-sm text-muted-foreground mb-4">per 30 days</div>
                      <Button className="w-full">Upgrade Now</Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}