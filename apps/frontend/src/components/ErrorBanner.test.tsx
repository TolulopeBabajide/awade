import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ErrorBanner from './ErrorBanner'

describe('ErrorBanner (AWD-M-148)', () => {
    it('renders the error message', () => {
        render(<ErrorBanner message="Something went wrong" onDismiss={vi.fn()} />)
        expect(screen.getByRole('alert')).toHaveTextContent('Something went wrong')
    })

    it('has role="alert" so screen readers announce it immediately', () => {
        render(<ErrorBanner message="Error occurred" onDismiss={vi.fn()} />)
        expect(screen.getByRole('alert')).toBeInTheDocument()
    })

    it('calls onDismiss when the dismiss button is clicked', () => {
        const onDismiss = vi.fn()
        render(<ErrorBanner message="Error" onDismiss={onDismiss} />)
        fireEvent.click(screen.getByLabelText('Dismiss error'))
        expect(onDismiss).toHaveBeenCalledTimes(1)
    })

    it('uses the default aria-label "Dismiss error" when dismissLabel is omitted', () => {
        render(<ErrorBanner message="Error" onDismiss={vi.fn()} />)
        expect(screen.getByLabelText('Dismiss error')).toBeInTheDocument()
    })

    it('uses a custom dismissLabel when provided', () => {
        render(
            <ErrorBanner
                message="Load failed"
                onDismiss={vi.fn()}
                dismissLabel="Dismiss load error"
            />
        )
        expect(screen.getByLabelText('Dismiss load error')).toBeInTheDocument()
        expect(screen.queryByLabelText('Dismiss error')).not.toBeInTheDocument()
    })
})
