'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Logo from '@/components/ui/Logo';

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-slate-900">
      {/* Navigation Header */}
      <nav className="w-full py-6 px-4 border-b border-gray-100 dark:border-gray-800">
        <div className="container mx-auto flex items-center justify-between">
          <Link href="/">
            <Logo variant="black" size="lg" showText clickable />
          </Link>
          <Link 
            href="/" 
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            ← Back to Home
          </Link>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
            <CardHeader className="text-center pb-8">
              <CardTitle className="text-3xl font-bold text-gray-900 mb-4">
                Privacy Policy
              </CardTitle>
              <p className="text-gray-600">
                Last updated: {new Date().toLocaleDateString()}
              </p>
            </CardHeader>
            
            <CardContent className="prose prose-gray max-w-none">
              <div className="space-y-8">
                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Information We Collect</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We collect information you provide directly to us, such as when you create an account, 
                      use our service, or contact us for support.
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li><strong>Account Information:</strong> Email address, username, and password</li>
                      <li><strong>Content:</strong> URLs and text content you submit for thread generation</li>
                      <li><strong>Usage Data:</strong> Information about how you use our service</li>
                      <li><strong>Payment Information:</strong> Billing details processed securely through Stripe</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">How We Use Your Information</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>We use the information we collect to:</p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Provide, maintain, and improve our service</li>
                      <li>Process your requests for thread generation</li>
                      <li>Communicate with you about your account and our service</li>
                      <li>Monitor and analyze trends and usage</li>
                      <li>Detect, investigate and prevent fraudulent transactions</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Information Sharing</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We do not sell, trade, or otherwise transfer your personal information to third parties, 
                      except in the following circumstances:
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li><strong>Service Providers:</strong> We may share information with trusted third-party service providers who assist us in operating our service</li>
                      <li><strong>Legal Requirements:</strong> We may disclose information when required by law or to protect our rights</li>
                      <li><strong>AI Processing:</strong> Content submitted for thread generation is processed by OpenAI's API services</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Security</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We implement appropriate technical and organizational security measures to protect your 
                      personal information against unauthorized access, alteration, disclosure, or destruction.
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Encrypted data transmission using HTTPS</li>
                      <li>Secure password hashing</li>
                      <li>Regular security updates and monitoring</li>
                      <li>Limited access to personal data by authorized personnel only</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Retention</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We retain your information for as long as your account is active or as needed to provide 
                      you services. We will delete your personal information when you delete your account, 
                      subject to applicable legal requirements.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Rights</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>You have the right to:</p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Access and update your personal information</li>
                      <li>Delete your account and associated data</li>
                      <li>Opt out of certain communications</li>
                      <li>Request a copy of your data</li>
                      <li>Object to processing of your personal information</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Cookies and Tracking</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We use cookies and similar tracking technologies to provide and improve our service. 
                      You can control cookie preferences through your browser settings.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Changes to This Policy</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We may update this privacy policy from time to time. We will notify you of any changes 
                      by posting the new privacy policy on this page and updating the "Last updated" date.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Us</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      If you have any questions about this privacy policy, please contact us at:
                    </p>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p><strong>Email:</strong> privacy@threadr.app</p>
                      <p><strong>Website:</strong> https://threadr.app</p>
                    </div>
                  </div>
                </section>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}