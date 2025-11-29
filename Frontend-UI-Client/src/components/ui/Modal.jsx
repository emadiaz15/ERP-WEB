// src/components/ui/Modal.jsx
import React, { useEffect, useRef } from 'react';

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  position = 'center',
  maxWidth = 'max-w-xl',
  className = '',
  loading = false,
}) => {
  const modalRef = useRef(null);
  const modalId = useRef(`modal-${Math.random().toString(36).substr(2, 9)}`);
  const titleId = `${modalId.current}-title`;
  const contentId = `${modalId.current}-content`;
  const prevFocusedRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  // Aplicar aria-hidden/pointer-events a los hermanos del overlay (no al propio modal)
  useEffect(() => {
    if (!isOpen) return;
    // Usar ref directamente para evitar conflictos por IDs duplicados
    const overlayEl = modalRef.current;
    if (!overlayEl) return;
    const parent = overlayEl.parentElement || document.body;
    const siblings = Array.from(parent.children).filter((el) => el !== overlayEl);

    // Si el foco quedó fuera del modal, quítalo antes de ocultar
    const active = document.activeElement;
    if (active && !overlayEl.contains(active)) {
      try { active.blur(); } catch {}
    }

    // Evitar usar 'inert' por problemas de selección en algunos navegadores/polyfills
    siblings.forEach((el) => {
      // Marcar que este aria-hidden fue aplicado por el modal
      el.setAttribute('aria-hidden', 'true');
      el.setAttribute('data-aria-hidden-by-modal', 'true');
      // Bloquear interacción visual sin tocar el árbol de accesibilidad
      el.classList.add('pointer-events-none');
    });

    return () => {
      siblings.forEach((el) => {
        if (el.getAttribute('data-aria-hidden-by-modal') === 'true') {
          el.removeAttribute('aria-hidden');
          el.removeAttribute('data-aria-hidden-by-modal');
        }
        el.classList.remove('pointer-events-none');
      });
      // Restaurar foco al elemento previo si sigue en el documento
      const prev = prevFocusedRef.current;
      if (prev && typeof prev.focus === 'function' && document.contains(prev)) {
        try { prev.focus({ preventScroll: true }); } catch {}
      }
    };
  }, [isOpen]);

  // Mover el foco después de ajustar aria-hidden en los hermanos
  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Guardar el elemento previamente enfocado
      prevFocusedRef.current = document.activeElement;

      // Mover foco al primer elemento focusable dentro del modal
      const firstFocusable = modalRef.current.querySelector(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const target = firstFocusable || modalRef.current;
      try {
        target.focus({ preventScroll: true });
      } catch {}
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const positionClasses = {
    center: 'items-center justify-center',
    top: 'items-start justify-center pt-10',
    bottom: 'items-end justify-center pb-10',
    left: 'items-center justify-start pl-10',
    right: 'items-center justify-end pr-10',
  };

  return (
    <div
      id={modalId.current}
      className={`fixed inset-0 z-[9999] flex p-4 bg-black bg-opacity-60 transition-opacity duration-300 ease-in-out ${positionClasses[position]}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? titleId : undefined}
      aria-describedby={contentId}
      tabIndex={-1}
      ref={modalRef}
      onClick={(e) => {
        // Solo cierra si el click fue en el backdrop, no dentro del contenedor
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className={`bg-background-100 p-6 rounded-lg shadow-xl w-full ${maxWidth} relative max-h-[90vh] overflow-visible flex flex-col ${className}`} onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4 flex-shrink-0">
          {title && (
            <h2 id={titleId} className="text-xl md:text-2xl font-semibold text-text-primary">
              {title}
            </h2>
          )}
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-400 rounded-full p-1 ml-auto"
            aria-label="Cerrar modal"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Contenido */}
        <div id={contentId} className="text-text-primary overflow-y-auto relative">
          {loading && (
            <div className="absolute inset-0 bg-white/60 dark:bg-black/40 flex items-center justify-center z-10">
              <svg className="animate-spin h-8 w-8 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
              </svg>
            </div>
          )}
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
