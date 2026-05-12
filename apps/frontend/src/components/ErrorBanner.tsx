import React from 'react';

interface ErrorBannerProps {
    message: string;
    onDismiss: () => void;
    /** Accessible label for the dismiss button. Defaults to "Dismiss error". */
    dismissLabel?: string;
}

/**
 * Shared dismissible error banner for admin pages.
 * Renders as a role="alert" div so screen readers announce the error immediately.
 * Used by ModerationList and UserList (AWD-M-148).
 */
const ErrorBanner: React.FC<ErrorBannerProps> = ({
    message,
    onDismiss,
    dismissLabel = 'Dismiss error',
}) => (
    <div
        role="alert"
        className="flex items-center justify-between rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800"
    >
        <span>{message}</span>
        <button
            onClick={onDismiss}
            aria-label={dismissLabel}
            className="ml-4 text-red-500 hover:text-red-700 font-bold"
        >
            ✕
        </button>
    </div>
);

export default ErrorBanner;
