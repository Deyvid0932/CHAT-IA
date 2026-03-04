'use client'

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="relative w-6 h-6">
        {/* Outer rotating ring */}
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-emerald-400 border-r-emerald-400 animate-spin"></div>

        {/* Inner dots */}
        <div className="absolute inset-1 rounded-full flex items-center justify-center">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
        </div>
      </div>
    </div>
  )
}
