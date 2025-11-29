// jest.setup.js
// Mock global para import.meta.env en tests con Jest
if (typeof global.import === 'undefined') {
  global.import = { meta: { env: { VITE_API_BASE_URL: "/api/v1" } } };
}

// Polyfill: scrollIntoView (usado por Radix Select)
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = function scrollIntoView() { /* noop for jsdom */ };
}

// Polyfill: ResizeObserver (usado por Floating UI / Radix)
if (typeof global.ResizeObserver === 'undefined') {
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

// Polyfill: MutationObserver si faltara (algunas lib lo tocan)
if (typeof global.MutationObserver === 'undefined') {
  global.MutationObserver = class {
    constructor() {}
    observe() {}
    disconnect() {}
    takeRecords() { return []; }
  };
}

// Silenciar warnings ruidosos de React Router v7 future flags en tests
const originalWarn = global.console.warn;
global.console.warn = (...args) => {
  const msg = String(args[0] || "");
  if (msg.includes('React Router Future Flag Warning')) return;
  originalWarn(...args);
};

// Silenciar logs ruidosos de Axios en tests (solo caso conocido de productos)
const originalError = global.console.error;
global.console.error = (...args) => {
  const msg = String(args[0] || "");
  if (msg.includes('Error al obtener productos') && msg.includes('AxiosError')) return;
  originalError(...args);
};
