'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/hooks/useAuth';

export default function AccountPage() {
  const { user, updateProfile } = useAuth();

  const handleSaveProfile = () => {
    // Profile update logic will be implemented
    console.log('Save profile clicked');
  };

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="border-b border-x-border pb-6">
        <h1 className="text-2xl font-bold text-white mb-2">Account Settings</h1>
        <p className="text-x-gray">
          Manage your account preferences and profile information.
        </p>
      </div>

      <div className="grid gap-6">
        {/* Profile Information */}
        <Card className="bg-x-dark border-x-border">
          <CardHeader>
            <CardTitle className="text-white">Profile Information</CardTitle>
            <CardDescription className="text-x-gray">Update your personal information and preferences.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-white">Email</label>
                <Input 
                  type="email" 
                  value={user?.email || ''} 
                  disabled 
                  className="bg-x-hover border-x-border text-x-gray"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-white">Username</label>
                <Input 
                  type="text" 
                  placeholder="Enter username" 
                  value={user?.username || ''} 
                  className="bg-x-dark border-x-border text-white placeholder:text-x-gray"
                />
              </div>
            </div>
            <Button onClick={handleSaveProfile} className="bg-x-blue hover:bg-x-blue/90">
              Save Changes
            </Button>
          </CardContent>
        </Card>

        {/* Subscription Status */}
        <Card className="bg-x-dark border-x-border">
          <CardHeader>
            <CardTitle className="text-white">Subscription Status</CardTitle>
            <CardDescription className="text-x-gray">Your current plan and billing information.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-white">
                  {user?.isPremium ? '✨ Premium Plan' : '🆓 Free Plan'}
                </p>
                <p className="text-sm text-x-gray">
                  {user?.isPremium 
                    ? `Expires: ${user.premiumExpiresAt ? new Date(user.premiumExpiresAt).toLocaleDateString() : 'Never'}` 
                    : 'Limited to 5 threads per day'
                  }
                </p>
              </div>
              {!user?.isPremium && (
                <Button className="bg-amber-500 hover:bg-amber-600 text-black font-medium">
                  Upgrade to Premium
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Usage Statistics */}
        <Card className="bg-x-dark border-x-border">
          <CardHeader>
            <CardTitle className="text-white">Usage Statistics</CardTitle>
            <CardDescription className="text-x-gray">Your current usage for this period.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-x-hover rounded-lg">
                <div className="text-2xl font-bold text-white">0</div>
                <div className="text-sm text-x-gray">Threads Today</div>
                <div className="text-xs text-x-gray">{user?.isPremium ? 'Unlimited' : '5 remaining'}</div>
              </div>
              <div className="text-center p-4 bg-x-hover rounded-lg">
                <div className="text-2xl font-bold text-white">0</div>
                <div className="text-sm text-x-gray">This Month</div>
                <div className="text-xs text-x-gray">{user?.isPremium ? 'Unlimited' : '20 remaining'}</div>
              </div>
              <div className="text-center p-4 bg-x-hover rounded-lg">
                <div className="text-2xl font-bold text-white">0</div>
                <div className="text-sm text-x-gray">Total Threads</div>
                <div className="text-xs text-x-gray">All time</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Actions */}
        <Card className="bg-x-dark border-x-border">
          <CardHeader>
            <CardTitle className="text-white">Account Actions</CardTitle>
            <CardDescription className="text-x-gray">Manage your account settings and data.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-x-hover rounded-lg">
              <div>
                <p className="font-medium text-white">Export Data</p>
                <p className="text-sm text-x-gray">Download all your threads and data</p>
              </div>
              <Button variant="secondary" className="bg-transparent border-x-border text-white hover:bg-x-hover">
                Export
              </Button>
            </div>
            <div className="flex items-center justify-between p-4 bg-x-hover rounded-lg">
              <div>
                <p className="font-medium text-red-400">Delete Account</p>
                <p className="text-sm text-x-gray">Permanently delete your account and all data</p>
              </div>
              <Button 
                variant="secondary" 
                className="bg-transparent border-red-600 text-red-400 hover:bg-red-600/10 hover:text-red-300"
              >
                Delete
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}