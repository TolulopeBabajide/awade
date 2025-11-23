/**
 * Input Sanitization Utility
 * 
 * This module provides functions to sanitize and normalize user input
 * to prevent prompt injection and ensure data consistency.
 */

/**
 * Sanitizes a string input by removing dangerous characters and normalizing whitespace.
 * 
 * @param input - The raw input string
 * @returns The sanitized string
 */
export const sanitizeInput = (input: string): string => {
    if (!input) return '';

    // 1. Normalize whitespace (replace multiple spaces/newlines with single space)
    let sanitized = input.replace(/\s+/g, ' ').trim();

    // 2. Remove potential prompt injection patterns
    // This is a basic list and should be expanded based on threat models
    const injectionPatterns = [
        /ignore previous instructions/gi,
        /system prompt/gi,
        /you are a/gi, // Context dependent, but often used in jailbreaks
        /bypass/gi,
        /override/gi
    ];

    injectionPatterns.forEach(pattern => {
        sanitized = sanitized.replace(pattern, '');
    });

    // 3. Strip control characters (except common ones like newline if needed, but we normalized above)
    // Remove non-printable ASCII characters
    sanitized = sanitized.replace(/[\x00-\x1F\x7F]/g, '');

    // 4. Basic HTML escaping (if input is rendered directly, though React handles this mostly)
    // We keep this lightweight as we are primarily concerned with LLM injection here
    sanitized = sanitized
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');

    return sanitized;
};

/**
 * Validates if the input contains any restricted patterns without modifying it.
 * Useful for rejecting input entirely.
 * 
 * @param input - The raw input string
 * @returns True if input is safe, False if it contains restricted patterns
 */
export const validateInput = (input: string): boolean => {
    const injectionPatterns = [
        /ignore previous instructions/gi,
        /system prompt/gi,
    ];

    return !injectionPatterns.some(pattern => pattern.test(input));
};
