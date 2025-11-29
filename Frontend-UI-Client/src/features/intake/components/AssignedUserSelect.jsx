import React, { useState, useRef, useEffect, useMemo } from 'react';
import { filterUsers } from '@/features/user/services/filterUsers';

const AssignedUserSelect = ({ label = 'Asignado a', value, onChange, required, onUsersLoaded }) => {
  const [open, setOpen] = useState(false);
  const [users, setUsers] = useState([]);
  const [query, setQuery] = useState('');
  const anchorRef = useRef(null);
  const popRef = useRef(null);

  useEffect(() => {
    let active = true;
    filterUsers({ is_active: 'true', page_size: 1000 })
      .then(res => {
        if (!active) return;
        const results = res?.results || res?.data || res || [];
        setUsers(results);
        onUsersLoaded?.(results);
      })
      .catch(() => {});
    return () => { active = false; };
  }, [onUsersLoaded]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return users;
    return users.filter(u => {
      const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.toLowerCase().trim();
      return full.includes(q) || (u.username || '').toLowerCase().includes(q) || (u.email || '').toLowerCase().includes(q);
    });
  }, [users, query]);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e) => {
      if (e.key === 'Escape') { setOpen(false); return; }
      if (popRef.current && !popRef.current.contains(e.target) && !anchorRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onDoc);
    document.addEventListener('keydown', onDoc);
    return () => {
      document.removeEventListener('mousedown', onDoc);
      document.removeEventListener('keydown', onDoc);
    };
  }, [open]);

  const currentLabel = useMemo(() => {
    if (!value) return required ? 'Seleccione usuario...' : 'Sin asignar';
    const u = users.find(u => String(u.id) === String(value));
    if (!u) return '—';
    const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.trim();
    return full || u.username || u.email || `ID ${u.id}`;
  }, [value, users, required]);

  return (
    <div className="mb-4 relative" ref={anchorRef}>
      <label className="block text-sm font-medium text-text-secondary">
        {label}{required && <span className="text-error-500"> *</span>}
      </label>
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        className={`mt-1 w-full px-3 py-2 border rounded-md text-left text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200 bg-white flex items-center justify-between ${open ? 'ring-2 ring-primary-500' : ''}`}
      >
        <span className={`truncate mr-2 ${!value ? 'text-text-secondary' : ''}`}>{currentLabel}</span>
        <svg className={`w-5 h-5 text-gray-500 transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.21 8.29a.75.75 0 01.02-1.08z" clipRule="evenodd" /></svg>
      </button>
      {open && (
        <div ref={popRef} className="absolute z-50 mt-1 w-full max-h-64 overflow-y-auto rounded-md border border-background-200 bg-white shadow-lg">
          <div className="p-2 border-b bg-background-100 sticky top-0">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar usuario..."
              className="w-full px-2 py-1 text-sm border border-background-200 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <ul className="py-1 text-sm">
            {filtered.map(u => {
              const id = String(u.id);
              const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.trim();
              return (
                <li key={id}>
                  <button
                    type="button"
                    onClick={() => { onChange(id); setOpen(false); }}
                    className={`w-full text-left px-3 py-2 hover:bg-primary-50 ${String(value) === id ? 'bg-primary-100 font-medium' : ''}`}
                  >
                    {full || u.username || u.email || `ID ${id}`}
                  </button>
                </li>
              );
            })}
            {filtered.length === 0 && (
              <li className="px-3 py-2 text-xs text-muted-foreground">Sin resultados</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AssignedUserSelect;
