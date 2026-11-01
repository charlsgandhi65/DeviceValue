import { ChevronDown, Search } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

export default function SearchableSelect({
  id: idProp,
  label,
  required,
  helperText,
  error,
  placeholder = 'Search or select…',
  options,
  value,
  onChange,
  allowCustom = false,
  customValue = '',
  onCustomChange,
  customPlaceholder = 'Enter custom value',
}) {
  const autoId = useId()
  const id = idProp ?? autoId
  const listId = `${id}-list`
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const containerRef = useRef(null)

  const showCustom = allowCustom && value === 'Other (type below)'
  const filtered = options.filter((opt) =>
    opt.toLowerCase().includes(query.trim().toLowerCase()),
  )

  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={containerRef} className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-slate-200">
        {label}
        {required && <span className="text-blue-400"> *</span>}
      </label>
      {helperText && <p className="text-xs text-slate-500">{helperText}</p>}

      <div className="relative">
        <button
          type="button"
          id={id}
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-controls={listId}
          className={`input-field flex items-center justify-between gap-2 text-left ${error ? 'input-field-error' : ''}`}
          onClick={() => setOpen((o) => !o)}
        >
          <span className={value ? 'text-white' : 'text-slate-500'}>
            {value || placeholder}
          </span>
          <ChevronDown className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`} />
        </button>

        {open && (
          <div
            id={listId}
            role="listbox"
            className="absolute z-30 mt-1 max-h-56 w-full overflow-hidden rounded-xl border border-white/10 bg-navy-800 shadow-xl"
          >
            <div className="flex items-center gap-2 border-b border-white/10 px-3 py-2">
              <Search className="h-4 w-4 text-slate-500" />
              <input
                type="search"
                className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
                placeholder="Filter options…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                autoFocus
              />
            </div>
            <ul className="max-h-44 overflow-y-auto py-1">
              {filtered.length === 0 ? (
                <li className="px-4 py-2 text-sm text-slate-500">No matches</li>
              ) : (
                filtered.map((opt) => (
                  <li key={opt}>
                    <button
                      type="button"
                      role="option"
                      aria-selected={value === opt}
                      className={`w-full px-4 py-2 text-left text-sm transition-colors hover:bg-white/5 ${value === opt ? 'bg-blue-500/15 text-blue-200' : 'text-slate-200'}`}
                      onClick={() => {
                        onChange(opt)
                        setOpen(false)
                        setQuery('')
                      }}
                    >
                      {opt}
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </div>

      {showCustom && (
        <input
          type="text"
          className={`input-field mt-2 ${error ? 'input-field-error' : ''}`}
          placeholder={customPlaceholder}
          value={customValue}
          onChange={(e) => onCustomChange(e.target.value)}
        />
      )}

      {error && (
        <p className="text-xs text-red-400" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
