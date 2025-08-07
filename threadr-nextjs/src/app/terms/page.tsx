'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Logo from '@/components/ui/Logo';

export default function TermsOfServicePage() {
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
                Terms of Service
              </CardTitle>
              <p className="text-gray-600">
                Last updated: {new Date().toLocaleDateString()}
              </p>
            </CardHeader>
            
            <CardContent className="prose prose-gray max-w-none">
              <div className="space-y-8">
                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Acceptance of Terms</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      By accessing and using Threadr ("Service"), you accept and agree to be bound by the 
                      terms and provision of this agreement. If you do not agree to abide by the above, 
                      please do not use this service.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Description of Service</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      Threadr is an AI-powered service that converts articles, blog posts, and other content 
                      into Twitter thread format. The service includes:
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Content analysis and thread generation</li>
                      <li>Thread editing and customization tools</li>
                      <li>Templates and formatting options</li>
                      <li>Analytics and performance tracking</li>
                      <li>Premium features for enhanced functionality</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">User Accounts</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      To access certain features of the Service, you must register for an account. You agree to:
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Provide accurate, current and complete information</li>
                      <li>Maintain the security of your password</li>
                      <li>Accept responsibility for all activities under your account</li>
                      <li>Notify us immediately of any breach of security</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Acceptable Use</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>You agree not to use the Service to:</p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Generate content that is illegal, harmful, threatening, abusive, or defamatory</li>
                      <li>Violate any laws or regulations</li>
                      <li>Infringe on intellectual property rights</li>
                      <li>Distribute spam or unsolicited communications</li>
                      <li>Attempt to gain unauthorized access to the Service</li>
                      <li>Use the Service for any commercial purpose without permission</li>
                      <li>Generate content that promotes hate speech or discrimination</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Content and Intellectual Property</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      You retain ownership of content you submit to the Service. By submitting content, you grant 
                      us a limited license to use, process, and display your content solely for the purpose of 
                      providing the Service.
                    </p>
                    <p>
                      The Service and its original content, features, and functionality are owned by Threadr and 
                      are protected by international copyright, trademark, patent, trade secret, and other 
                      intellectual property laws.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Subscription and Payment</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      Some features of the Service require a paid subscription:
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>Subscription fees are billed in advance on a monthly or annual basis</li>
                      <li>All fees are non-refundable except as required by law</li>
                      <li>We may change subscription fees with 30 days notice</li>
                      <li>You may cancel your subscription at any time</li>
                      <li>Payment processing is handled securely through Stripe</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">AI and Third-Party Services</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      Our Service uses artificial intelligence (OpenAI's GPT) to generate content. You acknowledge that:
                    </p>
                    <ul className="list-disc pl-6 space-y-2">
                      <li>AI-generated content may not always be accurate or appropriate</li>
                      <li>You are responsible for reviewing and editing generated content</li>
                      <li>We cannot guarantee the quality or accuracy of AI-generated content</li>
                      <li>Your content may be processed by third-party AI services</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Disclaimers</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      THE SERVICE IS PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS. WE EXPRESSLY DISCLAIM 
                      ALL WARRANTIES OF ANY KIND, WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING THE IMPLIED 
                      WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT.
                    </p>
                    <p>
                      We do not warrant that the Service will be uninterrupted, timely, secure, or error-free.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Limitation of Liability</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      IN NO EVENT SHALL THREADR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL 
                      OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION, LOSS OF PROFITS, DATA, USE, GOODWILL, 
                      OR OTHER INTANGIBLE LOSSES, RESULTING FROM YOUR USE OF THE SERVICE.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Termination</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We may terminate or suspend your account and bar access to the Service immediately, 
                      without prior notice or liability, under our sole discretion, for any reason whatsoever 
                      and without limitation, including but not limited to a breach of the Terms.
                    </p>
                    <p>
                      Upon termination, your right to use the Service will cease immediately.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Governing Law</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      These Terms shall be interpreted and governed by the laws of the jurisdiction in which 
                      we operate, without regard to its conflict of law provisions.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Changes to Terms</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      We reserve the right to modify these terms at any time. We will notify users of any 
                      changes by posting the new Terms of Service on this page and updating the "Last updated" date.
                    </p>
                    <p>
                      Your continued use of the Service after any modifications indicates your acceptance of 
                      the new Terms of Service.
                    </p>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
                  <div className="text-gray-700 space-y-3">
                    <p>
                      If you have any questions about these Terms of Service, please contact us:
                    </p>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p><strong>Email:</strong> legal@threadr.app</p>
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