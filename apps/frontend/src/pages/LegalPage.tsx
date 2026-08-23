import { Link } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';

type LegalPageKind = 'terms' | 'privacy';

interface LegalPageProps {
  kind: LegalPageKind;
}

const LegalPage = ({ kind }: LegalPageProps) => {
  const isPrivacy = kind === 'privacy';

  return (
    <main className="min-h-screen bg-primary-50 px-4 py-8 sm:px-6 sm:py-12">
      <article className="mx-auto max-w-3xl rounded-2xl border border-primary-100 bg-white p-6 shadow-sm sm:p-10">
        <Link
          to="/signup"
          className="mb-8 inline-flex min-h-11 items-center gap-2 rounded-lg px-3 text-sm font-semibold text-primary-700 hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          <FaArrowLeft aria-hidden="true" />
          Back to create account
        </Link>

        <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-primary-600">Awade</p>
        <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
          {isPrivacy ? 'Privacy Policy' : 'Terms & Conditions'}
        </h1>
        <p className="mt-3 text-sm text-gray-500">Last updated 22 August 2026</p>

        {isPrivacy ? (
          <div className="mt-8 space-y-7 text-base leading-7 text-gray-700">
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Information we collect</h2>
              <p className="mt-2">We collect account details and the learning information parents or educators choose to provide. Child information is provided by a parent or guardian; Awade does not ask children to create accounts.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">How we use information</h2>
              <p className="mt-2">We use this information to provide learning guides, lesson-planning tools, account support, security, and service improvements. We do not sell personal information.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Your choices</h2>
              <p className="mt-2">You may request access, correction, export, or deletion of your information. Parents and guardians may also review or delete information associated with a child profile.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Safety and retention</h2>
              <p className="mt-2">We limit access to personal information, retain it only as needed to provide the service or meet legal obligations, and apply safeguards appropriate to the information involved.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Questions</h2>
              <p className="mt-2">For privacy questions or data requests, contact the Awade support team through the contact details provided on the main website.</p>
            </section>
          </div>
        ) : (
          <div className="mt-8 space-y-7 text-base leading-7 text-gray-700">
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Using Awade</h2>
              <p className="mt-2">You must provide accurate account information, keep your account secure, and use Awade only for lawful educational purposes. Parents or guardians must manage profiles for children.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Learning content</h2>
              <p className="mt-2">Awade provides educational support, not a replacement for professional teaching or safeguarding judgement. Review generated material before using it with a learner.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Acceptable use</h2>
              <p className="mt-2">Do not misuse the service, attempt unauthorised access, submit harmful material, or use Awade in a way that infringes another person’s rights.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Availability</h2>
              <p className="mt-2">We work to keep Awade reliable, but the service may occasionally change or be unavailable. We may restrict accounts that threaten users, learners, or the service.</p>
            </section>
            <section>
              <h2 className="text-xl font-semibold text-gray-900">Privacy</h2>
              <p className="mt-2">Our <Link to="/privacy-policy" className="font-semibold text-primary-700 underline">Privacy Policy</Link> explains how personal information is handled.</p>
            </section>
          </div>
        )}
      </article>
    </main>
  );
};

export default LegalPage;
