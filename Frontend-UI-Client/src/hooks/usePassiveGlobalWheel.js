// src/hooks/usePassiveGlobalWheel.js
// Optional helper to attach a passive wheel listener if you need to observe wheel without preventing default.
// Use only if you own the listener; many libraries already handle this correctly.
import { useEffect } from 'react';

export function usePassiveGlobalWheel(enabled = false, handler = null) {
  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;
    const onWheel = (e) => {
      // NOTE: Do not call e.preventDefault() in a passive listener
      if (typeof handler === 'function') handler(e);
    };
    window.addEventListener('wheel', onWheel, { passive: true });
    return () => window.removeEventListener('wheel', onWheel);
  }, [enabled, handler]);
}
